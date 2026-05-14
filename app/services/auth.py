"""
User authentication and password services.

Provides bcrypt hashing (sync and async) and credential validation that loads users
from the database layer.
"""

from typing import Final

import anyio
import bcrypt
from fastapi import HTTPException, status
from pydantic import EmailStr
from app.config import settings
from app.dao.exceptions import ObjectNotFoundException
from app.api.dependencies.dao import UserDAODep
from app.models.models import User
from app.services.constants import Fields, UTF_8, Messages
from app.schemas.users import AuthServiceUserDomain


class PasswordService:
    """Service for password hashing and verification."""

    _ENCODING: Final[str] = UTF_8

    # It's a base sync methods to use in thread pool for async def
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

    # It's async methods to use sync with thread pool
    @classmethod
    async def get_async_password_hash(cls, password: str) -> str:
        """Hash a password off the event loop via a worker thread.

        Args:
            password: Plain text password to hash.

        Returns:
            str: Hashed password.
        """
        async_password_hash: str = await anyio.to_thread.run_sync(
            cls.get_password_hash, password
        )

        return async_password_hash

    @classmethod
    async def get_async_verify_password(
        cls, plain_password: str, hashed_password: str
    ) -> bool:
        """Verify credentials off the event loop via a worker thread.

        Args:
            plain_password: Plain text password to verify.
            hashed_password: Hashed password to verify against.

        Returns:
            bool: True if password matches, False otherwise.
        """
        verify_result: bool = await anyio.to_thread.run_sync(
            cls.verify_password, plain_password, hashed_password
        )

        return verify_result


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
            user_dao: User data access dependency.

        Returns:
            AuthServiceUserDomain: Authenticated user projection without secrets.

        Raises:
            HTTPException: If credentials are invalid or account is disabled.
        """
        try:
            user: User = await user_dao.get_one_user(filter_by={Fields.EMAIL: email})
        except ObjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.USER_NOT_FOUND,
            )

        if not await cls.get_async_verify_password(
            plain_password=password, hashed_password=str(user.password_hash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.USER_NOT_FOUND,
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.USER_DISABLED,
            )

        return AuthServiceUserDomain.model_validate(user)
