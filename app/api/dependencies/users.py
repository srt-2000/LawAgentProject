"""
HTTP auth dependency: read JWT from request cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends

from app.api.dependencies.base import get_current_active_user
from app.api.dependencies.dao import UserDAODep
from app.api.dependencies.tokens import AccessTokenServiceDep, HttpAccessTokenDep

from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO


async def get_request_current_active_user(
    user_dao: UserDAODep,
    http_token_service: AccessTokenServiceDep,
    http_access_token: HttpAccessTokenDep,
) -> ResponseUserDTO:
    """Get current active user from an HTTP request access token.

    Args:
        user_dao: UserDAO Dependency,
        http_token_service: HTTPTokenService Dependency,
        http_access_token: JWT access token from request cookies.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """
    payload: ResponseAccessTokenPayloadDTO = (
        await http_token_service.async_decode_access_token(http_access_token)
    )
    return await get_current_active_user(payload, user_dao)


CurrentUserDep = Annotated[ResponseUserDTO, Depends(get_request_current_active_user)]
