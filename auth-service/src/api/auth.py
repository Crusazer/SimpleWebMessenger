import logging

from fastapi import APIRouter, Depends, Form
from pydantic import EmailStr

from ..database.models.user import User
from ..database.schemas.token import SToken
from ..dependencies import (
    get_authorization_service,
    get_token_service,
    get_current_active_user,
)
from ..dependencies import get_current_user_for_refresh
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login/", response_model=SToken)
async def login(
    email: str = Form(),
    password: str = Form(),
    auth_service: AuthService = Depends(get_authorization_service),
):
    return await auth_service.login(email, password)


@router.post("logout")
async def logout(
    refresh_token: str = Form(),
    user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_authorization_service),
):
    await auth_service.logout(refresh_token)
    return {"message": "Successfully logged out"}


@router.post("/refresh_token/", response_model=SToken)
async def refresh_jwt_token(
    refresh_token: str = Form(),
    auth_service: AuthService = Depends(get_authorization_service),
    token_service=Depends(get_token_service),
) -> SToken:
    user: User = await get_current_user_for_refresh(refresh_token, token_service)
    return await auth_service.refresh_jwt_token(refresh_token, user)


@router.post("/register", response_model=SToken)
async def create_user(
    email: EmailStr = Form(),
    password: str = Form(),
    re_password: str = Form(),
    auth_service: AuthService = Depends(get_authorization_service),
) -> SToken:
    return await auth_service.register_user(email, password, re_password)
