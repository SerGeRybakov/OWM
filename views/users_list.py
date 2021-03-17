"""View for list of users."""
from fastapi import APIRouter, Depends

from database.engine import session
from database.models import User
from sqlalchemy import select

from validators.authentication import get_current_user

router = APIRouter(tags=["users"])


@router.get("/users")
async def users_list(current_user: User = Depends(get_current_user)):
    """Get list of users' usernames.

    With aim to forward an item to any other user
    one should know the exact username of the achiever.
    """
    if current_user:
        async with session:
            query = select(User.username)
            result = await session.execute(query)
        users = result.scalars().fetchall()

        return {"existing_users": users}
