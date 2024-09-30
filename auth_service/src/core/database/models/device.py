import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Device(Base):
    __tablename__ = 'device'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), index=True)
    user_agent: Mapped[str] = mapped_column(String(length=255), nullable=False)
    ip: Mapped[str] = mapped_column(String(length=45), nullable=False)
    location: Mapped[str] = mapped_column(String(length=255), nullable=False)
    jti: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)  # refresh JWT id

    user: Mapped["User"] = relationship(back_populates="devices")

    def __repr__(self):
        return f"<Device(user_id={self.user_id})>"

    def __str__(self):
        return f"<Device(user_id={self.user_id}, device={self.user_agent})>"
