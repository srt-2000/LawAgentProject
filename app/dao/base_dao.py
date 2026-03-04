"""
Base Data Access Object for database operations.

This module provides a generic DAO class with common CRUD operations
for all database models.
"""

from typing import TypeVar, Generic, Type, ClassVar, cast

from sqlalchemy import update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Result, CursorResult

from app.database import async_session_maker, BaseSQLModel

T = TypeVar("T", bound=BaseSQLModel)


class BaseDAO(Generic[T]):
    """Base DAO providing common database operations.

    Type Parameters:
        T: SQLAlchemy model type bound to BaseSQLModel.

    Attributes:
        model: SQLAlchemy model class to operate on.
    """

    model: ClassVar[Type[BaseSQLModel]]

    @classmethod
    async def add(cls, **kwargs) -> T:
        """Add a new record to the database.

        Args:
            **kwargs: Field values for the new record.

        Returns:
            T: Created model instance.

        Raises:
            SQLAlchemyError: If database operation fails.
        """
        async with async_session_maker() as async_session:
            async with async_session.begin():
                new_instance = cls.model(**kwargs)
                async_session.add(new_instance)
                try:
                    await async_session.commit()
                except SQLAlchemyError as error:
                    await async_session.rollback()
                    raise error
                return cast(T, new_instance)

    @classmethod
    async def update(cls, filter_by: dict[str, str | int | bool], **kwargs) -> int:
        """Update records matching the filter criteria.

        Args:
            filter_by: Dictionary of field-value pairs to filter records.
            **kwargs: Field values to update.

        Returns:
            int: Number of rows affected.

        Raises:
            SQLAlchemyError: If database operation fails.
        """
        async with async_session_maker() as async_session:
            async with async_session.begin():
                query = (
                    update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**kwargs)
                    .execution_options(synchronize_session="fetch")
                )
                result: Result[tuple[T]] = await async_session.execute(query)
                cursor_result: CursorResult[tuple[T]] = cast(
                    CursorResult[tuple[T]], result
                )

                try:
                    await async_session.commit()
                except SQLAlchemyError as error:
                    await async_session.rollback()
                    raise error

                rows_affected: int = int(getattr(cursor_result, "rowcount"))
                return rows_affected

    @classmethod
    async def delete(cls, filter_by: dict[str, str | int | bool]) -> int:
        """Delete records matching the filter criteria.

        Args:
            filter_by: Dictionary of field-value pairs to filter records.

        Returns:
            int: Number of rows affected.

        Raises:
            SQLAlchemyError: If database operation fails.
        """
        async with async_session_maker() as async_session:
            async with async_session.begin():
                query = delete(cls.model).filter_by(**filter_by)
                result: Result[tuple[T]] = await async_session.execute(query)
                cursor_result: CursorResult[tuple[T]] = cast(
                    CursorResult[tuple[T]], result
                )

                try:
                    await async_session.commit()
                except SQLAlchemyError as error:
                    await async_session.rollback()
                    raise error

                rows_affected: int = int(getattr(cursor_result, "rowcount"))
                return rows_affected
