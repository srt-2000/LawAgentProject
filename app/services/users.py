"""
User authentication and password services.

This module provides password hashing, verification, and JWT token management.
"""

from datetime import timedelta, datetime, timezone
from typing import cast

import bcrypt
import jwt
from fastapi import HTTPException, status
from pydantic import EmailStr
from app.config import settings
from app.dependencies.dao import UserDAODep
from app.models.models import User
from app.schemas.config import AuthConfigDTO
from app.schemas.users import ResponseUserDTO


class PasswordService:
    """Service for password hashing and verification."""

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password to hash.

        Returns:
            str: Hashed password.
        """
        salt = bcrypt.gensalt(rounds=settings.auth.ROUNDS)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

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
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )


class AuthService(PasswordService):
    """Service for user authentication and token management."""

    @classmethod
    async def authenticate_user(
        cls,
        email: EmailStr,
        password: str,
        user_dao: UserDAODep
    ) -> ResponseUserDTO | None:
        """Authenticate user by email and password.

        Args:
            email: User's email address.
            password: User's plain text password.
            user_dao: UserDAO Dependency.

        Returns:
            ResponseUserDTO | None: User data if authenticated, None if invalid credentials.

        Raises:
            HTTPException: If user account is not active.
        """
        user: User | None = await user_dao.find_one_or_none(email=email)

        if not user or not cls.verify_password(
            plain_password=password, hashed_password=str(user.password_hash)
        ):
            return None
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active"
            )

        return ResponseUserDTO.model_validate(user)

    @staticmethod
    def create_access_token(data: str) -> str:
        """Create JWT access token for user.

        Args:
            data: User ID to encode in token.

        Returns:
            str: Encoded JWT token.
        """
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(days=5)
        to_encode = {"sub": data, "exp": expire_time}
        auth_data: AuthConfigDTO = cast(AuthConfigDTO, settings.auth.auth_config)
        encode_jwt: str = jwt.encode(
            to_encode, auth_data.secret_key, algorithm=auth_data.algorithm
        )
        return encode_jwt
