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
from fastapi import Request, WebSocket
from jwt import DecodeError, ExpiredSignatureError

from app.dao.redis_storage import RedisDAO

from app.schemas.config import AuthConfigDataDomain
from app.schemas.services import (
    ResponseAccessTokenPayloadDTO,
    RedisRefreshTokenDTO,
    ResponseRefreshTokenPayloadDTO,
)
from app.services.constants import (
    Fields,
    Messages,
    REFRESH,
    USERS_ACCESS_TOKEN,
    USERS_REFRESH_TOKEN,
)
from app.services.exceptions import TokenCheckFailed


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
            Fields.TOKEN_SUB: user_id,
            Fields.TOKEN_EXP: expire_time,
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
            Fields.TOKEN_SUB: str(user_id),
            Fields.TOKEN_EXP: expire_time,
            Fields.REFRESH_TOKEN_JTI: jti,
            Fields.REFRESH_TOKEN_TYPE: REFRESH,
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
            TokenCheckFailed: If token is invalid, expired, or missing expiration.
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
            loguru.logger.warning(Messages.ACCESS_TOKEN_DECODE_ERROR)
            raise TokenCheckFailed

        expire: int | None = valid_payload.exp

        if expire is None:
            loguru.logger.warning(Messages.TOKEN_EXPIRATION_IS_NONE)
            raise TokenCheckFailed

        expire_time: datetime = datetime.fromtimestamp(expire, tz=timezone.utc)

        if expire_time < datetime.now(timezone.utc):
            loguru.logger.warning(Messages.TOKEN_IS_EXPIRED)
            raise TokenCheckFailed

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
            TokenCheckFailed: If decoding fails or token type is not ``refresh``.
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
            loguru.logger.warning(Messages.REFRESH_TOKEN_DECODE_ERROR)
            raise TokenCheckFailed

        if valid_payload.typ != REFRESH:
            loguru.logger.warning(Messages.INVALID_TOKEN_TYPE)
            raise TokenCheckFailed

        return valid_payload

    @staticmethod
    def get_access_token_from_http(request: Request) -> str:
        """Extract access token from HTTP request cookies.

        Args:
            request: FastAPI request instance.

        Returns:
            str: JWT access token.

        Raises:
            TokenCheckFailed: If access token cookie is missing.
        """
        current_token: str | None = request.cookies.get(USERS_ACCESS_TOKEN)

        if not current_token:
            loguru.logger.warning(Messages.TOKEN_NOT_FOUND)
            raise TokenCheckFailed

        return current_token

    @staticmethod
    def get_access_token_from_websocket(storage: WebSocket) -> str:
        """Extract access token from the WebSocket handshake cookies.

        Args:
            storage: WebSocket connection (cookies are taken from the handshake).

        Returns:
            str: JWT access token string.

        Raises:
            TokenCheckFailed: If access token cookie is missing from the handshake.
        """
        current_token: str | None = storage.cookies.get(USERS_ACCESS_TOKEN)

        if not current_token:
            loguru.logger.warning(Messages.TOKEN_NOT_FOUND)
            raise TokenCheckFailed

        return current_token

    @staticmethod
    def get_refresh_token_from_http(request: Request) -> str:
        """Extract refresh token from HTTP request cookies.

        Args:
            request: FastAPI request instance.

        Returns:
            str: JWT refresh token string.

        Raises:
            TokenCheckFailed: If refresh token cookie is missing or empty.
        """
        current_token: str | None = request.cookies.get(USERS_REFRESH_TOKEN)

        if not current_token:
            loguru.logger.warning(Messages.TOKEN_NOT_FOUND)
            raise TokenCheckFailed

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
            TokenCheckFailed: If decoding fails, Redis data is missing, or subjects mismatch.
        """
        payload_dto: ResponseRefreshTokenPayloadDTO = self.service.decode_refresh_token(
            refresh_token
        )

        deleted_user_id: str = await self.dao.get_del_data_by_key(payload_dto.jti)

        if deleted_user_id != payload_dto.sub:
            loguru.logger.warning(
                f"{Messages.REFRESH_TOKEN_REDIS_ERROR} {Messages.USER_ID_DONT_MATCH}"
            )
            raise TokenCheckFailed

        return deleted_user_id
