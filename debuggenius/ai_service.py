"""Gemini client wrapper.

Encapsulates *all* knowledge of the Google Generative AI SDK so the rest of the
app depends only on our typed models and exceptions. Adds streaming, bounded
retries with exponential backoff, and friendly error classification.
"""

from __future__ import annotations

import time
from typing import Iterator

import google.generativeai as genai

from .config import AppConfig
from .exceptions import AIServiceError, NetworkError, RateLimitError
from .logging_setup import get_logger
from .models import DebugRequest
from .prompts import build_prompt

logger = get_logger(__name__)

try:  # The API-core exceptions are optional but usually present.
    from google.api_core import exceptions as _gax
except Exception:  # pragma: no cover - defensive
    _gax = None  # type: ignore[assignment]


def _classify(exc: Exception) -> tuple[AIServiceError, bool]:
    """Map a raw SDK exception to a typed error and whether it's retryable."""

    name = type(exc).__name__
    text = str(exc)

    if _gax is not None:
        if isinstance(exc, _gax.ResourceExhausted):
            return (
                RateLimitError(
                    "Gemini rate limit reached.",
                    hint="Wait a moment and try again, or check your quota in "
                    "Google AI Studio.",
                ),
                True,
            )
        if isinstance(
            exc,
            (
                _gax.ServiceUnavailable,
                _gax.DeadlineExceeded,
                _gax.InternalServerError,
                _gax.GatewayTimeout,
            ),
        ):
            return (
                NetworkError(
                    "Gemini is temporarily unavailable.",
                    hint="This is usually transient — please retry shortly.",
                ),
                True,
            )
        if isinstance(exc, (_gax.PermissionDenied, _gax.Unauthenticated)):
            return (
                AIServiceError(
                    "Your API key was rejected.",
                    hint="Double-check GEMINI_API_KEY is valid and enabled.",
                ),
                False,
            )
        if isinstance(exc, _gax.InvalidArgument):
            return (
                AIServiceError(
                    "Gemini rejected the request.",
                    hint="The image or model name may be unsupported.",
                ),
                False,
            )

    # Fall back to string sniffing for connectivity issues.
    lowered = text.lower()
    if any(t in lowered for t in ("timeout", "connection", "network", "unavailable")):
        return (
            NetworkError(
                "Couldn't reach Gemini.",
                hint="Check your internet connection and retry.",
            ),
            True,
        )

    logger.warning("Unclassified AI error (%s): %s", name, text)
    return (
        AIServiceError(
            "The AI service returned an unexpected error.",
            hint="Please try again; if it persists, check the logs.",
        ),
        False,
    )


class GeminiDebugger:
    """Thin, retrying wrapper around a Gemini vision model."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        genai.configure(api_key=config.api_key)
        self._model = genai.GenerativeModel(
            config.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=config.temperature
            ),
        )
        logger.info("Initialised Gemini model '%s'.", config.model_name)

    # -- public API --------------------------------------------------------

    def analyze_stream(self, request: DebugRequest) -> Iterator[str]:
        """Yield the model's analysis incrementally as text chunks.

        Raises
        ------
        AIServiceError
            (or a subclass) if the call fails after exhausting retries.
        """

        response = self._start_stream_with_retry(request)
        try:
            for chunk in response:
                text = getattr(chunk, "text", None)
                if text:
                    yield text
        except ValueError as exc:
            # Raised by the SDK when a response is blocked / has no text part.
            raise AIServiceError(
                "Gemini returned no readable content.",
                hint="The image may have been blocked by safety filters. Try a "
                "cleaner code screenshot.",
            ) from exc
        except Exception as exc:  # noqa: BLE001 - re-classified below
            typed, _ = _classify(exc)
            raise typed from exc

    # -- internals ---------------------------------------------------------

    def _build_parts(self, request: DebugRequest) -> list[object]:
        return [
            {"mime_type": request.mime_type, "data": request.image_bytes},
            build_prompt(request.mode),
        ]

    def _start_stream_with_retry(self, request: DebugRequest):
        """Open a streaming response, retrying transient failures with backoff."""

        parts = self._build_parts(request)
        last_error: AIServiceError | None = None

        for attempt in range(1, self._config.max_retries + 1):
            try:
                return self._model.generate_content(
                    parts,
                    stream=True,
                    request_options={"timeout": self._config.request_timeout},
                )
            except Exception as exc:  # noqa: BLE001 - classified immediately
                typed, retryable = _classify(exc)
                last_error = typed
                if not retryable or attempt == self._config.max_retries:
                    raise typed from exc
                delay = self._config.retry_backoff_seconds * (2 ** (attempt - 1))
                logger.info(
                    "Transient AI error (attempt %d/%d): %s — retrying in %.1fs.",
                    attempt,
                    self._config.max_retries,
                    typed.message,
                    delay,
                )
                time.sleep(delay)

        # Unreachable, but keeps type-checkers happy.
        raise last_error or AIServiceError("Unknown AI error.")
