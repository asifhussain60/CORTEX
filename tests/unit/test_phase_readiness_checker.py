"""
Unit tests for Phase Readiness Checker.

Tests all 4 readiness stages:
1. Governance compliance validation
2. Audit trail verification
3. Test coverage validation
4. Documentation completeness
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Generator, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.phase_readiness_checker import (
    PhaseReadinessChecker,
    PhaseReadinessReport,
    ReadinessCheckResult,
    ReadinessLevel,
    ReadinessStage,
)


class TestReadinessDataStructures:
    """Test data structure classes."""

    def test_readiness_check_result_to_dict(self) -> None:
        """Test ReadinessCheckResult.to_dict() method."""
        result = ReadinessCheckResult(
            stage=ReadinessStage.GOVERNANCE,
            passed=True,
            level=ReadinessLevel.INFO,
            message="Test message",
            details=["detail1", "detail2"],
        )

        data = result.to_dict()

        assert data["stage"] == "governance"
        assert data["passed"] is True
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["details"] == ["detail1", "detail2"]

    def test_phase_readiness_report_to_dict(self) -> None:
        """Test PhaseReadinessReport.to_dict() method."""
        check = ReadinessCheckResult(
            stage=ReadinessStage.TESTS,
            passed=True,
            level=ReadinessLevel.INFO,
            message="All tests pass",
        )

        report = PhaseReadinessReport(
            phase_id="PHASE-09",
            ready_for_lock=True,
            overall_percentage=100.0,
            checks=[check],
            blockers=[],
            recommendations=["Ready to lock"],
            timestamp="2024-01-01T00:00:00Z",
        )

        data = report.to_dict()

        assert data["phase_id"] == "PHASE-09"
        assert data["ready_for_lock"] is True
        assert data["overall_percentage"] == 100.0
        assert len(data["checks"]) == 1
        assert data["timestamp"] == "2024-01-01T00:00:00Z"

    def test_readiness_stage_enum_values(self) -> None:
        """Test ReadinessStage enum."""
        assert ReadinessStage.GOVERNANCE.value == "governance"
        assert ReadinessStage.AUDIT.value == "audit"
        assert ReadinessStage.TESTS.value == "tests"
        assert ReadinessStage.DOCUMENTATION.value == "documentation"

    def test_readiness_level_enum_values(self) -> None:
        """Test ReadinessLevel enum."""
        assert ReadinessLevel.CRITICAL.value == 0
        assert ReadinessLevel.WARNING.value == 1
        assert ReadinessLevel.INFO.value == 2


class TestPhaseReadinessChecker:
    """Test PhaseReadinessChecker class."""

    @pytest.fixture
    def temp_workspace(self) -> Generator[Path, Any, Any]:
        """Create temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "src" / "tools").mkdir(parents=True)
            (workspace / "cortex-brain" / "state").mkdir(parents=True)
            (workspace / "docs" / "phases").mkdir(parents=True)
            (workspace / "tests").mkdir(parents=True)

            # Create dummy governance CLI
            cli_path = workspace / "src" / "tools" / "governance-cli.py"
            cli_path.write_text("#!/usr/bin/env python3\nprint('governance-cli')")

            yield workspace

    def test_checker_initialization(self, temp_workspace: Path) -> None:
        """Test PhaseReadinessChecker initialization."""
        checker = PhaseReadinessChecker(temp_workspace)

        assert checker.workspace_root == temp_workspace
        assert checker.cli_script == temp_workspace / "src" / "tools" / "governance-cli.py"
        assert checker.governance_db == temp_workspace / "cortex-brain" / "state" / "governance.db"

    def test_checker_default_workspace(self) -> None:
        """Test PhaseReadinessChecker with default workspace."""
        checker = PhaseReadinessChecker()

        assert checker.workspace_root == Path.cwd()

    def test_get_phase_directory(self, temp_workspace: Path) -> None:
        """Test _get_phase_directory method."""
        checker = PhaseReadinessChecker(temp_workspace)

        phase_dir = checker._get_phase_directory("PHASE-09")

        assert phase_dir == temp_workspace / "src" / "phases" / "phase-09"

    def test_check_governance_compliance_no_cli(self, temp_workspace: Path) -> None:
        """Test governance compliance check when CLI not found."""
        # Remove the CLI script
        cli_path = temp_workspace / "src" / "tools" / "governance-cli.py"
        cli_path.unlink()

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_governance_compliance("PHASE-09")

        assert result.stage == ReadinessStage.GOVERNANCE
        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING
        assert "not found" in result.message

    def test_check_governance_compliance_no_phase_dir(self, temp_workspace: Path) -> None:
        """Test governance compliance check when phase directory doesn't exist."""
        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_governance_compliance("PHASE-99")

        assert result.stage == ReadinessStage.GOVERNANCE
        assert result.passed is True
        assert result.level == ReadinessLevel.INFO
        assert "N/A" in result.message

    @patch('subprocess.run')
    def test_check_governance_compliance_success(self, mock_run, temp_workspace: Path) -> None:
        """Test governance compliance check success."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Create phase directory
        phase_dir = temp_workspace / "src" / "phases" / "phase-09"
        phase_dir.mkdir(parents=True)

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_governance_compliance("PHASE-09")

        assert result.stage == ReadinessStage.GOVERNANCE
        assert result.passed is True
        assert result.level == ReadinessLevel.INFO
        assert "complies" in result.message.lower()

    @patch('subprocess.run')
    def test_check_governance_compliance_violations(self, mock_run, temp_workspace: Path) -> None:
        """Test governance compliance check with violations."""
        violations_output = json.dumps({
            "violations": [
                {"rule_id": "CORE-008", "message": "Missing type hints", "severity": "warning"},
                {"rule_id": "CORE-012", "message": "Missing docstring", "severity": "warning"},
            ]
        })
        mock_run.return_value = Mock(returncode=1, stdout=violations_output, stderr="")

        # Create phase directory
        phase_dir = temp_workspace / "src" / "phases" / "phase-09"
        phase_dir.mkdir(parents=True)

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_governance_compliance("PHASE-09")

        assert result.stage == ReadinessStage.GOVERNANCE
        assert result.passed is True  # No CRITICAL violations
        assert result.level == ReadinessLevel.WARNING
        assert "2" in result.message

    @patch('subprocess.run')
    def test_check_governance_compliance_critical(self, mock_run, temp_workspace: Path) -> None:
        """Test governance compliance check with critical violations."""
        violations_output = json.dumps({
            "violations": [
                {"rule_id": "CORE-013", "message": "Bare except", "severity": "blocked"},
            ]
        })
        mock_run.return_value = Mock(returncode=1, stdout=violations_output, stderr="")

        # Create phase directory
        phase_dir = temp_workspace / "src" / "phases" / "phase-09"
        phase_dir.mkdir(parents=True)

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_governance_compliance("PHASE-09")

        assert result.stage == ReadinessStage.GOVERNANCE
        assert result.passed is False
        assert result.level == ReadinessLevel.CRITICAL

    @patch('subprocess.run')
    def test_check_governance_compliance_timeout(self, mock_run, temp_workspace: Path) -> None:
        """Test governance compliance check timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("test", 10)

        # Create phase directory to trigger subprocess call
        phase_dir = temp_workspace / "src" / "phases" / "phase-09"
        phase_dir.mkdir(parents=True)

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_governance_compliance("PHASE-09")

        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING
        assert "timeout" in result.message.lower()

    def test_check_audit_trail_no_db(self, temp_workspace: Path) -> None:
        """Test audit trail check when database doesn't exist."""
        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_audit_trail("PHASE-09")

        assert result.stage == ReadinessStage.AUDIT
        assert result.passed is False
        assert result.level == ReadinessLevel.CRITICAL
        assert "not found" in result.message

    def test_check_audit_trail_invalid_phase_id(self, temp_workspace: Path) -> None:
        """Test audit trail check with invalid phase ID."""
        # Create empty database
        db_path = temp_workspace / "cortex-brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE audit_log (ac_id TEXT)")
        conn.close()

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_audit_trail("INVALID")

        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING
        assert "parse" in result.message.lower()

    def test_check_audit_trail_no_entries(self, temp_workspace: Path) -> None:
        """Test audit trail check with no entries."""
        # Create database with audit_log table
        db_path = temp_workspace / "cortex-brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE audit_log (ac_id TEXT)")
        conn.close()

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_audit_trail("PHASE-09")

        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING
        assert "No audit entries" in result.message

    def test_check_audit_trail_incomplete_entries(self, temp_workspace: Path) -> None:
        """Test audit trail check with incomplete entries."""
        # Create database with audit entries (only 2 entries, need 3)
        # AC-GV-001-09 means AC for GV domain, AC number 001, phase 09
        db_path = temp_workspace / "cortex-brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE audit_log (ac_id TEXT)")
        conn.execute("INSERT INTO audit_log VALUES ('AC-GV-001-09')")
        conn.execute("INSERT INTO audit_log VALUES ('AC-GV-001-09')")
        conn.commit()
        conn.close()

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_audit_trail("PHASE-09")

        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING
        # Check message mentions incomplete ACs
        assert "AC" in result.message or "missing" in result.message.lower()

    def test_check_audit_trail_complete_entries(self, temp_workspace: Path) -> None:
        """Test audit trail check with complete entries."""
        # Create database with complete audit entries (3+ per AC)
        # AC-GV-001-09 means AC for GV domain, AC number 001, phase 09
        db_path = temp_workspace / "cortex-brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE audit_log (ac_id TEXT)")
        # Add 3 entries for AC-GV-001-09
        conn.execute("INSERT INTO audit_log VALUES ('AC-GV-001-09')")
        conn.execute("INSERT INTO audit_log VALUES ('AC-GV-001-09')")
        conn.execute("INSERT INTO audit_log VALUES ('AC-GV-001-09')")
        conn.commit()
        conn.close()

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_audit_trail("PHASE-09")

        assert result.passed is True
        assert result.level == ReadinessLevel.INFO
        assert "verified" in result.message.lower()

    @patch('subprocess.run')
    def test_check_test_coverage_no_tests(self, mock_run, temp_workspace: Path) -> None:
        """Test coverage check with no tests."""
        mock_run.return_value = Mock(returncode=0, stdout="0 passed", stderr="")

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_test_coverage("PHASE-09")

        assert result.stage == ReadinessStage.TESTS
        assert result.passed is True
        assert result.level == ReadinessLevel.INFO

    @patch('subprocess.run')
    def test_check_test_coverage_passing(self, mock_run, temp_workspace: Path) -> None:
        """Test coverage check with passing tests."""
        mock_run.return_value = Mock(returncode=0, stdout="42 passed in 1.23s", stderr="")

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_test_coverage("PHASE-09")

        assert result.stage == ReadinessStage.TESTS
        assert result.passed is True
        assert result.level == ReadinessLevel.INFO
        assert "42" in result.message

    @patch('subprocess.run')
    def test_check_test_coverage_failures(self, mock_run, temp_workspace: Path) -> None:
        """Test coverage check with test failures."""
        mock_run.return_value = Mock(returncode=1, stdout="5 failed, 37 passed", stderr="")

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_test_coverage("PHASE-09")

        assert result.stage == ReadinessStage.TESTS
        assert result.passed is False
        assert result.level == ReadinessLevel.CRITICAL
        assert "5 failed" in result.message

    @patch('subprocess.run')
    def test_check_test_coverage_timeout(self, mock_run, temp_workspace: Path) -> None:
        """Test coverage check timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("test", 30)

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_test_coverage("PHASE-09")

        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING

    def test_check_documentation_no_yaml(self, temp_workspace: Path) -> None:
        """Test documentation check with no phase YAML."""
        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_documentation("PHASE-09")

        assert result.stage == ReadinessStage.DOCUMENTATION
        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING
        assert "not found" in result.message

    def test_check_documentation_missing_status(self, temp_workspace: Path) -> None:
        """Test documentation check with missing status."""
        phase_yaml = temp_workspace / "docs" / "phases" / "phase-phase-09.yaml"
        phase_yaml.write_text("name: PHASE-09\nacs: 8\n")

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_documentation("PHASE-09")

        assert result.passed is False
        assert result.level == ReadinessLevel.WARNING
        assert "completion status" in result.message

    def test_check_documentation_completed(self, temp_workspace: Path) -> None:
        """Test documentation check with completed status."""
        phase_yaml = temp_workspace / "docs" / "phases" / "phase-phase-09.yaml"
        phase_yaml.write_text("name: PHASE-09\nstatus: COMPLETED\n")

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_documentation("PHASE-09")

        assert result.passed is True
        assert result.level == ReadinessLevel.INFO
        assert "updated" in result.message

    def test_check_documentation_completed_quoted(self, temp_workspace: Path) -> None:
        """Test documentation check with quoted completed status."""
        phase_yaml = temp_workspace / "docs" / "phases" / "phase-phase-09.yaml"
        phase_yaml.write_text('name: PHASE-09\nstatus: "COMPLETED"\n')

        checker = PhaseReadinessChecker(temp_workspace)
        result = checker._check_documentation("PHASE-09")

        assert result.passed is True
        assert result.level == ReadinessLevel.INFO


class TestPhaseReadinessReport:
    """Test phase readiness report generation."""

    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_governance_compliance')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_audit_trail')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_test_coverage')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_documentation')
    def test_check_phase_readiness_all_pass(
        self,
        mock_doc: Mock,
        mock_test: Mock,
        mock_audit: Mock,
        mock_gov: Mock,
    ) -> None:
        """Test phase readiness when all checks pass."""
        mock_gov.return_value = ReadinessCheckResult(
            stage=ReadinessStage.GOVERNANCE,
            passed=True,
            level=ReadinessLevel.INFO,
            message="OK",
        )
        mock_audit.return_value = ReadinessCheckResult(
            stage=ReadinessStage.AUDIT,
            passed=True,
            level=ReadinessLevel.INFO,
            message="OK",
        )
        mock_test.return_value = ReadinessCheckResult(
            stage=ReadinessStage.TESTS,
            passed=True,
            level=ReadinessLevel.INFO,
            message="OK",
        )
        mock_doc.return_value = ReadinessCheckResult(
            stage=ReadinessStage.DOCUMENTATION,
            passed=True,
            level=ReadinessLevel.INFO,
            message="OK",
        )

        checker = PhaseReadinessChecker()
        report = checker.check_phase_readiness("PHASE-09")

        assert report.phase_id == "PHASE-09"
        assert report.ready_for_lock is True
        assert report.overall_percentage == 100.0
        assert len(report.checks) == 4
        assert len(report.blockers) == 0

    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_governance_compliance')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_audit_trail')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_test_coverage')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_documentation')
    def test_check_phase_readiness_critical_blocker(
        self,
        mock_doc: Mock,
        mock_test: Mock,
        mock_audit: Mock,
        mock_gov: Mock,
    ) -> None:
        """Test phase readiness with critical blocker."""
        mock_gov.return_value = ReadinessCheckResult(
            stage=ReadinessStage.GOVERNANCE,
            passed=False,
            level=ReadinessLevel.CRITICAL,
            message="Violations found",
        )
        mock_audit.return_value = ReadinessCheckResult(
            stage=ReadinessStage.AUDIT,
            passed=True,
            level=ReadinessLevel.INFO,
            message="OK",
        )
        mock_test.return_value = ReadinessCheckResult(
            stage=ReadinessStage.TESTS,
            passed=True,
            level=ReadinessLevel.INFO,
            message="OK",
        )
        mock_doc.return_value = ReadinessCheckResult(
            stage=ReadinessStage.DOCUMENTATION,
            passed=True,
            level=ReadinessLevel.INFO,
            message="OK",
        )

        checker = PhaseReadinessChecker()
        report = checker.check_phase_readiness("PHASE-09")

        assert report.ready_for_lock is False
        assert len(report.blockers) > 0
        assert report.overall_percentage == 75.0

    def test_generate_recommendations_ready(self) -> None:
        """Test recommendation generation when ready."""
        checks = [
            ReadinessCheckResult(ReadinessStage.GOVERNANCE, True, ReadinessLevel.INFO, "OK"),
            ReadinessCheckResult(ReadinessStage.AUDIT, True, ReadinessLevel.INFO, "OK"),
            ReadinessCheckResult(ReadinessStage.TESTS, True, ReadinessLevel.INFO, "OK"),
            ReadinessCheckResult(ReadinessStage.DOCUMENTATION, True, ReadinessLevel.INFO, "OK"),
        ]
        report = PhaseReadinessReport(
            phase_id="PHASE-09",
            ready_for_lock=True,
            overall_percentage=100.0,
            checks=checks,
        )

        checker = PhaseReadinessChecker()
        recommendations = checker._generate_recommendations(report)

        assert len(recommendations) > 0
        assert any("lock" in r.lower() for r in recommendations)


class TestAcceptanceCriteriaGV00402:
    """Test Acceptance Criteria for GV-004-02."""

    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_governance_compliance')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_audit_trail')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_test_coverage')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_documentation')
    def test_ac_1_readiness_validator_checks_all_stages(
        self,
        mock_doc: Mock,
        mock_test: Mock,
        mock_audit: Mock,
        mock_gov: Mock,
    ) -> None:
        """AC-GV-004-02-01: Validator checks all 4 stages."""
        mock_gov.return_value = ReadinessCheckResult(
            ReadinessStage.GOVERNANCE, True, ReadinessLevel.INFO, "OK"
        )
        mock_audit.return_value = ReadinessCheckResult(
            ReadinessStage.AUDIT, True, ReadinessLevel.INFO, "OK"
        )
        mock_test.return_value = ReadinessCheckResult(
            ReadinessStage.TESTS, True, ReadinessLevel.INFO, "OK"
        )
        mock_doc.return_value = ReadinessCheckResult(
            ReadinessStage.DOCUMENTATION, True, ReadinessLevel.INFO, "OK"
        )

        checker = PhaseReadinessChecker()
        report = checker.check_phase_readiness("PHASE-09")

        # Verify all 4 stages are checked
        stages_checked = {c.stage for c in report.checks}
        assert stages_checked == {
            ReadinessStage.GOVERNANCE,
            ReadinessStage.AUDIT,
            ReadinessStage.TESTS,
            ReadinessStage.DOCUMENTATION,
        }

    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_governance_compliance')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_audit_trail')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_test_coverage')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_documentation')
    def test_ac_2_clear_pass_fail_report(
        self,
        mock_doc: Mock,
        mock_test: Mock,
        mock_audit: Mock,
        mock_gov: Mock,
    ) -> None:
        """AC-GV-004-02-02: Report clearly indicates pass/fail."""
        # Test PASS case
        mock_gov.return_value = ReadinessCheckResult(
            ReadinessStage.GOVERNANCE, True, ReadinessLevel.INFO, "OK"
        )
        mock_audit.return_value = ReadinessCheckResult(
            ReadinessStage.AUDIT, True, ReadinessLevel.INFO, "OK"
        )
        mock_test.return_value = ReadinessCheckResult(
            ReadinessStage.TESTS, True, ReadinessLevel.INFO, "OK"
        )
        mock_doc.return_value = ReadinessCheckResult(
            ReadinessStage.DOCUMENTATION, True, ReadinessLevel.INFO, "OK"
        )

        checker = PhaseReadinessChecker()
        report_pass = checker.check_phase_readiness("PHASE-09")

        assert report_pass.ready_for_lock is True
        assert report_pass.overall_percentage == 100.0
        assert len(report_pass.recommendations) > 0

        # Test FAIL case
        mock_gov.return_value = ReadinessCheckResult(
            ReadinessStage.GOVERNANCE, False, ReadinessLevel.CRITICAL, "Violations"
        )

        report_fail = checker.check_phase_readiness("PHASE-09")

        assert report_fail.ready_for_lock is False
        assert report_fail.overall_percentage == 75.0
        assert len(report_fail.blockers) > 0

    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_governance_compliance')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_audit_trail')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_test_coverage')
    @patch('src.tools.phase_readiness_checker.PhaseReadinessChecker._check_documentation')
    def test_ac_3_phase_lock_integration(
        self,
        mock_doc: Mock,
        mock_test: Mock,
        mock_audit: Mock,
        mock_gov: Mock,
    ) -> None:
        """AC-GV-004-02-03: Report integrates with phase lock mechanism."""
        # Scenario: Block phase lock if critical issues
        mock_gov.return_value = ReadinessCheckResult(
            ReadinessStage.GOVERNANCE, False, ReadinessLevel.CRITICAL, "Type errors"
        )
        mock_audit.return_value = ReadinessCheckResult(
            ReadinessStage.AUDIT, True, ReadinessLevel.INFO, "OK"
        )
        mock_test.return_value = ReadinessCheckResult(
            ReadinessStage.TESTS, True, ReadinessLevel.INFO, "OK"
        )
        mock_doc.return_value = ReadinessCheckResult(
            ReadinessStage.DOCUMENTATION, True, ReadinessLevel.INFO, "OK"
        )

        checker = PhaseReadinessChecker()
        report = checker.check_phase_readiness("PHASE-09")

        # Phase should NOT be lockable
        assert report.ready_for_lock is False

        # Blockers should list the critical issues
        assert len(report.blockers) > 0
        assert any("Governance" in b for b in report.blockers)
