from typing import Any

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database.repository.redis import RedisConfig, RedisPoolConfig
from core.logging.logger import CoreLogger

logger = CoreLogger.get_logger("lifespan")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    from conf.settings import settings

    try:
        await RedisPoolConfig.ensure_pool(RedisConfig(dsn=settings.redis.dsn, password=settings.redis.password))
        logger.info("Connected to Redis!")
        yield
    finally:
        await RedisPoolConfig.close_pool()
