"""
HTTP request authentication dependencies.

This module provides dependencies for authenticating standard HTTP requests
using cookies.
"""

from typing import Annotated

from fastapi import HTTPException, Request, status, Depends

from app.dependencies.base_dependencies import decode_token, get_current_active_user
from app.schemas.dependencies_schema import ResponsePayloadDTO
from app.schemas.users_schema import ResponseUserDTO


def extract_token(request: Request) -> str:
    """Extract authentication token from HTTP request cookies.

    Args:
        request: FastAPI request instance.

    Returns:
        str: JWT access token.

    Raises:
        HTTPException: If token not found in cookies.
    """
    current_token: str | None = request.cookies.get("users_access_token")

    if not current_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found"
        )
    return current_token


async def get_request_current_active_user(
    token: str = Depends(extract_token),
) -> ResponseUserDTO:
    """Get current active user from HTTP request token.

    Args:
        token: JWT token from request cookies.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """
    payload: ResponsePayloadDTO = await decode_token(token)
    return await get_current_active_user(payload)


CurrentUserDep = Annotated[ResponseUserDTO, Depends(get_request_current_active_user)]
