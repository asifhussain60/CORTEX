"""
Wave 7 Track 2: Coverage Enhancement Tests

Additional tests to achieve 85%+ coverage target.
Focus on edge cases, error paths, and previously uncovered branches.
"""

import pytest
from unittest.mock import Mock, MagicMock
from cortex.orchestrators.domain.enhanced_refactoring_orchestrator_v2 import (
    EnhancedRefactoringOrchestrator,
    RefactoringResult,
    CodeReviewResult,
    SecurityReviewResult,
    RefactoringType,
)
from cortex.orchestrators.domain.debugger_orchestrator import (
    DebuggerOrchestrator,
    DebugMarker,
    DebugSession,
    RegressionEvent,
    GovernanceViolation,
)


class TestEnhancedRefactoringOrchestratorCoverage:
    """Additional tests for coverage enhancement."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return EnhancedRefactoringOrchestrator()

    # ────────────────────────────────────────────────────────────────────────
    # EDGE CASES: Refactoring
    # ────────────────────────────────────────────────────────────────────────

    def test_refactor_empty_code(self, orchestrator):
        """Edge case: refactoring empty string."""
        result = orchestrator.refactor("", "extract_method")
        assert result.success is False
        assert result.error_message == "Empty code provided"

    def test_refactor_whitespace_only(self, orchestrator):
        """Edge case: refactoring whitespace-only code."""
        result = orchestrator.refactor("   \n\t\n   ", "rename_variable")
        assert result.success is False

    def test_refactor_unknown_type(self, orchestrator):
        """Edge case: unknown refactoring type."""
        result = orchestrator.refactor("x = 1", "unknown_refactoring")
        assert result.success is False
        assert "Unknown refactoring type" in result.error_message

    def test_refactor_all_strategy_types(self, orchestrator):
        """Coverage: All 6 refactoring strategies."""
        code = "def test(): x = 1"
        strategies = [
            "extract_method",
            "rename_variable",
            "extract_class",
            "simplify_conditional",
            "reduce_parameters",
            "resolve_duplication",
        ]

        for strategy in strategies:
            result = orchestrator.refactor(code, strategy)
            assert result is not None
            assert isinstance(result, RefactoringResult)
            assert result.risk_level in ["low", "medium", "high"]

    # ────────────────────────────────────────────────────────────────────────
    # EDGE CASES: Code Review
    # ────────────────────────────────────────────────────────────────────────

    def test_review_empty_code(self, orchestrator):
        """Edge case: reviewing empty code."""
        result = orchestrator.review_code("")
        assert result.quality_score == 50
        assert "Empty code" in result.issues[0]

    def test_review_very_long_function(self, orchestrator):
        """Edge case: 100-line function (exceeds 50-line threshold)."""
        lines = ["def long_func():"] + ["    x = 1"] * 100 + ["    return x"]
        long_code = "\n".join(lines)
        result = orchestrator.review_code(long_code)
        assert "god_function" in " ".join(result.issues).lower()

    def test_review_high_complexity(self, orchestrator):
        """Edge case: high conditional complexity."""
        code = """
