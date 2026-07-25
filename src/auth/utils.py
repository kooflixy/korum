import bcrypt
import jwt

from src.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.PRIVATE_KEY,
    algorithm: str = settings.ALGORITHM,
):
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
    return bcrypt.checkpw(password.encode, hashed_password)
