from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy.engine import Result

from app.dao.base_dao import BaseDAO
from app.database import async_session_maker
from app.models.models import User
from app.schemas.users_schema import DBUserDTO


class UserDAO(BaseDAO):

    model = User

    @classmethod
    async def find_one_or_none(cls, **kwargs) -> DBUserDTO | None:
        async with async_session_maker() as async_session:
            query: Select[tuple[User]] = (
                select(cls.model)
                .options(selectinload(cls.model.chats))
                .filter_by(**kwargs)
            )
            result: Result[tuple[User]] = await async_session.execute(query)
            user: DBUserDTO | None = result.scalar_one_or_none()
            return DBUserDTO.model_validate(user)