def complex(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            return 'high'
    return 'low'
"""
        result = orchestrator.review_code(code)
        assert result.complexity_level in ["high", "critical"]
        assert result.quality_score < 100

    def test_review_perfect_code(self, orchestrator):
        """Edge case: well-documented, typed code."""
        code = '''
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
'''
        result = orchestrator.review_code(code)
        assert result.quality_score >= 90
        assert len(result.issues) <= 1  # Minimal issues

    def test_review_recommendations_generated(self, orchestrator):
        """Coverage: recommendation generation for each issue type."""
        code_with_issues = """
def func(x, y, z):
    if x:
        if y:
            if z:
                pass
"""
        result = orchestrator.review_code(code_with_issues)
        assert len(result.recommendations) > 0
        # Should have recommendations for complexity
        assert any("simplify" in r.lower() for r in result.recommendations)

    # ────────────────────────────────────────────────────────────────────────
    # EDGE CASES: Security Review
    # ────────────────────────────────────────────────────────────────────────

    def test_security_review_sql_injection_variations(self, orchestrator):
        """Coverage: Different SQL injection patterns."""
        variations = [
            'f"SELECT * FROM users WHERE id = {user_id}"',
            "f'SELECT * FROM table WHERE x = {var}'",
        ]

        for code in variations:
            result = orchestrator.security_review(code)
            assert len(result.vulnerabilities) > 0
            assert "SQL" in " ".join(result.vulnerabilities)

    def test_security_review_no_vulnerabilities(self, orchestrator):
        """Edge case: secure code."""
        code = """
def safe_query(db, user_id):
    cursor = db.cursor()
    return cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
"""
        result = orchestrator.security_review(code)
        assert result.risk_level == "low"
        assert len(result.vulnerabilities) == 0

    def test_security_review_multiple_vulnerabilities(self, orchestrator):
        """Edge case: code with multiple vulnerabilities."""
        code = """
import pickle
password = "secret123"
eval(user_input)
query = f"SELECT * FROM users WHERE id = {user_id}"
"""
        result = orchestrator.security_review(code)
        assert result.risk_level in ["high", "critical"]
        assert len(result.vulnerabilities) >= 3

    def test_security_owasp_categories(self, orchestrator):
        """Coverage: OWASP category classification."""
        code = 'query = f"SELECT * FROM users WHERE id = {x}"'
        result = orchestrator.security_review(code)
        assert len(result.owasp_categories) > 0
        assert any("Injection" in cat for cat in result.owasp_categories)

    # ────────────────────────────────────────────────────────────────────────
    # DATA STRUCTURE COVERAGE
    # ────────────────────────────────────────────────────────────────────────

    def test_refactoring_result_fields(self, orchestrator):
        """Coverage: All RefactoringResult fields."""
        result = orchestrator.refactor("x = 1", "rename_variable")
        assert hasattr(result, "success")
        assert hasattr(result, "refactored_code")
        assert hasattr(result, "changes")
        assert hasattr(result, "risk_level")
        assert hasattr(result, "error_message")

    def test_code_review_result_fields(self, orchestrator):
        """Coverage: All CodeReviewResult fields."""
        result = orchestrator.review_code("def f(): pass")
        assert hasattr(result, "quality_score")
        assert hasattr(result, "issues")
        assert hasattr(result, "recommendations")
        assert hasattr(result, "complexity_level")

    def test_security_result_fields(self, orchestrator):
        """Coverage: All SecurityReviewResult fields."""
        result = orchestrator.security_review("x = 1")
        assert hasattr(result, "risk_level")
        assert hasattr(result, "vulnerabilities")
        assert hasattr(result, "recommendations")
        assert hasattr(result, "owasp_categories")


class TestDebuggerOrchestratorCoverage:
    """Additional tests for DebuggerOrchestrator coverage."""

    @pytest.fixture
    def debugger(self):
        """Create debugger instance."""
        return DebuggerOrchestrator(event_bus=MagicMock())

    # ────────────────────────────────────────────────────────────────────────
    # SESSION MANAGEMENT
    # ────────────────────────────────────────────────────────────────────────

    def test_multiple_active_sessions(self, debugger):
        """Coverage: Multiple concurrent debug sessions."""
        # Create first session
        session1 = debugger.handle_test_failure(
            "test_foo",
            "AssertionError: x != y",
            "cortex/test_foo.py",
            42,
        )

        # Create second session
        session2 = debugger.handle_regression(
            RegressionEvent(
                orchestrator="RefactoringOrchestrator",
                method="refactor",
                input_data="x = 1",
                expected_output="y = 1",
                actual_output="z = 1",
                error_message="Unexpected output",
            )
        )

        # Both should be active
        active = debugger.get_active_sessions()
        assert len(active) >= 2
        assert session1.session_id in [s.session_id for s in active]
        assert session2.session_id in [s.session_id for s in active]

    def test_clear_specific_session(self, debugger):
        """Coverage: Clearing individual sessions."""
        session = debugger.handle_test_failure(
            "test_bar",
            "Error",
            "test.py",
            10,
        )

        before = len(debugger.get_active_sessions())
        debugger.clear_session(session.session_id)
        after = len(debugger.get_active_sessions())

        assert after < before

    def test_cleanup_markers(self, debugger):
        """Coverage: Marker cleanup."""
        # Inject multiple markers
        debugger.handle_test_failure("test1", "Error1", "file1.py", 1)
        debugger.handle_test_failure("test2", "Error2", "file2.py", 2)

        markers_before = len(debugger.get_injected_markers())
        cleaned = debugger.cleanup_markers()

        assert cleaned > 0
        assert len(debugger.get_injected_markers()) == 0

    # ────────────────────────────────────────────────────────────────────────
    # EVENT HANDLING EDGE CASES
    # ────────────────────────────────────────────────────────────────────────

    def test_regression_event_fields(self, debugger):
        """Coverage: RegressionEvent data handling."""
        event = RegressionEvent(
            orchestrator="Orchestrator1",
            method="method1",
            input_data="input",
            expected_output="expected",
            actual_output="actual",
            error_message="error",
        )

        session = debugger.handle_regression(event)

        assert session is not None
        assert "error" in session.error_message.lower()
        assert session.markers_injected[0].marker_type == "REGRESSION"

    def test_governance_violation_handling(self, debugger):
        """Coverage: Governance violation processing."""
        violation = GovernanceViolation(
            rule_id="CORE-008",
            severity="P0",
            description="Test not written before code",
            file_path="cortex/test.py",
            line_number=42,
        )

        session = debugger.handle_governance_violation(violation)

        assert session is not None
        assert session.error_message == violation.description
        assert session.file_path == violation.file_path

    def test_marker_properties(self, debugger):
        """Coverage: DebugMarker properties."""
        session = debugger.handle_test_failure(
            "test_name",
            "test error",
            "file.py",
            100,
        )

        marker = session.markers_injected[0]
        assert marker.file_path == "file.py"
        assert marker.line_number == 100
        assert marker.marker_type == "TEST_FAILURE"
        assert "test_name" in marker.message
        assert marker.timestamp is not None

    # ────────────────────────────────────────────────────────────────────────
    # DATA INTEGRITY
    # ────────────────────────────────────────────────────────────────────────

    def test_debug_session_ready_flag(self, debugger):
        """Coverage: Debug session ready state."""
        session = debugger.handle_test_failure(
            "test",
            "error",
            "file.py",
            1,
        )

        assert session.ready is True
        assert len(session.markers_injected) > 0

    def test_event_bus_integration_ready(self, debugger):
        """Coverage: EventBus is stored and accessible."""
        assert debugger.event_bus is not None


class TestCombinedAnalysis:
    """Tests for combined analysis workflow."""

    @pytest.fixture
    def orchestrator(self):
        return EnhancedRefactoringOrchestrator()

    def test_combined_analysis_structure(self, orchestrator):
        """Coverage: Combined analysis output structure."""
        code = "x = 1"
        result = orchestrator.combined_analysis(code)

        assert "refactoring_opportunities" in result
        assert "code_review" in result
        assert "security_review" in result
        assert "overall_recommendation" in result

    def test_combined_analysis_recommendation_logic(self, orchestrator):
        """Coverage: Overall recommendation generation."""
        # Secure, clean code
        clean_code = """
def add(a: int, b: int) -> int:
    '''Add two numbers.'''
    return a + b
"""
        result = orchestrator.combined_analysis(clean_code)
        assert "OK" in result["overall_recommendation"] or "acceptable" in result[
            "overall_recommendation"
        ].lower()

        # Vulnerable code
        vulnerable = 'eval(f"SELECT * FROM {table}")'
        result = orchestrator.combined_analysis(vulnerable)
        assert (
            "BLOCKED" in result["overall_recommendation"]
            or "Security" in result["overall_recommendation"]
        )


class TestPerformance:
    """Performance and latency tests."""

    @pytest.fixture
    def orchestrator(self):
        return EnhancedRefactoringOrchestrator()

    def test_refactor_latency(self, orchestrator):
        """Coverage: Performance validation."""
        import time

        code = "x = 1\ny = 2\nz = x + y"
        start = time.time()
        orchestrator.refactor(code, "rename_variable")
        elapsed = time.time() - start

        # Should complete in <50ms (target <200ms)
        assert elapsed < 0.2

    def test_review_latency(self, orchestrator):
        """Coverage: Code review performance."""
        import time

        code = "def f(): pass\ndef g(): pass"
        start = time.time()
        orchestrator.review_code(code)
        elapsed = time.time() - start

        assert elapsed < 0.2

    def test_security_review_latency(self, orchestrator):
        """Coverage: Security analysis performance."""
        import time

        code = "x = 1"
        start = time.time()
        orchestrator.security_review(code)
        elapsed = time.time() - start

        assert elapsed < 0.2
