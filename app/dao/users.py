"""
User Data Access Object.

This module provides database access methods specific to User model.
"""

from sqlalchemy.orm import selectinload

from app.dao.base import BaseDAO
from app.models.models import User, Chat


class UserDAO(BaseDAO[User]):
    """Data Access Object for User model operations."""

    model = User

    async def get_one_user(self, filter_by: dict[str, object]) -> User:
        """Find a single user by filter criteria with related chats.

        Args:
            filter_by: Filter criteria as field-value pairs.

        Returns:
            User: User instance if found, Exception otherwise.
        """
        user: User = await self.get_one(
            filter_by=filter_by,
            options=[
                selectinload(self.__class__.model.chats).selectinload(Chat.messages)
            ],
        )

        return user
