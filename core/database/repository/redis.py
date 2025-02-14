from typing import Self

from asyncio import Lock
from datetime import timedelta
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError

from core.logging.logger import CoreLogger

logger = CoreLogger.get_logger("redis_repository")


class TokenStatus(StrEnum):
    REVOKED = "REVOKED"


class TokenNamespace(BaseModel):
    """Token namespace."""

    namespace: str = "blacklist"


class TokenKey(BaseModel):
    """Token key wrapper."""

    jti: str
    namespace: TokenNamespace = TokenNamespace()

    @computed_field(alias="key", repr=True)  # type: ignore[prop-decorator]
    @property
    def key(self) -> str:
        return f"{self.namespace}:{self.jti}"


class TokenData(BaseModel):
    """Token storage model"""

    key: str = Field(min_length=1)
    value: str = Field(default=TokenStatus.REVOKED, min_length=1)
    expires: timedelta

    @property
    def expiration_seconds(self) -> int:
        return int(self.expires.total_seconds())

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class RedisRepository:
    """Redis repository."""

    __slots__ = ("_redis",)

    def __init__(self, redis: Redis) -> None:  # type: ignore[type-arg]
        self._redis = redis

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:  # type: ignore[no-untyped-def]
        await self._redis.aclose()  # type: ignore[attr-defined]

    async def set(self, data: TokenData) -> bool | None:
        logger.info("Setting token data: %s", data)
        result = await self._redis.set(name=data.key, value=data.value, ex=data.expires)
        logger.info("Set result: %s", result)
        return bool(result)

    async def get(self, key: str) -> str | None:
        return await self._redis.get(key)

    async def get_all(self) -> list[str] | None:  # type: ignore[return]
        try:
            keys = await self._redis.keys("*")
            keys = [await self._redis.get(key) for key in keys]
            logger.info("Keys: %s", keys)
        except RedisError as e:
            logger.exception("Redis error: %s", exc_info=e)
        else:
            return keys

    async def delete(self, key: str) -> bool:
        return bool(await self._redis.delete(key))

    async def exists(self, key: str) -> bool:
        logger.info("Checking if token exists: %s", key)
        return bool(await self._redis.exists(key))


class RedisConfig(BaseModel):
    dsn: str
    password: str


class RedisPoolConfig:
    pool: ConnectionPool | None = None  # type: ignore[type-arg]
    _lock = Lock()

    @classmethod
    async def ensure_pool(cls, config: RedisConfig) -> None:
        async with cls._lock:
            if cls.pool is None:
                try:
                    cls.pool = ConnectionPool.from_url(
                        url=config.dsn,
                        password=config.password,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        retry_on_timeout=True,
                    )
                    logger.info("Redis connection pool initialized")
                except Exception as e:
                    logger.exception("Redis initialization failed: %s", exc_info=e)
                    raise RedisConnectionError("Redis connection error") from e

    @classmethod
    async def close_pool(cls) -> None:
        if cls.pool:
            await cls.pool.disconnect()
            cls.pool = None
            logger.info("Redis pool closed")


async def get_redis_client(config: RedisConfig) -> Redis:  # type: ignore[type-arg]
    if RedisPoolConfig.pool is None:
        await RedisPoolConfig.ensure_pool(config)
    return Redis(connection_pool=RedisPoolConfig.pool, auto_close_connection_pool=False)
