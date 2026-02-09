"""
Chat Data Access Object.

This module provides database access methods specific to the Chat model.
"""


from sqlalchemy import Select, select, Result, ScalarResult
from sqlalchemy.orm import selectinload

from app.dao.base_dao import BaseDAO
from app.database import async_session_maker
from app.models.models import Chat


class ChatDAO(BaseDAO[Chat]):
    """Data Access Object for Chat model operations."""

    model = Chat

    @classmethod
    async def find_one_or_none_by_id(cls, **kwargs) -> Chat | None:
        """Find a single chat by filter criteria with related messages.

        Args:
            **kwargs: Filter criteria as field-value pairs (e.g. id, user_id).

        Returns:
            Chat | None: Chat instance if found, None otherwise.
        """
        async with async_session_maker() as async_session:
            query: Select[tuple[Chat]] = (
                select(cls.model)
                .options(selectinload(cls.model.messages))
                .filter_by(**kwargs)
            )
            result: Result[tuple[Chat]] = await async_session.execute(query)
            chat: Chat | None = result.scalar_one_or_none()

            if not chat:
                return None

            return chat

    @classmethod
    async def get_user_chat_list(cls, **kwargs) -> ScalarResult[Chat]:
        """Return list of chats for a user without loading messages.

        Args:
            **kwargs: Filter criteria (e.g. user_id).

        Returns:
            ScalarResult[Chat]: Scalar result of chat instances.
        """
        async with async_session_maker() as async_session:
            # No options(selectinload()) because we don't need load all messages here
            query: Select[tuple[Chat]] = select(cls.model).filter_by(**kwargs)
            result: Result[tuple[Chat]] = await async_session.execute(query)
            scalar_chat_list: ScalarResult[Chat] = result.scalars()

            return scalar_chat_list
