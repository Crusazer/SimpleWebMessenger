from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db_session: AsyncSession):
        self._session: AsyncSession = db_session
        self._repository = UserRepository(self._session)
