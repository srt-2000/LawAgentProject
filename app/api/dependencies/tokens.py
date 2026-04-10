"""
Token-related FastAPI dependencies.

This module provides cached factories for auth config and JWT token services,
plus small dependencies that extract access tokens from HTTP/WebSocket cookies.
"""

from functools import lru_cache
from typing import Annotated, cast

from fastapi import Depends, Request, WebSocket

from app.config import settings
from app.schemas.config import AuthConfigDataDomain
from app.services.tokens import AccessTokenService, RefreshTokenService


@lru_cache(maxsize=1)
def get_auth_config_data() -> AuthConfigDataDomain:
    """Get validated authentication configuration.

    Returns:
        AuthConfigDataDomain: Auth settings used for JWT encode/decode.
    """
    auth_config_data: AuthConfigDataDomain = cast(
        AuthConfigDataDomain, settings.auth.auth_config
    )

    return auth_config_data


@lru_cache(maxsize=1)
def get_access_token_service() -> AccessTokenService:
    """Create a singleton AccessTokenService instance.

    Returns:
        AccessTokenService: Service for creating/decoding access tokens.
    """
    auth_data: AuthConfigDataDomain = get_auth_config_data()
    access_token_service: AccessTokenService = AccessTokenService(auth_data)

    return access_token_service


@lru_cache(maxsize=1)
def get_refresh_token_service() -> RefreshTokenService:
    """Create a singleton RefreshTokenService instance.

    Returns:
        RefreshTokenService: Service for refresh-token operations.
    """
    auth_data: AuthConfigDataDomain = get_auth_config_data()
    refresh_token_service: RefreshTokenService = RefreshTokenService(auth_data)

    return refresh_token_service


AccessTokenServiceDep = Annotated[AccessTokenService, Depends(get_access_token_service)]
RefreshTokenServiceDep = Annotated[
    RefreshTokenService, Depends(get_refresh_token_service)
]


def get_access_token_from_http(request: Request) -> str:
    """Extract the access token from an HTTP request.

    Args:
        request: FastAPI request carrying cookies.

    Returns:
        str: Access token string.
    """
    http_access_token: str = AccessTokenService.get_access_token_from_http(request)

    return http_access_token


def get_access_token_from_websocket(websocket: WebSocket) -> str:
    """Extract the access token from a WebSocket handshake.

    Args:
        websocket: WebSocket connection (cookies are taken from the handshake).

    Returns:
        str: Access token string.
    """
    ws_access_token: str = AccessTokenService.get_access_token_from_websocket(websocket)

    return ws_access_token


HttpAccessTokenDep = Annotated[str, Depends(get_access_token_from_http)]
WSAccessTokenDep = Annotated[str, Depends(get_access_token_from_websocket)]
