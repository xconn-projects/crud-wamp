from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    fullname = Column(String(50))
    age = Column(Integer)
    email = Column(String(100), unique=True)


class TempAccount(Base):
    __tablename__ = "temp_account"
    id = Column(Integer, primary_key=True)
    fullname = Column(String(50))
    age = Column(Integer)
    email = Column(String(100), unique=True)
    relationship("Otp", cascade='all, delete', uselist=False)


class Otp(Base):
    __tablename__ = "otp"
    id = Column(Integer, primary_key=True)
    otp = Column(Integer())
    email = Column(String(), ForeignKey('account.email'), unique=True)
