import functools

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class ConfigDB(BaseSettings):
    HOST: str
    PORT: str
    USERNAME: str
    NAME: str
    PASSWORD: str

    HOST_TEST: str
    PORT_TEST: str
    USERNAME_TEST: str
    NAME_TEST: str
    PASSWORD_TEST: str

    @functools.cached_property
    def url(self):
        # postgresql+asyncpg://user:password@host:port/dbname
        return f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @functools.cached_property
    def url_test(self):
        return (
            f"postgresql+asyncpg://{self.USERNAME_TEST}:{self.PASSWORD_TEST}@{self.HOST_TEST}:"
            f"{self.PORT_TEST}/{self.NAME_TEST}"
        )

    model_config = SettingsConfigDict(env_prefix="DB_")


class RedisConfig(BaseSettings):
    HOST: str
    PORT: int
    PASSWORD: str | None = None
    DEFAULT_DB: int = 0

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class JWTConfig(BaseSettings):
    ACCESS_TOKEN_LIFE: int = 3  # In minutes
    REFRESH_TOKEN_LIFE: int = 30 * 24 * 60  # In minutes. Default 30 days.
    ALGORITHM: str = "RS256"
    PRIVATE_KEY: str
    PUBLIC_KEY: str

    model_config = SettingsConfigDict(env_prefix="JWT_")


class Config(BaseSettings):
    DEBUG: bool = True
    SITE_DOMAIN: str = "127.0.0.1"
    DB: ConfigDB = ConfigDB()
    JWT: JWTConfig = JWTConfig()
    REDIS: RedisConfig = RedisConfig()


settings = Config()
