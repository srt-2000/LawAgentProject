"""
HTTP auth dependency: read JWT from request cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends

from app.api.dependencies.base import get_current_active_user
from app.api.dependencies.dao import UserDAODep
from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO
from app.services.tokens import AccessTokenService


http_token_service: AccessTokenService = AccessTokenService()
HttpAccessToken = Annotated[str, Depends(http_token_service.get_access_token_from_http)]


async def get_request_current_active_user(
    user_dao: UserDAODep, token: HttpAccessToken
) -> ResponseUserDTO:
    """Get current active user from HTTP request token.

    Args:
        user_dao: UserDAO Dependency,
        token: JWT token from request cookies.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """
    payload: ResponseAccessTokenPayloadDTO = (
        await http_token_service.decode_access_token(token)
    )
    return await get_current_active_user(payload, user_dao)


CurrentUserDep = Annotated[ResponseUserDTO, Depends(get_request_current_active_user)]
