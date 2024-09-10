import datetime

from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions import (
    UserNotFoundException,
    UserAuthenticationException,
    NotMatchPasswordException,
    InvalidTokenException,
)
from ..database.models.user import User
from ..database.repositories.user_repository import UserRepository
from ..database.schemas.token import SToken
from ..database.schemas.user_schemas import SUserCreate
from ..utils.auth import validate_password, hash_password
from ..config import settings
from .token_service import TokenService
from .redis_service import RedisService


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self._session: AsyncSession = db_session
        self._repository = UserRepository(self._session)
        self._token_service = TokenService(self._session)

    def _generate_tokens(self, user: User) -> SToken:
        access_token: str = self._token_service.create_access_token(user)
        refresh_token: str = self._token_service.create_refresh_token(user)
        return SToken(access_token=access_token, refresh_token=refresh_token)

    async def login(self, email: str, password: str) -> SToken:
        """Check password and authenticate user"""
        user = await self._repository.get_user_by_field(email=email)
        if not user:
            raise UserNotFoundException

        if not validate_password(password, user.password):
            raise UserAuthenticationException

        return self._generate_tokens(user)

    async def register_user(self, email: str, password: str, re_password: str):
        """Create new user if not exists and passwords match"""
        if password != re_password:
            raise NotMatchPasswordException

        hashed_password = hash_password(password)
        s_user = SUserCreate(email=email, password=hashed_password)

        if await self._repository.get_user_by_field(email=s_user.email) is not None:
            raise UserAuthenticationException(detail="Email already registered")

        user = await self._repository.create_user(s_user)
        return self._generate_tokens(user)

    async def refresh_jwt_token(self, refresh_token: str, user: User) -> SToken:
        """Generate new pair and add old refresh to blacklist"""
        redis = RedisService()
        payload = self._token_service.get_current_token_payload(refresh_token)
        jti = payload.get("jti")

        # Check current refresh token in blocked list
        if await redis.is_token_blacklisted(jti):
            raise InvalidTokenException

        # Add current refresh token to blacklist
        exp: int = payload.get("exp")
        if exp:
            expiration_time = exp - int(
                datetime.datetime.now(datetime.timezone.utc).timestamp()
            )
        else:
            expiration_time = settings.JWT.REFRESH_TOKEN_LIFE
        await redis.set_token(jti, "blacklist", expiration_time)

        # Return new pair tokens
        return self._generate_tokens(user)
