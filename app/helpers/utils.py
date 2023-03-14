from datetime import datetime, timedelta
from app.core.config import settings

from app.core.security import ALGORITHM
import jwt
import re


def generate_token(
    email: str,
    key: str,
    expire_time_in_hours: int,
) -> str:
    delta = timedelta(hours=expire_time_in_hours)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        key,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def verify_token(token: str, key: str) -> str | None:
    try:
        decoded_token = jwt.decode(token, key, algorithms=[ALGORITHM])
        return decoded_token["sub"]
    except jwt.PyJWTError:
        return None


def slugify(value: str):
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    value = re.sub(r"^-+|-+$", "", value)
    return value
