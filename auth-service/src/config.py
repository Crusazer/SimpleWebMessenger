from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class ConfigDB(BaseSettings):
    DB_URL: PostgresDsn
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_NAME: str
    DB_PASSWORD: str


class Config(BaseSettings):
    DB: ConfigDB
    SITE_DOMAIN: str = "127.0.0.1"


settings = Config(DB=ConfigDB())

