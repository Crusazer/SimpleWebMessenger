import uuid

from pydantic import BaseModel


class DeviceDTO(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str
    ip: str
    location: str
    jti: uuid.UUID

    class ConfigDict:
        from_attributes = True


class SDeviceGet(BaseModel):
    id: uuid.UUID
    user_agent: str
    ip: str
    location: str


class SDeviceCreate(BaseModel):
    user_id: uuid.UUID
    user_agent: str
    ip: str
    location: str
    jti: uuid.UUID
