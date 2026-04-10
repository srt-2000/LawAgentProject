"""
Shared auth logic for HTTP and WebSocket.

Load the current active user from DB.
"""

from fastapi import HTTPException, status

from app.constants import BaseConstants
from app.dao.exceptions import ObjectNotFoundException
from app.api.dependencies.constants import DependencyMessages
from app.api.dependencies.dao import UserDAODep
from app.models.models import User
from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.schemas.users import ResponseUserDTO


async def get_current_active_user(
    payload: ResponseAccessTokenPayloadDTO, user_dao: UserDAODep
) -> ResponseUserDTO:
    """Get current active user from a decoded access-token payload.

    Args:
        payload: Decoded access-token payload containing user ID.
        user_dao: UserDAO Dependency.

    Returns:
        ResponseUserDTO: Current authenticated user data.

    Raises:
        HTTPException: If user not found or account is disabled.
    """
    user_id: str = payload.sub

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=DependencyMessages.USER_NOT_FOUND,
        )

    try:
        user: User = await user_dao.get_one_user(
            filter_by={BaseConstants.ID: int(user_id)}
        )
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=DependencyMessages.USER_NOT_FOUND,
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=BaseConstants.USER_DISABLED
        )

    return ResponseUserDTO.model_validate(user)
