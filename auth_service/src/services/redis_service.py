import datetime
import logging

from redis import asyncio

from src.config import settings
from src.exceptions import RedisException

logger = logging.getLogger(__name__)


class RedisService:
    token_prefix = "refresh_"

    def __init__(self):
        self.__redis_connection: asyncio.Redis = asyncio.Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            password=settings.REDIS.PASSWORD,
            db=settings.REDIS.DEFAULT_DB,
            max_connections=10
        )
        logger.info(f"Redis service initialized {settings.REDIS}")

    async def set_token(
        self,
        token_jti: str,
        value: str | bytes | float | int = datetime.datetime.now(
            datetime.timezone.utc
        ).timestamp(),
        expires: datetime.timedelta | int | None = None,
    ) -> None:
        try:
            await self.__redis_connection.set(
                f"{self.token_prefix}{token_jti}", value, ex=expires
            )
        except asyncio.RedisError as e:
            logger.critical("Redis connection error", exc_info=True)
            raise RedisException(e)

    async def get_token(self, token_jti: str) -> None:
        try:
            return await self.__redis_connection.get(f"{self.token_prefix}{token_jti}")
        except asyncio.RedisError:
            logger.critical("Redis connection error", exc_info=True)
            raise RedisException

    async def is_token_blacklisted(self, token_jti: str) -> bool:
        try:
            return bool(
                await self.__redis_connection.get(f"{self.token_prefix}{token_jti}")
            )
        except asyncio.RedisError:
            logger.critical("Redis connection error", exc_info=True)
            raise RedisException
