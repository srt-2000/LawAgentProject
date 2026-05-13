"""
User authentication and profile API.

Endpoints cover registration, login (sets cookies), logout, token refresh, current user
profile read/update, and account disable.
"""

from fastapi import APIRouter, HTTPException, status, Response
from pydantic import EmailStr

from app.api.dependencies.tokens import (
    TokenServiceDep,
    RefreshManagerDep,
    HttpRefreshTokenDep,
)
from app.constants import BaseConstants
from app.dao.exceptions import ObjectNotFoundException
from app.api.constants import Fields, Values, Messages, LAX, ROOT_PATH, REFRESH_PATH
from app.api.dependencies.dao import UserDAODep
from app.models.models import User
from app.schemas.users import (
    RequestUserRegistrationDTO,
    RequestUserAuthDTO,
    ResponseUserDTO,
    RequestUserUpdateDTO,
    ResponseMessageDTO,
    ResponseDataUserLoginDTO,
    AuthServiceUserDomain,
    ResponseDataUserRefreshDTO,
)
from app.services.auth import AuthService
from app.api.dependencies.users import CurrentUserDep

router = APIRouter(prefix="/user", tags=[Values.USER_TAG])


@router.post("/register")
async def register_user(
    new_user_data: RequestUserRegistrationDTO, user_dao: UserDAODep
) -> ResponseMessageDTO:
    """Register a new user.

    Args:
        new_user_data: User registration data.
        user_dao: User data access dependency.

    Returns:
        ResponseMessageDTO: Success message with username.

    Raises:
        HTTPException: If user with email already exists.
    """
    try:
        await user_dao.get_one_user(filter_by={"email": new_user_data.email})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Messages.USER_IS_EXIST,
        )
    except ObjectNotFoundException:
        new_user_data_to_add: dict[str, str] = new_user_data.model_dump(
            exclude={Fields.PASSWORD_CONFIRM}
        )
        new_user_data_to_add[
            Fields.PASSWORD_HASH
        ] = await AuthService.get_async_password_hash(
            new_user_data_to_add.pop(Fields.PASSWORD)
        )
        await user_dao.add(**new_user_data_to_add)
        message: dict[str, str] = {
            BaseConstants.MESSAGE_FIELD: f"{new_user_data.name} {Messages.USER_REGISTERED}"
        }
    return ResponseMessageDTO.model_validate(message)


@router.post("/login")
async def login_user(
    response: Response,
    login_user_data: RequestUserAuthDTO,
    user_dao: UserDAODep,
    token_service: TokenServiceDep,
    refresh_token_manager: RefreshManagerDep,
) -> ResponseDataUserLoginDTO:
    """Authenticate user and set HTTP-only access and refresh token cookies.

    Args:
        response: FastAPI response object used to set cookies.
        login_user_data: User login credentials.
        user_dao: User data access dependency.
        token_service: JWT access token creation and validation service.
        refresh_token_manager: Redis-backed refresh token rotation manager.

    Returns:
        ResponseDataUserLoginDTO: Login response with tokens.

    Raises:
        HTTPException: If credentials are invalid.
    """
    try:
        check_user: AuthServiceUserDomain = await AuthService.authenticate_user(
            email=login_user_data.email,
            password=login_user_data.password,
            user_dao=user_dao,
        )
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Messages.AUTH_DATA_NOT_CORRECT,
        )

    access_token: str = token_service.create_access_token(str(check_user.id))
    refresh_token: str = await refresh_token_manager.create_refresh_token(check_user.id)

    response.set_cookie(
        key=Values.USERS_ACCESS_TOKEN,
        value=access_token,
        httponly=True,
        samesite=LAX,
        secure=True,
        path=ROOT_PATH,
    )
    response.set_cookie(
        key=Values.USERS_REFRESH_TOKEN,
        value=refresh_token,
        httponly=True,
        samesite=LAX,
        secure=True,
        path=REFRESH_PATH,
    )
    response_data = {
        Fields.OK: True,
        Fields.ACCESS_TOKEN: access_token,
        BaseConstants.MESSAGE_FIELD: Messages.AUTH_SUCCESS,
    }
    return ResponseDataUserLoginDTO.model_validate(response_data)


