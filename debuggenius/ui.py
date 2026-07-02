"""Reusable presentation components.

Each function renders one cohesive piece of the interface. Domain logic lives
elsewhere — these functions only *render* (and read widget input).

Elements tagged with ``data-dg-anim`` (and ``.dg-chip``) are picked up by the
framer-motion bridge (:mod:`debuggenius.motion`) for entrance animations.
"""

from __future__ import annotations

import html
from dataclasses import dataclass

import streamlit as st

from .config import AppConfig
from .exceptions import DebugGeniusError
from .models import DebugMode, HistoryEntry
from .state import clear_history, get_history

APP_NAME = "DebugGenius"
APP_TAGLINE = "error analysis from screenshots"


@dataclass(frozen=True, slots=True)
class SidebarSelections:
    """What the user configured in the sidebar this run."""

    uploaded_file: object | None
    mode: DebugMode


# ─────────────────────────────  Hero  ──────────────────────────────


def render_hero(engine_label: str = "Ollama Vision") -> None:
    st.markdown(
        f"""
        <div class="dg-hero" data-dg-anim="rise">
          <span class="dg-hero__badge"><i></i>{html.escape(engine_label)}</span>
          <h1 class="dg-hero__title">{APP_NAME}</h1>
          <p class="dg-hero__lede">
            Upload a screenshot of an error — a stack trace, compiler output,
            a console full of red — and get back what broke, why it broke,
            and how to fix it, streamed live from the model.
          </p>
          <div class="dg-features">
            <span class="dg-chip">Any language</span>
            <span class="dg-chip">Screenshot in, fix out</span>
            <span class="dg-chip">Streaming answers</span>
            <span class="dg-chip">Markdown export</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _overline(number: str, title: str) -> None:
    st.markdown(
        f'<div class="dg-overline"><b>{number}</b>{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )


# ────────────────────────────  Sidebar  ────────────────────────────


def render_sidebar(config: AppConfig) -> SidebarSelections:
    """Render upload + mode controls and return the user's selections."""

    with st.sidebar:
        _overline("01", "Screenshot")
        uploaded_file = st.file_uploader(
            "Error screenshot",
            type=list(config.allowed_extensions),
            help="A clear screenshot of the error message or stack trace.",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

        st.markdown("")
        _overline("02", "Response depth")
        options = {m.label: m for m in DebugMode}
        chosen_label = st.radio(
            "Response depth",
            options=list(options.keys()),
            captions=[m.description for m in DebugMode],
            label_visibility="collapsed",
        )
        mode = options[chosen_label]

        _render_history_panel()

    return SidebarSelections(uploaded_file=uploaded_file, mode=mode)


def _render_history_panel() -> None:
    history = get_history()
    if not history:
        return

    st.markdown("")
    _overline("03", "Session log")
    st.markdown(
        '<div class="dg-log">'
        + "".join(_history_item_html(entry) for entry in history)
        + "</div>",
        unsafe_allow_html=True,
    )

    if st.button("Clear log", use_container_width=True, key="dg_clear_history"):
        clear_history()
        st.rerun()


def _history_item_html(entry: HistoryEntry) -> str:
    name = html.escape(entry.filename)
    return f"""
    <div>
      <div class="dg-log__row">
        <span class="dg-log__name" title="{name}">{name}</span>
        <span class="dg-log__dots"></span>
        <span class="dg-log__time">{entry.created_label}</span>
      </div>
      <span class="dg-log__mode">{html.escape(entry.mode.label.lower())}</span>
    </div>
    """


# ─────────────────────────  Main actions  ──────────────────────────


def render_primary_action(*, enabled: bool) -> bool:
    """Render the centered CTA. Returns ``True`` when clicked this run."""

    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        clicked = st.button(
            "Run analysis" if enabled else "Add a screenshot to begin",
            type="primary",
            use_container_width=True,
            disabled=not enabled,
            key="dg_analyze",
        )
    return clicked


# ─────────────────────────  Result states  ─────────────────────────


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="dg-empty" data-dg-anim="rise">
          <div class="dg-empty__title">No runs yet</div>
          <div>Add a screenshot in the left panel, choose how much help
          you want back, then run the analysis.</div>
          <div class="dg-empty__hint">accepts png · jpg · jpeg · webp</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def skeleton_html() -> str:
    """Return the shimmer-skeleton markup (for use inside a streaming slot)."""

    return """
        <div class="dg-skeleton w-40"></div>
        <div class="dg-skeleton w-90"></div>
        <div class="dg-skeleton w-70"></div>
        <div class="dg-skeleton w-90"></div>
        <div class="dg-skeleton w-40"></div>
    """


def result_card_header(entry_mode: DebugMode, filename: str) -> None:
    st.markdown(
        f"""
        <div class="dg-result-head">
          <span class="dg-result-head__title">Analysis</span>
          <span class="dg-result-head__meta">{html.escape(entry_mode.label.lower())}
          &nbsp;·&nbsp; {html.escape(filename)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_static_result(entry: HistoryEntry) -> None:
    """Render a previously completed result (e.g. after a rerun)."""

    with st.container(border=True):
        result_card_header(entry.mode, entry.filename)
        # Render stored Markdown directly so fenced code blocks (and their
        # built-in copy buttons) parse correctly — wrapping in raw HTML would
        # prevent CommonMark from parsing the content.
        st.markdown(entry.response)
        _render_result_actions(entry)


def _render_result_actions(entry: HistoryEntry) -> None:
    st.download_button(
        "Download as Markdown",
        data=entry.response,
        file_name=f"debuggenius-{entry.entry_id}.md",
        mime="text/markdown",
        key=f"dg_dl_{entry.entry_id}",
    )


def render_result_actions(entry: HistoryEntry) -> None:
    """Public wrapper so the entrypoint can attach actions to a fresh result."""

    _render_result_actions(entry)


# ───────────────────────────  Errors  ──────────────────────────────


def render_app_error(error: DebugGeniusError) -> None:
    """Render a friendly, actionable error block."""

    st.error(f"**{error.message}**")
    if error.hint:
        st.info(error.hint)


# ───────────────────────────  Footer  ──────────────────────────────


def render_footer(engine_label: str = "") -> None:
    engine = html.escape(engine_label) if engine_label else "Ollama"
    st.markdown(
        f"""
        <div class="dg-footer">
          <span>{APP_NAME} — {APP_TAGLINE}</span>
          <span>{engine} · screenshots are analyzed in memory, never stored</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
