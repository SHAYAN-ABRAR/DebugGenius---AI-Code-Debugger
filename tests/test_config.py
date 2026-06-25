"""Tests for configuration loading."""

from __future__ import annotations

import pytest

from debuggenius import config as config_module
from debuggenius.config import AppConfig
from debuggenius.exceptions import ConfigurationError


def test_load_raises_without_key(monkeypatch):
    monkeypatch.setattr(config_module, "_resolve_api_key", lambda: None)
    with pytest.raises(ConfigurationError) as exc_info:
        AppConfig.load()
    assert exc_info.value.hint  # actionable hint is present


def test_load_succeeds_with_key(monkeypatch):
    monkeypatch.setattr(config_module, "_resolve_api_key", lambda: "abc123")
    cfg = AppConfig.load()
    assert cfg.api_key == "abc123"
    assert cfg.model_name  # has a default


def test_model_override_from_env(monkeypatch):
    monkeypatch.setattr(config_module, "_resolve_api_key", lambda: "abc123")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-custom")
    cfg = AppConfig.load()
    assert cfg.model_name == "gemini-custom"


def test_allowed_extensions_match_mime_keys():
    cfg = AppConfig(api_key="k")
    assert set(cfg.allowed_extensions) == set(cfg.allowed_mime_types.keys())
    assert "png" in cfg.allowed_extensions
