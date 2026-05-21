"""
WebSocket auth: read JWT from handshake cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import Depends, WebSocket, HTTPException, WebSocketException
from loguru import logger
from starlette.status import WS_1008_POLICY_VIOLATION

from app.api.dependencies.base import get_current_active_user
from app.api.constants import Messages, REASON_LEN_LIMIT
from app.api.dependencies.dao import UserDAODep
from app.api.dependencies.exceptions import CurrentUserNotActiveException
from app.api.dependencies.tokens import TokenServiceDep
from app.schemas.services import ResponseAccessTokenPayloadDTO
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
        payload: ResponseAccessTokenPayloadDTO = token_service.decode_access_token(
            ws_access_token
        )
        current_active_user: ResponseUserDTO = await get_current_active_user(
            payload, user_dao
        )
    except CurrentUserNotActiveException as exception:
        reason: str = Messages.AUTH_DATA_NOT_CORRECT[:REASON_LEN_LIMIT]
        logger.warning(str(exception))
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        ) from exception
    except TokenCheckFailed as exception:
        reason = Messages.AUTH_DATA_NOT_CORRECT[:REASON_LEN_LIMIT]
        logger.warning(str(exception))
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        ) from exception
    except HTTPException as exception:
        reason = Messages.AUTH_DATA_NOT_CORRECT[:REASON_LEN_LIMIT]
        logger.warning(f"{Messages.ERROR_GET_WS_ACTIVE_USER} - {str(exception)}")
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason=reason,
        ) from exception

    return current_active_user


WebsocketCurrentUserDep = Annotated[
    ResponseUserDTO, Depends(get_websocket_current_active_user)
]
