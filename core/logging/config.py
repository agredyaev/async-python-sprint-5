from typing import Any

from pydantic import BaseModel


class LogConfig(BaseModel):
    """Config for logging."""

    HANDLER_CLASS: str = "logging.StreamHandler"
    HANDLER_STREAM: str = "ext://sys.stdout"

    LOGGER_NAME: str = "core"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_LEVEL: str = "DEBUG"

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict[str, dict[str, Any]] = {
        "default": {"format": LOG_FORMAT, "datefmt": "%Y-%m-%d %H:%M:%S"},
        "uvicorn_default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(levelname)s - %(message)s",
            "use_colors": True,
        },
        "uvicorn_access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    }
    handlers: dict[str, dict[str, Any]] = {
        "default": {"formatter": "default", "class": HANDLER_CLASS, "stream": HANDLER_STREAM},
        "uvicorn_default": {"formatter": "uvicorn_default", "class": HANDLER_CLASS, "stream": HANDLER_STREAM},
        "uvicorn_access": {"formatter": "uvicorn_access", "class": HANDLER_CLASS, "stream": HANDLER_STREAM},
    }
    loggers: dict[str, dict[str, Any]] = {
        "": {"handlers": ["default"], "level": LOG_LEVEL},
        "uvicorn": {"handlers": ["uvicorn_default"], "level": "INFO"},
        "uvicorn.error": {"handlers": ["uvicorn_default"], "level": "INFO"},
        "uvicorn.access": {"handlers": ["uvicorn_access"], "level": "INFO", "propagate": False},
    }
