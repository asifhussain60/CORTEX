"""
Tests for EnforcementOrchestrator — CORE-008 TDD compliance.

Covers:
- CheckResult and EnforcementReport data models
- _check_markdown_artifacts (CORE-002)
- _check_file_naming (CORE-028)
- _check_tdd_gate (CORE-008)
- _check_health_policy (health rules)
- _check_mcp_policy (MCP server rules)
- EnforcementOrchestrator.run_checks() — integration

AC_START: AC-GIT-ORCH-003-TESTS
Testing: cortex/orchestrators/git/enforcement_orchestrator.py
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.orchestrators.git.enforcement_orchestrator import (
    CheckResult,
    EnforcementOrchestrator,
    EnforcementReport,
    _check_file_naming,
    _check_health_policy,
    _check_markdown_artifacts,
    _check_mcp_policy,
    _check_tdd_gate,
)


# ===========================================================================
# CheckResult
# ===========================================================================


class TestCheckResult:
    def test_passed_defaults(self) -> None:
        result = CheckResult(name="test_check", passed=True)
        assert result.passed is True
        assert result.violations == []
        assert result.skipped is False

    def test_failed_with_violations(self) -> None:
        result = CheckResult(
            name="test_check", passed=False, violations=["v1", "v2"]
        )
        assert result.passed is False
        assert len(result.violations) == 2

    def test_skipped_flag(self) -> None:
        result = CheckResult(name="test_check", passed=True, skipped=True)
        assert result.skipped is True


# ===========================================================================
# EnforcementReport
# ===========================================================================


class TestEnforcementReport:
    def test_passed_report(self) -> None:
        report = EnforcementReport(passed=True, checks=[], violations=[])
        assert report.passed is True

    def test_failed_report(self) -> None:
        report = EnforcementReport(
            passed=False, checks=[], violations=["CORE-002: blocked file"]
        )
        assert report.passed is False
        assert len(report.violations) == 1

    def test_run_checks_shim_returns_self(self) -> None:
        """Compatibility shim must return self."""
        report = EnforcementReport(passed=True)
        assert report.run_checks("/any/path") is report


# ===========================================================================
# _check_markdown_artifacts (CORE-002)
# ===========================================================================


class TestCheckMarkdownArtifacts:
    def test_blocked_report_md(self) -> None:
        result = _check_markdown_artifacts(["DEPLOYMENT-v1-REPORT.md"])
        assert result.passed is False
        assert any("CORE-002" in v for v in result.violations)

    def test_blocked_summary_md(self) -> None:
        result = _check_markdown_artifacts(["SESSION-SUMMARY.md"])
        assert result.passed is False

    def test_blocked_completion_md(self) -> None:
        result = _check_markdown_artifacts(["PHASE-01-COMPLETION.md"])
        assert result.passed is False

    def test_blocked_status_md(self) -> None:
        result = _check_markdown_artifacts(["ORCHESTRATOR-STATUS.md"])
        assert result.passed is False

    def test_allowed_docs_prefix(self) -> None:
        """Markdown under docs/ should be allowed."""
        result = _check_markdown_artifacts(["docs/architecture/DESIGN-REPORT.md"])
        assert result.passed is True

    def test_allowed_regular_readme(self) -> None:
        result = _check_markdown_artifacts(["README.md"])
        assert result.passed is True

    def test_no_markdown_files(self) -> None:
        result = _check_markdown_artifacts(["cortex/foo.py", "tests/test_foo.py"])
        assert result.passed is True

    def test_check_name(self) -> None:
        result = _check_markdown_artifacts([])
        assert result.name == "markdown_artifact_prevention"


# ===========================================================================
# _check_file_naming (CORE-028)
# ===========================================================================


class TestCheckFileNaming:
    def test_pascal_case_blocked(self) -> None:
        result = _check_file_naming(["cortex/MyClass.py"])
        assert result.passed is False
        assert any("CORE-028" in v for v in result.violations)

    def test_snake_case_allowed(self) -> None:
        result = _check_file_naming(["cortex/my_class.py"])
        assert result.passed is True

    def test_dunder_files_allowed(self) -> None:
        result = _check_file_naming(["cortex/__init__.py", "cortex/__main__.py"])
        assert result.passed is True

    def test_non_python_files_ignored(self) -> None:
        result = _check_file_naming(["cortex/MyModule.ts", "README.md"])
        assert result.passed is True

    def test_multiple_violations(self) -> None:
        result = _check_file_naming(["cortex/FooBar.py", "cortex/BazQux.py"])
        assert result.passed is False
        assert len(result.violations) == 2

    def test_check_name(self) -> None:
        result = _check_file_naming([])
        assert result.name == "file_naming_snake_case"


# ===========================================================================
# _check_tdd_gate (CORE-008)
# ===========================================================================


class TestCheckTddGate:
    def test_pass_when_test_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "cortex" / "foo.py"
            src.parent.mkdir(parents=True)
            src.write_text("x = 1")
            test = Path(tmpdir) / "tests" / "unit" / "test_foo.py"
            test.parent.mkdir(parents=True)
            test.write_text("def test_x(): pass")
            result = _check_tdd_gate(["cortex/foo.py"], tmpdir)
        assert result.passed is True

    def test_fail_when_no_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "cortex" / "bar.py"
            src.parent.mkdir(parents=True)
            src.write_text("x = 1")
            result = _check_tdd_gate(["cortex/bar.py"], tmpdir)
        assert result.passed is False
        assert any("CORE-008" in v for v in result.violations)

    def test_test_files_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _check_tdd_gate(["tests/unit/test_foo.py"], tmpdir)
        assert result.passed is True

    def test_non_cortex_files_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _check_tdd_gate(["scripts/generate.py"], tmpdir)
        assert result.passed is True

    def test_init_files_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _check_tdd_gate(["cortex/__init__.py"], tmpdir)
        assert result.passed is True

    def test_check_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _check_tdd_gate([], tmpdir)
        assert result.name == "tdd_gate"


# ===========================================================================
# _check_health_policy
# ===========================================================================


class TestCheckHealthPolicy:
    def test_versioned_filename_blocked(self) -> None:
        result = _check_health_policy(["cortex/orchestrator_v2.py"])
        assert result.passed is False

    def test_backup_file_blocked(self) -> None:
        result = _check_health_policy(["cortex/config.backup"])
        assert result.passed is False

    def test_old_file_blocked(self) -> None:
        result = _check_health_policy(["cortex/config.old"])
        assert result.passed is False

    def test_bak_file_blocked(self) -> None:
        result = _check_health_policy(["cortex/config.bak"])
        assert result.passed is False

    def test_root_db_blocked(self) -> None:
        result = _check_health_policy(["data.db"])
        assert result.passed is False

    def test_nested_db_allowed(self) -> None:
        """DB files in subdirectories are allowed."""
        result = _check_health_policy(["cortex_intelligence/governance.db"])
        assert result.passed is True

    def test_clean_files_pass(self) -> None:
        result = _check_health_policy(["cortex/my_module.py", "README.md"])
        assert result.passed is True

    def test_check_name(self) -> None:
        result = _check_health_policy([])
        assert result.name == "health_policy"


# ===========================================================================
# _check_mcp_policy
# ===========================================================================


class TestCheckMcpPolicy:
    def test_pass_when_only_cortex_server(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mcp_file = Path(tmpdir) / "mcp.json"
            mcp_file.write_text(json.dumps({"servers": {"cortex": {}}}))
            result = _check_mcp_policy(["mcp.json"], tmpdir)
        assert result.passed is True

    def test_fail_when_non_cortex_server(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mcp_file = Path(tmpdir) / "mcp.json"
            mcp_file.write_text(
                json.dumps({"servers": {"cortex": {}, "other-tool": {}}})
            )
            result = _check_mcp_policy(["mcp.json"], tmpdir)
        assert result.passed is False
        assert any("other-tool" in v for v in result.violations)

    def test_no_mcp_files_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _check_mcp_policy(["cortex/foo.py"], tmpdir)
        assert result.passed is True

    def test_missing_file_skipped(self) -> None:
        """A staged mcp.json that doesn't exist yet should not fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _check_mcp_policy(["mcp.json"], tmpdir)
        assert result.passed is True

    def test_check_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _check_mcp_policy([], tmpdir)
        assert result.name == "mcp_policy"


