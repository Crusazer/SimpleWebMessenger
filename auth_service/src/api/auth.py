import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Body, Request
from pydantic import EmailStr
from starlette.responses import JSONResponse

from src.core.database.models.user import User
from src.core.schemas.device import SDeviceGet
from src.core.schemas.token import SToken
from src.dependencies import (
    get_current_user_for_refresh,
    get_authorization_service,
    get_token_service,
    get_current_active_user,
    get_user_agent,
)
from src.services.auth_service import AuthService
from src.services.token_service import TokenService

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login/", response_model=SToken)
async def login_user(
        request: Request,
        email: Annotated[EmailStr, Body()],
        password: Annotated[str, Body()],
        user_agent: Annotated[str, Depends(get_user_agent)],
        auth_service: Annotated[AuthService, Depends(get_authorization_service)],
):
    return await auth_service.login(email, password, user_agent, request.client.host)


@router.post("/logout/")
async def logout(
        refresh_token: Annotated[str, Body()],
        user: Annotated[User, Depends(get_current_active_user)],
        auth_service: Annotated[AuthService, Depends(get_authorization_service)],
):
    await auth_service.logout(refresh_token)
    return JSONResponse({"message": "Successfully logged out"})


@router.post("/refresh/", response_model=SToken)
async def refresh_jwt_token(
        refresh_token: Annotated[str, Body()],
        user_agent: Annotated[str, Depends(get_user_agent)],
        auth_service: Annotated[AuthService, Depends(get_authorization_service)],
        token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SToken:
    user: User = await get_current_user_for_refresh(refresh_token, token_service)
    return await auth_service.refresh_jwt_token(refresh_token, user, user_agent)


@router.post("/register/", response_model=SToken, status_code=201)
async def registration(
        request: Request,
        email: Annotated[EmailStr, Body()],
        password: Annotated[str, Body()],
        re_password: Annotated[str, Body()],
        user_agent: Annotated[str, Depends(get_user_agent)],
        auth_service: Annotated[AuthService, Depends(get_authorization_service)],
) -> SToken:
    ip: str = request.client.host
    return await auth_service.register_user(
        email, password, re_password, ip, user_agent
    )


@router.get("/devices/", response_model=list[SDeviceGet])
async def get_my_devices(
        user: Annotated[User, Depends(get_current_active_user)],
        auth_service: Annotated[AuthService, Depends(get_authorization_service)]
) -> list[SDeviceGet]:
    return await auth_service.get_my_devices(user)
