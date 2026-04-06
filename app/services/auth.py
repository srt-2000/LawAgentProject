"""
User authentication and password services.

This module provides password hashing, verification, and JWT token management.
"""

from typing import Final

import bcrypt
from fastapi import HTTPException, status
from pydantic import EmailStr
from app.config import settings
from app.constants import BaseConstants
from app.dao.exceptions import ObjectNotFoundException
from app.api.dependencies.dao import UserDAODep
from app.models.models import User
from app.services.constants import FieldNames, FieldsValues, StandardMessages
from app.schemas.users import AuthServiceUserDomain


class PasswordService:
    """Service for password hashing and verification."""

    _ENCODING: Final[str] = FieldsValues.UTF_8

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password to hash.

        Returns:
            str: Hashed password.
        """
        salt = bcrypt.gensalt(rounds=settings.auth.ROUNDS)
        hashed = bcrypt.hashpw(password.encode(cls._ENCODING), salt)
        return hashed.decode(cls._ENCODING)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify.
            hashed_password: Hashed password to verify against.

        Returns:
            bool: True if password matches, False otherwise.
        """
        return bcrypt.checkpw(
            plain_password.encode(cls._ENCODING), hashed_password.encode(cls._ENCODING)
        )


class AuthService(PasswordService):
    """Service for user authentication."""

    @classmethod
    async def authenticate_user(
        cls, email: EmailStr, password: str, user_dao: UserDAODep
    ) -> AuthServiceUserDomain:
        """Authenticate user by email and password.

        Args:
            email: User's email address.
            password: User's plain text password.
            user_dao: UserDAO Dependency.

        Returns:
            AuthServiceUserDomain | None: User data if authenticated, None if invalid credentials.

        Raises:
            HTTPException: If user account is not active.
        """
        try:
            user: User = await user_dao.get_one_user(
                filter_by={FieldNames.EMAIL: email}
            )
        except ObjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.USER_NOT_FOUND,
            )

        if not cls.verify_password(
            plain_password=password, hashed_password=str(user.password_hash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.USER_NOT_FOUND,
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=BaseConstants.USER_DISABLED,
            )

        return AuthServiceUserDomain.model_validate(user)
