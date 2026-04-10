"""
JWT token services.

This module implements helpers for creating, extracting, and decoding access tokens
used by the API and WebSocket authentication dependencies.
"""

from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Request, HTTPException, status, WebSocket
from jwt import DecodeError, ExpiredSignatureError

from app.schemas.config import AuthConfigDataDomain
from app.schemas.services import ResponseAccessTokenPayloadDTO
from app.services.constants import FieldsValues, FieldNames, StandardMessages


class BaseTokenService:
    """Base class for token services that need auth configuration."""

    def __init__(self, auth_data: AuthConfigDataDomain) -> None:
        """Initialize the service with validated auth configuration.

        Args:
            auth_data: JWT secrets, algorithm, and expiration settings.
        """
        self.auth_data = auth_data


class AccessTokenService(BaseTokenService):
    """Service for issuing and validating JWT access tokens."""

    def create_access_token(self, data: str) -> str:
        """Create a JWT access token.

        Args:
            data: User ID to encode into the token subject claim.

        Returns:
            str: Encoded JWT access token.
        """
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=self.auth_data.access_token_exp_time_minutes
        )
        to_encode: dict[str, str | datetime] = {
            FieldNames.TOKEN_SUB: data,
            FieldNames.TOKEN_EXP: expire_time,
        }
        encoded_jwt: str = jwt.encode(
            payload=to_encode,
            key=self.auth_data.secret_key,
            algorithm=self.auth_data.algorithm,
        )
        return encoded_jwt

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
        current_token: str | None = request.cookies.get(FieldsValues.USERS_ACCESS_TOKEN)

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
        current_token: str | None = storage.cookies.get(FieldsValues.USERS_ACCESS_TOKEN)

        if not current_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.TOKEN_NOT_VALID,
            )
        return current_token

    async def decode_access_token(self, token: str) -> ResponseAccessTokenPayloadDTO:
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
                key=self.auth_data.secret_key,
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


class RefreshTokenService(BaseTokenService):
    """Service for refresh-token operations.

    Note:
        Refresh token logic is not implemented yet in this project.
    """
