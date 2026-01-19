"""
Database configuration and base model.

This module sets up the async SQLAlchemy engine, session maker,
and provides a base model class for all database models.
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from app.config import settings


DATABASE_URL: str = settings.database.db_url  # type: ignore[assignment]
async_engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


class BaseSQLModel(AsyncAttrs, DeclarativeBase):
    """Base SQLAlchemy model with common fields and table name generation.

    Automatically generates lowercase table names and includes timestamp fields
    for tracking creation and update times.
    """

    __abstract__ = True

    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name in lowercase.

        Returns:
            str: Lowercase class name for table name.
        """
        return f"{cls.__name__.lower()}"

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=datetime.now
    )
