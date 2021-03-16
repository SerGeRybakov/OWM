"""Models for mapping request data."""
from pydantic.main import BaseModel

__all__ = ["UserData", "ItemData"]


class UserData(BaseModel):
    """Map login and register data from request."""

    username: str
    password: str


class ItemData(BaseModel):
    """Map item data from request."""

    title: str
