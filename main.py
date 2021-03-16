"""Main module."""
from functools import lru_cache

import uvicorn
from fastapi import Depends, FastAPI, APIRouter
from views import reg_router, login_router, users_list_router
from config import Settings

app = FastAPI()


@lru_cache()
def get_settings():
    """Initiate app settings."""
    return Settings()


settings: Settings = Depends(get_settings)

root_router = APIRouter(prefix="/api/v1")

root_router.include_router(login_router)
root_router.include_router(users_list_router)
root_router.include_router(reg_router)

app.include_router(root_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="debug", use_colors=True)
