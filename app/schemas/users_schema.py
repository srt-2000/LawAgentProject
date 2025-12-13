from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict

from app.schemas.chats_schema import ChatOut
from app.models.models import Role


class RequestUserRegistrationDTO(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Name, from 3 to 50 symbols")
    email: EmailStr = Field(..., description="Email", examples=["user@example.com"])
    password: str = Field(..., min_length=6, max_length=50, description="Password, from 6 tp 50 symbols")
    password_confirm: str = Field(..., min_length=6, max_length=50, description="Password confirmation")

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class RequestUserAuthDTO(BaseModel):
    email: EmailStr = Field(..., description="Email", examples=["user@example.com"])
    password: str = Field(..., min_length=6, max_length=50, description="Password, from 6 tp 50 symbols")


class RequestUserUpdateDTO(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    password_confirm: str | None = None

    @model_validator(mode="after")
    def passwords_update_match(self) -> Self:
        if self.password is not None and self.password_confirm is not None:
            if self.password != self.password_confirm:
                raise ValueError("Passwords do not match")
        elif (self.password is None) ^ (self.password_confirm is None):
            raise ValueError("Both password and password confirm must be provided")
        return self


class ResponseUserDTO(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    is_active: bool
    chats: list[ChatOut] | None = None

    model_config = ConfigDict(from_attributes=True)


class DBUserDTO(BaseModel):
    id: int
    name: str
    email: EmailStr
    password_hash: str
    role: Role
    is_active: bool
    chats: list[ChatOut] | None = None

    model_config = ConfigDict(from_attributes=True)


class ResponseMessageDTO(BaseModel):
    message: str | None


class ResponseDataUserLoginDTO(BaseModel):
    ok: bool
    access_token: str
    refresh_token: str | None
    message: str
