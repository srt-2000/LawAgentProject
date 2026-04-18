"""
WebSocket auth: read JWT from handshake cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends, WebSocket, HTTPException, WebSocketException
from loguru import logger
from starlette.status import WS_1008_POLICY_VIOLATION

from app.api.dependencies.base import get_current_active_user
from app.api.dependencies.constants import Values, DependencyMessages
from app.api.dependencies.dao import UserDAODep
from app.api.dependencies.tokens import TokenServiceDep
from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO


async def get_websocket_current_active_user(
    user_dao: UserDAODep,
    websocket: WebSocket,
    token_service: TokenServiceDep,
) -> ResponseUserDTO:
    """Get current active user from WebSocket token.

    Args:
        user_dao: User data access dependency.
        websocket: Incoming WebSocket connection (cookies from handshake).
        token_service: JWT service used to read and decode the access token.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """

    try:
        ws_access_token: str = token_service.get_access_token_from_websocket(websocket)
        payload: ResponseAccessTokenPayloadDTO = token_service.decode_access_token(
            ws_access_token
        )
        current_active_user: ResponseUserDTO = await get_current_active_user(
            payload, user_dao
        )
    except HTTPException as exception:
        reason: str = str(exception.detail)[: Values.REASON_LEN_LIMIT]
        logger.warning(DependencyMessages.ERROR_GET_WS_ACTIVE_USER)
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        ) from exception

    return current_active_user


WebsocketCurrentUserDep = Annotated[
    ResponseUserDTO, Depends(get_websocket_current_active_user)
]
