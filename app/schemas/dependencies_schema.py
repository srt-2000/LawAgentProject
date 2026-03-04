"""
Schemas used by auth dependencies.

Decoded JWT payload shape for get_current_user and WebSocket auth.
"""

from pydantic import BaseModel


class ResponsePayloadDTO(BaseModel):
    """Decoded JWT payload after verification.

    Attributes:
        sub: Subject (user ID as string).
        exp: Expiration time (Unix timestamp); None if not present.
    """

    sub: str
    exp: int | None
