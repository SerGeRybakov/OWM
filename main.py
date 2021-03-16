"""Main module."""

import uvicorn
from fastapi import APIRouter, FastAPI

from views import *

app = FastAPI()

root_router = APIRouter(prefix="/api/v1")

root_router.include_router(reg_router)
root_router.include_router(login_router)
root_router.include_router(items_router)
root_router.include_router(users_list_router)

app.include_router(root_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="debug", use_colors=True)
