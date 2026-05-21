"""
User authentication and password services.

Provides bcrypt hashing (sync and async) and credential validation that loads users
from the database layer.
"""

from typing import Final

import anyio
import bcrypt
from loguru import logger
from pydantic import EmailStr
from app.config import settings
from app.dao.users import UserDAO
from app.models.models import User
from app.services.constants import Fields, UTF_8, Messages
from app.schemas.users import AuthServiceUserDomain
from app.services.exceptions import AuthenticationFailed


class PasswordService:
    """Service for password hashing and verification."""

    _ENCODING: Final[str] = UTF_8

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password to hash.

        Returns:
            str: Hashed password.
        """
        salt: bytes = bcrypt.gensalt(rounds=settings.auth.ROUNDS)
        hashed: bytes = bcrypt.hashpw(password.encode(cls._ENCODING), salt)
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
        cls, email: EmailStr, password: str, user_dao: UserDAO
    ) -> AuthServiceUserDomain:
        """Authenticate user by email and password.

        Args:
            email: User's email address.
            password: User's plain text password.
            user_dao: User data access dependency.

        Returns:
            AuthServiceUserDomain: Authenticated user projection without secrets.

        Raises:
            AuthenticationFailed: If password is invalid or account is disabled.
            ObjectNotFoundException: If no user exists for the given email (propagated from DAO).
        """
        user: User = await user_dao.get_one_user(filter_by={Fields.EMAIL: email})

        if not await cls.get_async_verify_password(
            plain_password=password, hashed_password=str(user.password_hash)
        ):
            logger.warning(Messages.PASSWORD_DOESNT_MATCH)
            raise AuthenticationFailed

        if not user.is_active:
            logger.warning(Messages.USER_DISABLED)
            raise AuthenticationFailed

        return AuthServiceUserDomain.model_validate(user)
