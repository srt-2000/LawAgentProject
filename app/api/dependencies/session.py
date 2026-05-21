"""Async database session dependencies.

This module provides request-scoped async SQLAlchemy sessions that are
shared across all DAO instances created within a single request.
"""

from typing import AsyncGenerator, Annotated

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.constants import Messages
from app.storage.database import async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped async database session.

    The session is created from the global async session maker and is
    automatically closed when the request lifecycle finishes.

    Yields:
        AsyncSession: Live async SQLAlchemy session.

    On normal request completion the session is committed; on any exception it is
    rolled back, ``Messages.SESSION_FAILED`` is logged, and the exception is re-raised.
    The session is always closed in ``finally``.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            logger.warning(Messages.SESSION_FAILED)
            await session.rollback()
            raise
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
