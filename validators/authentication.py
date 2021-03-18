"""Users' authentication."""
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from sqlalchemy import select
from starlette import status

from config import Settings, get_settings
from database.engine import session
from database.models import User, UserToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


async def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Check user's credentials received in headers.

    :return database user entry
    :raise HTTP_401_UNAUTHORIZED
    """
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: username and password required",
            headers={"WWW-Authenticate": "OAuth2 Bearer"},
        )

    async with session:
        query = select(User).where(User.username == form_data.username)
        result = await session.execute(query)
    user: User = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorized: {form_data.username} is not registered",
            headers={"WWW-Authenticate": "OAuth2 Bearer"},
        )

    if not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=401, detail="Unauthorized: Wrong password", headers={"WWW-Authenticate": "Basic"}
        )

    return user


async def get_current_user(token: str = Depends(oauth2_scheme), settings: Settings = Depends(get_settings)):
    """Validate user's token.

    :return database user entry
    :raise HTTP_401_UNAUTHORIZED
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Invalid token",
        headers={"WWW-Authenticate": "OAuth2 Bearer"},
    )
    try:
        payload = decode_token(token, settings.SECRET_KEY)
        user_id: str = payload.get("id")
        if not user_id:
            raise credentials_exception
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorized: {e.args[0]}",
            headers={"WWW-Authenticate": "OAuth2 Bearer"},
        )

    async with session:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise credentials_exception

    async with session:
        query = select(UserToken.token).where(UserToken.user_id == user_id)
        result = await session.execute(query)
    user_token = result.scalars().first()
    if not user_token or user_token != token:
        raise credentials_exception
    return user


def decode_token(token, key):
    """Decode token."""
    try:
        payload = jwt.decode(token, key, algorithms=["HS256"])
        return payload
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
