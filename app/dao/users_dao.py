"""
User Data Access Object.

This module provides database access methods specific to User model.
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy.engine import Result

from app.dao.base_dao import BaseDAO
from app.models.models import User, Chat


class UserDAO(BaseDAO[User]):
    """Data Access Object for User model operations."""

    model = User

    async def find_one_or_none(self, **kwargs) -> User | None:
        """Find a single user by filter criteria with related chats.

        Args:
            **kwargs: Filter criteria as field-value pairs.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        query: Select[tuple[User]] = (
            select(self.__class__.model)
            .options(
                selectinload(self.__class__.model.chats).selectinload(Chat.messages)
            )
            .filter_by(**kwargs)
        )
        result: Result[tuple[User]] = await self._async_session.execute(query)
        user: User | None = result.scalar_one_or_none()

        if not user:
            return None

        return user
