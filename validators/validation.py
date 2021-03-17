"""Username and password validators."""

import re

from sqlalchemy import select

from database.engine import session
from database.models import User

__all__ = ["ValidationError", "validate"]


class ValidationError(Exception):
    """Validation error."""

    pass


async def __validate(credentials):
    """Starts validation."""
    username = credentials.username
    password = credentials.password
    try:
        await __validate_username(username)
        await __validate_password(password)
        return True
    except ValueError as e:
        raise ValidationError(e.args[0])


async def __validate_username(username):
    """Validates username is unique."""
    async with session:
        query = select(User.id).where(User.username == username)
        result = await session.execute(query)
    user = result.scalars().first()
    if user:
        raise ValueError(f"Username '{username}' has been already registered by another user")
    return True


async def __validate_password(password):
    """Validates password."""
    try:
        if all(
            (
                await __check_letters(password),
                await __check_len(password),
                await __check_ascii(password),
                await __check_nums(password),
                await __check_punctuation(password),
                await __check_case(password),
            )
        ):
            return True
    except ValueError as e:
        raise ValueError(e.args[0])


async def __check_ascii(password: str) -> bool:
    """All symbols must be ASCII."""
    if password.isascii():
        return True
    raise ValueError("Weak password: Letters must be ASCII")


async def __check_len(password: str) -> bool:
    """Password length must be from 8 to 14."""
    if 8 <= len(password) <= 14:
        return True
    raise ValueError("Weak password: Password length should be at least 8 but no more than 14 symbols")


async def __check_nums(password: str) -> bool:
    """Check if numbers are in password."""
    if re.findall(r"\d", password):
        return True
    raise ValueError("Weak password: At least one digit is required")


async def __check_letters(password: str) -> bool:
    """Check if letters are in password."""
    from unicodedata import category

    if any(category(i).startswith("L") for i in password):
        return True
    raise ValueError("Weak password: At least two letters are required")


async def __check_punctuation(password: str) -> bool:
    """Check if punctuation signs are in password."""
    if re.findall(r"\W|_", password):
        return True
    raise ValueError("Weak password: At least one punctuation sign is required")


async def __check_case(password: str) -> bool:
    """Check if letters of different case are in password."""
    if password != password.upper() and password != password.lower():
        return True
    raise ValueError("Weak password: Letters must be in different case")


async def validate(credentials):
    """Validate new user's credentials."""
    try:
        if credentials is None or not credentials.username or not credentials.password:
            raise ValueError("Both username and password required")
        return await __validate(credentials)
    except ValueError as e:
        raise ValidationError(e.args[0])
