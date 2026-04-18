"""
JWT token services.

Provides access and refresh token lifecycle helpers consumed by HTTP dependencies,
WebSocket authentication, and Redis-backed refresh rotation.
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Literal

import jwt
import loguru
from fastapi import Request, HTTPException, status, WebSocket
from jwt import DecodeError, ExpiredSignatureError

from app.dao.exceptions import RedisKeyValueNotFoundException
from app.dao.redis_storage import RedisDAO

from app.schemas.config import AuthConfigDataDomain
from app.schemas.services import (
    ResponseAccessTokenPayloadDTO,
    RedisRefreshTokenDTO,
    ResponseRefreshTokenPayloadDTO,
)
from app.services.constants import FieldValues, FieldNames, StandardMessages


class TokenService:
    """Create, decode, and extract JWT access and refresh tokens."""

    def __init__(self, auth_data: AuthConfigDataDomain) -> None:
        """Initialize the service with validated auth configuration.

        Args:
            auth_data: JWT secrets, algorithm, and expiration settings.
        """
        self.auth_data = auth_data

    def create_access_token(self, user_id: str) -> str:
        """Create a JWT access token.

        Args:
            user_id: User ID to encode into the token subject claim.

        Returns:
            str: Encoded JWT access token.
        """
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=self.auth_data.access_token_exp_time_minutes
        )
        to_encode: dict[str, str | datetime] = {
            FieldNames.TOKEN_SUB: user_id,
            FieldNames.TOKEN_EXP: expire_time,
        }
        encoded_jwt: str = jwt.encode(
            payload=to_encode,
            key=self.auth_data.access_secret_key,
            algorithm=self.auth_data.algorithm,
        )
        return encoded_jwt

    def create_refresh_token_dto(self, user_id: int) -> RedisRefreshTokenDTO:
        """Mint a refresh JWT plus Redis metadata for server-side rotation.

        Args:
            user_id: Numeric user identifier encoded into the ``sub`` claim.

        Returns:
            RedisRefreshTokenDTO: Serialized refresh token, JWT ID, and Redis TTL seconds.
        """
        jti: str = secrets.token_urlsafe(self.auth_data.refresh_token_entropy)
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(
            hours=self.auth_data.refresh_token_exp_time_hours
        )

        to_encode: dict[str, str | datetime | Literal["refresh"]] = {
            FieldNames.TOKEN_SUB: str(user_id),
            FieldNames.TOKEN_EXP: expire_time,
            FieldNames.REFRESH_TOKEN_JTI: jti,
            FieldNames.REFRESH_TOKEN_TYPE: FieldValues.REFRESH,
        }
        encoded_jwt: str = jwt.encode(
            payload=to_encode,
            key=self.auth_data.refresh_secret_key,
            algorithm=self.auth_data.algorithm,
        )
        ttl_to_redis_seconds = int(
            (expire_time.timestamp() - datetime.now(timezone.utc).timestamp())
        )
        refresh_token_dto: RedisRefreshTokenDTO = RedisRefreshTokenDTO(
            refresh_token=encoded_jwt, jti=jti, exp=ttl_to_redis_seconds
        )
        return RedisRefreshTokenDTO.model_validate(refresh_token_dto)

    def decode_access_token(self, token: str) -> ResponseAccessTokenPayloadDTO:
        """Decode and validate a JWT access token.

        Args:
            token: JWT access token string to decode.

        Returns:
            ResponseAccessTokenPayloadDTO: Decoded and validated token payload.

        Raises:
            HTTPException: If token is invalid or expired.
        """
        try:
            payload: ResponseAccessTokenPayloadDTO = jwt.decode(
                jwt=token,
                key=self.auth_data.access_secret_key,
                algorithms=[self.auth_data.algorithm],
            )
            valid_payload: ResponseAccessTokenPayloadDTO = (
                ResponseAccessTokenPayloadDTO.model_validate(payload)
            )
        except (DecodeError, ExpiredSignatureError, Exception):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.TOKEN_NOT_VALID,
            )

        expire: int | None = valid_payload.exp

        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.TOKEN_NOT_VALID,
            )

        expire_time: datetime = datetime.fromtimestamp(expire, tz=timezone.utc)

        if expire_time < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.TOKEN_IS_EXPIRED,
            )

        return valid_payload

    def decode_refresh_token(
        self, refresh_token: str
    ) -> ResponseRefreshTokenPayloadDTO:
        """Decode and validate a refresh JWT (type, signature, structure).

        Args:
            refresh_token: Encoded refresh JWT extracted from cookies.

        Returns:
            ResponseRefreshTokenPayloadDTO: Normalized refresh payload including ``jti``.

        Raises:
            HTTPException: If decoding fails or token type is not ``refresh``.
        """
        try:
            payload: ResponseRefreshTokenPayloadDTO = jwt.decode(
                jwt=refresh_token,
                key=self.auth_data.refresh_secret_key,
                algorithms=[self.auth_data.algorithm],
            )
            valid_payload: ResponseRefreshTokenPayloadDTO = (
                ResponseRefreshTokenPayloadDTO.model_validate(payload)
            )
        except (DecodeError, ExpiredSignatureError, Exception):
            loguru.logger.exception(StandardMessages.REFRESH_TOKEN_DECODE_ERROR)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.REFRESH_TOKEN_IS_NOT_VALID,
            )

        if valid_payload.typ != FieldValues.REFRESH:
            loguru.logger.exception(StandardMessages.INVALID_TOKEN_TYPE)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.INVALID_TOKEN_TYPE,
            )

        return valid_payload

    @staticmethod
    def get_access_token_from_http(request: Request) -> str:
        """Extract access token from HTTP request cookies.

        Args:
            request: FastAPI request instance.

        Returns:
            str: JWT access token.

        Raises:
            HTTPException: If access token not found in cookies.
        """
        current_token: str | None = request.cookies.get(FieldValues.USERS_ACCESS_TOKEN)

        if not current_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.TOKEN_NOT_VALID,
            )
        return current_token

    @staticmethod
    def get_access_token_from_websocket(storage: WebSocket) -> str:
        """Extract access token from the WebSocket handshake cookies.

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
                detail=StandardMessages.TOKEN_NOT_VALID,
            )
        return current_token

    @staticmethod
    def get_refresh_token_from_http(request: Request) -> str:
        """Extract refresh token from HTTP request cookies.

        Args:
            request: FastAPI request instance.

        Returns:
            str: JWT refresh token string.

        Raises:
            HTTPException: If refresh token cookie is missing or empty.
        """
        current_token: str | None = request.cookies.get(FieldValues.USERS_REFRESH_TOKEN)

        if not current_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.TOKEN_NOT_VALID,
            )
        return current_token


