import asyncio

from conf.settings import settings
from core.connections import MinioConnectionChecker, PostgresConnectionChecker, RedisConnectionChecker
from core.logging.logger import CoreLogger
from core.services.waiter import ServiceWaiter

logger = CoreLogger.get_logger("services_waiter")


async def main() -> None:
    services = [
        ServiceWaiter(
            checker=PostgresConnectionChecker(dsn=settings.pg.dsn_pg),
            logger=logger,
            max_time=settings.backoff.max_time,
            max_tries=settings.backoff.max_tries,
        ),
        ServiceWaiter(
            checker=RedisConnectionChecker(dsn=settings.redis.dsn),
            logger=logger,
            max_time=settings.backoff.max_time,
            max_tries=settings.backoff.max_tries,
        ),
        ServiceWaiter(
            checker=MinioConnectionChecker(
                endpoint=settings.minio.endpoint,
                access_key=settings.minio.root_user,
                secret_key=settings.minio.root_password,
                secure=settings.minio.secure,
            ),
            logger=logger,
            max_time=settings.backoff.max_time,
            max_tries=settings.backoff.max_tries,
        ),
    ]

    await asyncio.gather(*(service.wait_for_service() for service in services))
    logger.info("All services are ready. Starting the application.")


if __name__ == "__main__":
    asyncio.run(main())
