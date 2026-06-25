"""Provider abstraction shared by every AI backend.

Both :class:`~debuggenius.ai_service.GeminiDebugger` and
:class:`~debuggenius.ollama_service.OllamaDebugger` structurally satisfy this
Protocol, so the rest of the app depends on the interface — never a concrete
vendor SDK.
"""

from __future__ import annotations

from typing import Iterator, Protocol, runtime_checkable

from .models import DebugRequest


@runtime_checkable
class AIProvider(Protocol):
    """Anything that can stream a debugging analysis for a request."""

    #: Human-friendly label for the active engine (shown in the UI).
    engine_label: str

    def analyze_stream(self, request: DebugRequest) -> Iterator[str]:
        """Yield the model's analysis incrementally as text chunks."""
        ...
