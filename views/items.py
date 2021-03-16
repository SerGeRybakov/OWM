"""Views for items handling."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select

from database.engine import session
from database.models import Item, User
from database.data_models import ItemData
from validators.authentication import get_current_user

router = APIRouter(tags=["items"])


@router.get("/items")
async def get_items(current_user: User = Depends(get_current_user)):
    """Get item and attach it to creator."""
    if current_user:
        async with session:
            query = select(Item.id, Item.title).where(Item.user_id == current_user.id)
            result = await session.execute(query)
        items = result.fetchall()
        return {f"{current_user.username} items": items}


@router.post("/items/new", status_code=201)
async def create_new_item(item: ItemData, current_user: User = Depends(get_current_user)):
    """Create new item and attach it to creator.

    If many items were passed only the last one will be promoted.
    """
    async with session:
        query = select(Item).where(Item.title == item.title)
        result = await session.execute(query)
    _item = result.scalars().first()
    if _item:
        raise HTTPException(status_code=400, detail=f"{item.title} has been already stored")
    if current_user:
        new_item = Item(title=item.title, user_id=current_user.id)
        async with session:
            session.add(new_item)
            await session.commit()
        return {"message": f"Item {item.title} was successfully added"}


@router.delete("/items/:{item_id}", status_code=204)
async def delete_item(item_id: int, current_user: User = Depends(get_current_user)) -> None:
    """Delete an item by its id."""
    if current_user:
        async with session:
            query = select(Item).where(Item.id == item_id)
            result = await session.execute(query)
            item = result.scalars().first()
            session.delete(item)
            await session.commit()
