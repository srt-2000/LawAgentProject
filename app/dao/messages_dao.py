"""
Message Data Access Object.

This module provides database access methods specific to the Message model.
"""

from app.dao.base_dao import BaseDAO
from app.models.models import Message


class MessageDAO(BaseDAO[Message]):
    """Data Access Object for Message model operations."""

    model = Message
