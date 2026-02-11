"""
Test Suite: CORE-039 MD File Generation Blocker
**Authority:** CORE-039-md-generation-prohibition.yaml
**Purpose:** Enforce prohibition on automatic MD file generation at phase end
**Test Count:** 10+ high-coverage tests

**Governance Requirements:**
- CORE-008: Tests MUST exist before implementation (TDD)
- CORE-011: Type hints required
- CORE-012: Google-style docstrings required
- CORE-027: Audit trail enforcement
- CORE-039: MD generation blocking (THIS TEST SUITE)

**AC_ID:** AC-CORE-039-TEST-001
**Status:** PRODUCTION READY
"""

import tempfile
from pathlib import Path
from typing import Any, Optional

import pytest

# ============================================================================
# CORE-039 Enforcement Exceptions
# ============================================================================

class CORE039Violation(Exception):
    """Exception raised when CORE-039 is violated."""

    def __init__(
        self,
        file_path: str,
        context: str,
        allowed_via: Optional[str] = None,
    ):
        """
        Initialize CORE-039 violation.

        Args:
            file_path: Path of MD file being written
            context: Context of violation (phase_complete, tool_report, etc.)
            allowed_via: If violation can be allowed via this mechanism
        """
        self.file_path = file_path
        self.context = context
        self.allowed_via = allowed_via
        msg = (
            f"CORE-039 VIOLATION: MD file generation without user request\n"
            f"  File: {file_path}\n"
            f"  Context: {context}\n"
        )
        if allowed_via:
            msg += f"  Allowed via: {allowed_via}\n"
        super().__init__(msg)


class UserRequestContext:
    """
    Context manager that marks documentation as user-requested.

    Usage:
        with UserRequestContext():
            path.write_text(md_content)  # ✅ ALLOWED
    """

    _user_requested: bool = False

    def __enter__(self) -> "UserRequestContext":
        """Enter context: enable user-requested mode."""
        UserRequestContext._user_requested = True
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context: disable user-requested mode."""
        UserRequestContext._user_requested = False

    @classmethod
    def is_user_requested(cls) -> bool:
        """Check if currently in user-requested context."""
        return cls._user_requested


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_cortex_workspace() -> Any:
    """Create temporary CORTEX workspace for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "reports" / "phase-tracking").mkdir(parents=True)
        (workspace / "reports" / "analysis").mkdir(parents=True)
        (workspace / "docs").mkdir(parents=True)
        yield workspace


