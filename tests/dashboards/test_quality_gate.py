"""Tests — DashboardQualityGate (Phase 152-e)

CORE: CORE-008 (TDD), CORE-011
Source: GitHub Issue #18 — FB-20260312-001
"""

from __future__ import annotations

import pytest

from cortex.dashboards.quality_gate import DashboardQualityGate, QualityIssue, QualityReport


def test_quality_issue_has_required_fields() -> None:
    """QualityIssue dataclass exposes rule_id, tab_id, severity, message."""
    issue = QualityIssue(rule_id="QR-001", tab_id="overview", severity="P0", message="Missing metric card")
    assert issue.rule_id == "QR-001"
    assert issue.tab_id == "overview"
    assert issue.severity == "P0"
    assert issue.message == "Missing metric card"


def test_quality_report_passed_true_when_no_p0() -> None:
    """QualityReport.passed is True when there are no P0 issues."""
    report = QualityReport(issues=[], passed=True, score=100)
    assert report.passed is True


def test_quality_report_passed_false_when_p0_present() -> None:
    """QualityReport.passed is False when at least one P0 issue exists."""
    issue = QualityIssue(rule_id="QR-001", tab_id="overview", severity="P0", message="fail")
    report = QualityReport(issues=[issue], passed=False, score=80)
    assert report.passed is False


def test_quality_score_100_with_no_issues() -> None:
    """evaluate() returns score 100 when no issues found."""
    gate = DashboardQualityGate()
    narratives = {"overview": "word " * 160}
    viz = {}
    report = gate.evaluate(narratives=narratives, viz_selections=viz)
    assert report.score == 100
    assert report.passed is True
    assert report.issues == []


def test_quality_score_decreases_per_issue() -> None:
    """Score decreases when issues are present."""
    gate = DashboardQualityGate()
    # Short narrative triggers min-words rule
    narratives = {"overview": "too short"}
    report = gate.evaluate(narratives=narratives, viz_selections={})
    assert report.score < 100


def test_min_narrative_rule_fires_on_short_narrative() -> None:
    """QR-003 fires when a tab narrative is < 150 words."""
    gate = DashboardQualityGate()
    narratives = {"metrics": "only a few words here"}
    report = gate.evaluate(narratives=narratives, viz_selections={})
    rule_ids = {i.rule_id for i in report.issues}
    assert "QR-003" in rule_ids


def test_no_dead_sections_fires_on_empty_narrative() -> None:
    """QR-004 fires when a tab narrative is empty."""
    gate = DashboardQualityGate()
    narratives = {"health": ""}
    report = gate.evaluate(narratives=narratives, viz_selections={})
    rule_ids = {i.rule_id for i in report.issues}
    assert "QR-004" in rule_ids


def test_evaluate_returns_quality_report_instance() -> None:
    """evaluate() always returns a QualityReport."""
    gate = DashboardQualityGate()
    result = gate.evaluate(narratives={}, viz_selections={})
    assert isinstance(result, QualityReport)