class RefreshTokenSessionManager:
    """Coordinate refresh JWT issuance with Redis lookups keyed by JWT ID."""

    def __init__(self, service: TokenService, dao: RedisDAO) -> None:
        """Capture collaborators required for refresh lifecycle management.

        Args:
            service: Token encoder/decoder sharing auth configuration.
            dao: Redis persistence used to map ``jti`` values to ``user_id`` strings.
        """
        self.service = service
        self.dao = dao

    async def create_refresh_token(self, user_id: int) -> str:
        """Persist refresh metadata and return the encoded JWT for clients.

        Args:
            user_id: Authenticated user owning the refresh session.

        Returns:
            str: Encoded refresh JWT stored alongside Redis metadata.
        """
        token_dto: RedisRefreshTokenDTO = self.service.create_refresh_token_dto(user_id)

        await self.dao.save_one(
            key=token_dto.jti, new_data=str(user_id), ttl=token_dto.exp
        )

        refresh_token: str = token_dto.refresh_token

        return refresh_token

    async def revoke_refresh_token(self, refresh_token: str) -> str:
        """Validate a refresh token, consume Redis state, and return the subject user id.

        Args:
            refresh_token: Refresh JWT presented by the client.

        Returns:
            str: Subject user identifier extracted after Redis verification.

        Raises:
            HTTPException: If decoding fails, Redis data is missing, or subjects mismatch.
        """
        payload_dto: ResponseRefreshTokenPayloadDTO = self.service.decode_refresh_token(
            refresh_token
        )

        try:
            deleted_user_id: str = await self.dao.get_del_data_by_key(payload_dto.jti)
        except RedisKeyValueNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.REFRESH_TOKEN_REDIS_ERROR,
            )

        if deleted_user_id != payload_dto.sub:
            loguru.logger.exception(
                f"{StandardMessages.REFRESH_TOKEN_REDIS_ERROR} {StandardMessages.USER_ID_DONT_MATCH}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=StandardMessages.REVOKE_REFRESH_TOKEN_ERROR,
            )

        return deleted_user_id
