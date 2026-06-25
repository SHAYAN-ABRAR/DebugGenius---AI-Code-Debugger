"""Application configuration and secret resolution.

All tunable knobs live here as a single, immutable :class:`AppConfig` object so
the rest of the code never reaches for ``os.getenv`` or magic numbers directly.

The Gemini API key is resolved from (in order):

1. ``st.secrets["GEMINI_API_KEY"]``  – for Streamlit Cloud deployments.
2. the ``GEMINI_API_KEY`` environment variable / ``.env`` file – for local dev.
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

#: Default Gemini model used for vision analysis.
_DEFAULT_MODEL = "gemini-2.0-flash"

#: Allowed upload extensions mapped to their canonical MIME type.
_ALLOWED_MIME_TYPES: Mapping[str, str] = MappingProxyType(
    {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}
)


def _resolve_api_key() -> str | None:
    """Return the Gemini API key from Streamlit secrets or the environment."""

    # Environment / .env first — cheap and never raises.
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key.strip()

    # st.secrets raises if no secrets file exists, so guard defensively.
    try:
        import streamlit as st

        secret = st.secrets.get("GEMINI_API_KEY")  # type: ignore[attr-defined]
        if secret:
            return str(secret).strip()
    except Exception:  # pragma: no cover - depends on runtime secrets file
        logger.debug("No Streamlit secrets available; relying on environment.")

    return None


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Immutable application configuration."""

    api_key: str
    model_name: str = _DEFAULT_MODEL
    temperature: float = 0.3
    request_timeout: int = 60
    max_retries: int = 3
    retry_backoff_seconds: float = 1.5
    max_file_bytes: int = 10 * 1024 * 1024  # 10 MB
    max_image_dimension: int = 4096  # px on the longest side
    max_history_items: int = 12
    allowed_mime_types: Mapping[str, str] = field(default_factory=lambda: _ALLOWED_MIME_TYPES)

    @property
    def allowed_extensions(self) -> tuple[str, ...]:
        """File extensions accepted by the uploader widget."""

        return tuple(self.allowed_mime_types.keys())

    @classmethod
    def load(cls) -> "AppConfig":
        """Build configuration from the environment, validating required keys.

        Raises
        ------
        ConfigurationError
            If no API key can be found.
        """

        api_key = _resolve_api_key()
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not configured.",
                hint=(
                    "Add GEMINI_API_KEY to a .env file in the project root, or to "
                    "Streamlit secrets when deploying. Get a key at "
                    "https://aistudio.google.com/app/apikeys."
                ),
            )

        return cls(
            api_key=api_key,
            model_name=os.getenv("GEMINI_MODEL", _DEFAULT_MODEL),
        )
