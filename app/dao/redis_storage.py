from loguru import logger

from redis import RedisError
from redis.asyncio import Redis

from app.dao.constants import DAOStandardMessages, DAOFieldValues, DAOFieldNames
from app.dao.exceptions import RedisKeyValueNotFoundException
from app.schemas.services import RedisKeyValueDomain


class RedisDAO:
    def __init__(self, redis: Redis):
        self._redis_session = redis

    async def get_data_by_key(self, key: str) -> RedisKeyValueDomain:
        try:
            data: str | None = await self._redis_session.get(key)
        except RedisError as error:
            logger.exception(
                f"{DAOFieldValues.KEY_VALUE} {DAOStandardMessages.READING_FAILED} {DAOFieldNames.KEY} {key}"
            )

            raise error

        if data is None:
            logger.error(
                f"{DAOStandardMessages.DATA_IS_NONE} {DAOFieldNames.KEY} {key}"
            )

            raise RedisKeyValueNotFoundException(DAOFieldValues.KEY_VALUE)

        redis_key_value_domain_object: RedisKeyValueDomain = RedisKeyValueDomain(
            key=key, value_hash=data
        )

        return redis_key_value_domain_object

    async def save_one_by_key(
        self, key: str, new_data_hash: str
    ) -> RedisKeyValueDomain:
        try:
            await self._redis_session.set(key, new_data_hash)
            stored_new_data: str = await self._redis_session.get(key)
        except RedisError as error:
            logger.exception(
                f"{DAOFieldValues.KEY_VALUE} {DAOStandardMessages.SAVING_FAILED} {DAOFieldNames.KEY} {key}"
            )

            raise error

        if stored_new_data != new_data_hash or stored_new_data is None:
            logger.error(
                f"{DAOStandardMessages.SAVING_FAILED} {DAOFieldNames.KEY} {key}"
            )

            raise RedisKeyValueNotFoundException(DAOFieldValues.KEY_VALUE)

        redis_key_value_domain_object: RedisKeyValueDomain = RedisKeyValueDomain(
            key=key, value_hash=stored_new_data
        )

        return redis_key_value_domain_object

    async def delete_one_by_key(self, key: str) -> int:
        try:
            deleted_status: int = await self._redis_session.delete(key)
        except RedisError as error:
            logger.exception(
                f"{DAOStandardMessages.DELETE_FAILED} {DAOFieldNames.KEY} {key}"
            )
            raise error

        return deleted_status
