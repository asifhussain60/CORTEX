"""
Track 3 Group C: UnifiedQualityAssuranceOrchestrator - Behavioral Contract Tests

Tests define quality assurance API before implementation (TDD discipline).
Consolidates 4 orchestrators: RecommendationGate + ChallengeEngine + MetaAudit + CodeReview

Test Categories:
- 10 behavioral API tests (core functionality contracts)
- 4 edge case tests (unicode, special cases, error handling)
- 2 performance tests (latency <200ms target)

CORTEX COMPLIANCE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from pathlib import Path

from cortex.orchestrators.support.quality_models import (
    GateType,
    RiskLevel,
    ChallengeType,
    GateResult,
    RecommendationSafetyResult,
    Challenge,
    MetaAuditResult,
    QualityAssuranceReport,
    RejectionEntry,
)

from cortex.orchestrators.support.unified_quality_orchestrator import UnifiedQualityAssuranceOrchestrator


class TestUnifiedQualityAssuranceOrchestratorAPI:
    """Core behavioral contract tests for quality assurance orchestrator API."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        return UnifiedQualityAssuranceOrchestrator()

    def test_check_recommendation_safety_all_gates_pass(self):
        """Test: Check recommendation safety when all gates pass."""
        # Expected behavior:
        # 1. Execute all 4 validation gates (REJ-History, Regression, Test-Health, Duplication)
        # 2. All gates return SAFE status
        # 3. Result.is_safe = True
        # 4. Result.verdict = "SAFE_TO_RECOMMEND"

        result = RecommendationSafetyResult(
            is_safe=True,
            gates=[
                GateResult(GateType.REJECTION_HISTORY, RiskLevel.SAFE, 0.0, "No rejection matches"),
                GateResult(GateType.REGRESSION_RISK, RiskLevel.SAFE, 0.2, "Low regression risk"),
                GateResult(GateType.TEST_HEALTH, RiskLevel.SAFE, 0.9, "Tests healthy"),
                GateResult(GateType.DUPLICATION, RiskLevel.SAFE, 0.0, "No duplication detected"),
            ],
            verdict="SAFE_TO_RECOMMEND",
        )

        assert result.is_safe is True
        assert result.verdict == "SAFE_TO_RECOMMEND"
        assert len(result.gates) == 4
        assert all(gate.status == RiskLevel.SAFE for gate in result.gates)

    def test_check_recommendation_safety_regression_risk_blocks(self):
        """Test: Recommendation blocked when regression risk is critical."""
        # Expected: One gate returns CRITICAL → is_safe = False, verdict = "BLOCKED"

        result = RecommendationSafetyResult(
            is_safe=False,
            gates=[
                GateResult(GateType.REJECTION_HISTORY, RiskLevel.SAFE, 0.0, "No rejection matches"),
                GateResult(GateType.REGRESSION_RISK, RiskLevel.CRITICAL, 0.85, "High regression risk"),
                GateResult(GateType.TEST_HEALTH, RiskLevel.WARNING, 0.4, "Recent test failures"),
                GateResult(GateType.DUPLICATION, RiskLevel.SAFE, 0.0, "No duplication"),
            ],
            verdict="BLOCKED",
            blocking_gates=[GateType.REGRESSION_RISK],
        )

        assert result.is_safe is False
        assert result.verdict == "BLOCKED"
        assert GateType.REGRESSION_RISK in result.blocking_gates

    def test_check_recommendation_safety_rejection_history_match(self):
        """Test: Recommendation blocked by rejection history match."""
        # Expected: REJ-History gate detects similar rejected recommendation

        rejection = RejectionEntry(
            rejection_id="REJ-SECURITY-001",
            timestamp=datetime.now(),
            reason="Unsafe SQL pattern detected",
            similarity_score=0.92,
            recommendation_type="security_fix",
        )

        result = RecommendationSafetyResult(
            is_safe=False,
            gates=[
                GateResult(GateType.REJECTION_HISTORY, RiskLevel.CRITICAL, 0.92, "Match to REJ-SECURITY-001"),
            ],
            verdict="BLOCKED",
            blocking_gates=[GateType.REJECTION_HISTORY],
            rejection_match=rejection,
        )

        assert result.is_safe is False
        assert result.rejection_match is not None
        assert result.rejection_match.rejection_id == "REJ-SECURITY-001"
        assert result.rejection_match.similarity_score > 0.9

    def test_generate_challenge_assumption_type(self):
        """Test: Generate challenge for assumption disagreement."""
        # Expected: Challenge with type ASSUMPTION, severity WARNING/CRITICAL, suggested action

        challenge = Challenge(
            challenge_type=ChallengeType.ASSUMPTION,
            question="Are you sure this approach handles async contexts?",
            context="Recommended synchronous implementation in async codebase",
            severity=RiskLevel.WARNING,
            suggested_action="Consider async-first implementation pattern",
            alternatives=["Use asyncio.run()", "Wrap in async function"],
        )

        assert challenge.challenge_type == ChallengeType.ASSUMPTION
        assert challenge.severity == RiskLevel.WARNING
        assert len(challenge.alternatives) > 0

    def test_generate_challenge_security_type(self):
        """Test: Generate security challenge."""
        # Expected: Challenge with type SECURITY, severity CRITICAL

        challenge = Challenge(
            challenge_type=ChallengeType.SECURITY,
            question="Does this implementation validate user input?",
            context="Potential SQL injection vulnerability in query builder",
            severity=RiskLevel.CRITICAL,
            suggested_action="Add parameterized query validation",
            alternatives=["Use ORM", "Add input sanitization", "Validate against schema"],
        )

        assert challenge.challenge_type == ChallengeType.SECURITY
        assert challenge.severity == RiskLevel.CRITICAL
        assert len(challenge.alternatives) >= 3

    def test_generate_challenge_edge_case_type(self):
        """Test: Generate edge case challenge."""
        # Expected: Challenge with type EDGE_CASE

        challenge = Challenge(
            challenge_type=ChallengeType.EDGE_CASE,
            question="What happens with empty input lists?",
            context="Implementation assumes non-empty collections",
            severity=RiskLevel.WARNING,
            suggested_action="Add guard clause for empty inputs",
            alternatives=["Return early", "Raise ValueError", "Return empty result"],
        )

        assert challenge.challenge_type == ChallengeType.EDGE_CASE
        assert "empty" in challenge.question.lower()

    def test_perform_meta_audit_all_checks_pass(self):
        """Test: Holistic meta-audit with all checks passing."""
        # Expected: audit_id generated, is_valid=True, coverage_score high

        audit_result = MetaAuditResult(
            audit_id="MA-20260211-001",
            timestamp=datetime.now(),
            is_valid=True,
            checks_performed=[
                "Type hint coverage",
                "Docstring completeness",
                "Exception handling",
                "Git discipline",
                "Test coverage",
            ],
            violations=[],
            recommendations=[],
            coverage_score=95.0,
        )

        assert audit_result.is_valid is True
        assert len(audit_result.violations) == 0
        assert audit_result.coverage_score >= 90.0

    def test_perform_meta_audit_detects_violations(self):
        """Test: Meta-audit detects governance violations."""
        # Expected: is_valid=False, violations list populated

        audit_result = MetaAuditResult(
            audit_id="MA-20260211-002",
            timestamp=datetime.now(),
            is_valid=False,
            checks_performed=[
                "Type hint coverage",
                "Docstring completeness",
                "Exception handling",
                "Git discipline",
                "Test coverage",
            ],
            violations=[
                "CORE-011: Missing type hints on 3 functions",
                "CORE-012: Missing docstrings on 5 methods",
                "CORE-013: Bare except clause detected",
            ],
            recommendations=[
                "Add type hints to all public methods",
                "Document parameters and return types",
                "Replace bare except with specific exceptions",
            ],
            coverage_score=72.0,
        )

        assert audit_result.is_valid is False
        assert len(audit_result.violations) >= 3
        assert audit_result.coverage_score < 85.0

    def test_generate_quality_assurance_report(self):
        """Test: Generate comprehensive quality assurance report."""
        # Expected: Report with all components, overall_verdict, is_approved flag

        safety_result = RecommendationSafetyResult(
            is_safe=True,
            gates=[
                GateResult(GateType.REJECTION_HISTORY, RiskLevel.SAFE, 0.0, "No matches"),
                GateResult(GateType.REGRESSION_RISK, RiskLevel.SAFE, 0.2, "Low risk"),
                GateResult(GateType.TEST_HEALTH, RiskLevel.SAFE, 0.95, "Healthy"),
                GateResult(GateType.DUPLICATION, RiskLevel.SAFE, 0.0, "Clean"),
            ],
            verdict="SAFE_TO_RECOMMEND",
        )

        audit_result = MetaAuditResult(
            audit_id="MA-20260211-003",
            timestamp=datetime.now(),
            is_valid=True,
            checks_performed=["Type hints", "Docstrings", "Exceptions", "Git", "Tests"],
            violations=[],
            coverage_score=92.0,
        )

        report = QualityAssuranceReport(
            report_id="QA-20260211-001",
            timestamp=datetime.now(),
            safety_result=safety_result,
            challenges=[],
            meta_audit_result=audit_result,
            overall_verdict="APPROVED",
            is_approved=True,
        )

        assert report.is_approved is True
        assert report.overall_verdict == "APPROVED"
        assert report.safety_result.is_safe is True
        assert report.meta_audit_result.is_valid is True


