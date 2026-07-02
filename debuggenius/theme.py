"""The DebugGenius glassmorphism design system.

A single injected stylesheet themes every Streamlit primitive the app uses:
deep-space backdrop with drifting aurora orbs and film grain, frosted-glass
surfaces with gradient hairline borders, a violet→sky duotone, Manrope
display type, and JetBrains Mono for anything machine-adjacent.

Motion is driven by the framer-motion bridge (:mod:`debuggenius.motion`);
every element it animates also has a pure-CSS reveal fallback here, so the
page can never be left blank, and ``prefers-reduced-motion`` is respected.

Design tokens live in ``:root`` so the palette can be retuned in one place.
"""

from __future__ import annotations

import streamlit as st

_NOISE_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' "
    "height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' "
    "baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix "
    "type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' "
    "height='100%25' filter='url(%23n)' opacity='0.3'/%3E%3C/svg%3E"
)

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Tokens ─────────────────────────────────────────────────────── */
:root {{
  --violet: #7c6cff;
  --sky:    #38bdf8;
  --violet-rgb: 124, 108, 255;
  --sky-rgb:    56, 189, 248;

  --bg-0: #070810;
  --bg-1: #0b0d1a;

  --glass:        rgba(255, 255, 255, 0.05);
  --glass-strong: rgba(255, 255, 255, 0.085);
  --stroke:        rgba(255, 255, 255, 0.10);
  --stroke-strong: rgba(255, 255, 255, 0.20);

  --text:       #eef0fa;
  --text-muted: #9ba0bc;
  --text-faint: #666b8a;

  --ok:  #34d399;
  --err: #fb7185;

  --r-lg: 24px;
  --r-md: 14px;
  --r-sm: 10px;

  --blur: 22px;
  --shadow: 0 24px 60px rgba(3, 4, 11, 0.55);
  --inner-light: inset 0 1px 0 rgba(255, 255, 255, 0.09);
  --glow: 0 10px 34px rgba(var(--violet-rgb), 0.30);

  --sans: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --mono: 'JetBrains Mono', ui-monospace, 'Cascadia Mono', Consolas, monospace;
}}

/* ── Base / backdrop ────────────────────────────────────────────── */
html, body, [class*="css"] {{ font-family: var(--sans); }}

.stApp {{
  background:
    radial-gradient(1100px 520px at 12% -10%, rgba(var(--violet-rgb), 0.16), transparent 60%),
    radial-gradient(950px 620px at 108% 4%, rgba(var(--sky-rgb), 0.12), transparent 55%),
    linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 55%, var(--bg-0) 100%);
  background-attachment: fixed;
  color: var(--text);
}}

/* Aurora orbs — real elements so the framer-motion bridge can drive them. */
.dg-orb {{
  position: fixed; border-radius: 50%;
  filter: blur(90px); pointer-events: none; z-index: 0;
}}
.dg-orb--a {{
  width: 480px; height: 480px; left: -140px; top: -100px;
  background: radial-gradient(circle at 32% 32%, rgba(var(--violet-rgb), 0.34), transparent 70%);
}}
.dg-orb--b {{
  width: 420px; height: 420px; right: -150px; top: 18%;
  background: radial-gradient(circle at 60% 40%, rgba(var(--sky-rgb), 0.26), transparent 70%);
}}
.dg-orb--c {{
  width: 380px; height: 380px; left: 30%; bottom: -180px;
  background: radial-gradient(circle at 50% 50%, rgba(217, 70, 239, 0.14), transparent 70%);
}}

/* Film grain — kills the flat, too-clean look. */
.dg-noise {{
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image: url("{_NOISE_SVG}");
  opacity: 0.35; mix-blend-mode: overlay;
}}

