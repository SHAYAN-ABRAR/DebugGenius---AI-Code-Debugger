"""Tests for the Ollama provider's request construction (no network)."""

from __future__ import annotations

import base64

from debuggenius.models import DebugMode, DebugRequest
from debuggenius.ollama_service import OllamaDebugger


def _debugger(api_key: str | None = None) -> OllamaDebugger:
    return OllamaDebugger(
        host="http://localhost:11434/",
        model="gemma4:31b-cloud",
        temperature=0.2,
        timeout=60,
        max_retries=2,
        retry_backoff_seconds=0.5,
        api_key=api_key,
    )


def _request() -> DebugRequest:
    return DebugRequest(
        image_bytes=b"\x89PNG-fake-bytes",
        mime_type="image/png",
        mode=DebugMode.SOLUTION,
        filename="err.png",
    )


def test_host_trailing_slash_is_normalised():
    assert _debugger()._host == "http://localhost:11434"


def test_engine_label_includes_model():
    assert "gemma4:31b-cloud" in _debugger().engine_label


def test_payload_structure_and_image_encoding():
    payload = _debugger()._build_payload(_request())

    assert payload["model"] == "gemma4:31b-cloud"
    assert payload["stream"] is True
    assert payload["options"]["temperature"] == 0.2

    message = payload["messages"][0]
    assert message["role"] == "user"
    assert "Corrected Code" in message["content"]  # SOLUTION-mode prompt

    encoded = message["images"][0]
    assert base64.b64decode(encoded) == b"\x89PNG-fake-bytes"


def test_no_auth_header_without_key():
    headers = _debugger()._headers()
    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"


def test_bearer_header_when_key_present():
    headers = _debugger(api_key="sk-ollama-123")._headers()
    assert headers["Authorization"] == "Bearer sk-ollama-123"


def test_hints_mode_prompt_used_in_payload():
    request = DebugRequest(
        image_bytes=b"x", mime_type="image/png", mode=DebugMode.HINTS, filename="a.png"
    )
    payload = _debugger()._build_payload(request)
    assert "Corrected Code" not in payload["messages"][0]["content"]
