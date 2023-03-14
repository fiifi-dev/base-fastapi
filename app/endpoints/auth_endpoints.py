from datetime import datetime, timedelta
from typing import Any
import sqlalchemy as sa
from fastapi import APIRouter, Body, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import AnyHttpUrl, EmailStr
from sqlalchemy.orm import Session

from app.core import dependencies, exceptions, models, security
from app.core.config import settings
from app.crud import user_crud
from app.schemas import user_schemas
from app.helpers import general_schemas, utils, emails

router = APIRouter()


@router.post("/access-token", response_model=general_schemas.TokenSchema)
def login_access_token(
    db: Session = Depends(dependencies.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_crud.crud.authenticate(
        db,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise exceptions.BadRequest(detail="Incorrect email or password")
    elif not user_crud.crud.is_active(user):
        raise exceptions.BadRequest(detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    user_crud.crud.update_last_login(db, instance=user)

    return {
        "access_token": security.create_access_token(
            user.id,
            expires_delta=access_token_expires,
        ),
        "token_type": "bearer",
    }


@router.post("/reset_password", response_model=general_schemas.MessageSchema)
def reset_password(
    background_tasks: BackgroundTasks,
    email: EmailStr = Body(..., embed=True),
    db: Session = Depends(dependencies.get_db),
):
    print("hello world")
    user = user_crud.crud.get_by_email(db, email=email)

    if user is None:
        raise exceptions.PermissionDenied("Account does not exist")

    token = utils.generate_token(
        user.email,
        key=security.generate_user_secret_key(user),
        expire_time_in_hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
    )

    background_tasks.add_task(
        emails.send_reset_password_email,
        user=user,
        token=token,
    )

    return {"detail": f"{user.email} password reset successfully"}


@router.post("/reset-password-complete/", response_model=general_schemas.MessageSchema)
def reset_password_complete(
    token: str,
    uid: int,
    item: user_schemas.ResetUserPasswordSchema,
    db: Session = Depends(dependencies.get_db),
) -> Any:
    """
    Reset password
    """
    user = user_crud.crud.read_one(db, id=uid)

    if user is None:
        raise exceptions.NotFound(detail="This account does not exist")
    elif not user_crud.crud.is_active(user):
        raise exceptions.BadRequest(detail="This account is inactive")

    decodedEmail = utils.verify_token(
        token=token, key=security.generate_user_secret_key(user)
    )

    if decodedEmail is None:
        raise exceptions.BadRequest(detail="Invalid token")

    user_crud.crud.reset_password_complete(
        db,
        instance=user,
        item_schema=item,
    )

    return {"detail": "Password updated successfully"}
