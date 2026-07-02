"""Framer Motion bridge.

Streamlit renders Python, not React — so to animate the app with the real
``framer-motion`` package we inline its react-free DOM bundle
(``framer-motion/dist/dom.js``, vendored in ``assets/``) into a zero-height
component. Streamlit components are same-origin iframes, so the script can
reach ``window.parent.document`` and animate the app's own DOM:

* staggered entrances for the hero, chips, and glass cards (re-applied after
  every Streamlit rerun via a ``MutationObserver``);
* the aurora orbs in the backdrop, which drift on infinite mirrored tweens.

Every animated element also carries a pure-CSS reveal fallback (see
``theme.py``), so nothing can be left invisible if this bridge fails, and
``prefers-reduced-motion`` is honoured by skipping the whole show.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

_BUNDLE_PATH = Path(__file__).parent / "assets" / "framer-motion-dom.js"

_BRIDGE_JS = """
(function () {
  var win, doc;
  try { win = window.parent; doc = win.document; } catch (e) { return; }

  // Collapse our own host block so the invisible iframe leaves no gap.
  try {
    var host = window.frameElement &&
      window.frameElement.closest('div[data-testid="stElementContainer"]');
    if (host) host.style.display = 'none';
  } catch (e) { /* non-fatal */ }

  var M = window.Motion;
  if (!M || !M.animate || !doc || !doc.body) return;
  if (win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // A rerun remounts this iframe; retire the previous bridge's observer.
  if (win.__dgMotion && win.__dgMotion.observer) win.__dgMotion.observer.disconnect();
  var state = win.__dgMotion = { observer: null };

  var EASE = [0.22, 1, 0.36, 1];

  function rise(el, delay) {
    if (el.dataset.dgAnimated) return;
    el.dataset.dgAnimated = '1';
    try {
      M.animate(el,
        { opacity: [0, 1], transform: ['translateY(18px) scale(0.99)', 'translateY(0px) scale(1)'] },
        { duration: 0.7, delay: delay || 0, ease: EASE });
    } catch (e) { el.style.opacity = '1'; }
  }

  function drift(orb, i) {
    if (orb.dataset.dgDrift) return;
    orb.dataset.dgDrift = '1';
    var dx = (i % 2 ? -1 : 1) * (60 + i * 25);
    var dy = (i % 2 ? 1 : -1) * (45 + i * 15);
    try {
      M.animate(orb,
        { transform: ['translate(0px, 0px) scale(1)',
                      'translate(' + dx + 'px, ' + dy + 'px) scale(1.18)'] },
        { duration: 16 + i * 5, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' });
    } catch (e) { /* backdrop stays static — fine */ }
  }

  function sweep() {
    var rises = doc.querySelectorAll(
      '[data-dg-anim]:not([data-dg-animated]), ' +
      '[data-testid="stVerticalBlockBorderWrapper"]:not([data-dg-animated])');
    for (var i = 0; i < rises.length; i++) rise(rises[i], 0.04 * i);

    var chips = doc.querySelectorAll('.dg-chip:not([data-dg-animated])');
    for (var j = 0; j < chips.length; j++) rise(chips[j], 0.25 + j * 0.07);

    var orbs = doc.querySelectorAll('.dg-orb:not([data-dg-drift])');
    for (var k = 0; k < orbs.length; k++) drift(orbs[k], k);
  }

  sweep();

  // Streamlit swaps DOM nodes on every rerun — catch newcomers as they land.
  var pending = null;
  state.observer = new MutationObserver(function () {
    if (pending) return;
    pending = win.requestAnimationFrame(function () { pending = null; sweep(); });
  });
  state.observer.observe(doc.body, { childList: true, subtree: true });
})();
"""


@lru_cache(maxsize=1)
def _bridge_html() -> str:
    bundle = _BUNDLE_PATH.read_text(encoding="utf-8")
    return f"<script>{bundle}</script>\n<script>{_BRIDGE_JS}</script>"


def mount_motion() -> None:
    """Mount the invisible framer-motion bridge. Call once per script run."""

    if hasattr(components, "html"):
        # Proven to give the srcdoc iframe same-origin parent access.
        components.html(_bridge_html(), height=0)
    else:
        # ``components.v1.html`` is deprecated (removal announced for after
        # 2026-06-01); ``st.iframe`` is its replacement on newer Streamlit.
        st.iframe(f"<!DOCTYPE html><html><body>{_bridge_html()}</body></html>", height=1)
