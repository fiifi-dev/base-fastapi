import logging
from sqlalchemy.orm import Session

from core.config import settings
from core import database
from helpers import storage
import sqlalchemy_utils
from crud import user_crud


def create_first_user(db: Session):
    logging.info("hello world!")
    email = email = settings.ROOT_USER_EMAIL
    password = settings.ROOT_USER_PASSWORD

    if settings.DEBUG:
        print("Creating user...")

    user = user_crud.crud.create_superuser(
        db,
        email=email,
        password=password,
    )

    if user:
        if settings.DEBUG:
            print(f"Created user: {email}")
        else:
            logging.info(f"Created user: {email}")
    else:
        if settings.DEBUG:
            print(f"User: {email} already exist")
        if settings.DEBUG:
            logging.info(f"User: {email} already exist")


def create_database():
    url = database.engine.url
    if not sqlalchemy_utils.database_exists(url):
        sqlalchemy_utils.create_database(url)

        if settings.DEBUG:
            print("Creating Database...")
        else:
            logging.info("Creating Database...")


def create_minio_bucket():
    if settings.USE_MINIO:
        minio_storage = storage.MinioStorage()
        minio_storage.check_bucket_existence()
