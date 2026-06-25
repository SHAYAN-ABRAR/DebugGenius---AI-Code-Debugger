"""Tests for the domain models."""

from __future__ import annotations

import pytest

from debuggenius.models import DebugMode, HistoryEntry


def test_mode_label_roundtrip():
    for mode in DebugMode:
        assert DebugMode.from_label(mode.label) is mode


def test_mode_from_unknown_label_raises():
    with pytest.raises(ValueError):
        DebugMode.from_label("does-not-exist")


def test_mode_metadata_present():
    for mode in DebugMode:
        assert mode.icon and mode.label and mode.description


def test_history_entry_defaults():
    entry = HistoryEntry(filename="a.png", mode=DebugMode.HINTS, response="ok")
    assert len(entry.entry_id) == 8
    assert ":" in entry.created_label  # HH:MM


def test_history_entry_ids_are_unique():
    ids = {
        HistoryEntry(filename="f", mode=DebugMode.HINTS, response="r").entry_id
        for _ in range(50)
    }
    assert len(ids) == 50
