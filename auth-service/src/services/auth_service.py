import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.models.user import User
from src.database.repositories.user_repository import UserRepository
from src.database.schemas.token import SToken
from src.database.schemas.user_schemas import SUserCreate
from src.exceptions import (
    UserNotFoundException,
    UserAuthenticationException,
    NotMatchPasswordException,
    InvalidTokenException,
)
from src.utils.auth import validate_password, hash_password
from .redis_service import RedisService
from .token_service import TokenService


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self._session: AsyncSession = db_session
        self._repository = UserRepository(self._session)
        self._token_service = TokenService(self._session)

    def _generate_tokens(self, user: User) -> SToken:
        access_token: str = self._token_service.create_access_token(user)
        refresh_token: str = self._token_service.create_refresh_token(user)
        return SToken(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def _add_token_to_blacklist(
        payload: dict,
        redis: RedisService,
    ) -> None:
        """Add refresh token to blacklist"""
        exp: int = payload.get("exp")
        if exp:
            now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            expiration_time = exp - now
        else:
            expiration_time = settings.JWT.REFRESH_TOKEN_LIFE
        await redis.set_token(payload.get("jti"), "blacklist", expiration_time)

    @staticmethod
    async def _check_token_in_blacklist(
        jti: str, redis_service: RedisService()
    ) -> None:
        if await redis_service.is_token_blacklisted(jti):
            raise InvalidTokenException

    async def login(self, email: str, password: str) -> SToken:
        """Check password and authenticate user"""
        user = await self._repository.get_user_by_field(email=email)
        if not user:
            raise UserNotFoundException

        if not validate_password(password, user.password):
            raise UserAuthenticationException

        return self._generate_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        """Logout user and add refresh token to blacklist"""
        redis = RedisService()
        payload = self._token_service.get_current_token_payload(refresh_token)

        await self._check_token_in_blacklist(payload.get("jti"), redis)
        await self._add_token_to_blacklist(payload, redis)

    async def refresh_jwt_token(self, refresh_token: str, user: User) -> SToken:
        """Generate new pair and add old refresh to blacklist"""
        redis = RedisService()
        payload = self._token_service.get_current_token_payload(refresh_token)

        await self._check_token_in_blacklist(payload.get("jti"), redis)
        await self._add_token_to_blacklist(payload, redis)
        return self._generate_tokens(user)

    async def register_user(self, email: str, password: str, re_password: str):
        """Create new user if not exists and passwords match"""
        if password != re_password:
            raise NotMatchPasswordException

        hashed_password = hash_password(password)
        s_user = SUserCreate(email=email, password=hashed_password)

        if await self._repository.get_user_by_field(email=s_user.email) is not None:
            raise UserAuthenticationException(
                detail="A user with this email already exists."
            )

        user = await self._repository.create_user(s_user)
        return self._generate_tokens(user)
