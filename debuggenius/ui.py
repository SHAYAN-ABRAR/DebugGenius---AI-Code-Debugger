"""Reusable presentation components.

Each function renders one cohesive piece of the interface. Domain logic lives
elsewhere — these functions only *render* (and read widget input).
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
APP_TAGLINE = "AI-powered code-error analysis"


@dataclass(frozen=True, slots=True)
class SidebarSelections:
    """What the user configured in the sidebar this run."""

    uploaded_file: object | None
    mode: DebugMode


# ─────────────────────────────  Hero  ──────────────────────────────


def render_hero(engine_label: str = "AI Vision") -> None:
    st.markdown(
        f"""
        <div class="dg-hero">
          <span class="dg-hero__badge">⚡ {html.escape(engine_label)}</span>
          <h1 class="dg-hero__title">{APP_NAME}</h1>
          <p class="dg-hero__subtitle">
            Drop in a screenshot of any error or stack trace and get an instant,
            structured explanation — root cause, fix, and the corrected code.
          </p>
          <div class="dg-features">
            <span class="dg-chip">🧠 Any language</span>
            <span class="dg-chip">🖼️ Screenshot in</span>
            <span class="dg-chip">⚡ Streaming answers</span>
            <span class="dg-chip">📋 One-click copy</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ────────────────────────────  Sidebar  ────────────────────────────


def render_sidebar(config: AppConfig) -> SidebarSelections:
    """Render upload + mode controls and return the user's selections."""

    with st.sidebar:
        st.markdown("### 📤 Upload error screenshot")
        uploaded_file = st.file_uploader(
            "Drag a PNG/JPG/WEBP of your error here",
            type=list(config.allowed_extensions),
            help="A clear screenshot of the error message or stack trace.",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

        st.markdown("### 🎚️ Debug mode")
        options = {f"{m.icon}  {m.label}": m for m in DebugMode}
        chosen_label = st.radio(
            "Debug mode",
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

    st.markdown("### 🕑 This session")
    for entry in history:
        st.markdown(_history_item_html(entry), unsafe_allow_html=True)

    if st.button("Clear history", use_container_width=True, key="dg_clear_history"):
        clear_history()
        st.rerun()


def _history_item_html(entry: HistoryEntry) -> str:
    name = html.escape(entry.filename)
    return f"""
    <div class="dg-history-item">
      <div class="dg-history-item__top">
        <span class="dg-history-item__name">{name}</span>
        <span class="dg-history-item__time">{entry.created_label}</span>
      </div>
      <span class="dg-history-item__mode">{entry.mode.icon} {html.escape(entry.mode.label)}</span>
    </div>
    """


# ─────────────────────────  Main actions  ──────────────────────────


def render_primary_action(*, enabled: bool) -> bool:
    """Render the centered CTA. Returns ``True`` when clicked this run."""

    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        clicked = st.button(
            "🚀 Analyze error" if enabled else "⬅ Upload a screenshot to start",
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
        <div class="dg-empty">
          <div class="dg-empty__icon">🪄</div>
          <div class="dg-empty__title">No analysis yet</div>
          <div>Upload an error screenshot and hit <b>Analyze error</b> to begin.</div>
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


def render_skeleton() -> None:
    st.markdown(f'<div class="dg-card">{skeleton_html()}</div>', unsafe_allow_html=True)


def result_card_header(entry_mode: DebugMode, filename: str) -> None:
    st.markdown(
        f"#### ✅ Analysis · {entry_mode.icon} {entry_mode.label} "
        f"<span style='color:var(--dg-text-faint);font-weight:400'>· "
        f"{html.escape(filename)}</span>",
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
        "⬇️ Download as Markdown",
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
        st.info(f"💡 {error.hint}")


def render_config_error(error: DebugGeniusError) -> None:
    """Full-page configuration error (shown when the app can't start)."""

    render_hero()
    st.markdown("###")
    with st.container(border=True):
        st.error(f"**{error.message}**")
        if error.hint:
            st.info(f"💡 {error.hint}")
        st.code("GEMINI_API_KEY=your_api_key_here", language="bash")


# ───────────────────────────  Footer  ──────────────────────────────


def render_footer(engine_label: str = "") -> None:
    engine = f" · {html.escape(engine_label)}" if engine_label else ""
    st.markdown(
        f"""
        <div style="text-align:center;color:var(--dg-text-faint);
                    font-size:0.85rem;margin-top:3rem;">
          {APP_NAME} · {APP_TAGLINE}{engine}
        </div>
        """,
        unsafe_allow_html=True,
    )
