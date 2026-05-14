"""
Service-level DTOs used by dependencies and token services.

Includes schemas for decoded JWT payloads and small value objects used in Redis.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.constants import FORBID_VALUE


class ResponseAccessTokenPayloadDTO(BaseModel):
    """Decoded JWT payload after verification.

    Attributes:
        sub: Subject (user ID as string).
        exp: Expiration time (Unix timestamp); None if not present.
    """

    sub: str
    exp: int | None


class RedisRefreshTokenDTO(BaseModel):
    """Envelope created when issuing a refresh token bound for Redis metadata.

    Attributes:
        refresh_token: Encoded refresh JWT passed to HTTP clients.
        jti: Unique token identifier stored as the Redis key.
        exp: Redis TTL (seconds) aligned with refresh token expiry, not the JWT ``exp`` claim.
    """

    refresh_token: str
    jti: str
    exp: int


class ResponseRefreshTokenPayloadDTO(BaseModel):
    """Decoded Refresh JWT payload after verification.

    Attributes:
        sub: Subject (user ID as string).
        exp: Expiration time (Unix timestamp); None if not present.
        jti: Token identifier (JWT ID).
        typ: Token type (always "refresh" for refresh tokens).
    """

    sub: str
    exp: int
    jti: str
    typ: Literal["refresh"]


class RedisKeyValueDomain(BaseModel):
    """Immutable key/value pair stored in Redis.

    Attributes:
        key: Redis key.
        value: Stored value (typically a hash string).
    """

    model_config = ConfigDict(frozen=True, extra=FORBID_VALUE)

    key: str
    value: str


class SaveRedisKeyValueDomain(RedisKeyValueDomain):
    """Redis key/value pair augmented with TTL metadata.

    Attributes:
        key: Redis key.
        value: Stored string payload.
        ttl: Time-to-live for the key in whole seconds (``SET EX`` semantics).
    """

    ttl: int
