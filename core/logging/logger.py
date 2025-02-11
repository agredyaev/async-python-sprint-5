import logging

from logging import config

from core.logging.config import LogConfig


class CoreLogger:
    _instance: logging.Logger | None = None

    @classmethod
    def setup(cls) -> None:
        """Initialize logging."""
        log_config = LogConfig()
        config.dictConfig(log_config.model_dump())

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get logger instance."""
        if not cls._instance:
            cls.setup()
        return logging.getLogger(name)
