import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from src.core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.PRIVATE_KEY,
    algorithm: str = settings.ALGORITHM,
    expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: Optional[timedelta] = None,
):
    payload = payload.copy()
    now = datetime.now(timezone.utc)

    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    payload.update(iat=now, exp=expire)

    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.PUBLIC_KEY,
    algorithm: str = settings.ALGORITHM,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(refresh_token: str) -> bytes:
    return hashlib.sha256(refresh_token.encode()).digest()
