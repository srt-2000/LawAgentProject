"""
Message-related request/response schemas.

Defines DTOs for WebSocket chat: payload sent to and from the client
(message text, chat_id, and whether the sender is the bot).
"""
from typing import Literal

from pydantic import BaseModel


WS_message_type = Literal["welcome", "user", "assistant"]


class WebSocketMessageDomain(BaseModel):
    """One chat message used by services.

    Attributes:
        message_type: Type of message.
        message: Message body. Maybe None for error placeholders.
        chat_id: Chat this message belongs to (set by server).
        is_bot: True for agent/bot messages, False for user messages.
    """

    message_type: WS_message_type
    message: str | None
    chat_id: int
    is_bot: bool = False


class WebSocketMessageDTO(BaseModel):
    """One chat message used by routers.

    Attributes:
        message_type: Type of message.
        message: Message body. Maybe None for error placeholders.
        chat_id: Chat this message belongs to (set by server).
        is_bot: True for agent/bot messages, False for user messages.
    """

    message_type: WS_message_type
    message: str | None
    chat_id: int
    is_bot: bool = False


class WSIncomingMessageDTO(BaseModel):
    """Incoming message from the client over WS"""

    message: str | None = None
