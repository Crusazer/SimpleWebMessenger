import datetime

from redis import asyncio

from ..config import settings
from ..exceptions import RedisException


class RedisService:
    token_prefix = "refresh_"
    __redis_connection: asyncio.Redis = asyncio.Redis(
        host=settings.REDIS.HOST,
        port=settings.REDIS.PORT,
        password=settings.REDIS.PASSWORD,
        db=settings.REDIS.DEFAULT_DB,
    )

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
            raise RedisException(e)  # TODO: use logger

    async def get_token(self, token_jti: str) -> None:
        try:
            return await self.__redis_connection.get(f"{self.token_prefix}{token_jti}")
        except asyncio.RedisError:
            print(f"Failed to get token: {token_jti}")
            raise RedisException

    async def is_token_blacklisted(self, token_jti: str) -> bool:
        try:
            return bool(
                await self.__redis_connection.get(f"{self.token_prefix}{token_jti}")
            )  # TODO: check how this work
        except asyncio.RedisError:
            print(f"Failed to check token: {token_jti}")
            raise RedisException
