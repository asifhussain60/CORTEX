"""Tests — DashboardGenerator → TabRenderer → PersonaLayer wiring (Phase 151-d)

Enforces GV-032: no tab HTML emitted outside the pipeline.

CORE: CORE-008 (TDD), GV-030, GV-032
Source: GitHub Issue #18 — FB-20260312-007
"""

from unittest.mock import MagicMock, patch

import pytest

from cortex.infrastructure.deployment.dashboard_generator import DashboardGenerator


def test_dashboard_generator_has_tab_renderer() -> None:
    """DashboardGenerator instantiates with a _tab_renderer attribute."""
    dg = DashboardGenerator()
    assert hasattr(dg, "_tab_renderer")


def test_dashboard_generator_has_persona_layer() -> None:
    """DashboardGenerator instantiates with a _persona_layer attribute."""
    dg = DashboardGenerator()
    assert hasattr(dg, "_persona_layer")


def test_render_tab_returns_str() -> None:
    """render_tab() returns a str."""
    dg = DashboardGenerator()
    result = dg.render_tab("01-overview", {})
    assert isinstance(result, str)


def test_render_tab_routes_through_tab_renderer() -> None:
    """render_tab() calls _tab_renderer.render_tab()."""
    dg = DashboardGenerator()
    dg._tab_renderer = MagicMock(return_value="<div>tab</div>")
    # Patch persona_layer to return whatever tab_renderer gives
    dg._persona_layer = MagicMock()
    dg._persona_layer.adapt = MagicMock(return_value="<div>adapted</div>")
    dg.render_tab("01-overview", {"title": "Test"})
    dg._tab_renderer.render_tab.assert_called_once()  # type: ignore[attr-defined]


def test_render_tab_routes_through_persona_layer() -> None:
    """render_tab() calls _persona_layer.adapt()."""
    dg = DashboardGenerator()
    dg._tab_renderer = MagicMock()
    dg._tab_renderer.render_tab = MagicMock(return_value="<div>raw</div>")
    dg._persona_layer = MagicMock()
    dg._persona_layer.adapt = MagicMock(return_value="<div>adapted</div>")
    dg.render_tab("01-overview", {})
    dg._persona_layer.adapt.assert_called_once()  # type: ignore[attr-defined]


def test_render_tab_default_persona_engineer() -> None:
    """render_tab() default persona is 'engineer'."""
    dg = DashboardGenerator()
    dg._tab_renderer = MagicMock()
    dg._tab_renderer.render_tab = MagicMock(return_value="<html/>")
    dg._persona_layer = MagicMock()
    adapted_calls = []
    dg._persona_layer.adapt = lambda html, persona: adapted_calls.append(persona) or html
    dg.render_tab("01-overview", {})
    assert adapted_calls == ["engineer"]
