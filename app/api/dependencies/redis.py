from typing import AsyncGenerator, Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis, ConnectionPool


async def get_redis(request: Request) -> AsyncGenerator[Redis, None]:
    redis_pool: ConnectionPool = request.app.state.redis_pool
    redis_client: Redis = Redis(connection_pool=redis_pool)

    try:
        yield redis_client
    finally:
        await redis_client.aclose()


RedisDep = Annotated[Redis, Depends(get_redis)]