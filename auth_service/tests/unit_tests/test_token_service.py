import uuid
from unittest import mock

import pytest
from unittest.mock import AsyncMock, patch

from src.core.database.models.user import User
from src.services.token_service import TokenService, TokenType

from src.config import settings


class TestTokenService:
    @patch("src.services.token_service.encode_jwt")
    async def test_create_access_token(self, mock_create_jwt):
        # Arrange
        mock_create_jwt.return_value = "mock_access_token"
        user = User(id=uuid.uuid4())
        token_service = TokenService(db_session=AsyncMock())

        # Act
        access_token = token_service.create_access_token(user)

        # Assert
        mock_create_jwt.assert_called_once_with(
            {"sub": f"{user.id}", TokenType.TYPE: TokenType.ACCESS},
            expire_minutes=settings.JWT.ACCESS_TOKEN_LIFE  # JWT.ACCESS_TOKEN_LIFE
        )
        assert access_token == "mock_access_token"

    @patch("src.services.token_service.encode_jwt")
    async def test_create_refresh_token(self, mock_create_jwt):
        # Arrange
        mock_create_jwt.return_value = "mock_refresh_token"
        user = User(id=uuid.uuid4())
        token_service = TokenService(db_session=AsyncMock())

        # Act
        refresh_token = token_service.create_refresh_token(user)

        # Assert
        mock_create_jwt.assert_called_once_with(
            {"sub": f"{user.id}", "jti": mock.ANY, TokenType.TYPE.value: TokenType.REFRESH.value},
            expire_minutes=settings.JWT.REFRESH_TOKEN_LIFE
        )
        assert refresh_token == "mock_refresh_token"
