from contextlib import asynccontextmanager
from typing import AsyncGenerator, cast

from fastapi import FastAPI
from redis.asyncio import ConnectionPool

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis_url: str = cast(str, settings.redis.redis_url)
    app.state.redis_pool = ConnectionPool.from_url(
        redis_url,
        decode_responses=True
    )
    yield
    await app.state.redis_pool.disconnect()
