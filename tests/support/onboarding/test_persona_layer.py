"""Tests — PersonaLayer (Phase 151-c)

Covers: adapt() semantics, fail-safe (GV-031), PERSONAS frozenset.

CORE: CORE-008 (TDD), GV-030, GV-031
Source: GitHub Issue #18 — FB-20260312-007
"""

import pytest

from cortex.orchestrators.support.onboarding.tab_renderers import PersonaLayer


def test_persona_layer_adapt_engineer_returns_str() -> None:
    """PersonaLayer().adapt(html, 'engineer') returns str."""
    pl = PersonaLayer()
    result = pl.adapt("<div>hello</div>", "engineer")
    assert isinstance(result, str)


def test_persona_layer_adapt_architect_returns_str() -> None:
    """PersonaLayer().adapt(html, 'architect') returns str."""
    pl = PersonaLayer()
    result = pl.adapt("<div>hello</div>", "architect")
    assert isinstance(result, str)


def test_persona_layer_adapt_manager_returns_str() -> None:
    """PersonaLayer().adapt(html, 'manager') returns str."""
    pl = PersonaLayer()
    result = pl.adapt("<div>hello</div>", "manager")
    assert isinstance(result, str)


def test_persona_layer_adapt_unknown_persona_passthrough() -> None:
    """Unknown persona returns html_fragment unchanged (passthrough)."""
    pl = PersonaLayer()
    html = "<div>content</div>"
    result = pl.adapt(html, "unknown-persona")
    assert result == html


def test_persona_layer_adapt_never_raises() -> None:
    """GV-031: adapt() must not raise even on malformed input."""
    pl = PersonaLayer()
    try:
        result = pl.adapt(None, "engineer")  # type: ignore[arg-type]
        assert isinstance(result, str)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"PersonaLayer.adapt() raised unexpectedly: {exc}")


def test_persona_layer_adapt_empty_html_returns_empty() -> None:
    """adapt('', 'engineer') returns '' (empty in, empty out)."""
    pl = PersonaLayer()
    result = pl.adapt("", "engineer")
    assert result == ""


def test_persona_layer_personas_is_frozenset() -> None:
    """PERSONAS is a frozenset (GV-028 equivalence for PersonaLayer)."""
    assert isinstance(PersonaLayer.PERSONAS, frozenset)


def test_persona_layer_personas_contains_required() -> None:
    """PERSONAS must contain engineer, architect, manager."""
    required = {"engineer", "architect", "manager"}
    assert required.issubset(PersonaLayer.PERSONAS)