[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stToolbar"] {{ right: 1rem; }}
#MainMenu, footer {{ visibility: hidden; }}

.block-container {{
  position: relative; z-index: 1;
  padding-top: 2.4rem; padding-bottom: 4rem;
  max-width: 1140px;
}}

::selection {{ background: rgba(var(--violet-rgb), 0.35); }}
:focus-visible {{ outline: 2px solid var(--sky); outline-offset: 2px; }}

h1, h2, h3, h4 {{ color: var(--text); letter-spacing: -0.015em; }}
a {{ color: var(--sky); }}

/* Hide the zero-height framer-motion bridge iframe's slot. */
div[data-testid="stElementContainer"]:has(> iframe[height="0"]) {{ display: none; }}

/* ── Motion fallback ────────────────────────────────────────────────
   The bridge animates these from opacity 0; this guarantees they appear
   even if it never runs. Inline styles set by framer-motion win over the
   base rule, so there is no flash and no double-animation. */
[data-dg-anim], .dg-chip, [data-testid="stVerticalBlockBorderWrapper"] {{
  opacity: 0;
  animation: dg-reveal 0.01s linear 1.1s forwards;
}}
@keyframes dg-reveal {{ to {{ opacity: 1; }} }}

/* ── Glass hero ─────────────────────────────────────────────────── */
.dg-hero {{
  position: relative; overflow: hidden;
  display: flex; flex-direction: column; gap: 0.6rem;
  padding: 2.3rem 2.4rem;
  border-radius: var(--r-lg);
  border: 1px solid transparent;
  background:
    linear-gradient(rgba(255,255,255,0.055), rgba(255,255,255,0.028)) padding-box,
    linear-gradient(135deg, rgba(var(--violet-rgb), 0.55), rgba(255,255,255,0.07) 45%, rgba(var(--sky-rgb), 0.45)) border-box;
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  box-shadow: var(--inner-light), var(--shadow);
}}
.dg-hero__badge {{
  align-self: flex-start;
  display: inline-flex; align-items: center; gap: 0.5rem;
  font-family: var(--mono); font-size: 0.7rem; font-weight: 500;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: #cfd2ee;
  padding: 0.34rem 0.75rem; border-radius: 999px;
  border: 1px solid var(--stroke-strong);
  background: var(--glass-strong);
}}
.dg-hero__badge i {{
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--ok);
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.9);
  animation: dg-pulse 2.4s ease-in-out infinite;
}}
.dg-hero__title {{
  margin: 0.3rem 0 0;
  font-size: clamp(2.1rem, 4.5vw, 2.9rem); font-weight: 800; line-height: 1.04;
  letter-spacing: -0.03em;
  background: linear-gradient(95deg, #ffffff 12%, #c9c6ff 55%, #7dd3fc 96%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.dg-hero__lede {{
  color: var(--text-muted); font-size: 1.06rem; line-height: 1.6; max-width: 58ch;
}}

/* ── Chips ──────────────────────────────────────────────────────── */
.dg-features {{ display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.5rem; }}
.dg-chip {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  font-size: 0.82rem; font-weight: 500; color: var(--text-muted);
  padding: 0.42rem 0.85rem; border-radius: 999px;
  background: var(--glass); border: 1px solid var(--stroke);
  backdrop-filter: blur(10px);
}}
.dg-chip::before {{
  content: ""; width: 6px; height: 6px; border-radius: 50%;
  background: linear-gradient(135deg, var(--violet), var(--sky));
}}

