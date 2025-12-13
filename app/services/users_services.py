from datetime import timedelta, datetime, timezone

import jwt
from fastapi import HTTPException, status
from pydantic import EmailStr
from passlib.context import CryptContext
from app.config import get_auth_data, get_pwd_context
from app.dao.users_dao import UserDAO
from app.schemas.config_schema import ResponseAuthDataDTO
from app.schemas.users_schema import ResponseUserDTO, DBUserDTO


class PasswordService:
    pwd_context: CryptContext = get_pwd_context()

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)


class AuthService(PasswordService):

    @classmethod
    async def authenticate_user(cls, email: EmailStr, password: str) -> ResponseUserDTO | None:
        user: DBUserDTO | None = await UserDAO.find_one_or_none(email=email)

        if not user or not cls.verify_password(
                plain_password=password,
                hashed_password=str(user.password_hash)
        ):
            return None
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not active"
            )

        serialized_user: ResponseUserDTO = user.model_dump(exclude={"password_hash"})

        return ResponseUserDTO.model_validate(serialized_user)

    @staticmethod
    def create_access_token(data: str) -> str:
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(days=5)
        to_encode = {"sub": data, "exp": expire_time}
        auth_data: ResponseAuthDataDTO = get_auth_data()
        encode_jwt: str = jwt.encode(to_encode, auth_data.secret_key, algorithm=auth_data.algorithm)
        return encode_jwt
