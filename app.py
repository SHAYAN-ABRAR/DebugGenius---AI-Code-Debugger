"""DebugGenius — application entrypoint.

A deliberately thin orchestration layer: configure the page, apply the theme,
resolve config, and route user actions through the ``debuggenius`` package.

Run with::

    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from debuggenius import ui
from debuggenius.config import AppConfig
from debuggenius.exceptions import DebugGeniusError
from debuggenius.logging_setup import get_logger
from debuggenius.models import DebugRequest, HistoryEntry
from debuggenius.ollama_service import OllamaDebugger
from debuggenius.state import add_history, get_last_result, init_state
from debuggenius.theme import apply_theme
from debuggenius.validation import validate_image

logger = get_logger(__name__)

# ``set_page_config`` must be the first Streamlit command executed.
st.set_page_config(
    page_title="DebugGenius — AI Code Debugger",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def _build_ollama(
    host: str,
    model: str,
    temperature: float,
    timeout: int,
    retries: int,
    backoff: float,
    api_key: str | None,
) -> OllamaDebugger:
    """Cache the Ollama client across reruns (keyed on primitive settings)."""

    return OllamaDebugger(
        host=host,
        model=model,
        temperature=temperature,
        timeout=timeout,
        max_retries=retries,
        retry_backoff_seconds=backoff,
        api_key=api_key,
    )


def get_debugger(config: AppConfig) -> OllamaDebugger:
    """Return the cached Ollama client for the current configuration."""

    return _build_ollama(
        config.ollama_host,
        config.ollama_model,
        config.temperature,
        config.request_timeout,
        config.max_retries,
        config.retry_backoff_seconds,
        config.ollama_api_key,
    )


def run_analysis(
    debugger: OllamaDebugger, config: AppConfig, selections: ui.SidebarSelections
) -> None:
    """Validate the upload, stream the model's answer, and persist the result."""

    uploaded = selections.uploaded_file
    assert uploaded is not None  # guarded by the caller

    try:
        validated = validate_image(uploaded.getvalue(), uploaded.name, config)
    except DebugGeniusError as exc:
        ui.render_app_error(exc)
        return

    request = DebugRequest(
        image_bytes=validated.image_bytes,
        mime_type=validated.mime_type,
        mode=selections.mode,
        filename=uploaded.name,
    )

    with st.container(border=True):
        ui.result_card_header(selections.mode, uploaded.name)
        placeholder = st.empty()
        placeholder.markdown(
            f'<div>{ui.skeleton_html()}</div>', unsafe_allow_html=True
        )

        chunks: list[str] = []
        try:
            for chunk in debugger.analyze_stream(request):
                chunks.append(chunk)
                placeholder.markdown("".join(chunks) + " ▌")
        except DebugGeniusError as exc:
            placeholder.empty()
            logger.warning("Analysis failed: %s", exc.message)
            ui.render_app_error(exc)
            return

        full_text = "".join(chunks).strip()
        if not full_text:
            placeholder.empty()
            st.warning("The model returned an empty response. Please try again.")
            return

        placeholder.markdown(full_text)  # final render, without the cursor
        entry = HistoryEntry(
            filename=uploaded.name, mode=selections.mode, response=full_text
        )
        add_history(entry, max_items=config.max_history_items)
        ui.render_result_actions(entry)

    st.toast("Analysis complete", icon="✅")


def main() -> None:
    apply_theme()
    init_state()

    config = AppConfig.load()
    engine_label = f"Ollama · {config.ollama_model}"

    ui.render_hero(engine_label)
    st.markdown("")  # vertical breathing room

    selections = ui.render_sidebar(config)
    has_file = selections.uploaded_file is not None
    clicked = ui.render_primary_action(enabled=has_file)

    if clicked and has_file:
        run_analysis(get_debugger(config), config, selections)
    elif (last := get_last_result()) is not None:
        ui.render_static_result(last)
    else:
        ui.render_empty_state()

    ui.render_footer(engine_label)


if __name__ == "__main__":
    main()
