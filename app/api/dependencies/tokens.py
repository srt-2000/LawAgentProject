"""
Token-related FastAPI dependencies.

This module provides cached factories for auth config and JWT token services,
plus small dependencies that extract access tokens from HTTP/WebSocket cookies.
"""

from functools import lru_cache
from typing import Annotated, cast

from fastapi import Depends, Request

from app.api.dependencies.dao import RedisDAODep
from app.config import settings
from app.schemas.config import AuthConfigDataDomain
from app.services.tokens import TokenService, RefreshTokenSessionManager


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


def get_token_service() -> TokenService:
    """Create a TokenService instance.

    Returns:
        TokenService: Service for creating/decoding/getting access and refresh tokens.
    """
    auth_data: AuthConfigDataDomain = get_auth_config_data()
    token_service: TokenService = TokenService(auth_data)

    return token_service


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


async def get_refresh_token_manager(
    service: TokenServiceDep, dao: RedisDAODep
) -> RefreshTokenSessionManager:
    """Create a refresh-token session manager for Redis-backed rotation.

    Args:
        service: JWT token service for encoding and decoding tokens.
        dao: Redis DAO for storing refresh token metadata by JTI.

    Returns:
        RefreshTokenSessionManager: Manager for create/revoke refresh flows.
    """
    refresh_manager: RefreshTokenSessionManager = RefreshTokenSessionManager(
        service, dao
    )

    return refresh_manager


RefreshManagerDep = Annotated[
    RefreshTokenSessionManager, Depends(get_refresh_token_manager)
]


def get_access_token_from_http(request: Request) -> str:
    """Extract the access token from an HTTP request.

    Args:
        request: FastAPI request carrying cookies.

    Returns:
        str: Access token string.
    """
    http_access_token: str = TokenService.get_access_token_from_http(request)

    return http_access_token


def get_refresh_token_from_http(request: Request) -> str:
    """Extract the refresh token from an HTTP request.

    Args:
        request: FastAPI request carrying cookies.

    Returns:
        str: Refresh token string.
    """
    http_refresh_token: str = TokenService.get_refresh_token_from_http(request)

    return http_refresh_token


HttpAccessTokenDep = Annotated[str, Depends(get_access_token_from_http)]
HttpRefreshTokenDep = Annotated[str, Depends(get_refresh_token_from_http)]
