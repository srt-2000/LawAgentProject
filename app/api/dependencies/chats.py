"""
WebSocket auth: read JWT from handshake cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import WebSocket, HTTPException
from fastapi.params import Depends
from starlette import status

from app.api.dependencies.base import decode_token, get_current_active_user
from app.api.dependencies.constants import DependencyMessages, FieldValues
from app.api.dependencies.dao import UserDAODep
from app.schemas.dependencies import ResponsePayloadDTO
from app.schemas.users import ResponseUserDTO


def get_token_from_websocket(storage: WebSocket) -> str:
    """Extract JWT from the WebSocket handshake cookies.

    Args:
        storage: WebSocket connection (cookies are taken from the handshake).

    Returns:
        str: JWT access token string.

    Raises:
        HTTPException: 401 if cookie "users_access_token" is missing.
    """
    current_token: str | None = storage.cookies.get(FieldValues.USERS_ACCESS_TOKEN)

    if not current_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=DependencyMessages.TOKEN_NOT_VALID
        )
    return current_token


WebsocketToken = Annotated[str, Depends(get_token_from_websocket)]


async def get_websocket_current_active_user(
    token: WebsocketToken,
    user_dao: UserDAODep
) -> ResponseUserDTO:
    """Get current active user from WebSocket token.

    Args:
        token: JWT token from WebSocket cookies.
        user_dao: UserDAO Dependency.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """
    payload: ResponsePayloadDTO = await decode_token(token)
    return await get_current_active_user(payload, user_dao)


WebsocketCurrentUserDep = Annotated[
    ResponseUserDTO, Depends(get_websocket_current_active_user)
]
