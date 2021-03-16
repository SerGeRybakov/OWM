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
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=100)
    token = jwt.encode({"id": current_user.id, "exp": expiry}, settings.SECRET_KEY)

    async with session:
        query = select(UserToken).where(UserToken.user_id == current_user.id)
        result = await session.execute(query)
        user_token: UserToken = result.scalars().first()
        if user_token:
            user_token.token = token
        else:
            user_token = UserToken(user_id=current_user.id, token=token)
            session.add(user_token)
        await session.commit()

    return {"token": token}
