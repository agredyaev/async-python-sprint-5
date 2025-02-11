import asyncio

from conf.settings import settings
from core.connections import PostgresConnectionChecker
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
        )
    ]

    await asyncio.gather(*(service.wait_for_service() for service in services))
    logger.info("All services are ready. Starting the application.")


if __name__ == "__main__":
    asyncio.run(main())
