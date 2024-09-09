from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions import (
    UserNotFoundException,
    UserAuthenticationException,
    NotMatchPasswordException,
)
from ..database.models.user import User
from ..database.repositories.user_repository import UserRepository
from ..database.schemas.token import SToken
from ..database.schemas.user_schemas import SUserCreate
from .token_service import TokenService
from ..utils.auth import validate_password, hash_password


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

    async def refresh_jwt_token(self, user: User) -> SToken:
        """Generate new pair and add old refresh to blacklist"""
        return self._generate_tokens(user)
