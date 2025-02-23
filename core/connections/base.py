from typing import Any

from abc import ABC, abstractmethod

NOT_IMPLEMENTED = "This method should be implemented by subclasses."


class BaseConnectionChecker(ABC):
    """Base class for connection checkers."""

    __slots__ = ("exception",)

    exceptions: tuple[type[Exception], ...]

    @abstractmethod
    async def client(self) -> Any:
        """Return connection client."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    async def close(self) -> None:
        """Close connection."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    async def perform_check(self) -> bool:
        """Perform connection check."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    async def check_connection(self) -> bool:
        """Check connection."""
        try:
            return await self.perform_check()
        finally:
            await self.close()

    async def execute_check(self) -> None:
        """Execute connection check."""
        if not await self.check_connection():
            raise self.exceptions[0](f"Condition is not met for {self.__class__.__name__}.")
