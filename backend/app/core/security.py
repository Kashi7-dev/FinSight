from pwdlib import PasswordHash
import os
from datetime import datetime, timedelta, timezone
import jwt
from typing import Any
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(subject: str) -> tuple[str, int]:
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    expires_in = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    ) * 60

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=expires_in)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        secret_key,
        algorithm="HS256",
    )

    return token, expires_in

def decode_access_token(token: str) -> dict[str, Any]:
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    return jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
    )