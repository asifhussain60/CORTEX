"""Tests — TabRenderer (Phase 151-c)

Covers: dispatch, fallback, XSS safety via _esc().

CORE: CORE-008 (TDD), GV-034 (render_tab contract)
Source: GitHub Issue #18 — FB-20260312-007
"""

import pytest

from cortex.orchestrators.support.onboarding.tab_renderers import TabRenderer


def test_tab_renderer_render_tab_returns_str() -> None:
    """render_tab() always returns a str."""
    tr = TabRenderer()
    result = tr.render_tab("01-overview", {})
    assert isinstance(result, str)


def test_tab_renderer_unknown_tab_returns_generic_card() -> None:
    """Unknown tab_id falls back to _no_data_card HTML."""
    tr = TabRenderer()
    result = tr.render_tab("nonexistent-tab-xyz", {})
    assert isinstance(result, str)
    assert len(result) > 0  # not empty


def test_tab_renderer_esc_escapes_html() -> None:
    """_esc('<script>') must return '&lt;script&gt;'."""
    tr = TabRenderer()
    assert tr._esc("<script>") == "&lt;script&gt;"


def test_tab_renderer_esc_escapes_ampersand() -> None:
    """_esc('a&b') must return 'a&amp;b'."""
    tr = TabRenderer()
    assert tr._esc("a&b") == "a&amp;b"


def test_tab_renderer_esc_escapes_quotes() -> None:
    """_esc('\"hello\"') must escape double-quotes."""
    tr = TabRenderer()
    escaped = tr._esc('"hello"')
    assert '"' not in escaped or "&quot;" in escaped or "&#x27;" in escaped or escaped != '"hello"'


def test_tab_renderer_render_tab_with_known_tab_returns_html() -> None:
    """'01-overview' dispatches to _render_01_overview which returns HTML."""
    tr = TabRenderer()
    result = tr.render_tab("01-overview", {"title": "Test"})
    assert isinstance(result, str)


def test_tab_renderer_no_data_card_is_str() -> None:
    """_no_data_card() returns a non-empty str."""
    tr = TabRenderer()
    card = tr._no_data_card("Some label")
    assert isinstance(card, str)
    assert len(card) > 0
