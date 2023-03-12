from datetime import datetime
from pydantic import BaseModel, validator
from helpers import storage


class CreateStoreSchema(BaseModel):
    link: str
    thumb: str | None = None


minio = storage.MinioStorage()


class ReadStoreSchema(CreateStoreSchema):
    id: int | None = None
    created_at: datetime

    @validator("link")
    def pre_sign_link(cls, v):
        return minio.url(v)

    @validator("thumb")
    def pre_sign_thumb(cls, v):
        if not v:
            return None
        return minio.url(v)

    class Config:
        orm_mode = True
