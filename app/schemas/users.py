"""
User data transfer objects.

This module defines Pydantic schemas for user-related requests and responses.
"""

from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict

from app.schemas.chats import ChatWithMessagesDTO
from app.schemas.constants import FieldValues, StandardMessages
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
        ...,
        min_length=FieldValues.NAME_MIN_LEN,
        max_length=FieldValues.MAX_FIELD_LEN,
        description=FieldValues.NAME_FIELD_DESCRIPTION,
    )
    email: EmailStr = Field(
        ...,
        description=FieldValues.EMAIL_FIELD_DESCRIPTION,
        examples=[FieldValues.EMAIL_EXAMPLE],
    )
    password: str = Field(
        ...,
        min_length=FieldValues.PASS_MIN_LEN,
        max_length=FieldValues.MAX_FIELD_LEN,
        description=FieldValues.PASS_FIELD_DESCRIPTION,
    )
    password_confirm: str = Field(
        ...,
        min_length=FieldValues.PASS_MIN_LEN,
        max_length=FieldValues.MAX_FIELD_LEN,
        description=FieldValues.PASS_CONFIRM_DESCRIPTION,
    )

    @model_validator(mode=FieldValues.AFTER_MODE)
    def passwords_match(self) -> Self:
        """Validate that passwords match.

        Returns:
            Self: Validated instance.

        Raises:
            ValueError: If passwords don't match.
        """
        if self.password != self.password_confirm:
            raise ValueError(StandardMessages.PASSWORDS_NOT_MATCH)
        return self  # type: ignore[return-value]


class RequestUserAuthDTO(BaseModel):
    """User authentication request schema.

    Attributes:
        email: User's email address.
        password: User's password (6-50 characters).
    """

    email: EmailStr = Field(
        ...,
        description=FieldValues.EMAIL_FIELD_DESCRIPTION,
        examples=[FieldValues.EMAIL_EXAMPLE],
    )
    password: str = Field(
        ...,
        min_length=FieldValues.PASS_MIN_LEN,
        max_length=FieldValues.MAX_FIELD_LEN,
        description=FieldValues.PASS_FIELD_DESCRIPTION,
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

    @model_validator(mode=FieldValues.AFTER_MODE)
    def passwords_update_match(self) -> Self:
        """Validate password update requirements.

        Returns:
            Self: Validated instance.

        Raises:
            ValueError: If passwords don't match or only one is provided.
        """
        if self.password is not None and self.password_confirm is not None:
            if self.password != self.password_confirm:
                raise ValueError(StandardMessages.PASSWORDS_NOT_MATCH)
        elif (self.password is None) ^ (self.password_confirm is None):
            raise ValueError(StandardMessages.PASS_CONFIRM_REQUIRE)
        return self  # type: ignore[return-value]


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


class AuthServiceUserDomain(BaseModel):
    """User AuthService User Domain schema (without password).

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
        ok: Success flag for the authentication attempt.
        access_token: JWT access token string returned alongside cookies.
        message: Human-readable status message.
    """

    ok: bool
    access_token: str
    message: str


class ResponseDataUserRefreshDTO(BaseModel):
    """Refresh response schema.

    Attributes:
        ok: Success flag for the refresh operation.
        access_token: Newly minted JWT access token string.
        message: Human-readable status message.
    """

    ok: bool
    access_token: str
    message: str
