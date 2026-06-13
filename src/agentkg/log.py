"""Central loguru logger. Import `from .log import logger`; call configure() once
(the CLI does, from settings). Level via KG_LOG_LEVEL or the --log-level option.
"""
from __future__ import annotations

import os
import sys

from loguru import logger

_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | "
    "<cyan>{name}</cyan> - <level>{message}</level>"
)


def configure(level: str | None = None) -> None:
    logger.remove()
    lvl = (level or os.environ.get("KG_LOG_LEVEL", "INFO")).upper()
    logger.add(sys.stderr, level=lvl, format=_FORMAT, colorize=True)


configure()  # sensible default for library/import use; CLI re-configures

__all__ = ["logger", "configure"]