@router.post("/logout")
async def logout_user(
    response: Response,
    refresh_token: HttpRefreshTokenDep,
    refresh_token_manager: RefreshManagerDep,
) -> ResponseMessageDTO:
    """Log out user by revoking refresh storage and clearing auth cookies.

    Args:
        response: FastAPI response object used to delete cookies.
        refresh_token: Refresh token from HTTP cookies.
        refresh_token_manager: Manager that revokes the refresh token server-side.

    Returns:
        ResponseMessageDTO: Logout confirmation message.
    """
    await refresh_token_manager.revoke_refresh_token(refresh_token)
    response.delete_cookie(
        key=Values.USERS_ACCESS_TOKEN, path=ROOT_PATH
    )
    response.delete_cookie(
        key=Values.USERS_REFRESH_TOKEN, path=REFRESH_PATH
    )
    message: dict[str, str] = {
        BaseConstants.MESSAGE_FIELD: Messages.LOGOUT_MESSAGE
    }
    return ResponseMessageDTO.model_validate(message)


@router.post("/refresh")
async def refresh_access_token_session(
    response: Response,
    refresh_token: HttpRefreshTokenDep,
    token_service: TokenServiceDep,
    refresh_token_manager: RefreshManagerDep,
) -> ResponseDataUserRefreshDTO:
    """Rotate refresh session and issue new access and refresh token cookies.

    Args:
        response: FastAPI response object used to set cookies.
        refresh_token: Current refresh token from HTTP cookies.
        token_service: JWT access token creation service.
        refresh_token_manager: Manager that validates and rotates refresh tokens.

    Returns:
        ResponseDataUserRefreshDTO: Success payload with new access token and message.

    Raises:
        HTTPException: If refresh token is invalid, expired, or storage mismatches.
    """
    user_id: str = await refresh_token_manager.revoke_refresh_token(refresh_token)
    new_access_token: str = token_service.create_access_token(user_id)
    new_refresh_token: str = await refresh_token_manager.create_refresh_token(
        int(user_id)
    )

    response.set_cookie(
        key=Values.USERS_ACCESS_TOKEN,
        value=new_access_token,
        httponly=True,
        samesite=LAX,
        secure=True,
        path=ROOT_PATH,
    )
    response.set_cookie(
        key=Values.USERS_REFRESH_TOKEN,
        value=new_refresh_token,
        httponly=True,
        samesite=LAX,
        secure=True,
        path=REFRESH_PATH,
    )
    response_data = {
        Fields.OK: True,
        Fields.ACCESS_TOKEN: new_access_token,
        BaseConstants.MESSAGE_FIELD: Messages.ACCESS_TOKEN_REFRESHED,
    }
    return ResponseDataUserRefreshDTO.model_validate(response_data)


@router.get("/me", response_model=ResponseUserDTO)
async def get_me(current_user: CurrentUserDep) -> ResponseUserDTO:
    """Get current authenticated user information.

    Args:
        current_user: Authenticated current user.

    Returns:
        ResponseUserDTO: Current user data.
    """
    return ResponseUserDTO.model_validate(current_user)


@router.patch("/me", response_model=ResponseUserDTO)
async def update_me(
    update_user: RequestUserUpdateDTO,
    current_user: CurrentUserDep,
    user_dao: UserDAODep,
) -> ResponseUserDTO:
    """Update current user's profile information.

    Args:
        update_user: Fields to update.
        current_user: Authenticated current user.
        user_dao: User data access dependency.

    Returns:
        ResponseUserDTO: Updated user data.

    Raises:
        HTTPException: If user not found after update.
    """
    update_data: dict[str, str | EmailStr] = update_user.model_dump(
        exclude_none=True, exclude={Fields.PASSWORD_CONFIRM}
    )

    if Fields.PASSWORD in update_data:
        update_data[
            Fields.PASSWORD_HASH
        ] = await AuthService.get_async_password_hash(
            update_data.pop(Fields.PASSWORD)
        )

    if update_data:
        try:
            updated_user: User = await user_dao.update(
                filter_by={Fields.ID: current_user.id}, **update_data
            )
        except ObjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.USER_NOT_FOUND,
            )

        return ResponseUserDTO.model_validate(updated_user)

    return ResponseUserDTO.model_validate(current_user)


@router.patch("/me/disable")
async def disable_me(
    current_user: CurrentUserDep, user_dao: UserDAODep
) -> ResponseMessageDTO:
    """Disable current user's account.

    Args:
        current_user: Authenticated current user.
        user_dao: User data access dependency.

    Returns:
        ResponseMessageDTO: Confirmation message.
    """
    try:
        disabled_user: User = await user_dao.update(
            filter_by={Fields.ID: current_user.id}, is_active=False
        )

        if disabled_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=Messages.USER_NOT_DISABLED,
            )

    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Messages.USER_NOT_FOUND,
        )

    message: dict[str, str] = {
        BaseConstants.MESSAGE_FIELD: f"{disabled_user.name} {BaseConstants.USER_DISABLED}"
    }
    return ResponseMessageDTO.model_validate(message)
