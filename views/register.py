"""View for users register."""
from fastapi import APIRouter, HTTPException

from database.engine import session
from database.models import User
from database.validator import ValidationError, validate
from datamodels import UserData

router = APIRouter(tags=["register"])


@router.post("/register")
async def register_user(data: UserData):
    """New user registration.

    Requires a json with username and plain password in request body.
    """
    try:
        await validate(data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.args[0])

    user = User(data.username, data.password)
    async with session:
        session.add(user)
        await session.commit()
    return {"message": "User created successfully"}
