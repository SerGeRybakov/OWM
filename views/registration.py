"""View for users register."""
from fastapi import APIRouter, HTTPException

from database.engine import session
from database.models import User
from validators.validation import ValidationError, validate
from database.schemas import UserData

router = APIRouter(tags=["registration"])


@router.post("/registration", status_code=201)
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
        return {"message": f"User {user.username} was successfully registered"}
