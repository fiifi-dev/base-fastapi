from sqlalchemy.orm import Session

from core.config import settings
from crud import user_crud


def create_first_user(db: Session):
    email = email = settings.ROOT_USER_EMAIL
    password = settings.ROOT_USER_PASSWORD

    if settings.DEBUG:
        print("Creating user...")

    user = user_crud.crud.create_superuser(
        db,
        email=email,
        password=password,
    )

    if user and settings.DEBUG:
        print(f"Created user: {email}")
    else:
        if settings.DEBUG:
            print(f"User: {email} already exist")