# ===========================================================================
# EnforcementOrchestrator.run_checks() — integration
# ===========================================================================


class TestEnforcementOrchestrator:
    def _make_orchestrator(self, strict: bool = True) -> EnforcementOrchestrator:
        return EnforcementOrchestrator(strict=strict)

    def test_clean_repo_passes(self) -> None:
        """No staged files → all checks pass."""
        orch = self._make_orchestrator()
        with patch.object(orch, "_get_staged_files", return_value=[]):
            with patch.object(
                orch,
                "_run_pre_commit_validator",
                return_value=CheckResult(name="wiring_health", passed=True),
            ):
                report = orch.run_checks("/fake/repo")
        assert report.passed is True
        assert report.violations == []

    def test_markdown_violation_fails(self) -> None:
        orch = self._make_orchestrator()
        with patch.object(
            orch, "_get_staged_files", return_value=["PHASE-01-REPORT.md"]
        ):
            with patch.object(
                orch,
                "_run_pre_commit_validator",
                return_value=CheckResult(name="wiring_health", passed=True),
            ):
                report = orch.run_checks("/fake/repo")
        assert report.passed is False
        assert any("CORE-002" in v for v in report.violations)

    def test_naming_violation_fails(self) -> None:
        orch = self._make_orchestrator()
        with patch.object(
            orch, "_get_staged_files", return_value=["cortex/MyBadFile.py"]
        ):
            with patch.object(
                orch,
                "_run_pre_commit_validator",
                return_value=CheckResult(name="wiring_health", passed=True),
            ):
                report = orch.run_checks("/fake/repo")
        assert report.passed is False
        assert any("CORE-028" in v for v in report.violations)

    def test_health_violation_fails(self) -> None:
        orch = self._make_orchestrator()
        with patch.object(
            orch, "_get_staged_files", return_value=["cortex/old_config.bak"]
        ):
            with patch.object(
                orch,
                "_run_pre_commit_validator",
                return_value=CheckResult(name="wiring_health", passed=True),
            ):
                report = orch.run_checks("/fake/repo")
        assert report.passed is False

    def test_wiring_health_failure_fails(self) -> None:
        orch = self._make_orchestrator()
        with patch.object(orch, "_get_staged_files", return_value=[]):
            with patch.object(
                orch,
                "_run_pre_commit_validator",
                return_value=CheckResult(
                    name="wiring_health",
                    passed=False,
                    violations=["Wiring health check failed"],
                ),
            ):
                report = orch.run_checks("/fake/repo")
        assert report.passed is False

    def test_strict_false_downgrades_tdd(self) -> None:
        """In non-strict mode, missing tests are warnings not blockers."""
        orch = self._make_orchestrator(strict=False)
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "cortex" / "no_test_impl.py"
            src.parent.mkdir(parents=True)
            src.write_text("x = 1")
            with patch.object(
                orch, "_get_staged_files", return_value=["cortex/no_test_impl.py"]
            ):
                with patch.object(
                    orch,
                    "_run_pre_commit_validator",
                    return_value=CheckResult(name="wiring_health", passed=True),
                ):
                    report = orch.run_checks(tmpdir)
        # Should pass because TDD is skipped in non-strict mode
        assert report.passed is True

    def test_report_contains_all_checks(self) -> None:
        orch = self._make_orchestrator()
        with patch.object(orch, "_get_staged_files", return_value=[]):
            with patch.object(
                orch,
                "_run_pre_commit_validator",
                return_value=CheckResult(name="wiring_health", passed=True),
            ):
                report = orch.run_checks("/fake/repo")
        assert len(report.checks) == 6  # 5 function checks + wiring health

    def test_multiple_violations_aggregated(self) -> None:
        orch = self._make_orchestrator()
        staged = ["PHASE-REPORT.md", "cortex/BadName.py", "config.bak"]
        with patch.object(orch, "_get_staged_files", return_value=staged):
            with patch.object(
                orch,
                "_run_pre_commit_validator",
                return_value=CheckResult(name="wiring_health", passed=True),
            ):
                report = orch.run_checks("/fake/repo")
        assert report.passed is False
        # Expect violations from markdown, naming, and health checks
        assert len(report.violations) >= 3

# AC_COMPLETE: AC-GIT-ORCH-003-TESTS ✅
