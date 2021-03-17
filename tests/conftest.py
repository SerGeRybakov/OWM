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


@pytest.fixture(scope="module")
def test_client():
    """Test client."""
    return TestClient(app)


@pytest.fixture(scope="module")
def engine():
    """DB engine."""
    return create_async_engine("sqlite:///" + db_filename)


@pytest.fixture(scope="module")
def session(engine):
    """DB session."""
    return AsyncSession(engine)


@pytest.fixture(scope="module")
def test_session(engine, session):
    """Create test database and yield its session."""
    with patch("database.models.engine", engine):
        with patch("database.models.session", session) as session:
            asyncio.run(main(test=True))
            yield session
            os.remove(db_filename)


@pytest.fixture(scope="module")
def token(test_client, test_session):
    """Get test user login token."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": "testuser1", "password": "Qwerty123_"}
            response = test_client.post("api/v1/login", data=payload).json()
            return response["access_token"]
