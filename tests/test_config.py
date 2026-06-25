"""Tests for configuration loading."""

from __future__ import annotations

from debuggenius.config import AppConfig


def test_defaults(monkeypatch):
    for var in ("OLLAMA_HOST", "OLLAMA_MODEL", "OLLAMA_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    cfg = AppConfig.load()
    assert cfg.ollama_host == "http://localhost:11434"
    assert cfg.ollama_model == "gemma4:31b-cloud"
    assert cfg.ollama_api_key is None


def test_overrides_from_env(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "https://ollama.com")
    monkeypatch.setenv("OLLAMA_MODEL", "llava:13b")
    monkeypatch.setenv("OLLAMA_API_KEY", "sk-test")
    cfg = AppConfig.load()
    assert cfg.ollama_host == "https://ollama.com"
    assert cfg.ollama_model == "llava:13b"
    assert cfg.ollama_api_key == "sk-test"


def test_allowed_extensions_match_mime_keys():
    cfg = AppConfig()
    assert set(cfg.allowed_extensions) == set(cfg.allowed_mime_types.keys())
    assert "png" in cfg.allowed_extensions