/* ── Sidebar ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background: rgba(9, 11, 22, 0.62);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border-right: 1px solid var(--stroke);
}}
[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}

/* Numbered section labels, set in mono like a checklist. */
.dg-overline {{
  font-family: var(--mono); font-size: 0.68rem; font-weight: 600;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--text-muted);
  display: flex; align-items: center; gap: 0.55rem;
  margin: 0.5rem 0 0.75rem;
}}
.dg-overline b {{
  font-weight: 600;
  background: linear-gradient(135deg, var(--violet), var(--sky));
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.dg-overline::after {{ content: ""; flex: 1; border-top: 1px solid var(--stroke); }}

/* ── Glass cards (st.container(border=True)) ────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--glass);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border: 1px solid var(--stroke) !important;
  border-radius: var(--r-lg) !important;
  box-shadow: var(--inner-light), var(--shadow);
}}

/* ── Result card header ─────────────────────────────────────────── */
.dg-result-head {{
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 1rem; flex-wrap: wrap;
  padding-bottom: 0.65rem; margin-bottom: 0.3rem;
  border-bottom: 1px solid var(--stroke);
}}
.dg-result-head__title {{ font-size: 1.05rem; font-weight: 700; }}
.dg-result-head__meta {{
  font-family: var(--mono); font-size: 0.72rem; color: var(--text-faint);
}}

/* ── Empty state ────────────────────────────────────────────────── */
.dg-empty {{
  text-align: center; padding: 3rem 1.6rem;
  border: 1px dashed var(--stroke-strong); border-radius: var(--r-lg);
  background: var(--glass);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  color: var(--text-muted);
}}
.dg-empty__title {{ color: var(--text); font-size: 1.15rem; font-weight: 700; margin-bottom: 0.4rem; }}
.dg-empty__hint {{
  font-family: var(--mono); font-size: 0.72rem; color: var(--text-faint);
  margin-top: 1.1rem;
}}

/* ── Buttons ────────────────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {{
  font-family: var(--sans); font-weight: 600; font-size: 0.9rem;
  border-radius: var(--r-sm);
  border: 1px solid var(--stroke);
  background: var(--glass-strong); color: var(--text);
  padding: 0.55rem 1.1rem;
  backdrop-filter: blur(10px);
  transition: transform 0.18s ease, box-shadow 0.18s ease,
              border-color 0.18s ease, background 0.18s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  transform: translateY(-2px);
  border-color: var(--stroke-strong);
  background: rgba(var(--violet-rgb), 0.16);
  color: var(--text);
}}
.stButton > button:active, .stDownloadButton > button:active {{ transform: translateY(0); }}

.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, var(--violet), #5ea0f5 60%, var(--sky));
  border: none; color: #fff;
  box-shadow: var(--glow);
}}
.stButton > button[kind="primary"]:hover {{
  transform: translateY(-2px);
  box-shadow: 0 14px 42px rgba(var(--violet-rgb), 0.45);
}}
.stButton > button[kind="primary"]:disabled {{
  background: var(--glass-strong); color: var(--text-faint);
  box-shadow: none; border: 1px solid var(--stroke);
}}

/* ── File uploader ──────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {{
  background: var(--glass);
  border: 1.5px dashed var(--stroke-strong);
  border-radius: var(--r-md);
  backdrop-filter: blur(10px);
  transition: border-color 0.2s ease, background 0.2s ease;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
  border-color: var(--violet);
  background: rgba(var(--violet-rgb), 0.08);
}}
[data-testid="stFileUploaderDropzone"] button {{
  border: 1px solid var(--stroke-strong); border-radius: var(--r-sm);
  background: var(--glass-strong); color: var(--text);
}}

/* ── Radio as glass rows ────────────────────────────────────────── */
[data-testid="stRadio"] > div {{ gap: 0.5rem; }}
[data-testid="stRadio"] label {{
  background: var(--glass); border: 1px solid var(--stroke);
  border-radius: var(--r-sm); padding: 0.6rem 0.8rem;
  transition: border-color 0.18s ease, background 0.18s ease;
}}
[data-testid="stRadio"] label:hover {{
  border-color: var(--stroke-strong);
  background: var(--glass-strong);
}}
[data-testid="stRadio"] label p {{ font-weight: 600; color: var(--text); }}
[data-testid="stCaptionContainer"] p {{ color: var(--text-faint); font-size: 0.8rem; }}

/* ── Code & markdown ────────────────────────────────────────────── */
.stMarkdown pre, .stCode, pre {{
  background: rgba(4, 5, 12, 0.72) !important;
  border: 1px solid var(--stroke);
  border-radius: var(--r-md) !important;
  font-family: var(--mono);
}}
.stMarkdown code {{
  font-family: var(--mono); font-size: 0.85em;
  background: rgba(var(--violet-rgb), 0.14); color: #cfc9ff;
  padding: 0.1em 0.35em; border-radius: 5px;
}}
.stMarkdown pre code {{ background: transparent; color: #e6e8f5; }}

/* ── Alerts / toast ─────────────────────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: var(--r-md);
  border: 1px solid var(--stroke);
  background: var(--glass);
  backdrop-filter: blur(10px);
}}
[data-testid="stToast"] {{
  border-radius: var(--r-md);
  border: 1px solid var(--stroke-strong);
  background: rgba(11, 13, 26, 0.85);
  backdrop-filter: blur(var(--blur));
  font-family: var(--mono); font-size: 0.8rem; color: var(--text);
}}

/* ── History rows (dotted leaders, like a table of contents) ────── */
.dg-log {{ margin-bottom: 0.6rem; }}
.dg-log__row {{
  display: flex; align-items: baseline; gap: 0.5rem;
  padding: 0.34rem 0;
  font-size: 0.82rem;
}}
.dg-log__name {{
  color: var(--text); font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 10.5rem;
}}
.dg-log__dots {{ flex: 1; border-bottom: 1px dotted rgba(255, 255, 255, 0.22); }}
.dg-log__time {{ font-family: var(--mono); font-size: 0.7rem; color: var(--text-faint); }}
.dg-log__mode {{
  display: block; font-family: var(--mono); font-size: 0.68rem;
  color: var(--text-faint); margin-top: -0.1rem;
}}

/* ── Skeleton loader ────────────────────────────────────────────── */
.dg-skeleton {{
  height: 14px; border-radius: 8px; margin: 0.55rem 0;
  background: linear-gradient(90deg, var(--glass) 25%, var(--glass-strong) 37%, var(--glass) 63%);
  background-size: 400% 100%;
  animation: dg-shimmer 1.4s ease-in-out infinite;
}}
.dg-skeleton.w-40 {{ width: 40%; }} .dg-skeleton.w-70 {{ width: 70%; }} .dg-skeleton.w-90 {{ width: 90%; }}

/* ── Footer ─────────────────────────────────────────────────────── */
.dg-footer {{
  margin-top: 3.2rem; padding-top: 1.1rem;
  border-top: 1px solid var(--stroke);
  font-family: var(--mono); font-size: 0.7rem; color: var(--text-faint);
  display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
}}

/* ── Scrollbar ──────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
  background: var(--glass-strong); border-radius: 999px;
  border: 2px solid transparent; background-clip: content-box;
}}
::-webkit-scrollbar-thumb:hover {{
  background: rgba(var(--violet-rgb), 0.5); background-clip: content-box;
}}

/* ── Keyframes ──────────────────────────────────────────────────── */
@keyframes dg-shimmer {{ 0% {{ background-position: 100% 0; }} 100% {{ background-position: -100% 0; }} }}
@keyframes dg-pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.45; }} }}

@media (prefers-reduced-motion: reduce) {{
  [data-dg-anim], .dg-chip, [data-testid="stVerticalBlockBorderWrapper"] {{
    animation-delay: 0s;
  }}
  .dg-skeleton, .dg-hero__badge i {{ animation: none; }}
  * {{ transition: none !important; }}
}}
</style>

<div class="dg-orb dg-orb--a"></div>
<div class="dg-orb dg-orb--b"></div>
<div class="dg-orb dg-orb--c"></div>
<div class="dg-noise"></div>
"""


def apply_theme() -> None:
    """Inject the global stylesheet + backdrop. Call once, right after
    ``set_page_config``."""

    st.markdown(_CSS, unsafe_allow_html=True)
