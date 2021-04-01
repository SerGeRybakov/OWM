"""Views for items handling."""
import jwt
from fastapi import APIRouter, Depends, HTTPException
from jwt import PyJWTError
from sqlalchemy import select

from config import Settings, get_settings
from database.schemas import ItemData, TransferData
from database.engine import session
from database.models import Item, User
from validators.authentication import decode_token, get_current_user

items_router = APIRouter(prefix="/items", tags=["items"])
exchange_router = APIRouter(tags=["items_exchange"])


@items_router.get("/")
async def get_items(current_user: User = Depends(get_current_user)):
    """Get item and attach it to creator."""
    if current_user:
        async with session:
            query = select(Item.id, Item.title).where(Item.user_id == current_user.id)
            result = await session.execute(query)
        items = result.fetchall()
        return {current_user.username: items}


@items_router.post("/new", status_code=201)
async def create_new_item(item: ItemData, current_user: User = Depends(get_current_user)):
    """Create new item and attach it to creator.

    If many items were passed only the last one will be promoted.
    """
    async with session:
        query = select(Item).where(Item.title == item.title)
        result = await session.execute(query)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail=f"{item.title} has been already stored")

    if current_user:
        new_item = Item(title=item.title, user_id=current_user.id)
        async with session:
            session.add(new_item)
            await session.commit()
            query = (
                select(Item.id, Item.title, User.username)
                .where(Item.title == item.title)
                .join(User, User.id == current_user.id)
            )
            result = await session.execute(query)
        item = result.first()
        return {"message": "Item was successfully created", "item": item}


@items_router.delete("/:{item_id}", status_code=200)  # Actually it should return 204, but we need to return a message
async def delete_item(item_id: int, current_user: User = Depends(get_current_user)):
    """Delete an item by its id."""
    if current_user:
        async with session:
            query = select(Item).where(Item.id == item_id)
            result = await session.execute(query)
            item: Item = result.scalars().first()
            if item:
                session.delete(item)
                await session.commit()
                return {"message": f"Item {item.title} was successfully deleted"}
            raise HTTPException(status_code=404, detail=f"No item with id {item_id}")


@exchange_router.post("/send")
async def send_item(
    data: TransferData, current_user: User = Depends(get_current_user), settings: Settings = Depends(get_settings)
):
    """Create a link and a token for transfer an item to a certain user."""
    async with session:
        query = select(User.id).where(User.username == data.achiever)
        result = await session.execute(query)
        user = result.scalars().first()
        query = select(Item.id).where(Item.id == data.item_id)
        result = await session.execute(query)
        item_ = result.scalars().first()
    if user and user != current_user.id and item_:
        token = generate_exchange_token(current_user.id, user, data.item_id, settings.SECRET_KEY)
        return {"link": f"/api/v1/get?transfer_key={token}"}
    raise HTTPException(status_code=400, detail="Invalid data in request payload")


@exchange_router.get("/get")
async def get_item_by_achiever(
    transfer_key: str = None, current_user: User = Depends(get_current_user), settings: Settings = Depends(get_settings)
):
    """Obtain an item by the user encoded in the link-token."""
    if not transfer_key:
        raise HTTPException(status_code=404)

    transfer_data = decode_token(transfer_key, settings.SECRET_KEY)

    if not transfer_data.get("achiever_id"):
        raise HTTPException(status_code=400, detail="Invalid key")

    if transfer_data["achiever_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Sorry, this link isn't for you")

    async with session:
        query = select(Item).where(Item.id == transfer_data["item_id"])
        result = await session.execute(query)
        item: Item = result.scalars().first()
        if item.user_id == current_user.id:
            raise HTTPException(status_code=400, detail=f"Item {item.title} is already yours")
        if item.user_id != transfer_data["owner_id"]:
            raise HTTPException(status_code=400, detail=f"Item {item.title} was already passed to another user")
        item.user_id = transfer_data["achiever_id"]
        await session.commit()
        return {"message": f"You've just obtained {item.title}"}


def generate_exchange_token(owner: int, achiever: int, item_id: int, key: str):
    """Generate token for item transfer."""
    return jwt.encode({"owner_id": owner, "achiever_id": achiever, "item_id": item_id}, key)
