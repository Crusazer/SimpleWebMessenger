from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

load_dotenv()


class ConfigDB(BaseSettings):
    URL: PostgresDsn
    HOST: str
    PORT: str
    USER: str
    NAME: str
    PASSWORD: str

    class Config:
        env_prefix = "DB_"


class RedisConfig(BaseSettings):
    HOST: str
    PORT: int
    PASSWORD: str | None = None
    DEFAULT_DB: int = 0

    class Config:
        env_prefix = "REDIS_"


class JWTConfig(BaseSettings):
    ACCESS_TOKEN_LIFE: int = 3  # In minutes
    REFRESH_TOKEN_LIFE: int = 30 * 24 * 60  # In minutes. Default 30 days.
    ALGORITHM: str = "RS256"
    PRIVATE_KEY: str
    PUBLIC_KEY: str

    class Config:
        env_prefix = "JWT_"


class Config(BaseSettings):
    SITE_DOMAIN: str = "127.0.0.1"
    DB: ConfigDB = ConfigDB()
    JWT: JWTConfig = JWTConfig()
    REDIS: RedisConfig = RedisConfig()


settings = Config()
