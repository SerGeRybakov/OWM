"""Test models module."""

from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Object, User, main


@pytest.mark.asyncio
@pytest.mark.parametrize(("title", "user_id"), [("object1-1", 1), ("object1-2", 1), ("object2-1", 2), ("object2-2", 2)])
async def test_main_function(engine, session: AsyncSession, title, user_id):
    """Test database is created and primary inserts are done."""
    with patch("database.models.engine", engine):
        with patch("database.models.session", session) as session:
            await main()

    async with session:
        query = select(Object).where(Object.title == title)
        result = await session.execute(query)
    object = result.scalars().one()
    assert object.user_id == user_id


@pytest.mark.parametrize("example", ["Qwerty", "123456", "", " "])
def test_hash_password(example):
    """Test user password is being hashed."""
    user = User("test", example)
    assert example != user.get_password_hash(example)
    assert example != user.password


@pytest.mark.parametrize("example", ["Qwerty", "123456", "", " "])
def test_verify_hashed_password(example):
    """Test user password hash is being verified."""
    user = User("test", example)
    assert user.verify_password(example, user.password)


if __name__ == "__main__":
    pytest.main()
