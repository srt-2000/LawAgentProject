"""
Database engine, session factory, and base model.

Configures async PostgreSQL via SQLAlchemy; all ORM models inherit BaseSQLModel
and get created_at/updated_at and lowercase table names.
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
    """Base for all ORM models: table name = lower(class name), created_at/updated_at."""

    __abstract__ = True

    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Use the class name in lowercase as the table name.

        Returns:
            str: Table name (e.g. User -> "user").
        """
        return f"{cls.__name__.lower()}"

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=datetime.now
    )
