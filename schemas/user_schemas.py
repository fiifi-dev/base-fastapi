from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, validator


class RoleEnum(str, Enum):
    user = "user"
    editor = "editor"
    admin = "editor"


# Shared properties
class UserBaseSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class RegisterUserSchema(UserBaseSchema):
    password: str
    password_confirm: str

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


class CreateAdminSchema(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.user


class UpdateUserSchema(UserBaseSchema):
    pass


class ReadUserSchema(UserBaseSchema):
    id: int | None = None
    email: EmailStr | None = None
    role: RoleEnum = RoleEnum.user
    is_active: bool = False
    is_verified: bool = False
    is_superuser: bool = False
    last_login: datetime | None = None
    date_joined: datetime

    class Config:
        orm_mode = True


class WriteUserSchema(UserBaseSchema):
    hashed_password: str
    email: EmailStr
    role: RoleEnum = RoleEnum.user


class ChangeUserPasswordSchema(BaseModel):
    old_password: str
    password: str
    password_confirm: str

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


class ResetUserPasswordSchema(BaseModel):
    password: str
    password_confirm: str

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v
