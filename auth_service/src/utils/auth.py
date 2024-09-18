from datetime import datetime, timezone, timedelta

import bcrypt
import jwt

from src.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.JWT.PRIVATE_KEY,
    algorithm: str = settings.JWT.ALGORITHM,
    expire_minutes: int = settings.JWT.ACCESS_TOKEN_LIFE,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire, iat=now)
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.JWT.PUBLIC_KEY,
    algorithm: str = settings.JWT.ALGORITHM,
) -> dict:
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    password_bytes: bytes = password.encode()
    return bcrypt.hashpw(password=password_bytes, salt=salt).decode()


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=password.encode(), hashed_password=hashed_password.encode()
    )