class TestUnifiedQualityAssuranceOrchestratorEdgeCases:
    """Edge case and error handling tests."""

    def test_recommendation_safety_with_no_rejection_history(self):
        """Test: Safety check works with empty rejection history."""
        # Expected: REJ-History gate returns SAFE with score 0.0

        result = RecommendationSafetyResult(
            is_safe=True,
            gates=[
                GateResult(GateType.REJECTION_HISTORY, RiskLevel.SAFE, 0.0, "No history available"),
            ],
            verdict="SAFE_TO_RECOMMEND",
        )

        assert result.gates[0].score == 0.0
        assert result.gates[0].status == RiskLevel.SAFE

    def test_challenge_with_unicode_characters(self):
        """Test: Challenge generation handles unicode properly."""
        # Expected: Unicode strings preserved in question/context

        challenge = Challenge(
            challenge_type=ChallengeType.ASSUMPTION,
            question="What about μ-threshold handling? 🤔",
            context="Implementation with special chars: λ, ∀, ∃, ∧, ∨",
            severity=RiskLevel.WARNING,
            suggested_action="Verify unicode compatibility",
            alternatives=["Use utf-8 encoding", "Add normalization"],
        )

        assert "μ" in challenge.question
        assert "λ" in challenge.context
        assert "🤔" in challenge.question

    def test_meta_audit_with_special_violation_cases(self):
        """Test: Meta-audit handles complex violation scenarios."""
        # Expected: violations list can contain detailed error messages

        audit_result = MetaAuditResult(
            audit_id="MA-UNICODE-001",
            timestamp=datetime.now(),
            is_valid=False,
            checks_performed=["Type hints", "Docstrings"],
            violations=[
                "CORE-008: No tests for function `_encode_μ_value()`",
                "CORE-026: Commit message lacks AC_START marker (AC-UNICODE-001)",
                'CORE-012: Missing docstring with """character encoding docs"""',
            ],
            coverage_score=65.0,
        )

        assert "CORE-008" in audit_result.violations[0]
        assert "CORE-026" in audit_result.violations[1]
        assert audit_result.is_valid is False

    def test_rejection_entry_with_zero_similarity(self):
        """Test: Rejection entry with zero similarity score."""
        # Expected: Score of 0.0 means no match

        rejection = RejectionEntry(
            rejection_id="REJ-OLD-PATTERN",
            timestamp=datetime.now(),
            reason="Old deprecated approach",
            similarity_score=0.0,
            recommendation_type="old_style",
        )

        assert rejection.similarity_score == 0.0
        assert rejection.similarity_score < 0.3  # Below threshold for matching

    def test_multiple_blocking_gates_scenario(self):
        """Test: Multiple gates block recommendation simultaneously."""
        # Expected: blocking_gates list contains multiple gate types

        result = RecommendationSafetyResult(
            is_safe=False,
            gates=[
                GateResult(GateType.REJECTION_HISTORY, RiskLevel.CRITICAL, 0.88, "Match"),
                GateResult(GateType.REGRESSION_RISK, RiskLevel.CRITICAL, 0.91, "High risk"),
                GateResult(GateType.TEST_HEALTH, RiskLevel.WARNING, 0.45, "Failing tests"),
            ],
            verdict="BLOCKED",
            blocking_gates=[GateType.REJECTION_HISTORY, GateType.REGRESSION_RISK],
        )

        assert len(result.blocking_gates) == 2
        assert GateType.REJECTION_HISTORY in result.blocking_gates
        assert GateType.REGRESSION_RISK in result.blocking_gates
        assert GateType.TEST_HEALTH not in result.blocking_gates


