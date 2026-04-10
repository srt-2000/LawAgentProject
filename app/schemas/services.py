"""
Service-level DTOs used by dependencies and token services.

Includes schemas for decoded JWT payloads and small value objects used in Redis.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.constants import FieldValues


class ResponseAccessTokenPayloadDTO(BaseModel):
    """Decoded JWT payload after verification.

    Attributes:
        sub: Subject (user ID as string).
        exp: Expiration time (Unix timestamp); None if not present.
    """

    sub: str
    exp: int | None


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
    typ: Literal["refresh"] = FieldValues.REFRESH


class RedisKeyValueDomain(BaseModel):
    """Immutable key/value pair stored in Redis.

    Attributes:
        key: Redis key.
        value_hash: Stored value (typically a hash string).
    """

    model_config = ConfigDict(frozen=True, extra=FieldValues.FORBID_VALUE)

    key: str
    value_hash: str
