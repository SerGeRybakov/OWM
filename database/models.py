"""Database tables."""

import asyncio
import json
import os

from passlib.context import CryptContext
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from database.engine import engine, session

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """Table for storing users."""

    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    def __init__(self, username: str, password: str, id_: int = None):
        self.id = id_
        self.username = username
        self.password = self.get_password_hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class Object(Base):
    """Table for storing objects.

    One object can be bound to one user only.
    """

    __tablename__ = "object"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __init__(self, title: str, user_id: int, id_: int = None):
        self.id = id_
        self.title = title
        self.user_id = user_id


class UserToken(Base):
    """Table for storing users' access tokens.

    Constraint: user shall have just one token.
    If user logs in from different devices at the same time, just one token from the latest log-in will be stored.
    All the other tokens will be automatically revoked even if they are valid.
    """

    __tablename__ = "user_token"
    token = Column(String(255), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, nullable=False, unique=True)


async def main():
    """Create database and fill it with basic inserts."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    table_to_model_mapping = {"User": User, "Object": Object}

    with open(os.path.join(os.path.dirname(__file__), "initial_load.json"), "r", encoding="utf-8") as file:
        load = [table_to_model_mapping[dic["model"]](**dic["fields"]) for dic in json.load(file)]

    async with session:
        for model in load:
            session.add(model)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
