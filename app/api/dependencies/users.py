"""
HTTP auth dependency: read JWT from request cookies and resolve to current user.
"""

from typing import Annotated

from fastapi import HTTPException, Request, status, Depends

from app.api.dependencies.base import decode_token, get_current_active_user
from app.api.dependencies.constants import DependencyMessages, FieldValues
from app.api.dependencies.dao import UserDAODep
from app.schemas.dependencies import ResponsePayloadDTO
from app.schemas.users import ResponseUserDTO


def extract_token(request: Request) -> str:
    """Extract authentication token from HTTP request cookies.

    Args:
        request: FastAPI request instance.

    Returns:
        str: JWT access token.

    Raises:
        HTTPException: If token not found in cookies.
    """
    current_token: str | None = request.cookies.get(FieldValues.USERS_ACCESS_TOKEN)

    if not current_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=DependencyMessages.TOKEN_NOT_VALID
        )
    return current_token


async def get_request_current_active_user(
    user_dao: UserDAODep,
    token: str = Depends(extract_token)
) -> ResponseUserDTO:
    """Get current active user from HTTP request token.

    Args:
        user_dao: UserDAO Dependency,
        token: JWT token from request cookies.

    Returns:
        ResponseUserDTO: Authenticated user data.
    """
    payload: ResponsePayloadDTO = await decode_token(token)
    return await get_current_active_user(payload, user_dao)


CurrentUserDep = Annotated[ResponseUserDTO, Depends(get_request_current_active_user)]
