"""
WebSocket auth: read JWT from handshake cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends, WebSocket, HTTPException, WebSocketException
from loguru import logger
from starlette.status import WS_1008_POLICY_VIOLATION

from app.api.dependencies.base import get_current_active_user
from app.api.constants import Messages, WS_AUTH_REASON
from app.api.dependencies.dao import UserDAODep
from app.api.dependencies.exceptions import CurrentUserNotActiveException
from app.api.dependencies.tokens import TokenServiceDep
from app.schemas.services import AccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO
from app.services.exceptions import TokenCheckFailed


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

    Raises:
        WebSocketException: Policy violation (1008) if the token is invalid, the user is
            inactive, or user resolution fails; close reason is truncated to
            ``REASON_LEN_LIMIT``.
    """
    try:
        ws_access_token: str = token_service.get_access_token_from_websocket(websocket)
        payload: AccessTokenPayloadDTO = token_service.decode_access_token(
            ws_access_token
        )
    except TokenCheckFailed as exception:
        reason: str = WS_AUTH_REASON
        logger.warning(str(exception))
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        ) from exception

    user_id: int = int(payload.sub)

    if not user_id:
        logger.warning(Messages.NO_USER_ID_IN_TOKEN)
        reason = WS_AUTH_REASON
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        )

    try:
        current_active_user: ResponseUserDTO = await get_current_active_user(
            user_id, user_dao
        )
    except CurrentUserNotActiveException as exception:
        reason = WS_AUTH_REASON
        logger.warning(str(exception))
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        ) from exception
    except HTTPException as exception:
        reason = WS_AUTH_REASON
        logger.warning(f"{Messages.ERROR_GET_WS_ACTIVE_USER} - {str(exception)}")
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        ) from exception

    return current_active_user


WebsocketCurrentUserDep = Annotated[
    ResponseUserDTO, Depends(get_websocket_current_active_user)
]
