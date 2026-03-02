"""
Base dependencies for authentication.

This module provides core authentication dependencies for decoding
tokens and retrieving active users.
"""

from datetime import datetime, timezone
from typing import cast

import jwt
from fastapi import HTTPException, status
from jwt import DecodeError, ExpiredSignatureError

from app.config import settings
from app.dependencies.dao_dependencies import UserDAODep
from app.models.models import User
from app.schemas.config_schema import AuthConfigDTO
from app.schemas.dependencies_schema import ResponsePayloadDTO
from app.schemas.users_schema import ResponseUserDTO


async def decode_token(token: str) -> ResponsePayloadDTO:
    """Decode and validate JWT token.

    Args:
        token: JWT token string to decode.

    Returns:
        ResponsePayloadDTO: Decoded and validated token payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        auth_data: AuthConfigDTO = cast(AuthConfigDTO, settings.auth.auth_config)
        payload: ResponsePayloadDTO = jwt.decode(
            token, auth_data.secret_key, algorithms=[auth_data.algorithm]
        )
        valid_payload: ResponsePayloadDTO = ResponsePayloadDTO.model_validate(payload)
    except (DecodeError, ExpiredSignatureError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid"
        )

    expire: int | None = valid_payload.exp

    if expire is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid"
        )

    expire_time: datetime = datetime.fromtimestamp(expire, tz=timezone.utc)

    if expire_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is expired"
        )

    return valid_payload


async def get_current_active_user(
    payload: ResponsePayloadDTO,
    user_dao: UserDAODep
) -> ResponseUserDTO:
    """Get current active user from token payload.

    Args:
        payload: Decoded token payload containing user ID.
        user_dao: UserDAO Dependency.

    Returns:
        ResponseUserDTO: Current authenticated user data.

    Raises:
        HTTPException: If user not found or account is disabled.
    """
    user_id: str = payload.sub

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    user: User | None = await user_dao.find_one_or_none(id=int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled"
        )

    return ResponseUserDTO.model_validate(user)
