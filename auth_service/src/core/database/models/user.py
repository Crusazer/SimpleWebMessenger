import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from . import Device


class User(Base):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_staff: Mapped[bool] = mapped_column(nullable=False, default=False)

    devices: Mapped[list["Device"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    def __str__(self):
        return f"<User(id={self.id}, email={self.email})>"
