"""The DebugGenius glassmorphism design system.

A single injected stylesheet themes every Streamlit primitive used by the app:
frosted-glass surfaces, an animated aurora backdrop, the brand gradient
(#6C63FF → #8B5CF6), Inter typography, and tasteful micro-interactions.

Design tokens live in ``:root`` so the whole palette can be retuned in one place.
"""

from __future__ import annotations

import streamlit as st

_CSS = """
<style>
/* ─────────────────────────  Typography  ───────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─────────────────────────  Design tokens  ────────────────────── */
:root {
  --dg-primary: #6C63FF;
  --dg-accent: #8B5CF6;
  --dg-primary-rgb: 108, 99, 255;
  --dg-accent-rgb: 139, 92, 246;

  --dg-bg-0: #07070d;
  --dg-bg-1: #0d0d18;

  --dg-surface: rgba(255, 255, 255, 0.06);
  --dg-surface-strong: rgba(255, 255, 255, 0.09);
  --dg-border: rgba(255, 255, 255, 0.14);
  --dg-border-strong: rgba(255, 255, 255, 0.22);

  --dg-text: #f4f5fb;
  --dg-text-muted: #a4a7bd;
  --dg-text-faint: #6f7290;

  --dg-success: #34d399;
  --dg-danger: #fb7185;
  --dg-warning: #fbbf24;

  --dg-radius-lg: 24px;
  --dg-radius-md: 16px;
  --dg-radius-sm: 12px;

  --dg-shadow-soft: 0 10px 40px rgba(0, 0, 0, 0.35);
  --dg-shadow-glow: 0 8px 32px rgba(var(--dg-primary-rgb), 0.28);
  --dg-blur: 22px;

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Courier New', monospace;
}

/* ─────────────────────────  Base / backdrop  ──────────────────── */
html, body, [class*="css"] { font-family: var(--font-sans); }

.stApp {
  background:
    radial-gradient(1200px 600px at 12% -8%, rgba(var(--dg-primary-rgb), 0.20), transparent 60%),
    radial-gradient(1000px 700px at 100% 0%, rgba(var(--dg-accent-rgb), 0.18), transparent 55%),
    linear-gradient(160deg, var(--dg-bg-0) 0%, var(--dg-bg-1) 100%);
  background-attachment: fixed;
  color: var(--dg-text);
}

/* Slow drifting aurora that lives behind everything. */
.stApp::before {
  content: "";
  position: fixed;
  inset: -20% -10% -10% -10%;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(520px 520px at 20% 30%, rgba(var(--dg-primary-rgb), 0.16), transparent 70%),
    radial-gradient(560px 560px at 80% 70%, rgba(var(--dg-accent-rgb), 0.14), transparent 70%);
  filter: blur(40px);
  animation: dg-aurora 22s ease-in-out infinite alternate;
}

@keyframes dg-aurora {
  0%   { transform: translate3d(0, 0, 0) scale(1); }
  100% { transform: translate3d(2%, -2%, 0) scale(1.08); }
}

/* Keep Streamlit's header out of the way but transparent. */
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 1rem; }
#MainMenu, footer { visibility: hidden; }

.block-container {
  position: relative;
  z-index: 1;
  padding-top: 2.4rem;
  padding-bottom: 4rem;
  max-width: 1180px;
}

/* ─────────────────────────  Sidebar (frosted)  ────────────────── */
[data-testid="stSidebar"] > div:first-child {
  background: rgba(13, 13, 24, 0.55);
  backdrop-filter: blur(var(--dg-blur));
  -webkit-backdrop-filter: blur(var(--dg-blur));
  border-right: 1px solid var(--dg-border);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

/* ─────────────────────────  Glass cards  ──────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--dg-surface);
  backdrop-filter: blur(var(--dg-blur));
  -webkit-backdrop-filter: blur(var(--dg-blur));
  border: 1px solid var(--dg-border) !important;
  border-radius: var(--dg-radius-lg) !important;
  box-shadow: var(--dg-shadow-soft);
}

.dg-card {
  background: var(--dg-surface);
  backdrop-filter: blur(var(--dg-blur));
  -webkit-backdrop-filter: blur(var(--dg-blur));
  border: 1px solid var(--dg-border);
  border-radius: var(--dg-radius-lg);
  box-shadow: var(--dg-shadow-soft);
  padding: 1.5rem 1.6rem;
}

/* ─────────────────────────  Hero  ─────────────────────────────── */
.dg-hero {
  display: flex; flex-direction: column; gap: 0.55rem;
  padding: 2.1rem 2.2rem;
  border-radius: var(--dg-radius-lg);
  border: 1px solid var(--dg-border);
  background:
    linear-gradient(135deg, rgba(var(--dg-primary-rgb), 0.18), rgba(var(--dg-accent-rgb), 0.10)),
    var(--dg-surface);
  backdrop-filter: blur(var(--dg-blur));
  -webkit-backdrop-filter: blur(var(--dg-blur));
  box-shadow: var(--dg-shadow-glow);
  overflow: hidden;
  position: relative;
  animation: dg-fade-up 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.dg-hero::after {  /* subtle glass reflection sweep */
  content: ""; position: absolute; top: 0; left: -40%;
  width: 40%; height: 100%;
  background: linear-gradient(105deg, transparent, rgba(255,255,255,0.10), transparent);
  transform: skewX(-18deg);
  animation: dg-sheen 7s ease-in-out 1.2s infinite;
}
.dg-hero__badge {
  align-self: flex-start;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #d7d4ff;
  padding: 0.3rem 0.7rem; border-radius: 999px;
  border: 1px solid var(--dg-border-strong);
  background: rgba(var(--dg-primary-rgb), 0.18);
}
.dg-hero__title {
  font-size: 2.5rem; font-weight: 800; line-height: 1.05; margin: 0.2rem 0 0;
  background: linear-gradient(100deg, #ffffff 10%, #c9c4ff 55%, var(--dg-accent) 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.dg-hero__subtitle { color: var(--dg-text-muted); font-size: 1.05rem; max-width: 56ch; }

/* ─────────────────────────  Feature chips  ────────────────────── */
.dg-features { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.4rem; }
.dg-chip {
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-size: 0.82rem; color: var(--dg-text-muted);
  padding: 0.4rem 0.8rem; border-radius: 999px;
  background: var(--dg-surface-strong); border: 1px solid var(--dg-border);
}

/* ─────────────────────────  Empty state  ──────────────────────── */
.dg-empty {
  text-align: center; padding: 3.2rem 1.5rem;
  border: 1px dashed var(--dg-border-strong); border-radius: var(--dg-radius-lg);
  background: var(--dg-surface); color: var(--dg-text-muted);
  animation: dg-fade-up 0.5s ease both;
}
.dg-empty__icon { font-size: 2.6rem; opacity: 0.9; }
.dg-empty__title { color: var(--dg-text); font-size: 1.2rem; font-weight: 700; margin: 0.6rem 0 0.3rem; }

/* ─────────────────────────  Buttons  ──────────────────────────── */
.stButton > button, .stDownloadButton > button {
  border-radius: var(--dg-radius-sm);
  border: 1px solid var(--dg-border);
  background: var(--dg-surface-strong);
  color: var(--dg-text);
  font-weight: 600;
  padding: 0.55rem 1.1rem;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-2px);
  border-color: var(--dg-border-strong);
  background: rgba(var(--dg-primary-rgb), 0.16);
}
.stButton > button:active, .stDownloadButton > button:active { transform: translateY(0); }

/* Primary CTA (type="primary"). */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--dg-primary), var(--dg-accent));
  border: none; color: #fff;
  box-shadow: var(--dg-shadow-glow);
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 38px rgba(var(--dg-primary-rgb), 0.45);
}

/* ─────────────────────────  File uploader  ────────────────────── */
[data-testid="stFileUploaderDropzone"] {
  background: var(--dg-surface);
  border: 1.5px dashed var(--dg-border-strong);
  border-radius: var(--dg-radius-md);
  transition: border-color 0.2s ease, background 0.2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--dg-primary);
  background: rgba(var(--dg-primary-rgb), 0.08);
}

/* ─────────────────────────  Radio as cards  ───────────────────── */
[data-testid="stRadio"] > div { gap: 0.5rem; }
[data-testid="stRadio"] label {
  background: var(--dg-surface); border: 1px solid var(--dg-border);
  border-radius: var(--dg-radius-sm); padding: 0.6rem 0.8rem;
  transition: border-color 0.18s ease, background 0.18s ease;
}
[data-testid="stRadio"] label:hover {
  border-color: var(--dg-border-strong);
  background: var(--dg-surface-strong);
}

/* ─────────────────────────  Code & markdown  ──────────────────── */
.stMarkdown pre, .stCode, pre {
  background: rgba(7, 7, 13, 0.7) !important;
  border: 1px solid var(--dg-border);
  border-radius: var(--dg-radius-md) !important;
  font-family: var(--font-mono);
}
.stMarkdown code { font-family: var(--font-mono); }
.dg-result h1, .dg-result h2, .dg-result h3 { color: #ffffff; }
.dg-result { animation: dg-fade-up 0.4s ease both; }

/* ─────────────────────────  Alerts / toast  ───────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--dg-radius-md);
  backdrop-filter: blur(8px);
}
[data-testid="stToast"] {
  border-radius: var(--dg-radius-md);
  border: 1px solid var(--dg-border);
  backdrop-filter: blur(var(--dg-blur));
}

/* ─────────────────────────  History items  ────────────────────── */
.dg-history-item {
  display: flex; flex-direction: column; gap: 0.15rem;
  padding: 0.6rem 0.8rem; border-radius: var(--dg-radius-sm);
  border: 1px solid var(--dg-border); background: var(--dg-surface);
  margin-bottom: 0.5rem;
}
.dg-history-item__top { display: flex; justify-content: space-between; font-size: 0.8rem; }
.dg-history-item__name { color: var(--dg-text); font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 11rem; }
.dg-history-item__time { color: var(--dg-text-faint); }
.dg-history-item__mode { color: var(--dg-text-muted); font-size: 0.76rem; }

/* ─────────────────────────  Skeleton loader  ──────────────────── */
.dg-skeleton {
  height: 14px; border-radius: 8px; margin: 0.55rem 0;
  background: linear-gradient(90deg, var(--dg-surface) 25%, var(--dg-surface-strong) 37%, var(--dg-surface) 63%);
  background-size: 400% 100%;
  animation: dg-shimmer 1.4s ease-in-out infinite;
}
.dg-skeleton.w-40 { width: 40%; } .dg-skeleton.w-70 { width: 70%; } .dg-skeleton.w-90 { width: 90%; }

/* ─────────────────────────  Scrollbar  ────────────────────────── */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--dg-surface-strong); border-radius: 999px;
  border: 2px solid transparent; background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover { background: rgba(var(--dg-primary-rgb), 0.5); background-clip: content-box; }

/* ─────────────────────────  Keyframes  ────────────────────────── */
@keyframes dg-fade-up { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes dg-shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
@keyframes dg-sheen { 0%, 60% { left: -40%; } 85%, 100% { left: 140%; } }

/* Respect reduced-motion preferences. */
@media (prefers-reduced-motion: reduce) {
  .stApp::before, .dg-hero::after, .dg-skeleton { animation: none; }
  .dg-hero, .dg-empty, .dg-result { animation: none; }
}
</style>
"""


def apply_theme() -> None:
    """Inject the global stylesheet. Call once, right after ``set_page_config``."""

    st.markdown(_CSS, unsafe_allow_html=True)
