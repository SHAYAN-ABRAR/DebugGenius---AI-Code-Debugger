"""Application configuration and secret resolution.

All tunable knobs live here as a single, immutable :class:`AppConfig` object so
the rest of the code never reaches for ``os.getenv`` or magic numbers directly.

Every value is read from the environment / ``.env`` first, then from
``st.secrets`` — so the same configuration works locally and on Streamlit Cloud.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from dotenv import load_dotenv

from .logging_setup import get_logger

logger = get_logger(__name__)

# Load .env once at import time (no-op if the file is absent).
load_dotenv()

#: Defaults.
_DEFAULT_OLLAMA_HOST = "http://localhost:11434"
_DEFAULT_OLLAMA_MODEL = "gemma4:31b-cloud"

#: Allowed upload extensions mapped to their canonical MIME type.
_ALLOWED_MIME_TYPES: Mapping[str, str] = MappingProxyType(
    {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}
)


def _resolve_secret(name: str) -> str | None:
    """Return a secret from the environment / .env, falling back to st.secrets."""

    # Environment / .env first — cheap and never raises.
    value = os.getenv(name)
    if value:
        return value.strip()

    # st.secrets raises if no secrets file exists, so guard defensively.
    try:
        import streamlit as st

        secret = st.secrets.get(name)  # type: ignore[attr-defined]
        if secret:
            return str(secret).strip()
    except Exception:  # pragma: no cover - depends on runtime secrets file
        logger.debug("No Streamlit secrets available; relying on environment.")

    return None


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Immutable application configuration."""

    ollama_host: str = _DEFAULT_OLLAMA_HOST
    ollama_model: str = _DEFAULT_OLLAMA_MODEL
    ollama_api_key: str | None = None  # only needed for remote ollama.com

    # Shared tuning
    temperature: float = 0.3
    request_timeout: int = 120
    max_retries: int = 3
    retry_backoff_seconds: float = 1.5
    max_file_bytes: int = 10 * 1024 * 1024  # 10 MB
    max_image_dimension: int = 4096  # px on the longest side
    max_history_items: int = 12
    allowed_mime_types: Mapping[str, str] = field(
        default_factory=lambda: _ALLOWED_MIME_TYPES, compare=False
    )

    @property
    def allowed_extensions(self) -> tuple[str, ...]:
        """File extensions accepted by the uploader widget."""

        return tuple(self.allowed_mime_types.keys())

    @classmethod
    def load(cls) -> "AppConfig":
        """Build configuration from the environment / Streamlit secrets."""

        return cls(
            ollama_host=_resolve_secret("OLLAMA_HOST") or _DEFAULT_OLLAMA_HOST,
            ollama_model=_resolve_secret("OLLAMA_MODEL") or _DEFAULT_OLLAMA_MODEL,
            ollama_api_key=_resolve_secret("OLLAMA_API_KEY"),
        )
