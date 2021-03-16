"""View for users login."""

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from datamodels import UserData

router = APIRouter(tags=["login"])


@router.post("/login")
async def login(data: UserData):
    """Login view.

    Return token
    """
    return jsonable_encoder(data)
