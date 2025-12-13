from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import WebSocket, HTTPException
from fastapi.params import Depends
from jwt import DecodeError, ExpiredSignatureError
from starlette import status

from app.config import get_auth_data
from app.dao.users_dao import UserDAO
from app.schemas.config_schema import ResponseAuthDataDTO
from app.schemas.dependencies_schema import ResponsePayloadDTO
from app.schemas.users_schema import ResponseUserDTO, DBUserDTO


def get_current_token_from_websocket(storage: WebSocket) -> str:
    current_token: str | None = storage.cookies.get("users_access_token")

    if not current_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found"
        )
    return current_token


async def decode_token_from_websocket(token: str = Depends(get_current_token_from_websocket)) -> ResponsePayloadDTO:
    try:
        auth_data: ResponseAuthDataDTO = get_auth_data()
        payload: ResponsePayloadDTO = jwt.decode(
            token,
            auth_data.secret_key,
            algorithms=[auth_data.algorithm]
        )
        valid_payload: ResponsePayloadDTO = ResponsePayloadDTO.model_validate(payload)
    except (DecodeError, ExpiredSignatureError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not valid")

    expire: int | None = valid_payload.exp
    expire_time: datetime = datetime.fromtimestamp(expire, tz=timezone.utc)

    if (not expire) or expire_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired")

    return valid_payload


async def get_websocket_current_active_user(payload: ResponsePayloadDTO = Depends(decode_token_from_websocket)) -> ResponseUserDTO:
    user_id: str = payload.sub

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found")

    user: DBUserDTO = await UserDAO.find_one_or_none(id=int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled")

    serialized_user: ResponseUserDTO = user.model_dump(exclude={"password_hash"})

    return ResponseUserDTO.model_validate(serialized_user)

WebsocketCurrentUserDep = Annotated[ResponseUserDTO, Depends(get_websocket_current_active_user)]
