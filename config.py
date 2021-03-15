"""Global configuration settings."""
import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Base app settings."""

    SECRET_KEY = os.getenv("SECRET_KEY", "TEST_KEY")
