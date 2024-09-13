import uuid

from pydantic import EmailStr, BaseModel, ConfigDict


class SUser(BaseModel):
    id: uuid.UUID
    email: EmailStr
    password: bytes

    model_config = ConfigDict(from_attributes=True)


class SUserCreate(BaseModel):
    email: EmailStr
    password: str


class SUserMe(BaseModel):
    id: uuid.UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
