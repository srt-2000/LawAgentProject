"""
Message data access.

Uses BaseDAO add/update/delete for message records (create and delete only in practice).
"""

from app.dao.base_dao import BaseDAO
from app.models.models import Message


class MessageDAO(BaseDAO[Message]):
    """DAO for Message. Use add() to persist user and bot messages; delete via Chat cascade."""

    model = Message
