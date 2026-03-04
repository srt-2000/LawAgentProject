"""
Message-related request/response schemas.

Defines DTOs for WebSocket chat: payload sent to and from the client
(message text, chat_id, and whether the sender is the bot).
"""

from pydantic import BaseModel


class WebSocketMessageDTO(BaseModel):
    """One chat message as sent over WebSocket or stored for a chat.

    Attributes:
        message: Message body. Maybe None for error placeholders.
        chat_id: Chat this message belongs to (set by server).
        is_bot: True for agent/bot messages, False for user messages.
    """

    message: str | None
    chat_id: int
    is_bot: bool = False
