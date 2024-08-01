from marshmallow import fields, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class AccountSchema(SQLAlchemyAutoSchema):
    fullname = fields.Str()
    age = fields.Int()
    email = fields.Email()

    @validates("age")
    def validate_age(self, age):
        if age > 120:
            raise ValidationError("Age is too old")
        elif age < 10 and age != 0:
            raise ValidationError("Age is too young")


class TempSchema(SQLAlchemyAutoSchema):
    fullname = fields.Str()
    age = fields.Int()
    email = fields.Email()

    @validates("age")
    def validate_age(self, age):
        if age > 120:
            raise ValidationError("Age is too old")
        elif age < 10:
            raise ValidationError("Age is too young")


class OtpSchema(SQLAlchemyAutoSchema):
    email = fields.Email()
    otp = fields.Int()
