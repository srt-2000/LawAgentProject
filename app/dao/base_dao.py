"""
Base Data Access Object for database operations.

This module provides a generic DAO class with common CRUD operations
for all database models.
"""

from typing import TypeVar, Generic, Type, ClassVar, cast

from sqlalchemy import delete, select, Select
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

        new_instance: BaseSQLModel = self.__class__.model(**kwargs)
        self._async_session.add(new_instance)
        await self._async_session.flush()

        return cast(T, new_instance)

    async def update(
        self, filter_by: dict[str, str | int | bool], **kwargs
    ) -> T | None:
        """Update records matching the filter criteria.

        Args:
            filter_by: Dictionary of field-value pairs to filter records.
            **kwargs: Field values to update.

        Returns:
            int: Number of rows affected.

        Raises:
            SQLAlchemyError: If database operation fails.
        """

        selected_objects: Select[tuple[BaseSQLModel]] = select(
            self.__class__.model
        ).where(*[getattr(self.__class__.model, k) == v for k, v in filter_by.items()])

        result: Result[tuple[T]] = await self._async_session.execute(selected_objects)
        updated_object: T | None = result.scalar_one_or_none()

        if updated_object is None:
            return None

        for key, value in kwargs.items():
            setattr(updated_object, key, value)

        await self._async_session.flush()
        await self._async_session.refresh(updated_object)

        return cast(T, updated_object)

    async def delete(self, filter_by: dict[str, str | int | bool]) -> int:
        """Delete records matching the filter criteria.

        Args:
            filter_by: Dictionary of field-value pairs to filter records.

        Returns:
            int: Number of rows affected.

        Raises:
            SQLAlchemyError: If database operation fails.
        """

        query = delete(self.__class__.model).filter_by(**filter_by)
        result: Result[tuple[T]] = await self._async_session.execute(query)
        cursor_result: CursorResult[tuple[T]] = cast(CursorResult[tuple[T]], result)

        rows_affected: int = int(getattr(cursor_result, "rowcount"))
        return rows_affected
