"""Tests — DashboardManifest + DashboardDataCollector (Phase 152-a)

CORE: CORE-008 (TDD), CORE-011, CORE-012
Source: GitHub Issue #18 — FB-20260312-001, AC-001-01
"""

import pytest

from cortex.dashboards.data_collector import DashboardDataCollector, DashboardManifest


def test_dashboard_manifest_instantiates() -> None:
    """DashboardManifest can be constructed with required fields."""
    m = DashboardManifest(
        repo_name="test-repo",
        repo_path="/tmp/test",
        tabs={"overview": {"title": "Overview"}},
        archetype="python-service",
        metadata={"key": "value"},
    )
    assert m.repo_name == "test-repo"
    assert m.repo_path == "/tmp/test"
    assert m.archetype == "python-service"


def test_dashboard_manifest_empty_tabs_no_crash() -> None:
    """DashboardManifest with empty tabs dict does not crash."""
    m = DashboardManifest(repo_name="r", repo_path="p", tabs={}, archetype="a", metadata={})
    assert m.tabs == {}


def test_data_collector_collect_returns_dashboard_manifest() -> None:
    """DashboardDataCollector.collect() returns a DashboardManifest."""
    collector = DashboardDataCollector()
    result = collector.collect({"repo_name": "my-repo", "repo_path": "/tmp"})
    assert isinstance(result, DashboardManifest)


def test_data_collector_collect_tolerates_empty_manifest() -> None:
    """collect() does not raise on a minimal empty manifest input."""
    collector = DashboardDataCollector()
    result = collector.collect({})
    assert isinstance(result, DashboardManifest)


def test_data_collector_collect_populates_repo_name() -> None:
    """collect() extracts repo_name from the input manifest."""
    collector = DashboardDataCollector()
    result = collector.collect({"repo_name": "awesome-repo"})
    assert result.repo_name == "awesome-repo"


def test_data_collector_collect_populates_tabs() -> None:
    """collect() populates tabs from the input manifest if present."""
    tabs = {"overview": {"title": "Overview"}, "metrics": {}}
    collector = DashboardDataCollector()
    result = collector.collect({"repo_name": "r", "tabs": tabs})
    assert isinstance(result.tabs, dict)
