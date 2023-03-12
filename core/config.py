import pathlib
from pydantic import AnyHttpUrl, BaseSettings, validator

BASE_DIR = pathlib.Path(__file__).parent.parent.as_posix()


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "mysql://root:testpass123@127.0.0.1:3306/student_management_system"
    )
    SECRET_KEY: str = "JCcwf0uIN6IUlFoBOqWipUdqqOjgr3UyFZTtTtfpI4UhdMdLjuNeYt9stvNOdEM9"
    DEBUG = True
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 60 * 24 * 8
    PROJECT_NAME = "flarewebs"
    SERVER_HOST: str = "localhost"  # for frontend email verification
    ALLOWED_HOSTS: list[AnyHttpUrl] = []
    MEDIA_DIR = (pathlib.Path(BASE_DIR) / "media").as_posix()

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> str | list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Email
    EMAIL_TEMPLATES_DIR = (pathlib.Path(BASE_DIR) / "templates").as_posix()
    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = "flarewebs@email.com"
    EMAILS_FROM_NAME: str | None = "flarewebs"

    # First User
    ROOT_USER_EMAIL: str = "testuser@email.com"
    ROOT_USER_PASSWORD: str = "testpass123"

    # Storage Minio
    USE_MINIO: bool = True
    MINIO_ENDPOINT: str | None = None
    MINIO_ACCESS_KEY: str | None = None
    MINIO_SECRET_KEY: str | None = None
    MINIO_BUCKET: str | None = None
    MINIO_PUBLIC_LOCATIONS = ["public"]
    MINIO_URL_EXPIRY_DAYS: int = 7


settings = Settings()
