import uuid

from pydantic import EmailStr, BaseModel


class SUser(BaseModel):
    id: uuid.UUID
    email: EmailStr
    password: bytes

    class Config:
        from_attribute = True


class SUserCreate(BaseModel):
    email: EmailStr
    password: str


class SUserMe(BaseModel):
    id: uuid.UUID
    email: EmailStr

    class Config:
        from_attributes = True
