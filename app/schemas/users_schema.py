"""
User data transfer objects.

This module defines Pydantic schemas for user-related requests and responses.
"""

from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict

from app.schemas.chats_schema import ChatWithMessagesDTO
from app.models.models import Role


class RequestUserRegistrationDTO(BaseModel):
    """User registration request schema.

    Attributes:
        name: User's display name (2-50 characters).
        email: User's email address.
        password: User's password (6-50 characters).
        password_confirm: Password confirmation.
    """

    name: str = Field(
        ..., min_length=2, max_length=50, description="Display name, 2 to 50 characters"
    )
    email: EmailStr = Field(..., description="Email", examples=["user@example.com"])
    password: str = Field(
        ..., min_length=6, max_length=50, description="Password, 6 to 50 characters"
    )
    password_confirm: str = Field(
        ..., min_length=6, max_length=50, description="Must match password"
    )

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        """Validate that passwords match.

        Returns:
            Self: Validated instance.

        Raises:
            ValueError: If passwords don't match.
        """
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class RequestUserAuthDTO(BaseModel):
    """User authentication request schema.

    Attributes:
        email: User's email address.
        password: User's password (6-50 characters).
    """

    email: EmailStr = Field(..., description="Email", examples=["user@example.com"])
    password: str = Field(
        ..., min_length=6, max_length=50, description="Password, 6 to 50 characters"
    )


class RequestUserUpdateDTO(BaseModel):
    """User profile update request schema.

    Attributes:
        name: Updated display name (optional).
        email: Updated email address (optional).
        password: Updated password (optional).
        password_confirm: Password confirmation (optional).
    """

    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    password_confirm: str | None = None

    @model_validator(mode="after")
    def passwords_update_match(self) -> Self:
        """Validate password update requirements.

        Returns:
            Self: Validated instance.

        Raises:
            ValueError: If passwords don't match or only one is provided.
        """
        if self.password is not None and self.password_confirm is not None:
            if self.password != self.password_confirm:
                raise ValueError("Passwords do not match")
        elif (self.password is None) ^ (self.password_confirm is None):
            raise ValueError("Both password and password confirm must be provided")
        return self


class ResponseUserDTO(BaseModel):
    """User response schema (without password).

    Attributes:
        id: User ID.
        name: User's display name.
        email: User's email address.
        role: User role (admin or user).
        is_active: Account active status.
        chats: List of user's chats.
    """

    id: int
    name: str
    email: EmailStr
    role: Role
    is_active: bool
    chats: list[ChatWithMessagesDTO] | None = None

    model_config = ConfigDict(from_attributes=True)


class DBUserDTO(BaseModel):
    """Database user schema (with password hash).

    Attributes:
        id: User ID.
        name: User's display name.
        email: User's email address.
        password_hash: Hashed password.
        role: User role (admin or user).
        is_active: Account active status.
        chats: List of user's chats.
    """

    id: int
    name: str
    email: EmailStr
    password_hash: str
    role: Role
    is_active: bool
    chats: list[ChatWithMessagesDTO] | None = None

    model_config = ConfigDict(from_attributes=True)


class ResponseMessageDTO(BaseModel):
    """Generic message response schema.

    Attributes:
        message: Response message text.
    """

    message: str | None


class ResponseDataUserLoginDTO(BaseModel):
    """Login response schema.

    Attributes:
        ok: Success status.
        access_token: JWT access token.
        refresh_token: JWT refresh token (not yet implemented).
        message: Response message.
    """

    ok: bool
    access_token: str
    refresh_token: str | None
    message: str
