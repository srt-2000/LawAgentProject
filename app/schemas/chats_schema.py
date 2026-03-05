"""
Chat and message DTOs for API and WebSocket.

Pydantic models for listing chats, opening a chat with messages,
and representing a single message in a chat.
"""

from datetime import datetime

from pydantic import ConfigDict, BaseModel, field_validator

from app.api.api_constants import RouterStandardMessages


class MessageDTO(BaseModel):
    """Single message in a chat (from DB: id, content, chat_id, is_bot).

    Attributes:
        id: Message primary key.
        context: Message text.
        chat_id: Parent chat ID.
        is_bot: True if from agent, False if from user.
    """

    id: int
    context: str
    chat_id: int
    is_bot: bool

    model_config = ConfigDict(from_attributes=True)


class ChatBaseDTO(BaseModel):
    """Shared chat fields: id, title, owner, created_at. Title default from settings if None.

    Attributes:
        id: Chat primary key.
        title: Display title; None is replaced by WELCOME_MESSAGE in validator.
        user_id: Owner (user) ID.
        created_at: When the chat was created.
    """

    id: int
    title: str | None
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("title", mode="before")
    @classmethod
    def title_none_default_validator(cls, title: str | None) -> str:
        """Use WELCOME_MESSAGE when title is None so the client always gets a string.

        Args:
            title: Raw title from DB or payload.

        Returns:
            str: title if set, else settings.WELCOME_MESSAGE.
        """
        if title is None:
            return RouterStandardMessages.WELCOME_MESSAGE
        else:
            return title


class ChatWithMessagesDTO(ChatBaseDTO):
    """Chat plus its messages. Used when opening a chat or creating a new one.

    Attributes:
        messages: Ordered list of messages; None or [] when not loaded or new chat.
    """

    messages: list[MessageDTO] | None = None


class ChatListSideBarItemDTO(ChatBaseDTO):
    """One chat in the sidebar: base fields plus updated_at for sorting/display.

    Attributes:
        updated_at: Last update time (e.g. last message or edit).
    """

    updated_at: datetime


class ChatListDTO(BaseModel):
    """Response body for GET /user/chats: list of chats for the sidebar.

    Attributes:
        chat_list: Chats owned by the user (id, title, user_id, created_at, updated_at).
    """

    chat_list: list[ChatListSideBarItemDTO] = []
