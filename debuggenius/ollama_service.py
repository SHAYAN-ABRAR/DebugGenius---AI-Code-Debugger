"""Ollama client wrapper (local daemon at ``/api/chat``).

Talks to a running Ollama server over its HTTP API using only the standard
library (no extra dependency). Supports vision models via the ``images`` field,
streaming NDJSON responses, bounded retries, and friendly error mapping —
mirroring the :class:`~debuggenius.ai_service.GeminiDebugger` interface.
"""

from __future__ import annotations

import base64
import json
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Iterator

from .exceptions import AIServiceError, NetworkError
from .logging_setup import get_logger
from .models import DebugRequest
from .prompts import build_prompt

logger = get_logger(__name__)


class OllamaDebugger:
    """Streaming debugger backed by a local/Cloud Ollama model."""

    def __init__(
        self,
        *,
        host: str,
        model: str,
        temperature: float,
        timeout: int,
        max_retries: int,
        retry_backoff_seconds: float,
        api_key: str | None = None,
    ) -> None:
        self._host = host.rstrip("/")
        self._model = model
        self._temperature = temperature
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff = retry_backoff_seconds
        self._api_key = api_key
        self.engine_label = f"Ollama · {model}"
        logger.info(
            "Initialised Ollama model '%s' at %s (auth: %s).",
            model,
            self._host,
            "key" if api_key else "local/none",
        )

    # -- public API --------------------------------------------------------

    def analyze_stream(self, request: DebugRequest) -> Iterator[str]:
        """Yield the model's analysis incrementally as text chunks."""

        payload = self._build_payload(request)
        response = self._open_with_retry(payload)
        try:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                obj = json.loads(line)
                if obj.get("error"):
                    raise self._map_stream_error(str(obj["error"]))
                chunk = obj.get("message", {}).get("content")
                if chunk:
                    yield chunk
                if obj.get("done"):
                    break
        except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
            raise NetworkError(
                "Lost the connection to Ollama mid-response.",
                hint="Check that the Ollama server is still running, then retry.",
            ) from exc
        finally:
            response.close()

    # -- internals ---------------------------------------------------------

    def _build_payload(self, request: DebugRequest) -> dict[str, Any]:
        """Build the ``/api/chat`` request body (pure — easy to unit-test)."""

        image_b64 = base64.b64encode(request.image_bytes).decode("ascii")
        return {
            "model": self._model,
            "stream": True,
            "messages": [
                {
                    "role": "user",
                    "content": build_prompt(request.mode),
                    "images": [image_b64],
                }
            ],
            "options": {"temperature": self._temperature},
        }

    def _headers(self) -> dict[str, str]:
        """Request headers — adds Bearer auth when an API key is configured."""

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _open_with_retry(self, payload: dict[str, Any]):
        """Open a streaming connection, retrying transient failures."""

        data = json.dumps(payload).encode("utf-8")
        url = f"{self._host}/api/chat"
        headers = self._headers()
        last_error: AIServiceError | None = None

        for attempt in range(1, self._max_retries + 1):
            request = urllib.request.Request(url, data=data, headers=headers)
            try:
                return urllib.request.urlopen(request, timeout=self._timeout)
            except urllib.error.HTTPError as exc:
                # HTTP errors are usually permanent (bad model, auth) — don't retry.
                raise self._map_http_error(exc) from exc
            except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
                last_error = NetworkError(
                    "Couldn't reach the Ollama server.",
                    hint=f"Is it running? Start it with 'ollama serve' "
                    f"(expected at {self._host}).",
                )
                if attempt == self._max_retries:
                    raise last_error from exc
                delay = self._backoff * (2 ** (attempt - 1))
                logger.info(
                    "Ollama connection failed (attempt %d/%d) — retrying in %.1fs.",
                    attempt,
                    self._max_retries,
                    delay,
                )
                time.sleep(delay)

        raise last_error or AIServiceError("Unknown Ollama error.")

    def _map_http_error(self, exc: urllib.error.HTTPError) -> AIServiceError:
        body = ""
        try:
            body = exc.read().decode("utf-8", "replace")
        except Exception:  # pragma: no cover - defensive
            pass
        detail = body.lower()

        if exc.code == 404 or "not found" in detail:
            return AIServiceError(
                f"Model '{self._model}' isn't available in Ollama.",
                hint=f"Pull it first: 'ollama pull {self._model}'.",
            )
        if exc.code in (401, 403) or "sign" in detail or "unauthor" in detail:
            return AIServiceError(
                "Ollama rejected the request (authentication).",
                hint="For '-cloud' models, sign in first: 'ollama signin'.",
            )
        logger.warning("Ollama HTTP %s: %s", exc.code, body[:300])
        return AIServiceError(
            f"Ollama returned an error (HTTP {exc.code}).",
            hint="Check the Ollama server logs for details.",
        )

    def _map_stream_error(self, message: str) -> AIServiceError:
        lowered = message.lower()
        if "sign" in lowered or "unauthor" in lowered:
            return AIServiceError(
                "Ollama Cloud needs you to sign in.",
                hint="Run 'ollama signin' in a terminal, then try again.",
            )
        logger.warning("Ollama stream error: %s", message)
        return AIServiceError("Ollama reported an error.", hint=message[:200])
