from typing import cast

from sqlalchemy import Select, select, Result, ScalarResult
from sqlalchemy.orm import selectinload

from app.dao.base_dao import BaseDAO, T
from app.database import async_session_maker
from app.models.models import Chat


class ChatDAO(BaseDAO[Chat]):

    model = Chat

    @classmethod
    async def find_one_or_none_by_id(cls, **kwargs) -> T | None:
        async with async_session_maker() as async_session:
            query: Select[tuple[Chat]] = (
                select(cls.model)
                .options(selectinload(cls.model.messages))
                .filter_by(**kwargs)
            )
            result: Result[tuple[Chat]] = await async_session.execute(query)
            chat: Chat | None = result.scalar_one_or_none()

            if not chat:
                return None

            return cast(T, chat)


    @classmethod
    async def get_user_chat_list(cls, **kwargs) -> ScalarResult[Chat] | None:
        async with async_session_maker() as async_session:
            query: Select[tuple[Chat]] = (
                select(cls.model)
                .options(selectinload(cls.model.messages))
                .filter_by(**kwargs)
            )
            result: Result[tuple[Chat]] = await async_session.execute(query)
            scalar_chat_list: ScalarResult[Chat] = result.scalars()

            if not scalar_chat_list:
                return None

            return scalar_chat_list
