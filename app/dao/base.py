"""
Generic async DAO for add, update, delete, and single-row fetch.

Subclass with ``model = YourModel``. All operations use the injected
:class:`~sqlalchemy.ext.asyncio.AsyncSession`; transaction boundaries are defined
by the caller (for example FastAPI session dependencies).
"""

from typing import TypeVar, Generic, Type, ClassVar, cast, Sequence

import loguru
from loguru import logger
from sqlalchemy import delete, select, Select, Delete, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result, CursorResult
from sqlalchemy.orm.interfaces import ORMOption

from app.dao.exceptions import ObjectNotFoundException
from app.dao.constants import ROWCOUNT, ID, Messages
from app.storage.database import BaseSQLModel

T = TypeVar("T", bound=BaseSQLModel)


class BaseDAO(Generic[T]):
    """Generic async DAO: add(**kwargs), update(filter_by, **kwargs), delete(filter_by).

    Subclasses must set model to their SQLAlchemy model class.
    """

    model: ClassVar[Type[BaseSQLModel]]

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def get_one(
        self,
        filter_by: dict[str, object],
        options: Sequence[ORMOption] | None = None,
        order_by: Sequence[ColumnElement[object]] | None = None,
    ) -> T:
        """Load a single row matching ``filter_by``, with optional eager options.

        Args:
            filter_by: Field names and values that identify the row.
            options: Optional SQLAlchemy loader options (e.g. ``select in load``).
            order_by: Optional SQLAlchemy order-by expressions.

        Returns:
            T: Matching model instance.

        Raises:
            ObjectNotFoundException: If no row matches the filter.
        """
        query: Select[tuple[BaseSQLModel]] = select(self.__class__.model)

        if options:
            query = query.options(*options)

        query = query.filter_by(**filter_by)

        if order_by:
            query = query.order_by(*order_by)
        else:
            query = query.order_by(getattr(self.__class__.model, ID))

        result: Result[tuple[BaseSQLModel]] = await self._async_session.execute(query)
        founded_object: BaseSQLModel | None = result.scalar_one_or_none()

        if founded_object is None:
            loguru.logger.warning(Messages.OBJECT_NOT_FOUND)
            raise ObjectNotFoundException(self.__class__.model.__name__)

        return cast(T, founded_object)

    async def add(self, **kwargs) -> T:
        """Insert a new row and flush so primary keys are available.

        Args:
            **kwargs: Column values for the new model instance.

        Returns:
            T: Persisted model instance after flush.
        """

        new_instance: BaseSQLModel = self.__class__.model(**kwargs)
        self._async_session.add(new_instance)
        await self._async_session.flush()

        return cast(T, new_instance)

    async def update(self, filter_by: dict[str, str | int | bool], **kwargs) -> T:
        """Update the first row matching ``filter_by`` and return the refreshed entity.

        Args:
            filter_by: Field names and values that identify the row to update.
            **kwargs: Column names and new values.

        Returns:
            T: Updated model instance after flush and refresh.

        Raises:
            ObjectNotFoundException: If no row matches the filter.
        """

        selected_objects: Select[tuple[BaseSQLModel]] = select(
            self.__class__.model
        ).where(*[getattr(self.__class__.model, k) == v for k, v in filter_by.items()])

        result: Result[tuple[T]] = await self._async_session.execute(selected_objects)
        updated_object: T | None = result.scalar_one_or_none()

        if updated_object is None:
            logger.error(
                f"{Messages.OBJECT_NOT_FOUND} - {Messages.UPDATE_FAILED} - {filter_by}"
            )
            raise ObjectNotFoundException(self.__class__.model.__name__)

        for key, value in kwargs.items():
            setattr(updated_object, key, value)

        await self._async_session.flush()
        await self._async_session.refresh(updated_object)

        return cast(T, updated_object)

    async def delete(self, filter_by: dict[str, str | int | bool]) -> int:
        """Delete rows matching ``filter_by`` and return the ORM delete row count.

        Args:
            filter_by: Field names and values passed to SQLAlchemy ``filter_by``.

        Returns:
            int: Number of rows reported as deleted by the database driver.
        """

        query: Delete = delete(self.__class__.model).filter_by(**filter_by)
        result: Result[tuple[T]] = await self._async_session.execute(query)
        cursor_result: CursorResult[tuple[T]] = cast(CursorResult[tuple[T]], result)

        rows_affected: int = int(getattr(cursor_result, ROWCOUNT))
        return rows_affected
