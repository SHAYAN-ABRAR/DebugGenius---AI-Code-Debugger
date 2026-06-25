"""Tests for prompt construction."""

from __future__ import annotations

from debuggenius.models import DebugMode
from debuggenius.prompts import build_prompt


def test_hints_prompt_excludes_corrected_code():
    prompt = build_prompt(DebugMode.HINTS)
    assert "Quick Tips" in prompt
    assert "Corrected Code" not in prompt
    assert "Do NOT write the corrected code" in prompt


def test_solution_prompt_includes_corrected_code():
    prompt = build_prompt(DebugMode.SOLUTION)
    assert "Corrected Code" in prompt
    assert "Explanation of Fix" in prompt


def test_both_modes_share_preamble():
    hints = build_prompt(DebugMode.HINTS)
    solution = build_prompt(DebugMode.SOLUTION)
    assert "DebugGenius" in hints and "DebugGenius" in solution
    assert hints != solution
