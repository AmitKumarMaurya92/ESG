"""
Structured logging configuration.
Uses Python's standard logging module with JSON-friendly formatting
to support log aggregation pipelines (e.g., Datadog, CloudWatch).

Secrets and sensitive payloads must NEVER be logged.
"""

import logging
import sys
from typing import Any, Dict

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Simple key=value structured formatter. Swap for JSON if needed."""

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        return (
            f"[{record.levelname}] "
            f"env={settings.ENVIRONMENT} "
            f"logger={record.name} | {base}"
        )


def setup_logging() -> None:
    """Configure root logger for the application."""
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        StructuredFormatter(
            fmt="%(asctime)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    # Quieten noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call once per module."""
    return logging.getLogger(name)
