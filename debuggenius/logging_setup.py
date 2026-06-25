"""Centralized logging configuration.

A single ``configure_logging`` call wires up a console handler with a concise,
readable format. Idempotent: safe to call on every Streamlit rerun.
"""

from __future__ import annotations

import logging
import os

_CONFIGURED = False
_DEFAULT_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def configure_logging(level: str | int | None = None) -> None:
    """Configure root logging exactly once per process.

    Parameters
    ----------
    level:
        Log level name or value. Falls back to the ``DEBUGGENIUS_LOG_LEVEL``
        environment variable, then ``INFO``.
    """

    global _CONFIGURED
    if _CONFIGURED:
        return

    resolved = level or os.getenv("DEBUGGENIUS_LOG_LEVEL", "INFO")
    logging.basicConfig(level=resolved, format=_DEFAULT_FORMAT)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module logger, ensuring logging is configured first."""

    configure_logging()
    return logging.getLogger(name)
