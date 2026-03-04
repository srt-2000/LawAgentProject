"""
Dependency schemas.

This module defines schemas used by FastAPI dependencies.
"""

from pydantic import BaseModel


class ResponsePayloadDTO(BaseModel):
    """JWT token payload schema.

    Attributes:
        sub: Subject (user ID).
        exp: Expiration timestamp.
    """

    sub: str
    exp: int | None
