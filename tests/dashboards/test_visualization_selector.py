"""Tests — VisualizationSelector (Phase 152-c)

CORE: CORE-008 (TDD), CORE-011
Source: GitHub Issue #18 — FB-20260312-001
"""

import pytest

from cortex.dashboards.visualization_selector import (
    ChartType,
    DataShape,
    VisualizationChoice,
    VisualizationSelector,
)


def test_data_shape_enum_members() -> None:
    """DataShape has all 5 required members."""
    required = {"RELATIONAL", "TEMPORAL", "PROPORTIONAL", "CATEGORICAL", "SCALAR"}
    actual = {m.name for m in DataShape}
    assert required.issubset(actual)


def test_chart_type_enum_members() -> None:
    """ChartType has at least 5 required members."""
    required = {"BAR", "LINE", "PIE", "TABLE", "METRIC_CARD"}
    actual = {m.name for m in ChartType}
    assert required.issubset(actual)


def test_visualization_choice_instantiates() -> None:
    """VisualizationChoice can be constructed with required fields."""
    vc = VisualizationChoice(
        tab_id="overview",
        chart_type=ChartType.METRIC_CARD,
        data_shape=DataShape.SCALAR,
        five_second_primary=True,
        f_pattern_position="top-left",
    )
    assert vc.tab_id == "overview"
    assert vc.five_second_primary is True


def test_selector_select_returns_list() -> None:
    """select() returns a list."""
    sel = VisualizationSelector()
    result = sel.select("overview", {})
    assert isinstance(result, list)


def test_selector_select_unknown_tab_returns_default() -> None:
    """Unknown tab → METRIC_CARD fallback (non-empty list)."""
    sel = VisualizationSelector()
    result = sel.select("nonexistent-tab-xyz", {})
    assert len(result) > 0
    assert result[0].chart_type == ChartType.METRIC_CARD


def test_selector_five_second_rule() -> None:
    """At least one VisualizationChoice has five_second_primary=True."""
    sel = VisualizationSelector()
    result = sel.select("overview", {})
    assert any(vc.five_second_primary for vc in result)


def test_selector_f_pattern_top_left() -> None:
    """At least one choice has f_pattern_position='top-left'."""
    sel = VisualizationSelector()
    result = sel.select("metrics", {})
    assert any(vc.f_pattern_position == "top-left" for vc in result)
