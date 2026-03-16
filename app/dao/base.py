"""
Generic DAO with async add, update, and delete.

Subclass with model = YourModel to get CRUD. Each method uses its own session and commit.
"""

from typing import TypeVar, Generic, Type, ClassVar, cast

from sqlalchemy import delete, select, Select, Delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result, CursorResult

from app.dao.exceptions import ObjectNotFoundException
from app.dao.constants import DAOFieldNames
from app.database import BaseSQLModel

T = TypeVar("T", bound=BaseSQLModel)


class BaseDAO(Generic[T]):
    """Generic async DAO: add(**kwargs), update(filter_by, **kwargs), delete(filter_by).

    Subclasses must set model to their SQLAlchemy model class.
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
    ) -> T:
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
            raise ObjectNotFoundException(
                self.__class__.model.__name__
            )

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

        query: Delete = delete(self.__class__.model).filter_by(**filter_by)
        result: Result[tuple[T]] = await self._async_session.execute(query)
        cursor_result: CursorResult[tuple[T]] = cast(CursorResult[tuple[T]], result)

        rows_affected: int = int(getattr(cursor_result, DAOFieldNames.ROWCOUNT))
        return rows_affected
