from typing import Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from core import models, security
from core.config import settings
from core.database import SessionLocal
from helpers import general_schemas
from crud import user_crud

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"auth/access-token")


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def paginate_params(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )

        token_data = general_schemas.TokenPayloadSchema(**payload)

    except (jwt.PyJWKError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = user_crud.crud.read_one(db, id=token_data.dict()["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:

    if not user_crud.crud.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not user_crud.crud.is_superuser(current_user):

        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )

    return current_user
