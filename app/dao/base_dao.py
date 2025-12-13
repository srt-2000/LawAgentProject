from typing import Coroutine

from sqlalchemy import update, delete
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session_maker



class BaseDAO:

    model = None

    @classmethod
    async def add(cls, **kwargs) -> Coroutine:
        async with async_session_maker() as async_session:
            async with async_session.begin():
                new_instance = cls.model(**kwargs)
                async_session.add(new_instance)
                try:
                    await async_session.commit()
                except SQLAlchemyError as error:
                    await async_session.rollback()
                    raise error
                return new_instance

    @classmethod
    async def update(cls, filter_by: dict, **kwargs) -> Coroutine:
        async with async_session_maker() as async_session:
            async with async_session.begin():
                query = (
                    update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**kwargs)
                    .execution_options(synchronize_session="fetch")
                )
                result = await async_session.execute(query)

                try:
                    await async_session.commit()
                except SQLAlchemyError as error:
                    await async_session.rollback()
                    raise error
                return result.rowcount

    @classmethod
    async def delete(cls, filter_by: dict) -> Coroutine:
        async with async_session_maker() as async_session:
            async with async_session.begin():
                query = delete(cls.model).filter_by(**filter_by)
                result = await async_session.execute(query)

                try:
                    await async_session.commit()
                except SQLAlchemyError as error:
                    await async_session.rollback()
                    raise error
                return result.rawcount
