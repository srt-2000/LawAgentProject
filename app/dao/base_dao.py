"""
Base Data Access Object for database operations.

This module provides a generic DAO class with common CRUD operations
for all database models.
"""

from typing import TypeVar, Generic, Type, ClassVar, cast

from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result, CursorResult

from app.database import BaseSQLModel

T = TypeVar("T", bound=BaseSQLModel)


class BaseDAO(Generic[T]):
    """Base DAO providing common database operations.

    Type Parameters:
        T: SQLAlchemy model type bound to BaseSQLModel.

    Attributes:
        model: SQLAlchemy model class to operate on.
    """

    model: ClassVar[Type[BaseSQLModel]]

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def add(self, **kwargs) -> T:
        """Add a new record to the database.

        Args:
            **kwargs: Field values for the new record.

        Returns:
            T: Created model instance.

        Raises:
            SQLAlchemyError: If database operation fails.
        """
        async with self._async_session.begin():
            new_instance = self.__class__.model(**kwargs)
            self._async_session.add(new_instance)
            await self._async_session.flush()

            return cast(T, new_instance)

    async def update(self, filter_by: dict[str, str | int | bool], **kwargs) -> int:
        """Update records matching the filter criteria.

        Args:
            filter_by: Dictionary of field-value pairs to filter records.
            **kwargs: Field values to update.

        Returns:
            int: Number of rows affected.

        Raises:
            SQLAlchemyError: If database operation fails.
        """

        async with self._async_session.begin():
            query = (
                update(self.__class__.model)
                .where(
                    *[
                        getattr(self.__class__.model, k) == v
                        for k, v in filter_by.items()
                    ]
                )
                .values(**kwargs)
                .execution_options(synchronize_session="fetch")
            )
            result: Result[tuple[T]] = await self._async_session.execute(query)
            cursor_result: CursorResult[tuple[T]] = cast(CursorResult[tuple[T]], result)

            rows_affected: int = int(getattr(cursor_result, "rowcount"))
            return rows_affected

    async def delete(self, filter_by: dict[str, str | int | bool]) -> int:
        """Delete records matching the filter criteria.

        Args:
            filter_by: Dictionary of field-value pairs to filter records.

        Returns:
            int: Number of rows affected.

        Raises:
            SQLAlchemyError: If database operation fails.
        """
        # async with async_session_maker() as async_session:
        async with self._async_session.begin():
            query = delete(self.__class__.model).filter_by(**filter_by)
            result: Result[tuple[T]] = await self._async_session.execute(query)
            cursor_result: CursorResult[tuple[T]] = cast(CursorResult[tuple[T]], result)

            rows_affected: int = int(getattr(cursor_result, "rowcount"))
            return rows_affected
