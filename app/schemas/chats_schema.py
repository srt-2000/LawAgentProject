"""
Chat and message data transfer objects.

This module defines Pydantic schemas for chat and message responses.
"""

from pydantic import ConfigDict, BaseModel


class MessageOut(BaseModel):
    """Message response schema.

    Attributes:
        id: Message ID.
        context: Message content.
        chat_id: Associated chat ID.
        is_bot: Whether message is from bot.
    """

    id: int
    context: str
    chat_id: int
    is_bot: bool

    model_config = ConfigDict(from_attributes=True)


class ChatOut(BaseModel):
    """Chat response schema.

    Attributes:
        id: Chat ID.
        title: Chat title.
        user_id: Associated user ID.
        messages: List of messages in chat.
    """

    id: int
    title: str
    user_id: int
    messages: list[MessageOut] | None = None

    model_config = ConfigDict(from_attributes=True)
