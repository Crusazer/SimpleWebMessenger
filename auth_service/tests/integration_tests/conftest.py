import pytest
from faker import Faker
from httpx import AsyncClient
from starlette import status

from src.core.schemas.token import SToken
from src.core.schemas.user_schemas import SUserCreate

fake = Faker()


@pytest.fixture()
async def random_user(ac: AsyncClient) -> tuple[SUserCreate, SToken]:
    """Return random user with access and refresh tokens."""
    user: SUserCreate = SUserCreate(email=fake.email(), password="1")
    request_data = {
        "email": user.email,
        "password": user.password,
        "re_password": user.password,
    }
    response = await ac.post("/auth/register/", json=request_data)
    assert (
        response.status_code == status.HTTP_201_CREATED
    ), "User creation failed in the fixture random_user."
    tokens: SToken = SToken(**response.json())
    return user, tokens
