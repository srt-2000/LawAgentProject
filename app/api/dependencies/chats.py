"""
WebSocket auth: read JWT from handshake cookies and resolve to current user.
"""

from typing import Annotated

from fastapi.params import Depends

from app.api.dependencies.base import get_current_active_user
from app.api.dependencies.dao import UserDAODep
from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO
from app.services.tokens import AccessTokenService


ws_token_service: AccessTokenService = AccessTokenService()
WebsocketAccessToken = Annotated[
    str, Depends(ws_token_service.get_access_token_from_websocket)
]


async def get_websocket_current_active_user(
    token: WebsocketAccessToken, user_dao: UserDAODep
) -> ResponseUserDTO:
    """Get current active user from WebSocket token.

    Args:
        token: JWT token from WebSocket cookies.
        user_dao: UserDAO Dependency.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """
    payload: ResponseAccessTokenPayloadDTO = await ws_token_service.decode_access_token(
        token
    )
    return await get_current_active_user(payload, user_dao)


WebsocketCurrentUserDep = Annotated[
    ResponseUserDTO, Depends(get_websocket_current_active_user)
]
