"""
User Data Access Object.

This module provides database access methods specific to User model.
"""


from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy.engine import Result

from app.dao.base_dao import BaseDAO
from app.database import async_session_maker
from app.models.models import User, Chat


class UserDAO(BaseDAO[User]):
    """Data Access Object for User model operations."""

    model = User

    @classmethod
    async def find_one_or_none(cls, **kwargs) -> User | None:
        """Find a single user by filter criteria with related chats.

        Args:
            **kwargs: Filter criteria as field-value pairs.

        Returns:
            DBUserDTO | None: User DTO if found, None otherwise.
        """
        async with async_session_maker() as async_session:
            query: Select[tuple[User]] = (
                select(cls.model)
                .options(selectinload(cls.model.chats).selectinload(Chat.messages))
                .filter_by(**kwargs)
            )
            result: Result[tuple[User]] = await async_session.execute(query)
            user: User | None = result.scalar_one_or_none()

            if not user:
                return None

            return user