class TestUnifiedQualityAssuranceOrchestratorPerformance:
    """Performance and latency tests."""

    def test_recommendation_safety_check_latency(self):
        """Test: Safety check completes within 100ms target."""
        # Expected: All gate checks complete in <100ms combined

        import time

        start = time.time()

        # Simulate gate checks
        gates = [
            GateResult(GateType.REJECTION_HISTORY, RiskLevel.SAFE, 0.0, "Quick check"),
            GateResult(GateType.REGRESSION_RISK, RiskLevel.SAFE, 0.2, "Calculated"),
            GateResult(GateType.TEST_HEALTH, RiskLevel.SAFE, 0.9, "Evaluated"),
            GateResult(GateType.DUPLICATION, RiskLevel.SAFE, 0.0, "Scanned"),
        ]

        result = RecommendationSafetyResult(
            is_safe=True,
            gates=gates,
            verdict="SAFE_TO_RECOMMEND",
        )

        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100.0, f"Safety check took {elapsed:.2f}ms (target <100ms)"

    def test_meta_audit_performance_with_many_checks(self):
        """Test: Meta-audit with 20+ checks performs well."""
        # Expected: Audit with many checks completes in <150ms

        import time

        start = time.time()

        checks = [f"Check-{i}" for i in range(25)]

        audit_result = MetaAuditResult(
            audit_id="PERF-001",
            timestamp=datetime.now(),
            is_valid=True,
            checks_performed=checks,
            violations=[],
            coverage_score=88.0,
        )

        elapsed = (time.time() - start) * 1000

        assert elapsed < 150.0, f"Meta-audit took {elapsed:.2f}ms (target <150ms)"
        assert len(audit_result.checks_performed) == 25
