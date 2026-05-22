"""Redis data-access helpers for ephemeral token and session storage."""

from loguru import logger

from redis import RedisError
from redis.asyncio import Redis

from app.dao.constants import Messages, KEY_VALUE, KEY
from app.dao.exceptions import RedisKeyValueNotFoundException


class RedisDAO:
    """Thin async wrapper around Redis commands used by refresh-token flows."""

    def __init__(self, redis: Redis) -> None:
        """Attach an async Redis client instance.

        Args:
            redis: Connected :class:`~redis.asyncio.Redis` client.
        """
        self._redis_session = redis

    async def get_del_data_by_key(self, key: str) -> str:
        """Atomically read and delete the value stored under ``key``.

        Args:
            key: Redis key previously written by this DAO.

        Returns:
            str: Value that was stored at ``key`` before deletion.

        Raises:
            RedisError: If the Redis GET/DEL operation fails.
            RedisKeyValueNotFoundException: If ``key`` is absent or yields no value.
        """
        try:
            deleted_data: str | None = await self._redis_session.getdel(key)
        except RedisError as error:
            logger.exception(
                f"{KEY_VALUE} {Messages.GET_DEL_OPERATION_FAILED} {KEY} {key}"
            )

            raise error

        if deleted_data is None:
            logger.error(f"{Messages.DATA_IS_NONE} {KEY} {key}")

            raise RedisKeyValueNotFoundException(KEY_VALUE)

        return deleted_data

    async def save_one(self, key: str, new_data: str, ttl: int) -> None:
        """Persist ``new_data`` at ``key`` with a time-to-live in seconds.

        Args:
            key: Redis key to write.
            new_data: Serialized payload stored as the key value.
            ttl: Expiration interval in seconds (``SET`` ``EX``).

        Raises:
            RedisError: If the Redis SET operation fails.
        """
        try:
            await self._redis_session.set(name=key, value=new_data, ex=ttl)
        except RedisError as error:
            logger.exception(f"{KEY_VALUE} {Messages.SAVING_FAILED} {KEY} {key}")

            raise error

        return
