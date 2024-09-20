import logging

import pytest
from httpx import AsyncClient, Response
from starlette import status

from src.core.schemas.token import SToken
from src.core.schemas.user_schemas import SUserCreate

logger = logging.getLogger(__name__)

class TestAuthService:
    @pytest.mark.parametrize("request_data, status_code", [
        ({"email": "a@a.com", "password": "123", "re_password": "123"}, status.HTTP_201_CREATED),
        ({"email": "a@.a", "password": "123", "re_password": "123"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"email": "a@.a", "password": "123", "re_password": "1"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ])
    async def test_register_user_async(self, ac: AsyncClient, request_data, status_code):
        """ Test registering a user with an email and password. """
        response = await ac.post("/auth/register/", json=request_data)
        data = response.json()
        assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {data}"
        if response.status_code == 201:
            assert data.get("access_token") is not None
            assert data.get("refresh_token") is not None
            assert data.get("token_type") == "Bearer"

    @pytest.mark.parametrize(
        "email, password, expected_status",
        [
            ("valid_email", "valid_password", status.HTTP_200_OK),
            ("valid_email", "incorrect_password", status.HTTP_403_FORBIDDEN),
            ("invalid_email@example.com", "valid_password", status.HTTP_404_NOT_FOUND),
            ("invalid_email_type", "valid_password", status.HTTP_422_UNPROCESSABLE_ENTITY)
        ]
    )
    async def test_login(
            self,
            ac: AsyncClient,
            random_user: tuple[SUserCreate, SToken],
            email, password, expected_status):
        """ Test various login scenarios. """
        user: SUserCreate = random_user[0]

        if email == "valid_email":
            email = user.email

        if password == "valid_password":
            password = user.password

        response_data = {"email": email, "password": password}
        response = await ac.post("/auth/login/", json=response_data)

        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}"

        if expected_status == status.HTTP_200_OK:
            data: dict = response.json()
            assert data.get("access_token") is not None
            assert data.get("refresh_token") is not None
            assert data.get("token_type") == "Bearer"

    async def test_logout(self,
                          ac: AsyncClient,
                          random_user: tuple[SUserCreate, SToken]):
        tokens: SToken = random_user[1]
        response_data = f"{tokens.refresh_token}"
        response: Response = await ac.post("/auth/logout/",
                                           json=response_data,
                                           headers={"Authorization": f"Bearer {tokens.access_token}"})
        assert response.status_code == status.HTTP_200_OK, f"response: {response.status_code}, {response.json()}"
