"""DebugGenius — an AI-powered code-error analyzer built on Streamlit + Ollama.

The package is organized into small, single-responsibility modules:

* :mod:`debuggenius.config`         – application settings & secret resolution.
* :mod:`debuggenius.models`         – typed domain models (enums / dataclasses).
* :mod:`debuggenius.exceptions`     – typed exception hierarchy.
* :mod:`debuggenius.validation`     – upload validation (pure, testable).
* :mod:`debuggenius.prompts`        – prompt construction (single source of truth).
* :mod:`debuggenius.ollama_service` – Ollama client wrapper (streaming + retries).
* :mod:`debuggenius.theme`          – the glassmorphism design system (CSS).
* :mod:`debuggenius.state`          – Streamlit session-state management.
* :mod:`debuggenius.ui`             – reusable presentation components.
"""

from __future__ import annotations

__all__ = ["__version__"]
__version__ = "3.0.0"
