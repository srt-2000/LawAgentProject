from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from redis.asyncio import ConnectionPool

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[..., None]:
    app.state.redis_pool = ConnectionPool.from_url(
        settings.redis.redis_url,
        decode_responses=True
    )
    yield
    await app.state.redis_pool.disconnect()
