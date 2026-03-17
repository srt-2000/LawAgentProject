"""DAO dependency providers.

This module exposes FastAPI dependency helpers that construct
request-scoped DAO instances sharing a single async database session.
"""

from typing import Annotated

from fastapi import Depends

from app.dao.chats import ChatDAO
from app.dao.messages import MessageDAO
from app.dao.users import UserDAO
from app.api.dependencies.session import SessionDep


async def get_user_dao(session: SessionDep) -> UserDAO:
    """Create a UserDAO instance bound to the current request session.

    Args:
        session: Async database session dependency.

    Returns:
        UserDAO: Data access object for user-related operations.
    """
    return UserDAO(session)


async def get_chat_dao(session: SessionDep) -> ChatDAO:
    """Create a ChatDAO instance bound to the current request session.

    Args:
        session: Async database session dependency.

    Returns:
        ChatDAO: Data access object for chat-related operations.
    """
    return ChatDAO(session)


async def get_message_dao(session: SessionDep) -> MessageDAO:
    """Create a MessageDAO instance bound to the current request session.

    Args:
        session: Async database session dependency.

    Returns:
        MessageDAO: Data access object for message-related operations.
    """
    return MessageDAO(session)


UserDAODep = Annotated[UserDAO, Depends(get_user_dao)]
ChatDAODep = Annotated[ChatDAO, Depends(get_chat_dao)]
MessageDAODep = Annotated[MessageDAO, Depends(get_message_dao)]
