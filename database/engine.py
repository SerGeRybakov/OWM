"""Database engine module."""
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


basedir = os.path.abspath(os.path.dirname(__file__))
filename = os.path.join(basedir, "prod.db")
engine = create_async_engine("sqlite:///" + filename, echo=False)
session = AsyncSession(engine)
