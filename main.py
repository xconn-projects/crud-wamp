import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from marshmallow import ValidationError
from xconn import XConnApp
from xconn.types import Invocation, Result
from xconn.exception import ApplicationError

from models import Base, TempAccount, Otp, Account
from serializers import TempSchema, OtpSchema, AccountSchema

engine = create_engine('sqlite:///user.db', echo=False)
session = sessionmaker(bind=engine)
with engine.begin() as conn:
    Base.metadata.create_all(conn)

app = XConnApp()


@app.register("io.xconn.account.create")
def create(invocation: Invocation) -> Result:
    temp_schema = TempSchema()
    otp_value = random.randint(10000, 99999)

    if invocation.args is None or len(invocation.args) != 3:
        raise ApplicationError("io.xconn.invalid_argument",
                               ["Exactly 3 arguments are required: fullname, age, email"])

    data = {
        "fullname": invocation.args[0],
        "age": invocation.args[1],
        "email": invocation.args[2]
    }

    try:
        validated_data = temp_schema.load(data)
    except ValidationError as err:
        raise ApplicationError("io.xconn.invalid_argument", [str(err)])

    temp_account = TempAccount(**validated_data)
    otp = Otp(otp=otp_value, email=validated_data['email'])
    print(otp_value)

    with session() as sess:
        sess.add(temp_account)
        sess.add(otp)
        sess.commit()
        return Result(args=[temp_schema.dump(temp_account)])


@app.register("io.xconn.account.activate")
def activate(invocation: Invocation) -> Result:
    if len(invocation.args) != 2:
        raise Exception("Exactly 2 arguments are required: fullname, email")

    data = {
        "email": invocation.args[0],
        "otp": invocation.args[1],
    }
    otp_schema = OtpSchema()

    try:
        validated_data = otp_schema.load(data)
    except ValidationError as err:
        raise Exception(err)

    otp_query = select(Otp.otp).where(Otp.email == validated_data["email"])
    account_query = select(TempAccount).where(TempAccount.email == validated_data["email"])

    with session() as sess:
        otp_result = sess.execute(otp_query)
        result = otp_result.scalars().first()
        if result is None:
            raise Exception("email not exists")
        if result != validated_data["otp"]:
            raise Exception("incorrect otp")
        temp_account = sess.execute(account_query)
        result_account = temp_account.scalars().first()
        account_schema = AccountSchema()
        sess.add(Account(fullname=result_account.fullname, age=result_account.age, email=result_account.email))
        sess.delete(result_account)
        sess.commit()
        return Result(args=[account_schema.dump(result_account)])


@app.register("io.xconn.account.get")
def get(invocation: Invocation) -> Result:
    if len(invocation.args) != 1:
        raise Exception("Exactly 1 argument is required: email")

    email = invocation.args[0]

    query = select(Account).where(Account.email == email)

    with session() as sess:
        account_schema = AccountSchema()
        account = sess.execute(query)

        result = account.scalars().first()
        if result is None:
            raise Exception("email not exists")

        return Result(args=[account_schema.dump(result)])
