"""
Shared auth logic for HTTP and WebSocket.

Load the current active user from the database. Inactive accounts raise a domain
exception mapped to HTTP or WebSocket errors in route dependencies.
"""

import loguru
from fastapi import HTTPException, status

from app.api.dependencies.exceptions import CurrentUserNotActiveException
from app.dao.exceptions import ObjectNotFoundException
from app.api.constants import Messages, Fields
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
        user_dao: User data access dependency.

    Returns:
        ResponseUserDTO: Current authenticated user data.

    Raises:
        HTTPException: If ``sub`` is missing or the user is not found.
        CurrentUserNotActiveException: If the user exists but ``is_active`` is False.
    """
    user_id: str = payload.sub

    if not user_id:
        loguru.logger.exception(Messages.NO_USER_ID_IN_TOKEN)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Messages.AUTH_DATA_NOT_CORRECT,
        )

    try:
        user: User = await user_dao.get_one_user(filter_by={Fields.ID: int(user_id)})
    except ObjectNotFoundException:
        loguru.logger.exception(Messages.USER_NOT_FOUND)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Messages.AUTH_DATA_NOT_CORRECT,
        )

    if not user.is_active:
        loguru.logger.warning(f"{user_id} {Messages.USER_IS_NOT_ACTIVE}")
        raise CurrentUserNotActiveException

    return ResponseUserDTO.model_validate(user)
