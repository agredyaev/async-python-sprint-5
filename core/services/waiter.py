from typing import Any

import logging

import backoff

from core.connections.base import BaseConnectionChecker


class ServiceWaiter:
    """Wait for service."""

    __slots__ = ("checker", "logger", "max_time", "max_tries")

    def __init__(
        self, checker: BaseConnectionChecker, logger: logging.Logger, max_time: int = 300, max_tries: int = 60
    ):
        self.checker = checker
        self.max_time = max_time
        self.max_tries = max_tries
        self.logger = logger

    def get_decorator(self) -> Any:
        return backoff.on_exception(
            backoff.expo, self.checker.exceptions, max_time=self.max_time, max_tries=self.max_tries
        )

    async def wait_for_service(self) -> None:
        @self.get_decorator()
        async def execute_command() -> None:
            checker_name = self.checker.__class__.__name__
            try:
                await self.checker.execute_check()
                self.logger.info("%s is ready.", checker_name)
            except Exception as e:
                self.logger.info("%s is not ready: %s. Retrying...", checker_name, e)
                raise

        await execute_command()
