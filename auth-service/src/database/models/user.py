import uuid

from pydantic import EmailStr
from sqlalchemy import Column, String, Boolean, UUID
from sqlalchemy.orm import Mapped

from .base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[EmailStr] = Column(String, nullable=False, unique=True)
    password: Mapped[str] = Column(String, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    is_staff: Mapped[bool] = Column(Boolean, nullable=False, default=False)
