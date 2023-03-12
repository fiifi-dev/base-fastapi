from typing import Any, Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ListBaseSchema(GenericModel, Generic[T]):
    next: int | None
    prev: int | None
    count: int = 0
    data: list[T] = []


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenPayloadSchema(BaseModel):
    sub: int | None = None


class MessageSchema(BaseModel):
    detail: str


class ErrorBody(BaseModel):
    body: dict[str, Any] = {}
    path: list[str] = []


class ErrorSchema(BaseModel):
    detail: ErrorBody
