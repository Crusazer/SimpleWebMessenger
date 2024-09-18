import logging

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.database import get_async_session
from src.core.database.models.user import User
from .exceptions import UserNotActiveException
from .services.auth_service import AuthService
from .services.token_service import TokenService, TokenType

logger = logging.getLogger(__name__)
def get_authorization_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)


def get_token_service(
    session: AsyncSession = Depends(get_async_session),
) -> TokenService:
    return TokenService(session)


async def get_current_auth_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    """Get current user from jwt token and check token type."""
    payload: dict = token_service.get_current_token_payload(credentials.credentials)
    token_service.check_token_type(payload, TokenType.ACCESS)
    user: User = await token_service.get_user_from_jwt(payload=payload)
    return user


async def get_current_user_for_refresh(
    refresh_token: str, token_service: TokenService = Depends(get_token_service)
) -> User:
    """Get current user from jwt refresh token and check token type."""
    payload: dict = token_service.get_current_token_payload(refresh_token)
    token_service.check_token_type(payload, TokenType.REFRESH)
    user: User = await token_service.get_user_from_jwt(payload=payload)
    return user


def get_current_active_user(user: User = Depends(get_current_auth_user)) -> User:
    if not user.is_active:
        raise UserNotActiveException
    return user
