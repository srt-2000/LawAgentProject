"""
Chat data access.

Create, read, and delete chats; load one chat with messages or list user chats without messages.
"""

from sqlalchemy import Select, select, Result, ScalarResult
from sqlalchemy.orm import selectinload

from app.dao.base import BaseDAO
from app.models.models import Chat


class ChatDAO(BaseDAO[Chat]):
    """Data Access Object for Chat model operations."""

    model = Chat

    async def get_one_chat(self, filter_by: dict[str, object]) -> Chat:
        """Find a single chat by filter criteria with related messages.

        Args:
            filter_by: Filter criteria as field-value pairs.

        Returns:
            chat: Chat instance if found, Exception otherwise.
        """
        chat: Chat = await self.get_one(
            filter_by=filter_by,
            options=[selectinload(Chat.messages)],
        )

        return chat

    async def get_user_chat_list(self, **kwargs) -> ScalarResult[Chat]:
        """Return list of chats for a user without loading messages.

        Args:
            **kwargs: Filter criteria (e.g. user_id).

        Returns:
            ScalarResult[Chat]: Scalar result of chat instances.
        """
        # No options(selectinload()) because we don't need load all messages here
        query: Select[tuple[Chat]] = select(self.__class__.model).filter_by(**kwargs)
        result: Result[tuple[Chat]] = await self._async_session.execute(query)
        scalar_chat_list: ScalarResult[Chat] = result.scalars()

        return scalar_chat_list
