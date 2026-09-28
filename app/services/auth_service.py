from datetime import datetime, timedelta, timezone
import os

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()


# Password hashing
password_hash = PasswordHash.recommended()


# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured in .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token