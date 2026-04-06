import hashlib
import hmac
import secrets

from fastapi import HTTPException
from loguru import logger
from redis import RedisError
from redis.asyncio import Redis
from starlette import status

from app.services.constants import FieldsValues, StandardMessages


class SecretsService:

    @staticmethod
    async def create_storage_key(session_id: str) -> str:
        storage_key: str = FieldsValues.REFRESH_KEY_PREFIX + session_id

        return storage_key

    @staticmethod
    async def get_hashed_secret(secret: str) -> str:
        encoded_secret: bytes = secret.encode(FieldsValues.UTF_8)
        hashed_secret: str = hashlib.sha256(encoded_secret).hexdigest()

        return hashed_secret


class RefreshTokenService(SecretsService):

    @classmethod
    async def create_refresh_token(
            cls,
            redis: Redis,
            user_id: str,
            ttl_seconds: int
            ) -> str:
        session_id: str = secrets.token_urlsafe(FieldsValues.SID_BYTES_QUERY)
        secret: str = secrets.token_urlsafe(FieldsValues.SECRET_BYTES_QUERY)
        secret_hash: str = await cls.get_hashed_secret(secret)
        storage_key: str = await cls.create_storage_key(session_id)
        storage_value: str = f"{user_id}|{secret_hash}"

        try:
            await redis.set(
                name=storage_key,
                value=storage_value,
                ex=ttl_seconds
                )
        except RedisError as error:
            logger.error(f"{StandardMessages.REFRESH_TOKEN_REDIS_ERROR}: {error}")
            raise error

        refresh_token: str = session_id + FieldsValues.TOKEN_SEPARATOR + secret

        return refresh_token

    @classmethod
    async def consume_rotate(
            cls,
            redis: Redis,
            refresh_token: str,
            ttl_seconds: int
    ) -> tuple[str, str]:

        if FieldsValues.TOKEN_SEPARATOR not in refresh_token:
            logger.error(f"{StandardMessages.REFRESH_TOKEN_IS_NOT_VALID}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.REFRESH_TOKEN_IS_NOT_VALID
            )

        separated_refresh_token: list[str] = refresh_token.split(FieldsValues.TOKEN_SEPARATOR, 1)
        session_id, secret = separated_refresh_token

        if not session_id or not secret:
            logger.error(f"{StandardMessages.REFRESH_TOKEN_IS_NOT_VALID}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.REFRESH_TOKEN_IS_NOT_VALID
            )

        key: str = await cls.create_storage_key(session_id)
        raw: str | None = await redis.get(key)

        if raw is None:
            logger.error(f"{StandardMessages.REFRESH_TOKEN_IS_NOT_VALID}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.REFRESH_TOKEN_IS_NOT_VALID
            )

        try:
            user_part, hash_part = raw.split(FieldsValues.CONCAT_SEPARATOR, 1)
        except ValueError as error:
            logger.error(f"{StandardMessages.REFRESH_TOKEN_IS_NOT_VALID}: {error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.REFRESH_TOKEN_IS_NOT_VALID
            )

        if not hmac.compare_digest(user_part, hash_part):
            await redis.delete(key)
            logger.error(f"{StandardMessages.REFRESH_TOKEN_IS_NOT_VALID}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=StandardMessages.REFRESH_TOKEN_IS_NOT_VALID
            )

        await redis.delete(key)
        new_refresh_token: str = await cls.create_refresh_token(
            redis,
            user_id=user_part,
            ttl_seconds=ttl_seconds
        )

        return user_part, new_refresh_token

    @classmethod
    async def revoke_token(
            cls,
            redis: Redis,
            refresh_token: str
    ) -> None:

        if not refresh_token or FieldsValues.TOKEN_SEPARATOR not in refresh_token:
            return

        separated_refresh_token: list[str] = refresh_token.split(FieldsValues.TOKEN_SEPARATOR, 1)
        session_id: str = separated_refresh_token[0]
        session_key_to_delete: str = await cls.create_storage_key(session_id)

        if session_id:
            await redis.delete(session_key_to_delete)
