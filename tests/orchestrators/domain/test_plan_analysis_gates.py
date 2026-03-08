"""Tests for PlanAnalysisGateRunner (CAPE sub-phase 136-c).

5 gates: 3 blocking (Threat / Quality / Security) + 2 informational
with CDR adjustment (RCA / OPJ).

TDD RED phase — imports fail until implementation exists.
"""
import pytest

from cortex.orchestrators.domain.plan_analysis_gates import (
    ThreatModelGate,
    QualityAnalysisGate,
    SecurityAssessmentGate,
    RCAHistoryGate,
    OPJConsultationGate,
    PlanAnalysisGateRunner,
    GateVerdict,
)


# ---------------------------------------------------------------------------
# ThreatModelGate
# ---------------------------------------------------------------------------

class TestThreatModelGate:

    def test_threat_gate_blocks_on_p0_threat(self) -> None:
        gate = ThreatModelGate()
        verdict: GateVerdict = gate.evaluate(threats=[{"severity": "P0", "name": "RCE"}])
        assert verdict.blocking is True

    def test_threat_gate_passes_no_threats(self) -> None:
        gate = ThreatModelGate()
        verdict = gate.evaluate(threats=[])
        assert verdict.blocking is False

    def test_threat_gate_passes_p2_threats_only(self) -> None:
        gate = ThreatModelGate()
        verdict = gate.evaluate(threats=[{"severity": "P2", "name": "Low risk"}])
        assert verdict.blocking is False

    def test_threat_gate_has_name(self) -> None:
        gate = ThreatModelGate()
        assert gate.name == "ThreatModel"


# ---------------------------------------------------------------------------
# QualityAnalysisGate
# ---------------------------------------------------------------------------

class TestQualityAnalysisGate:

    def test_quality_gate_blocks_below_threshold(self) -> None:
        gate = QualityAnalysisGate()
        verdict = gate.evaluate(quality_score=5.0)
        assert verdict.blocking is True

    def test_quality_gate_passes_at_threshold(self) -> None:
        gate = QualityAnalysisGate()
        verdict = gate.evaluate(quality_score=7.0)
        assert verdict.blocking is False

    def test_quality_gate_passes_above_threshold(self) -> None:
        gate = QualityAnalysisGate()
        verdict = gate.evaluate(quality_score=9.5)
        assert verdict.blocking is False

    def test_quality_gate_has_name(self) -> None:
        gate = QualityAnalysisGate()
        assert gate.name == "Quality"


# ---------------------------------------------------------------------------
# SecurityAssessmentGate
# ---------------------------------------------------------------------------

class TestSecurityAssessmentGate:

    def test_security_gate_blocks_p0_vulnerability(self) -> None:
        gate = SecurityAssessmentGate()
        verdict = gate.evaluate(vulnerabilities=[{"severity": "P0", "cve": "CVE-2025-0001"}])
        assert verdict.blocking is True

    def test_security_gate_passes_no_vulns(self) -> None:
        gate = SecurityAssessmentGate()
        verdict = gate.evaluate(vulnerabilities=[])
        assert verdict.blocking is False

    def test_security_gate_has_name(self) -> None:
        gate = SecurityAssessmentGate()
        assert gate.name == "Security"


# ---------------------------------------------------------------------------
# RCAHistoryGate (informational — never blocks)
# ---------------------------------------------------------------------------

class TestRCAHistoryGate:

    def test_rca_gate_informational_only(self) -> None:
        gate = RCAHistoryGate()
        verdict = gate.evaluate(rca_failures=20, cdr_score=0.5)
        assert verdict.blocking is False

    def test_rca_gate_adjustment_bounded_negative(self) -> None:
        gate = RCAHistoryGate()
        verdict = gate.evaluate(rca_failures=100, cdr_score=0.5)
        # adjustment must be clamped to [-0.3, 0.0]
        assert verdict.cdr_adjustment >= -0.3
        assert verdict.cdr_adjustment <= 0.0

    def test_rca_gate_no_failures_no_adjustment(self) -> None:
        gate = RCAHistoryGate()
        verdict = gate.evaluate(rca_failures=0, cdr_score=0.5)
        assert verdict.cdr_adjustment == pytest.approx(0.0, abs=1e-9)

    def test_rca_gate_has_name(self) -> None:
        gate = RCAHistoryGate()
        assert gate.name == "RCAHistory"


# ---------------------------------------------------------------------------
# OPJConsultationGate (informational — never blocks, ±0.3)
# ---------------------------------------------------------------------------

class TestOPJConsultationGate:

    def test_opj_gate_informational_only(self) -> None:
        gate = OPJConsultationGate()
        verdict = gate.evaluate(opj_score=0.0)
        assert verdict.blocking is False

    def test_opj_gate_positive_adjustment_bounded(self) -> None:
        gate = OPJConsultationGate()
        verdict = gate.evaluate(opj_score=1.0)
        assert verdict.cdr_adjustment <= 0.3

    def test_opj_gate_negative_adjustment_bounded(self) -> None:
        gate = OPJConsultationGate()
        verdict = gate.evaluate(opj_score=-1.0)
        assert verdict.cdr_adjustment >= -0.3

    def test_opj_gate_has_name(self) -> None:
        gate = OPJConsultationGate()
        assert gate.name == "OPJConsultation"


# ---------------------------------------------------------------------------
# PlanAnalysisGateRunner
# ---------------------------------------------------------------------------

class TestPlanAnalysisGateRunner:

    def test_runner_returns_ordered_dict(self) -> None:
        runner = PlanAnalysisGateRunner()
        verdicts = runner.run_all_gates(
            threats=[],
            quality_score=8.0,
            vulnerabilities=[],
            rca_failures=0,
            cdr_score=0.4,
            opj_score=0.5,
        )
        assert isinstance(verdicts, dict)
        keys = list(verdicts.keys())
        assert keys == ["ThreatModel", "Quality", "Security", "RCAHistory", "OPJConsultation"]

    def test_runner_blocks_if_any_blocking_gate_fails(self) -> None:
        runner = PlanAnalysisGateRunner()
        verdicts = runner.run_all_gates(
            threats=[{"severity": "P0", "name": "SQL injection"}],
            quality_score=9.0,
            vulnerabilities=[],
            rca_failures=0,
            cdr_score=0.4,
            opj_score=0.5,
        )
        assert verdicts["ThreatModel"].blocking is True
        assert runner.overall_approved(verdicts) is False

    def test_runner_all_pass(self) -> None:
        runner = PlanAnalysisGateRunner()
        verdicts = runner.run_all_gates(
            threats=[],
            quality_score=8.0,
            vulnerabilities=[],
            rca_failures=0,
            cdr_score=0.4,
            opj_score=0.5,
        )
        assert runner.overall_approved(verdicts) is True

    def test_runner_five_verdicts_always(self) -> None:
        runner = PlanAnalysisGateRunner()
        verdicts = runner.run_all_gates(
            threats=[],
            quality_score=9.9,
            vulnerabilities=[],
            rca_failures=5,
            cdr_score=0.6,
            opj_score=0.0,
        )
        assert len(verdicts) == 5
