import logging

import pytest
from httpx import AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_register_user_async(ac: AsyncClient):
    data = {
        "email": "a@a.com",
        "password": "a",
        "re_password": "a",
    }
    response = await ac.post("/auth/register/", json=data, )
    data = response.json()
    logger.info(data)
    print(data)
    assert response.status_code == 200
    assert data.get("access_token") is not None
    assert data.get("refresh_token") is not None
    assert data.get("token_type") == "Bearer"
