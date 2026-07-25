import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings
from app.schemas.auth import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#  Паролі

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


#  JWT — access / refresh токени

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        token_data = TokenPayload(**payload)

        if token_data.type != "access":
            return None  

        return token_data
    except (JWTError, ValueError):
        return None


#  Refresh token (окремий механізм — не JWT, а випадковий рядок + хеш у БД)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)


#  Токен для верифікації email (окремий JWT з іншим призначенням)

def create_email_verification_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "email_verification",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_email_verification_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        if payload.get("type") != "email_verification":
            return None

        return int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        return None