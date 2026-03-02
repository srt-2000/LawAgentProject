"""
Chat and message data transfer objects.

This module defines Pydantic schemas for chat and message responses.
"""

from datetime import datetime

from pydantic import ConfigDict, BaseModel, field_validator

from app.api.api_constants import StandardMessages


class MessageDTO(BaseModel):
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


class ChatBaseDTO(BaseModel):
    """Base chat schema with common fields.

    Attributes:
        id: Chat ID.
        title: Chat title (defaults to welcome message if None).
        user_id: Owner user ID.
        created_at: Creation timestamp.
    """

    id: int
    title: str | None
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("title", mode="before")
    @classmethod
    def title_none_default_validator(cls, title: str | None) -> str:
        """Replace None title with default welcome message.

        Args:
            title: Raw title value.

        Returns:
            str: Title or default welcome message.
        """
        if title is None:
            return StandardMessages.WELCOME_MESSAGE
        else:
            return title


class ChatWithMessagesDTO(ChatBaseDTO):
    """Chat response schema.

    Attributes:
        id: Chat ID.
        title: Chat title.
        user_id: Associated user ID.
        messages: List of messages in chat.
    """

    messages: list[MessageDTO] | None = None


class ChatListSideBarItemDTO(ChatBaseDTO):
    """Chat item schema for sidebar list (includes updated_at)."""

    updated_at: datetime


class ChatListDTO(BaseModel):
    """Response schema for list of user chats.

    Attributes:
        chat_list: List of chat sidebar items.
    """

    chat_list: list[ChatListSideBarItemDTO] = []
