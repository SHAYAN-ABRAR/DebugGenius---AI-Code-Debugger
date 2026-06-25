"""Tests for configuration loading."""

from __future__ import annotations

import pytest

from debuggenius import config as config_module
from debuggenius.config import PROVIDER_GEMINI, PROVIDER_OLLAMA, AppConfig
from debuggenius.exceptions import ConfigurationError


def test_default_provider_is_ollama_and_needs_no_key(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.setattr(config_module, "_resolve_api_key", lambda: None)
    cfg = AppConfig.load()
    assert cfg.provider == PROVIDER_OLLAMA
    assert cfg.active_model == cfg.ollama_model


def test_gemini_without_key_raises(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    monkeypatch.setattr(config_module, "_resolve_api_key", lambda: None)
    with pytest.raises(ConfigurationError) as exc_info:
        AppConfig.load()
    assert exc_info.value.hint  # actionable hint is present


def test_gemini_with_key_succeeds(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    monkeypatch.setattr(config_module, "_resolve_api_key", lambda: "abc123")
    cfg = AppConfig.load()
    assert cfg.provider == PROVIDER_GEMINI
    assert cfg.api_key == "abc123"
    assert cfg.active_model == cfg.model_name


def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "bananas")
    with pytest.raises(ConfigurationError):
        AppConfig.load()


def test_ollama_overrides_from_env(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llava:13b")
    monkeypatch.setenv("OLLAMA_HOST", "http://example:1234")
    cfg = AppConfig.load()
    assert cfg.ollama_model == "llava:13b"
    assert cfg.ollama_host == "http://example:1234"


def test_gemini_model_override_from_env(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    monkeypatch.setattr(config_module, "_resolve_api_key", lambda: "abc123")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-custom")
    cfg = AppConfig.load()
    assert cfg.model_name == "gemini-custom"


def test_allowed_extensions_match_mime_keys():
    cfg = AppConfig()
    assert set(cfg.allowed_extensions) == set(cfg.allowed_mime_types.keys())
    assert "png" in cfg.allowed_extensions
