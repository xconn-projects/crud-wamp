import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marshmallow import ValidationError
from xconn import XConnApp
from xconn.types import Invocation, Result
from xconn.exception import ApplicationError

from models import Base, TempAccount, Otp
from serializers import TempSchema

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
