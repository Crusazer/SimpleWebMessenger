from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .database.database import get_async_session
from .services.auth_service import AuthService
from .services.token_service import TokenService, TokenType
from .exceptions import UserNotActiveException
from .database.models.user import User


def get_authorization_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)


def get_token_service(
    session: AsyncSession = Depends(get_async_session),
) -> TokenService:
    print(f"Return TOKEN SERVICE")
    return TokenService(session)


def _get_user_from_token_factory(token_type: TokenType):
    async def get_auth_user_from_token(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        token_service: TokenService = Depends(get_token_service),
    ) -> User:
        """Get current user from jwt token."""
        payload: dict = token_service.get_current_token_payload(credentials)
        token_service.check_token_type(payload, token_type)
        user: User = await token_service.get_user_from_jwt(payload=payload)
        return user

    return get_auth_user_from_token


get_current_auth_user = _get_user_from_token_factory(TokenType.ACCESS)
get_current_user_for_refresh = _get_user_from_token_factory(TokenType.REFRESH)


def get_current_active_user(user: User = Depends(get_current_auth_user)) -> User:
    if not user.is_active:
        raise UserNotActiveException
    return user
