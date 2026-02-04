"""
TDD tests for review models - Phase 0 Foundation.

Tests for: PhaseReviewResult, GateDecision, FinalReviewResult, PlanFidelityReport
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD - tests BEFORE code), CORE-011 (type hints), CORE-012 (docstrings)
"""

import unittest
from datetime import datetime


class TestPhaseReviewResultModel(unittest.TestCase):
    """Tests for PhaseReviewResult data model."""
    
    def test_phase_review_result_pass(self) -> None:
        """Verify PhaseReviewResult can represent a passing review."""
        from cortex.models.review_models import PhaseReviewResult, ReviewStatus
        
        result = PhaseReviewResult(
            phase_id="phase_1",
            status=ReviewStatus.PASS,
            tests_run=10,
            tests_passed=10,
            issues_found=[],
            review_timestamp=datetime.now()
        )
        
        self.assertEqual(result.phase_id, "phase_1")
        self.assertEqual(result.status, ReviewStatus.PASS)
        self.assertEqual(result.tests_run, 10)
        self.assertEqual(len(result.issues_found), 0)
    
    def test_phase_review_result_fail(self) -> None:
        """Verify PhaseReviewResult can include failure details."""
        from cortex.models.review_models import PhaseReviewResult, ReviewStatus, ReviewIssue
        
        result = PhaseReviewResult(
            phase_id="phase_2",
            status=ReviewStatus.FAIL,
            tests_run=15,
            tests_passed=12,
            issues_found=[
                ReviewIssue(
                    issue_type="TEST_FAILURE",
                    description="3 unit tests failed",
                    severity="HIGH",
                    blocking=True
                )
            ],
            review_timestamp=datetime.now()
        )
        
        self.assertEqual(result.status, ReviewStatus.FAIL)
        self.assertEqual(len(result.issues_found), 1)
        self.assertTrue(result.issues_found[0].blocking)


class TestGateDecisionModel(unittest.TestCase):
    """Tests for GateDecision data model."""
    
    def test_gate_decision_approved(self) -> None:
        """Verify GateDecision can approve next phase."""
        from cortex.models.review_models import GateDecision
        
        decision = GateDecision(
            current_phase="phase_1",
            next_phase="phase_2",
            approved=True,
            conditions_met=["All tests pass", "No critical issues"],
            conditions_failed=[],
            decision_timestamp=datetime.now()
        )
        
        self.assertTrue(decision.approved)
        self.assertEqual(len(decision.conditions_met), 2)
        self.assertEqual(len(decision.conditions_failed), 0)
    
    def test_gate_decision_blocked(self) -> None:
        """Verify GateDecision can block next phase."""
        from cortex.models.review_models import GateDecision
        
        decision = GateDecision(
            current_phase="phase_2",
            next_phase="phase_3",
            approved=False,
            conditions_met=["All tests pass"],
            conditions_failed=["LENS complexity exceeds threshold"],
            decision_timestamp=datetime.now()
        )
        
        self.assertFalse(decision.approved)
        self.assertEqual(len(decision.conditions_failed), 1)


class TestPlanFidelityReportModel(unittest.TestCase):
    """Tests for PlanFidelityReport data model."""
    
    def test_plan_fidelity_report_perfect(self) -> None:
        """Verify PlanFidelityReport can represent perfect implementation."""
        from cortex.models.review_models import PlanFidelityReport
        
        report = PlanFidelityReport(
            score=100,
            missing_specs=[],
            extra_artifacts=[],
            deviations=[]
        )
        
        self.assertEqual(report.score, 100)
        self.assertEqual(len(report.missing_specs), 0)
        self.assertEqual(len(report.extra_artifacts), 0)
    
    def test_plan_fidelity_report_with_deviations(self) -> None:
        """Verify PlanFidelityReport can include deviations from plan."""
        from cortex.models.review_models import PlanFidelityReport, Deviation
        
        report = PlanFidelityReport(
            score=85,
            missing_specs=["function_spec_1"],
            extra_artifacts=["unplanned_helper.py"],
            deviations=[
                Deviation(
                    spec_type="FunctionSpec",
                    spec_id="process_data",
                    expected="def process_data(input: List) -> Dict",
                    actual="def process_data(input: List, verbose: bool = False) -> Dict",
                    impact="LOW"
                )
            ]
        )
        
        self.assertEqual(report.score, 85)
        self.assertEqual(len(report.deviations), 1)
        self.assertEqual(report.deviations[0].impact, "LOW")


class TestFinalReviewResultModel(unittest.TestCase):
    """Tests for FinalReviewResult data model."""
    
    def test_final_review_result_pass(self) -> None:
        """Verify FinalReviewResult can represent successful implementation."""
        from cortex.models.review_models import (
            FinalReviewResult, ReviewOutcome, PlanFidelityReport
        )
        
        result = FinalReviewResult(
            task_id="TASK-001",
            outcome=ReviewOutcome.PASS,
            plan_fidelity=PlanFidelityReport(score=95, missing_specs=[], extra_artifacts=[], deviations=[]),
            commit_analysis={"total_commits": 5, "atomic": True},
            coherence_status="PASS",
            review_duration_seconds=45.2
        )
        
        self.assertEqual(result.outcome, ReviewOutcome.PASS)
        self.assertEqual(result.plan_fidelity.score, 95)
        self.assertEqual(result.coherence_status, "PASS")
    
    def test_final_review_result_conditional_pass(self) -> None:
        """Verify FinalReviewResult can include recommendations."""
        from cortex.models.review_models import (
            FinalReviewResult, ReviewOutcome, PlanFidelityReport
        )
        
        result = FinalReviewResult(
            task_id="TASK-002",
            outcome=ReviewOutcome.CONDITIONAL_PASS,
            plan_fidelity=PlanFidelityReport(score=82, missing_specs=[], extra_artifacts=["debug.py"], deviations=[]),
            commit_analysis={"total_commits": 8, "atomic": False},
            coherence_status="PASS",
            review_duration_seconds=38.5,
            recommendations=["Remove debug.py before merge", "Squash commits"]
        )
        
        self.assertEqual(result.outcome, ReviewOutcome.CONDITIONAL_PASS)
        self.assertEqual(len(result.recommendations), 2)
    
    def test_review_outcome_enum_values(self) -> None:
        """Verify ReviewOutcome enum has expected values."""
        from cortex.models.review_models import ReviewOutcome
        
        expected = {"PASS", "CONDITIONAL_PASS", "FAIL"}
        actual = {o.name for o in ReviewOutcome}
        self.assertEqual(actual, expected)


class TestCommitAnalysisModel(unittest.TestCase):
    """Tests for CommitAnalysis data model."""
    
    def test_commit_analysis_creation(self) -> None:
        """Verify CommitAnalysis can capture git commit details."""
        from cortex.models.review_models import CommitAnalysis
        
        analysis = CommitAnalysis(
            total_commits=5,
            commits_with_task_reference=4,
            atomic_commits=True,
            commit_sequence_matches_plan=True,
            unrelated_changes_detected=False
        )
        
        self.assertEqual(analysis.total_commits, 5)
        self.assertTrue(analysis.atomic_commits)
        self.assertFalse(analysis.unrelated_changes_detected)


if __name__ == "__main__":
    unittest.main()
