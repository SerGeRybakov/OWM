"""Global configuration settings."""
import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import Depends
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Base app settings."""

    SECRET_KEY: str = os.getenv("SECRET_KEY", "TEST_KEY")


@lru_cache()
def get_settings():
    """Initiate app settings."""
    return Settings()
