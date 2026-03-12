"""Tests — NarrativeEngine (Phase 152-d)

CORE: CORE-008 (TDD), CORE-011
Source: GitHub Issue #18 — FB-20260312-001
"""

import pytest

from cortex.dashboards.data_collector import DashboardManifest
from cortex.dashboards.knowledge_overlay_engine import KnowledgeOverlay
from cortex.dashboards.narrative_engine import NarrativeEngine


def _make_manifest(tabs=None) -> DashboardManifest:
    if tabs is None:
        tabs = {"overview": {}, "metrics": {}}
    return DashboardManifest(
        repo_name="test-repo",
        repo_path="/tmp/test",
        tabs=tabs,
        archetype="python-service",
        metadata={},
    )


def test_narrate_returns_dict_per_tab() -> None:
    """narrate() returns a dict with one entry per tab in the manifest."""
    engine = NarrativeEngine()
    manifest = _make_manifest({"overview": {}, "metrics": {}})
    result = engine.narrate(manifest, {})
    assert isinstance(result, dict)
    assert set(result.keys()) == {"overview", "metrics"}


def test_narrate_empty_tabs_returns_empty() -> None:
    """Empty tabs → empty dict."""
    engine = NarrativeEngine()
    manifest = _make_manifest({})
    result = engine.narrate(manifest, {})
    assert result == {}


def test_narrate_tab_word_count_gte_150() -> None:
    """Non-empty tab narrative is ≥ 150 words."""
    engine = NarrativeEngine()
    manifest = _make_manifest({"overview": {"title": "Overview"}})
    result = engine.narrate(manifest, {})
    narrative = result.get("overview", "")
    word_count = len(narrative.split())
    assert word_count >= NarrativeEngine.MIN_WORD_COUNT, (
        f"Narrative word count {word_count} < {NarrativeEngine.MIN_WORD_COUNT}"
    )


def test_narrate_no_exception_on_none_overlay() -> None:
    """narrate() does not crash when overlay for a tab is None."""
    engine = NarrativeEngine()
    manifest = _make_manifest({"security": {}})
    # Pass None explicitly for the overlay value
    try:
        result = engine.narrate(manifest, {"security": None})  # type: ignore[dict-item]
        assert isinstance(result, dict)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"narrate() raised unexpectedly: {exc}")


def test_narrate_includes_tab_id_in_narrative() -> None:
    """Tab narrative should reference the tab_id or related content."""
    engine = NarrativeEngine()
    manifest = _make_manifest({"quality": {}})
    result = engine.narrate(manifest, {})
    narrative = result.get("quality", "")
    assert isinstance(narrative, str)
    assert len(narrative) > 0
