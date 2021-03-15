"""Pytest common fixtures."""
import asyncio
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from database.models import main
from main import app

basedir = os.path.abspath(os.path.dirname(__file__))
db_filename = os.path.join(basedir, "test.db")


@pytest.fixture()
def test_client():
    """Test client."""
    return TestClient(app)


@pytest.fixture()
def engine():
    """DB engine."""
    return create_async_engine("sqlite:///" + db_filename)


@pytest.fixture()
def session(engine):
    """DB session."""
    return AsyncSession(engine)
    # os.remove(db_filename)


@pytest.fixture()
def database(engine, session):
    """Create test database and yield its session."""
    with patch("database.models.engine", engine):
        with patch("database.models.session", session) as session:
            asyncio.run(main(test=True))
            yield session
            os.remove(db_filename)
