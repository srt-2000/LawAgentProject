from fastapi import APIRouter, HTTPException, status, Response
from pydantic import EmailStr

from app.models.models import User
from app.dao.users_dao import UserDAO
from app.schemas.users_schema import (
    RequestUserRegistrationDTO,
    RequestUserAuthDTO,
    ResponseUserDTO,
    RequestUserUpdateDTO,
    ResponseMessageDTO,
    ResponseDataUserLoginDTO
)
from app.services.users_services import AuthService
from app.dependencies.users_dependencies import CurrentUserDep

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/register")
async def register_user(new_user_data: RequestUserRegistrationDTO) -> ResponseMessageDTO | None:
    check_user = await UserDAO.find_one_or_none(email=new_user_data.email)

    if check_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already exist"
        )
    prepare_new_user_data: dict[str, str] = new_user_data.model_dump(exclude={"password_confirm"})
    prepare_new_user_data["password_hash"] = AuthService.get_password_hash(prepare_new_user_data.pop("password"))
    await UserDAO.add(**prepare_new_user_data)
    message = {"message": f"User {new_user_data.name} registered successfully"}
    return ResponseMessageDTO.model_validate(message)


@router.post("/login")
async def login_user(response: Response, login_user_data: RequestUserAuthDTO) -> ResponseDataUserLoginDTO | None:
    check_user: User | None = await AuthService.authenticate_user(
        email=login_user_data.email,
        password=login_user_data.password
    )

    if check_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login or Password is not right"
        )

    access_token: str = AuthService.create_access_token(str(check_user.id))

    response.set_cookie(
        key="users_access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )
    response_data = {
        "ok": True,
        "access_token": access_token,
        "refresh_token": None,
        "message": "Authorisation successful"
        }
    return ResponseDataUserLoginDTO.model_validate(response_data)


@router.post("/logout")
async def logout_user(response: Response) -> ResponseMessageDTO:
    response.delete_cookie(key="users_access_token")
    message = {"message": "User is logout"}
    return ResponseMessageDTO.model_validate(message)


@router.get("/me", response_model=ResponseUserDTO)
async def get_me(current_user: CurrentUserDep) -> ResponseUserDTO:
    return ResponseUserDTO.model_validate(current_user)


@router.patch("/me/update", response_model=ResponseUserDTO)
async def update_me(update_user: RequestUserUpdateDTO, current_user: CurrentUserDep) -> ResponseUserDTO:
    update_data: dict[str, str | EmailStr] = update_user.model_dump(exclude_none=True, exclude={"password_confirm"})

    if "password" in update_data:
        update_data["password_hash"] = AuthService.get_password_hash(update_data.pop("password"))

    if update_data:
        await UserDAO.update(filter_by={"id": current_user.id}, **update_data)
        updated_user: ResponseUserDTO | None = await UserDAO.find_one_or_none(id=current_user.id)
        return ResponseUserDTO.model_validate(updated_user)
    return ResponseUserDTO.model_validate(current_user)


@router.patch("/me/disable")
async def disable_me(current_user: CurrentUserDep) -> ResponseMessageDTO:
    await UserDAO.update(filter_by={"id": current_user.id}, is_active=False)
    message = {"message": "User is disabled"}
    return ResponseMessageDTO.model_validate(message)