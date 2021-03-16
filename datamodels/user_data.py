"""Models for mapping request data."""
from pydantic.main import BaseModel

__all__ = ["UserData"]


class UserData(BaseModel):
    """Map login and register data from request."""

    username: str
    password: str
