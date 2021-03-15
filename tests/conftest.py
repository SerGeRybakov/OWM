"""Pytest common fixtures."""
import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

basedir = os.path.abspath(os.path.dirname(__file__))
db_filename = os.path.join(basedir, "test.db")


@pytest.fixture()
def session(engine):
    """DB session."""
    yield AsyncSession(engine)
    os.remove(db_filename)


@pytest.fixture()
def engine():
    """DB engine."""
    return create_async_engine("sqlite:///" + db_filename)
