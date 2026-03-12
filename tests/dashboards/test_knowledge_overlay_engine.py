"""Tests — KnowledgeOverlayEngine (Phase 152-b)

CORE: CORE-008 (TDD), CORE-011
Source: GitHub Issue #18 — FB-20260312-001
"""

import pytest

from cortex.dashboards.data_collector import DashboardManifest
from cortex.dashboards.knowledge_overlay_engine import KnowledgeOverlay, KnowledgeOverlayEngine


def test_knowledge_overlay_instantiates() -> None:
    """KnowledgeOverlay can be constructed with required fields."""
    overlay = KnowledgeOverlay(
        tab_id="overview",
        domain="cortex-frame-context",
        knowledge_entries=[],
        source_yaml="path/to.yaml",
    )
    assert overlay.tab_id == "overview"
    assert overlay.domain == "cortex-frame-context"


def test_overlay_engine_returns_dict() -> None:
    """overlay() returns a dict keyed by tab_id."""
    engine = KnowledgeOverlayEngine()
    manifest = DashboardManifest(
        repo_name="r",
        repo_path="/tmp",
        tabs={"overview": {}, "metrics": {}},
        archetype="python",
        metadata={},
    )
    result = engine.overlay(manifest)
    assert isinstance(result, dict)


def test_overlay_engine_unknown_tab_returns_empty_overlay() -> None:
    """Unknown tab_id produces a KnowledgeOverlay with empty knowledge_entries."""
    engine = KnowledgeOverlayEngine()
    manifest = DashboardManifest(
        repo_name="r", repo_path="/", tabs={"unknown-tab-xyz": {}}, archetype="a", metadata={}
    )
    result = engine.overlay(manifest)
    assert "unknown-tab-xyz" in result
    overlay = result["unknown-tab-xyz"]
    assert isinstance(overlay, KnowledgeOverlay)
    assert overlay.knowledge_entries == []


def test_overlay_engine_overview_maps_to_cortex_frame() -> None:
    """'overview' tab maps to 'cortex-frame-context' domain."""
    engine = KnowledgeOverlayEngine()
    manifest = DashboardManifest(
        repo_name="r", repo_path="/", tabs={"overview": {}}, archetype="a", metadata={}
    )
    result = engine.overlay(manifest)
    assert result["overview"].domain == "cortex-frame-context"


def test_overlay_engine_graceful_on_missing_yaml() -> None:
    """overlay() does not raise when registry YAML is absent or unreadable."""
    engine = KnowledgeOverlayEngine()
    manifest = DashboardManifest(
        repo_name="r", repo_path="/", tabs={"quality": {}}, archetype="a", metadata={}
    )
    try:
        result = engine.overlay(manifest)
        assert isinstance(result, dict)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"overlay() raised unexpectedly: {exc}")
