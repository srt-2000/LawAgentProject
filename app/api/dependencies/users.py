"""
HTTP auth dependency: read JWT from request cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends

from app.api.dependencies.base import get_current_active_user
from app.api.dependencies.dao import UserDAODep
from app.api.dependencies.tokens import TokenServiceDep, HttpAccessTokenDep

from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO


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
    """
    payload: ResponseAccessTokenPayloadDTO = http_token_service.decode_access_token(
        http_access_token
    )
    return await get_current_active_user(payload, user_dao)


CurrentUserDep = Annotated[ResponseUserDTO, Depends(get_request_current_active_user)]
