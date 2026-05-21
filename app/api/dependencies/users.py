"""
HTTP auth dependency: read JWT from request cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from loguru import logger

from app.api.constants import Messages
from app.api.dependencies.base import get_current_active_user
from app.api.dependencies.dao import UserDAODep
from app.api.dependencies.exceptions import CurrentUserNotActiveException
from app.api.dependencies.tokens import TokenServiceDep, HttpAccessTokenDep

from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO
from app.services.exceptions import TokenCheckFailed


async def get_request_current_active_user(
    user_dao: UserDAODep,
    http_token_service: TokenServiceDep,
    http_access_token: HttpAccessTokenDep,
) -> ResponseUserDTO:
    """Get current active user from an HTTP request access token.

    Args:
        user_dao: User data access dependency.
        http_token_service: JWT encode/decode service dependency.
        http_access_token: JWT access token from HTTP request cookies.

    Returns:
        ResponseUserDTO: Authenticated user data.

    Raises:
        HTTPException: 401 if the access token is invalid or the user is inactive.
    """
    try:
        payload: ResponseAccessTokenPayloadDTO = http_token_service.decode_access_token(
            http_access_token
        )
    except TokenCheckFailed as error:
        logger.warning(str(error))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Messages.AUTH_DATA_NOT_CORRECT,
        )

    try:
        user: ResponseUserDTO = await get_current_active_user(payload, user_dao)
        return user
    except CurrentUserNotActiveException:
        logger.warning(Messages.USER_IS_NOT_ACTIVE)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Messages.AUTH_DATA_NOT_CORRECT,
        )


CurrentUserDep = Annotated[ResponseUserDTO, Depends(get_request_current_active_user)]
