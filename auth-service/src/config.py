# src.auth.config
import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn
    SITE_DOMAIN: str = "127.0.0.1"


settings = Config()
