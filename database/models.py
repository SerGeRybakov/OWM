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

    def __repr__(self):
        return f"{__class__.__name__}({self.username})"

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class Item(Base):
    """Table for storing objects.

    One object can be bound to one user only.
    """

    __tablename__ = "item"
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

    def __init__(self, token: str, user_id: int):
        self.token = token
        self.user_id = user_id


async def main(test: bool = False):
    """Create database and fill it with basic inserts."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    table_to_model_mapping = {"User": User, "Item": Item}
    filename = "initial_load.json" if not test else "test_load.json"
    with open(os.path.join(os.path.dirname(__file__), "fixtures", filename), "r", encoding="utf-8") as f:
        load = [table_to_model_mapping[dic["model"]](**dic["fields"]) for dic in json.load(f)]

    async with session:
        for model in load:
            session.add(model)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
