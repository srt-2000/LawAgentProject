"""
WebSocket auth: read JWT from handshake cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends

from app.api.dependencies.base import get_current_active_user
from app.api.dependencies.dao import UserDAODep
from app.api.dependencies.tokens import AccessTokenServiceDep, WSAccessTokenDep
from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO


async def get_websocket_current_active_user(
    user_dao: UserDAODep,
    ws_access_token_service: AccessTokenServiceDep,
    ws_access_token: WSAccessTokenDep,
) -> ResponseUserDTO:
    """Get current active user from WebSocket token.

    Args:
        ws_access_token_service: WebSocket access token service.
        ws_access_token: JWT access token from WebSocket cookies.
        user_dao: UserDAO Dependency.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """
    payload: ResponseAccessTokenPayloadDTO = (
        await ws_access_token_service.async_decode_access_token(ws_access_token)
    )
    return await get_current_active_user(payload, user_dao)


WebsocketCurrentUserDep = Annotated[
    ResponseUserDTO, Depends(get_websocket_current_active_user)
]
