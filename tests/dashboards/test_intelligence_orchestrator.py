"""Tests — DashboardIntelligenceOrchestrator (Phase 152-f)

CORE: CORE-008 (TDD), CORE-011
Source: GitHub Issue #18 — FB-20260312-001
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cortex.dashboards.intelligence_orchestrator import (
    DashboardIntelligenceOrchestrator,
    DashboardPipelineResult,
)


def test_generate_returns_pipeline_result() -> None:
    """generate() returns a DashboardPipelineResult instance."""
    orchestrator = DashboardIntelligenceOrchestrator()
    result = orchestrator.generate(manifest=None)
    assert isinstance(result, DashboardPipelineResult)


def test_pipeline_result_success_property_true_when_no_errors() -> None:
    """DashboardPipelineResult.success is True when errors is empty and quality passed."""
    from cortex.dashboards.quality_gate import QualityReport

    result = DashboardPipelineResult(
        html_path="",
        dashboard_manifest=None,
        knowledge_overlay={},
        narratives={},
        viz_selections={},
        quality_report=QualityReport(issues=[], passed=True, score=100),
        errors=[],
    )
    assert result.success is True


def test_pipeline_result_success_false_when_errors_present() -> None:
    """DashboardPipelineResult.success is False when errors list is non-empty."""
    from cortex.dashboards.quality_gate import QualityReport

    result = DashboardPipelineResult(
        html_path="",
        dashboard_manifest=None,
        knowledge_overlay={},
        narratives={},
        viz_selections={},
        quality_report=QualityReport(issues=[], passed=True, score=100),
        errors=["something went wrong"],
    )
    assert result.success is False


def test_pipeline_result_success_false_when_quality_failed() -> None:
    """DashboardPipelineResult.success is False when quality_report.passed is False."""
    from cortex.dashboards.quality_gate import QualityIssue, QualityReport

    issue = QualityIssue(rule_id="QR-004", tab_id="overview", severity="P0", message="dead")
    result = DashboardPipelineResult(
        html_path="",
        dashboard_manifest=None,
        knowledge_overlay={},
        narratives={},
        viz_selections={},
        quality_report=QualityReport(issues=[issue], passed=False, score=80),
        errors=[],
    )
    assert result.success is False


def test_generate_does_not_raise_on_none_manifest() -> None:
    """generate() never raises even when manifest is None."""
    orchestrator = DashboardIntelligenceOrchestrator()
    try:
        result = orchestrator.generate(manifest=None)
        assert isinstance(result, DashboardPipelineResult)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"generate() raised unexpectedly: {exc}")


def test_generate_calls_data_collector() -> None:
    """generate() invokes DashboardDataCollector.collect() (Stage 1)."""
    orchestrator = DashboardIntelligenceOrchestrator()
    with patch.object(
        orchestrator._collector, "collect", wraps=orchestrator._collector.collect
    ) as spy:
        orchestrator.generate(manifest={})
        spy.assert_called_once()


def test_generate_calls_overlay_engine() -> None:
    """generate() invokes KnowledgeOverlayEngine.overlay() (Stage 2)."""
    orchestrator = DashboardIntelligenceOrchestrator()
    with patch.object(
        orchestrator._overlay_engine, "overlay", wraps=orchestrator._overlay_engine.overlay
    ) as spy:
        orchestrator.generate(manifest={})
        spy.assert_called_once()


def test_generate_calls_narrative_engine() -> None:
    """generate() invokes NarrativeEngine.narrate() (Stage 4)."""
    orchestrator = DashboardIntelligenceOrchestrator()
    with patch.object(
        orchestrator._narrative_engine, "narrate", wraps=orchestrator._narrative_engine.narrate
    ) as spy:
        orchestrator.generate(manifest={})
        spy.assert_called_once()


def test_generate_calls_quality_gate() -> None:
    """generate() invokes DashboardQualityGate.evaluate() (Stage 6)."""
    orchestrator = DashboardIntelligenceOrchestrator()
    with patch.object(
        orchestrator._quality_gate, "evaluate", wraps=orchestrator._quality_gate.evaluate
    ) as spy:
        orchestrator.generate(manifest={})
        spy.assert_called_once()


def test_generate_captures_errors_gracefully() -> None:
    """generate() captures exceptions into errors list — never propagates."""
    orchestrator = DashboardIntelligenceOrchestrator()
    # Make the overlay engine raise to simulate a mid-pipeline failure
    orchestrator._overlay_engine.overlay = MagicMock(side_effect=RuntimeError("boom"))
    result = orchestrator.generate(manifest={})
    assert isinstance(result, DashboardPipelineResult)
    assert len(result.errors) > 0
