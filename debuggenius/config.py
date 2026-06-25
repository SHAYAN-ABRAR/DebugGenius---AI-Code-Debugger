"""Application configuration and secret resolution.

All tunable knobs live here as a single, immutable :class:`AppConfig` object so
the rest of the code never reaches for ``os.getenv`` or magic numbers directly.

The app supports two AI backends, chosen via the ``AI_PROVIDER`` env var:

* ``ollama`` (default) – a local/Cloud Ollama daemon; needs no API key.
* ``gemini``            – Google Gemini; needs ``GEMINI_API_KEY`` from either
  ``st.secrets`` (Streamlit Cloud) or the environment / ``.env`` (local).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from dotenv import load_dotenv

from .exceptions import ConfigurationError
from .logging_setup import get_logger

logger = get_logger(__name__)

# Load .env once at import time (no-op if the file is absent).
load_dotenv()

#: Supported AI backends.
PROVIDER_OLLAMA = "ollama"
PROVIDER_GEMINI = "gemini"
_VALID_PROVIDERS = frozenset({PROVIDER_OLLAMA, PROVIDER_GEMINI})

#: Defaults.
_DEFAULT_PROVIDER = PROVIDER_OLLAMA
_DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
_DEFAULT_OLLAMA_MODEL = "gemma4:31b-cloud"
_DEFAULT_OLLAMA_HOST = "http://localhost:11434"

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


def _resolve_api_key() -> str | None:
    """Return the Gemini API key from the environment or Streamlit secrets."""

    return _resolve_secret("GEMINI_API_KEY")


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Immutable application configuration."""

    provider: str = _DEFAULT_PROVIDER
    api_key: str | None = None

    # Gemini settings
    model_name: str = _DEFAULT_GEMINI_MODEL

    # Ollama settings
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

    @property
    def active_model(self) -> str:
        """The model name for the currently selected provider."""

        return self.ollama_model if self.provider == PROVIDER_OLLAMA else self.model_name

    @classmethod
    def load(cls) -> "AppConfig":
        """Build configuration from the environment, validating required keys.

        Raises
        ------
        ConfigurationError
            If the provider is unknown, or if Gemini is selected without a key.
        """

        # Every value resolves from environment / .env first, then st.secrets,
        # so the same config works locally and on Streamlit Cloud.
        provider = (_resolve_secret("AI_PROVIDER") or _DEFAULT_PROVIDER).strip().lower()
        if provider not in _VALID_PROVIDERS:
            raise ConfigurationError(
                f"Unknown AI_PROVIDER '{provider}'.",
                hint=f"Set AI_PROVIDER to one of: {', '.join(sorted(_VALID_PROVIDERS))}.",
            )

        api_key = _resolve_api_key()
        if provider == PROVIDER_GEMINI and not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not configured.",
                hint=(
                    "Add GEMINI_API_KEY to a .env file or Streamlit secrets, or "
                    "switch to Ollama with AI_PROVIDER=ollama. Get a Gemini key at "
                    "https://aistudio.google.com/app/apikeys."
                ),
            )

        return cls(
            provider=provider,
            api_key=api_key,
            model_name=_resolve_secret("GEMINI_MODEL") or _DEFAULT_GEMINI_MODEL,
            ollama_host=_resolve_secret("OLLAMA_HOST") or _DEFAULT_OLLAMA_HOST,
            ollama_model=_resolve_secret("OLLAMA_MODEL") or _DEFAULT_OLLAMA_MODEL,
            ollama_api_key=_resolve_secret("OLLAMA_API_KEY"),
        )
