"""
Service layer schemas.

This module defines schemas for service operations.
"""

from pydantic import BaseModel


class WebSocketMessageDTO(BaseModel):
    """WebSocket message schema.

    Attributes:
        message: Message content.
    """

    message: str
