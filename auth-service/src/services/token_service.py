import enum

from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.user import User
from ..config import settings
from ..utils.auth import encode_jwt, decode_jwt
from ..database.repositories.user_repository import UserRepository
from ..exceptions import (
    UserNotFoundException,
    InvalidTokenException,
    InvalidTokenTypeException,
)


class TokenType(enum.StrEnum):
    TYPE = "type"
    ACCESS = "access"
    REFRESH = "refresh"


class TokenService:

    def __init__(self, db_session: AsyncSession):
        self._session: AsyncSession = db_session
        self._repository: UserRepository = UserRepository(db_session)

    @staticmethod
    def _create_jwt_token(
        payload: dict, token_type: TokenType, expire_time_minutes: int
    ) -> str:
        payload[TokenType.TYPE.value] = token_type.value
        return encode_jwt(payload, expire_minutes=expire_time_minutes)

    def create_access_token(self, user: User) -> str:
        jwt_payload = {"sub": str(user.id)}
        return self._create_jwt_token(
            jwt_payload, TokenType.ACCESS, settings.JWT.ACCESS_TOKEN_LIFE
        )

    def create_refresh_token(self, user: User) -> str:
        jwt_payload = {
            "sub": str(user.id),
        }
        return self._create_jwt_token(
            jwt_payload, TokenType.REFRESH, settings.JWT.REFRESH_TOKEN_LIFE
        )

    async def get_user_from_jwt(self, payload: dict) -> User:
        """Get user from JWT via payload"""
        user: User | None = await self._repository.get_user_by_field(id=payload["sub"])

        if user is None:
            raise UserNotFoundException

        return user

    @staticmethod
    def get_current_token_payload(credentials) -> dict:
        token = credentials.credentials
        try:
            payload: dict = decode_jwt(token=token)
        except InvalidTokenError as e:
            raise InvalidTokenException
        return payload

    @staticmethod
    def check_token_type(payload: dict, token_type: TokenType) -> None:
        current_type_type = payload.get(TokenType.TYPE)
        if current_type_type != token_type:
            raise InvalidTokenTypeException(
                detail=f"Invalid token type {current_type_type!r}. Expected {token_type.value!r}"
            )
