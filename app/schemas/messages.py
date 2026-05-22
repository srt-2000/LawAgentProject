"""
Message-related request/response schemas.

Defines DTOs for WebSocket chat: payload sent to and from the client
(message text, chat_id, and whether the sender is the bot).
"""

from pydantic import BaseModel


class BaseWebSocketMessage(BaseModel):
    """Base class for WebSocket messages."""

    message: str
    chat_id: int
    is_bot: bool = False


class WebSocketMessageDomain(BaseWebSocketMessage):
    """One chat message used by services.

    Attributes:
        message: Message body. Maybe None for error placeholders.
        chat_id: Chat this message belongs to (set by server).
        is_bot: True for agent/bot messages, False for user messages.
    """


class WebSocketMessageDTO(BaseWebSocketMessage):
    """One chat message used by routers.

    Attributes:
        message: Message body. Maybe None for error placeholders.
        chat_id: Chat this message belongs to (set by server).
        is_bot: True for agent/bot messages, False for user messages.
    """


class WSIncomingMessageDTO(BaseModel):
    """Incoming message from the client over WS"""

    message: str | None = None
