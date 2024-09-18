from sqlalchemy import select, Select, Result, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.user import User
from src.core.schemas.user_schemas import SUserCreate


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def get_user_by_field(self, **kwargs) -> User | None:
        """Get a user bu given fields"""
        stmt: Select = select(User)
        conditions = [getattr(User, field) == value for field, value in kwargs.items()]
        stmt = stmt.where(and_(*conditions))
        result: Result = await self._session.execute(stmt)
        return result.scalars().first()

    async def create_user(self, new_user: SUserCreate) -> User:
        user = User(**new_user.model_dump())
        self._session.add(user)
        await self._session.commit()
        return user
