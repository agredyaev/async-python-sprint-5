import asyncio

from conf.settings import settings
from core.connections import AppConnectionChecker
from core.logging import CoreLogger
from core.services.waiter import ServiceWaiter

logger = CoreLogger.get_logger("app_waiter")


async def main() -> None:
    services = [
        ServiceWaiter(
            checker=AppConnectionChecker(url=settings.app.base_url + settings.app.health_check_path),
            logger=logger,
            max_time=settings.backoff.max_time,
            max_tries=settings.backoff.max_tries,
        )
    ]

    await asyncio.gather(*(service.wait_for_service() for service in services))
    logger.info("App is ready. Starting the workers.")


if __name__ == "__main__":
    asyncio.run(main())
