"""View for users login."""
import datetime

import jwt
import jwt.exceptions
from fastapi import APIRouter, Depends
from sqlalchemy import select

from config import Settings, get_settings
from database.engine import session
from database.models import User, UserToken
from validators.authentication import authenticate_user

router = APIRouter(tags=["login"])


@router.post("/login")
async def login(current_user: User = Depends(authenticate_user), settings: Settings = Depends(get_settings)):
    """Login view.

    Return token
    """
    access_token = create_access_token(current_user.id, settings.SECRET_KEY, {"minutes": 3600})

    async with session:
        query = select(UserToken).where(UserToken.user_id == current_user.id)
        result = await session.execute(query)
        user_token: UserToken = result.scalars().first()
        if user_token:
            user_token.token = access_token
        else:
            user_token = UserToken(user_id=current_user.id, token=access_token)
            session.add(user_token)
        await session.commit()

    return {"access_token": access_token, "token_type": "bearer"}


def create_access_token(user_id: int, key: str, expiry_time: dict) -> str:
    """Create an access token."""
    expiry = datetime.datetime.utcnow() + datetime.timedelta(**expiry_time)
    return jwt.encode({"id": user_id, "exp": expiry}, key)