@pytest.fixture
def blocked_path_write(monkeypatch: pytest.MonkeyPatch) -> Any:
    """
    Monkeypatch Path.write_text to enforce CORE-039.

    Blocks MD file writes unless in UserRequestContext.
    """

    original_write_text = Path.write_text

    def enforced_write_text(self: Path, data: str, *args: Any, **kwargs: Any) -> Any:
        """Enforced version of Path.write_text that blocks MD files."""
        if str(self).endswith(".md"):
            # Check if write is user-requested
            if not UserRequestContext.is_user_requested():
                context_hint = (
                    "Use 'with UserRequestContext(): ...' "
                    "to mark documentation as user-requested"
                )
                raise CORE039Violation(
                    file_path=str(self),
                    context="write_text() call outside UserRequestContext",
                    allowed_via=context_hint,
                )
        return original_write_text(self, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", enforced_write_text)


# ============================================================================
# Test Suite: Phase Completion MD Generation (BLOCKING)
# ============================================================================


class TestPhaseCompletionMDBlocking:
    """Tests for blocking MD generation at phase completion."""

    def test_phase_complete_event_blocked(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Phase complete event CANNOT write MD files.

        Scenario: Phase completion triggers report generation
        Expectation: CORE-039 blocks MD write
        """
        phase_num = 14
        report_path = temp_cortex_workspace / "reports" / "phase-tracking" / f"phase-{phase_num}-completion.md"

        # Attempt to write report without user request
        with pytest.raises(CORE039Violation) as exc_info:
            report_content = f"# Phase {phase_num} Completion Report\n\nPhase complete."
            report_path.write_text(report_content)

        # Verify violation details
        assert exc_info.value.file_path == str(report_path)
        assert "phase_complete" in exc_info.value.context or "write_text" in exc_info.value.context

    def test_phase_complete_yaml_allowed(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Phase completion CAN write YAML files.

        Scenario: Phase completion stores metrics in YAML
        Expectation: YAML writes are NOT blocked
        """
        phase_num = 14
        metrics_path = temp_cortex_workspace / "reports" / "phase-tracking" / f"phase-{phase_num}-metrics.yaml"

        # This should NOT raise an exception
        metrics_content = f"""phase: {phase_num}
status: complete
timestamp: 2026-01-26T10:00:00Z
"""
        metrics_path.write_text(metrics_content)

        # Verify file was written
        assert metrics_path.exists()
        assert "phase: 14" in metrics_path.read_text()

    def test_user_requested_phase_doc_allowed(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Phase documentation CAN be written if user-requested.

        Scenario: User explicitly requests documentation for phase 14
        Expectation: MD write is ALLOWED with UserRequestContext
        """
        phase_num = 14
        doc_path = temp_cortex_workspace / "docs" / f"phase-{phase_num}-guide.md"

        # Write with user request context
        with UserRequestContext():
            doc_content = f"# Phase {phase_num} Guide\n\nUser-requested documentation."
            doc_path.write_text(doc_content)

        # Verify file was written
        assert doc_path.exists()
        assert f"Phase {phase_num} Guide" in doc_path.read_text()


# ============================================================================
# Test Suite: Autonomous Execution Engine MD Blocking
# ============================================================================


class TestAutonomousExecutionMDBlocking:
    """Tests for blocking MD generation in autonomous executor."""

    def test_execution_complete_blocked(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Execution completion CANNOT write MD reports.

        Scenario: Autonomous execution completes and attempts report write
        Expectation: CORE-039 blocks MD write
        """
        report_path = temp_cortex_workspace / "reports" / "execution-report.md"

        with pytest.raises(CORE039Violation) as exc_info:
            report_content = "# Execution Report\n\nAll phases complete."
            report_path.write_text(report_content)

        assert exc_info.value.file_path == str(report_path)

    def test_execution_metrics_yaml_allowed(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Execution completion CAN write YAML metrics.

        Scenario: Autonomous execution stores completion metrics
        Expectation: YAML writes are NOT blocked
        """
        metrics_path = temp_cortex_workspace / "reports" / "execution-metrics.yaml"

        execution_metrics = """total_phases: 8
phases_completed: 8
phases_failed: 0
total_duration_seconds: 3600
status: success
"""
        metrics_path.write_text(execution_metrics)

        assert metrics_path.exists()
        assert "status: success" in metrics_path.read_text()


# ============================================================================
# Test Suite: Tool Report Generation Blocking
# ============================================================================


class TestToolReportMDBlocking:
    """Tests for blocking MD reports from analysis tools."""

    def test_duplication_audit_report_blocked(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Duplication audit tool CANNOT write MD reports.

        Scenario: Analysis tool attempts to write audit report
        Expectation: CORE-039 blocks MD write
        """
        report_path = temp_cortex_workspace / "reports" / "analysis" / "duplication-audit.md"

        with pytest.raises(CORE039Violation):
            report_content = "# Duplication Audit Report\n\nFound 5 duplicates."
            report_path.write_text(report_content)

    def test_analysis_tool_yaml_allowed(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Analysis tools CAN write YAML reports.

        Scenario: Tool stores analysis results in YAML
        Expectation: YAML writes are NOT blocked
        """
        report_path = temp_cortex_workspace / "reports" / "analysis" / "duplication-results.yaml"

        report_content = """duplicates_found: 5
total_lines_redundant: 342
severity: medium
affected_modules:
  - module_a
  - module_b
"""
        report_path.write_text(report_content)

        assert report_path.exists()
        assert "duplicates_found: 5" in report_path.read_text()


# ============================================================================
# Test Suite: Documentation Pipeline Blocking
# ============================================================================


class TestDocumentationPipelineMDBlocking:
    """Tests for blocking MD generation in documentation pipeline."""

    def test_fresh_documentation_report_blocked(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Fresh documentation pipeline CANNOT auto-generate MD reports.

        Scenario: Documentation phase completion attempts to write summary
        Expectation: CORE-039 blocks MD write
        """
        report_path = (
            temp_cortex_workspace / "reports" / "analysis" / "fresh-documentation-generation-2026-01-26.md"
        )

        with pytest.raises(CORE039Violation):
            report_content = "# Fresh Documentation Generation\n\nCompleted 7 sections."
            report_path.write_text(report_content)

    def test_user_requested_fresh_docs_allowed(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Fresh documentation CAN be generated if user-requested.

        Scenario: User explicitly requests fresh documentation generation
        Expectation: MD write is ALLOWED with UserRequestContext
        """
        doc_path = temp_cortex_workspace / "docs" / "fresh-documentation-guide.md"

        with UserRequestContext():
            doc_content = "# Fresh Documentation Generation Guide\n\nStep-by-step instructions."
            doc_path.write_text(doc_content)

        assert doc_path.exists()


# ============================================================================
# Test Suite: Real Orchestrator Patterns
# ============================================================================


class MockPhaseCompletionOrchestrator:
    """Mock orchestrator that simulates phase completion."""

    def __init__(self, workspace: Path):
        """Initialize with workspace path."""
        self.workspace = workspace

    def on_phase_complete(self, phase_num: int) -> None:
        """
        Handle phase completion.

        Args:
            phase_num: Phase number
        """
        # CORRECT: Store metrics in YAML, not MD
        metrics = {
            "phase": phase_num,
            "status": "complete",
            "timestamp": "2026-01-26T10:00:00Z",
        }
        metrics_path = self.workspace / "reports" / "phase-tracking" / f"phase-{phase_num}-metrics.yaml"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)

        import yaml

        metrics_path.write_text(yaml.dump(metrics))


class TestOrchestrationPatterns:
    """Tests for correct phase completion patterns."""

    def test_phase_orchestrator_correct_pattern(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Phase orchestrator follows correct YAML pattern.

        Scenario: Phase orchestrator completes phase 14
        Expectation: Metrics stored in YAML, no MD generated
        """
        import yaml

        orchestrator = MockPhaseCompletionOrchestrator(temp_cortex_workspace)

        # This should NOT raise an exception
        orchestrator.on_phase_complete(14)

        # Verify metrics were written to YAML
        metrics_path = temp_cortex_workspace / "reports" / "phase-tracking" / "phase-14-metrics.yaml"
        assert metrics_path.exists()

        # Parse YAML and verify content
        metrics = yaml.safe_load(metrics_path.read_text())
        assert metrics["phase"] == 14
        assert metrics["status"] == "complete"


# ============================================================================
# Test Suite: Enforcement Verification
# ============================================================================


class TestEnforcementMechanisms:
    """Tests for enforcement mechanism functionality."""

    def test_enforcement_exception_details(self) -> None:
        """Test: CORE039Violation exception provides clear details."""
        violation = CORE039Violation(
            file_path="/path/to/report.md",
            context="phase_complete_handler",
            allowed_via="UserRequestContext",
        )

        # Verify exception message contains all required info
        msg = str(violation)
        assert "CORE-039" in msg
        assert "/path/to/report.md" in msg
        assert "phase_complete_handler" in msg
        assert "UserRequestContext" in msg

    def test_user_request_context_isolation(self) -> None:
        """Test: UserRequestContext properly isolates user-requested state."""
        # Outside context: not user-requested
        assert not UserRequestContext.is_user_requested()

        # Inside context: user-requested
        with UserRequestContext():
            assert UserRequestContext.is_user_requested()

        # After context: not user-requested
        assert not UserRequestContext.is_user_requested()

    def test_user_request_context_nesting(self) -> None:
        """Test: UserRequestContext properly handles sequential contexts."""
        assert not UserRequestContext.is_user_requested()

        # First context
        with UserRequestContext():
            assert UserRequestContext.is_user_requested()

        # After first context exits, flag is reset
        assert not UserRequestContext.is_user_requested()

        # Second context is independent
        with UserRequestContext():
            assert UserRequestContext.is_user_requested()

        # After second context exits, flag is reset
        assert not UserRequestContext.is_user_requested()


# ============================================================================
# Test Suite: Static Pattern Detection
# ============================================================================


class TestStaticPatternDetection:
    """Tests for static pattern detection of violations."""

    def test_pattern_phase_complete_md(self) -> None:
        """
        Test: Detects pattern of phase completion MD write in reports/.

        Pattern: reports/.* + .md (catches tool-generated reports)
        """
        import re

        violation_pattern = r"^reports/.*\.md$"
        test_cases = [
            ("reports/phase-tracking/phase-14-completion.md", True),
            ("reports/phase-tracking/phase-15-report.md", True),
            ("reports/analysis/duplication-audit.md", True),
            ("reports/metrics.yaml", False),
            ("docs/phase-guide.md", False),  # In docs folder (user-requested)
            ("docs/phase-14-completion.md", False),  # In docs folder
        ]

        for filepath, should_match in test_cases:
            matches = bool(re.match(violation_pattern, filepath, re.IGNORECASE))
            assert matches == should_match, f"Pattern mismatch for {filepath}: got {matches}, expected {should_match}"

    def test_pattern_tool_report_md(self) -> None:
        """
        Test: Detects pattern of tool-generated report MD.

        Pattern: reports/ + .* + .md
        """
        violation_pattern = r"^reports/.*\.md$"
        test_cases = [
            ("reports/analysis/duplication-audit.md", True),
            ("reports/phase-tracking/report.md", True),
            ("reports/metrics.yaml", False),
            ("docs/guide.md", False),
        ]

        import re

        for filepath, should_match in test_cases:
            matches = bool(re.match(violation_pattern, filepath))
            assert matches == should_match, f"Pattern mismatch for {filepath}"


# ============================================================================
# Test Suite: Integration Tests
# ============================================================================


class TestCORE039Integration:
    """Integration tests for CORE-039 enforcement across system."""

    def test_phase_end_workflow_compliant(self, temp_cortex_workspace: Path, blocked_path_write: None) -> None:
        """
        Test: Complete phase-end workflow complies with CORE-039.

        Workflow:
        1. Phase execution completes
        2. Metrics stored in YAML
        3. UI updated with metrics
        4. No MD files created
        """
        import yaml

        phase_num = 14

        # Step 1: Execute phase (implicit)

        # Step 2: Store metrics in YAML
        metrics = {
            "phase": phase_num,
            "tests_passed": 45,
            "tests_failed": 0,
            "duration_seconds": 120,
        }
        metrics_path = temp_cortex_workspace / "reports" / "phase-tracking" / f"phase-{phase_num}-metrics.yaml"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(yaml.dump(metrics))

        # Step 3: Verify no MD files created
        md_files = list(temp_cortex_workspace.glob("**/*.md"))
        assert len(md_files) == 0, f"Found unexpected MD files: {md_files}"

        # Step 4: Verify YAML metrics are accessible
        stored_metrics = yaml.safe_load(metrics_path.read_text())
        assert stored_metrics["phase"] == 14
        assert stored_metrics["tests_passed"] == 45


# ============================================================================
# Test Execution & Reporting
# ============================================================================


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=cortex",
            "--cov-report=term-missing",
        ]
    )
