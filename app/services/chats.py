"""
WebSocket and chat session management.

This module provides connection tracking (one user, many connections) and
chat lifecycle: create new chat, load existing chat by ID for the current user.
"""

from fastapi import WebSocket

from app.api.dependencies.dao import ChatDAODep
from app.models.models import Chat
from app.schemas.chats import ChatWithMessagesDomain
from app.services.messages import WSMessageService
from app.services.constants import Fields, Messages


class WSConnectionManager:
    """Tracks WebSocket connections per user. One user may have multiple connections."""

    def __init__(self) -> None:
        """Initialize empty map: user_id -> set of WebSocket connections."""
        self.active_connections: dict[int, set[WebSocket]] = {}

    async def open_chat_connection(self, user_id: int, socket: WebSocket) -> None:
        """Accept the WebSocket and register it for the given user.

        Args:
            user_id: ID of the authenticated user.
            socket: The WebSocket connection to accept and track.
        """
        await socket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(socket)

    async def close_chat_connection(self, user_id: int, socket: WebSocket) -> None:
        """Unregister the WebSocket for the user. Call when client disconnects.

        Args:
            user_id: ID of the user who owns the connection.
            socket: The WebSocket connection to remove.
        """
        if (
            user_id in self.active_connections
            and socket in self.active_connections[user_id]
        ):
            self.active_connections[user_id].discard(socket)
        if user_id in self.active_connections and not self.active_connections[user_id]:
            del self.active_connections[user_id]


class CurrentChatService(WSMessageService):
    """Creates and loads chats for the current user (used by WebSocket and HTTP)."""

    def __init__(self, current_user_id: int, chat_dao: ChatDAODep) -> None:
        """Store the user ID for all operations.

        Args:
            current_user_id: Authenticated user's ID.
            chat_dao: ChatDAO dependency.
        """
        self.user_id: int = current_user_id
        self.chat_dao = chat_dao

    async def create_new_chat(self) -> ChatWithMessagesDomain:
        """Create a new chat for the current user. Returns DTO with empty messages.

        Returns:
            ChatWithMessagesDTO: New chat with id, title, user_id, created_at, messages=[].
        """
        data_to_create_new_chat: dict[str, str | int] = {
            Fields.TITLE: f"{Messages.NEW_CHAT_OF} {self.user_id}",
            Fields.USER_ID: self.user_id,
        }
        new_chat: Chat = await self.chat_dao.add(**data_to_create_new_chat)

        return ChatWithMessagesDomain(
            id=new_chat.id,
            title=new_chat.title,
            user_id=new_chat.user_id,
            created_at=new_chat.created_at,
            messages=[],
        )

    async def get_chat_with_id(self, current_chat_id: int) -> ChatWithMessagesDomain:
        """Load a chat by ID if it belongs to the current user.

        Args:
            current_chat_id: Chat ID to load.
        Returns:
            ChatWithMessagesDTO if found and owned by user, None otherwise.
        """

        chat: Chat = await self.chat_dao.get_one_chat(
            filter_by={
                Fields.ID: current_chat_id,
                Fields.USER_ID: self.user_id,
            }
        )

        return ChatWithMessagesDomain.model_validate(chat)
