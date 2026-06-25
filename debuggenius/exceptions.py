"""Typed exception hierarchy for DebugGenius.

A small, explicit hierarchy lets the UI layer present *actionable* messages
instead of leaking raw stack traces to the user. Every error carries a
human-friendly ``message`` and an optional ``hint`` describing the next step.
"""

from __future__ import annotations


class DebugGeniusError(Exception):
    """Base class for all application-level errors.

    Parameters
    ----------
    message:
        Short, user-facing description of what went wrong.
    hint:
        Optional, actionable suggestion shown alongside the message.
    """

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


class ValidationError(DebugGeniusError):
    """Raised when an uploaded file fails validation."""


class AIServiceError(DebugGeniusError):
    """Raised when the AI provider call fails after retries."""


class NetworkError(AIServiceError):
    """Raised when the AI provider call fails due to connectivity issues."""
