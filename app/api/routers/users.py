"""
User auth and profile: register, login (sets cookie), logout, me, update, disable.
"""

from fastapi import APIRouter, HTTPException, status, Response
from pydantic import EmailStr

from app.api.dependencies.redis import RedisDep
from app.constants import BaseConstants
from app.dao.exceptions import ObjectNotFoundException
from app.api.routers.constants import RouterFieldNames, FieldValues, RouterStandardMessages
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
)
from app.services.users import AuthService
from app.api.dependencies.users import CurrentUserDep

router = APIRouter(prefix="/user", tags=[FieldValues.USER_TAG])


@router.get("/check_redis")
async def get_redis_ping(redis: RedisDep):
    res = await redis.ping()
    return {"redis ping": f"{res}"}


@router.post("/register")
async def register_user(
    new_user_data: RequestUserRegistrationDTO, user_dao: UserDAODep
) -> ResponseMessageDTO:
    """Register a new user.

    Args:
        new_user_data: User registration data.
        user_dao: UserDAO Dependency.

    Returns:
        ResponseMessageDTO: Success message with username.

    Raises:
        HTTPException: If user with email already exists.
    """
    try:
        await user_dao.get_one_user(filter_by={"email": new_user_data.email})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=RouterStandardMessages.USER_IS_EXIST,
        )
    except ObjectNotFoundException:
        new_user_data_to_add: dict[str, str] = new_user_data.model_dump(
            exclude={RouterFieldNames.PASSWORD_CONFIRM}
        )
        new_user_data_to_add[RouterFieldNames.PASSWORD_HASH] = (
            AuthService.get_password_hash(
                new_user_data_to_add.pop(RouterFieldNames.PASSWORD)
            )
        )
        await user_dao.add(**new_user_data_to_add)
        message: dict[str, str] = {
            BaseConstants.MESSAGE_FIELD: f"{new_user_data.name} {RouterStandardMessages.USER_REGISTERED}"
        }
    return ResponseMessageDTO.model_validate(message)


@router.post("/login")
async def login_user(
    response: Response, login_user_data: RequestUserAuthDTO, user_dao: UserDAODep
) -> ResponseDataUserLoginDTO:
    """Authenticate user and set access token cookie.

    Args:
        response: FastAPI response object to set cookies.
        login_user_data: User login credentials.
        user_dao: UserDAO Dependency.

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
            detail=RouterStandardMessages.AUTH_DATA_NOT_CORRECT,
        )

    access_token: str = AuthService.create_access_token(str(check_user.id))

    response.set_cookie(
        key=FieldValues.USERS_ACCESS_TOKEN,
        value=access_token,
        httponly=True,
        samesite=FieldValues.LAX,
        secure=False,
        path=FieldValues.ROOT_PATH,
    )
    response_data = {
        RouterFieldNames.OK: True,
        RouterFieldNames.ACCESS_TOKEN: access_token,
        RouterFieldNames.REFRESH_TOKEN: None,
        BaseConstants.MESSAGE_FIELD: RouterStandardMessages.AUTH_SUCCESS,
    }
    return ResponseDataUserLoginDTO.model_validate(response_data)


@router.post("/logout")
async def logout_user(response: Response) -> ResponseMessageDTO:
    """Log out user by deleting access token cookie.

    Args:
        response: FastAPI response object to delete cookies.

    Returns:
        ResponseMessageDTO: Logout confirmation message.
    """
    response.delete_cookie(key=FieldValues.USERS_ACCESS_TOKEN)
    message = {BaseConstants.MESSAGE_FIELD: RouterStandardMessages.LOGOUT_MESSAGE}
    return ResponseMessageDTO.model_validate(message)


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
        user_dao: UserDAO Dependency.

    Returns:
        ResponseUserDTO: Updated user data.

    Raises:
        HTTPException: If user not found after update.
    """
    update_data: dict[str, str | EmailStr] = update_user.model_dump(
        exclude_none=True, exclude={RouterFieldNames.PASSWORD_CONFIRM}
    )

    if RouterFieldNames.PASSWORD in update_data:
        update_data[RouterFieldNames.PASSWORD_HASH] = AuthService.get_password_hash(
            update_data.pop(RouterFieldNames.PASSWORD)
        )

    if update_data:
        try:
            updated_user: User = await user_dao.update(
                filter_by={RouterFieldNames.ID: current_user.id}, **update_data
            )
        except ObjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RouterStandardMessages.USER_NOT_FOUND,
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
        user_dao: UserDAO Dependency.

    Returns:
        ResponseMessageDTO: Confirmation message.
    """
    try:
        disabled_user: User = await user_dao.update(
            filter_by={RouterFieldNames.ID: current_user.id}, is_active=False
        )

        if disabled_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=RouterStandardMessages.USER_NOT_DISABLED,
            )

    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=RouterStandardMessages.USER_NOT_FOUND,
        )

    message: dict[str, str] = {
        BaseConstants.MESSAGE_FIELD: f"{disabled_user.name} {BaseConstants.USER_DISABLED}"
    }
    return ResponseMessageDTO.model_validate(message)
