"""Typed domain models shared across layers.

Keeping these as plain dataclasses / enums (no Streamlit or Gemini imports)
makes the core logic trivially unit-testable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class DebugMode(Enum):
    """How much help the user wants back from the model."""

    HINTS = "hints"
    SOLUTION = "solution"

    @property
    def label(self) -> str:
        return {
            DebugMode.HINTS: "Hints only",
            DebugMode.SOLUTION: "Full solution",
        }[self]

    @property
    def icon(self) -> str:
        return {DebugMode.HINTS: "💡", DebugMode.SOLUTION: "🛠️"}[self]

    @property
    def description(self) -> str:
        return {
            DebugMode.HINTS: "Explanation, root cause and tips — no code rewrite.",
            DebugMode.SOLUTION: "Everything in Hints plus corrected, ready-to-paste code.",
        }[self]

    @classmethod
    def from_label(cls, label: str) -> "DebugMode":
        """Resolve a mode from its display label (used by the radio widget)."""

        for mode in cls:
            if mode.label == label:
                return mode
        raise ValueError(f"Unknown debug mode label: {label!r}")


@dataclass(frozen=True, slots=True)
class DebugRequest:
    """An immutable analysis request handed to the AI service."""

    image_bytes: bytes
    mime_type: str
    mode: DebugMode
    filename: str


@dataclass(slots=True)
class HistoryEntry:
    """A completed analysis, retained for the session-history panel."""

    filename: str
    mode: DebugMode
    response: str
    thumbnail_b64: str | None = None
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: float = field(default_factory=time.time)

    @property
    def created_label(self) -> str:
        """Human-friendly local timestamp, e.g. ``14:32``."""

        return time.strftime("%H:%M", time.localtime(self.created_at))
