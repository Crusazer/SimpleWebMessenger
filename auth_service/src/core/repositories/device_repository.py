from uuid import UUID

from sqlalchemy import (
    delete,
    Delete,
    CursorResult,
    select,
    Select,
    Result,
    update,
    Update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models import Device
from src.core.schemas.device import DeviceDTO, SDeviceCreate, SDeviceGet


class DeviceRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def create(self, device_dto: SDeviceCreate) -> DeviceDTO:
        """Create new user device"""
        device: Device = Device(**device_dto.model_dump())
        self._session.add(device)
        await self._session.flush()
        await self._session.refresh(device)
        await self._session.commit()
        return DeviceDTO.model_validate(device, from_attributes=True)

    async def get(self, user_id: UUID, jti: UUID) -> DeviceDTO:
        """Get user device by jti"""
        stmt: Select = select(Device).where(
            Device.user_id == user_id, Device.jti == jti
        )
        result: Result = await self._session.execute(stmt)
        device: Device = result.scalar_one_or_none()
        if device is None:
            raise ValueError("Device not found")

        return DeviceDTO.model_validate(device, from_attributes=True)

    async def get_user_devices(self, user_id: UUID) -> list[SDeviceGet]:
        """Return list of user devices"""
        stmt: Select = select(Device).where(Device.user_id == user_id)
        result: Result = await self._session.execute(stmt)
        return [
            SDeviceGet.model_validate(device, from_attributes=True)
            for device in result.scalars().all()
        ]

    async def update(self, user_id: UUID, current_jti: UUID, **kwargs):
        """Update user device"""
        stmt: Update = (
            update(Device)
            .where(Device.user_id == user_id, Device.jti == current_jti)
            .values(**kwargs)
        )
        result: CursorResult = await self._session.execute(stmt)
        if result.rowcount == 0:
            raise ValueError(f"User {user_id} have not device with jti {current_jti}.")
        await self._session.commit()

    async def delete_by_user_id_and_jti(self, user_id: UUID, jti: UUID) -> None:
        """Delete user device"""
        stmt: Delete = delete(Device).where(
            Device.user_id == user_id, Device.jti == jti
        )
        result: CursorResult = await self._session.execute(stmt)
        if result.rowcount == 0:
            raise ValueError(f"User {user_id} have not device with jti {jti}.")
        await self._session.commit()

    async def delete_by_user_id_and_device_id(
        self, user_id: UUID, device_id: UUID
    ) -> None:
        """Delete user device by user id and device id"""
        stmt: Delete = delete(Device).where(
            Device.user_id == user_id, Device.id == device_id
        )
        result: CursorResult = await self._session.execute(stmt)
        if result.rowcount == 0:
            raise ValueError(f"User {user_id} have not device with id {device_id}.")
        await self._session.commit()

    async def delete_all_user_devices(self, user_id: UUID) -> None:
        """Delete all user devices"""
        stmt: Delete = delete(Device).where(Device.user_id == user_id)
        result: CursorResult = await self._session.execute(stmt)
        if result.rowcount == 0:
            raise ValueError(f"User {user_id} have not devices.")
        await self._session.commit()
