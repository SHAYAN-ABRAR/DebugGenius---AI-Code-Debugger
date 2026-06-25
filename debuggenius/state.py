"""Streamlit session-state management.

Centralizes every ``st.session_state`` key behind small helpers so the rest of
the app never touches raw string keys. Keeps analysis history bounded.
"""

from __future__ import annotations

import streamlit as st

from .models import HistoryEntry

_HISTORY_KEY = "dg_history"
_LAST_RESULT_KEY = "dg_last_result"


def init_state() -> None:
    """Ensure all expected session-state keys exist. Idempotent."""

    st.session_state.setdefault(_HISTORY_KEY, [])
    st.session_state.setdefault(_LAST_RESULT_KEY, None)


def add_history(entry: HistoryEntry, *, max_items: int) -> None:
    """Prepend a completed analysis, trimming to ``max_items``."""

    history: list[HistoryEntry] = st.session_state[_HISTORY_KEY]
    history.insert(0, entry)
    del history[max_items:]
    st.session_state[_LAST_RESULT_KEY] = entry


def get_history() -> list[HistoryEntry]:
    return st.session_state.get(_HISTORY_KEY, [])


def get_last_result() -> HistoryEntry | None:
    return st.session_state.get(_LAST_RESULT_KEY)


def clear_history() -> None:
    st.session_state[_HISTORY_KEY] = []
    st.session_state[_LAST_RESULT_KEY] = None
