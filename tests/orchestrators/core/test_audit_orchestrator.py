"""Tests for AuditOrchestrator — filesystem check delegation to HealthOrchestrator.

CORE-008: Tests written FIRST (RED phase).
Verifies that AuditOrchestrator delegates filesystem checks (root clutter #6,
deprecated files #9) to HealthOrchestrator rather than reimplementing them.

AC-AUDIT-001, AC-AUDIT-002, AC-AUDIT-003
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.orchestrators.core.audit_orchestrator import AuditOrchestrator


class TestAuditOrchestratorInit:
    """AuditOrchestrator initialises correctly."""

    def test_default_workspace_root_is_none(self) -> None:
        """workspace_root defaults to None when not provided."""
        auditor = AuditOrchestrator()
        assert auditor.workspace_root is None

    def test_workspace_root_stored(self) -> None:
        """workspace_root is stored when provided."""
        auditor = AuditOrchestrator(workspace_root="/tmp/test")
        assert auditor.workspace_root == "/tmp/test"

    def test_audit_results_initialised_empty(self) -> None:
        """audit_results starts as an empty dict."""
        auditor = AuditOrchestrator()
        assert auditor.audit_results == {}


class TestAuditOrchestratorDelegatesFilesystemChecks:
    """AUDIT checks #6 and #9 delegate to HealthOrchestrator (no duplication)."""

    def test_check_root_clutter_delegates_to_health_orchestrator(self) -> None:
        """Check #6 (root clutter) calls HealthOrchestrator.scan(), not custom logic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = AuditOrchestrator(workspace_root=tmpdir)

            mock_scan_result = MagicMock()
            mock_scan_result.issues = []

            with patch(
                "cortex.orchestrators.core.audit_orchestrator.HealthOrchestrator"
            ) as MockHealth:
                mock_instance = MockHealth.return_value
                mock_instance.scan.return_value = mock_scan_result

                result = auditor.check_root_clutter()

                MockHealth.assert_called_once_with(Path(tmpdir))
                mock_instance.scan.assert_called_once()
                assert isinstance(result, list)

    def test_check_deprecated_files_delegates_to_health_orchestrator(self) -> None:
        """Check #9 (deprecated files) calls HealthOrchestrator.scan(), not custom logic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = AuditOrchestrator(workspace_root=tmpdir)

            mock_scan_result = MagicMock()
            mock_scan_result.issues = []

            with patch(
                "cortex.orchestrators.core.audit_orchestrator.HealthOrchestrator"
            ) as MockHealth:
                mock_instance = MockHealth.return_value
                mock_instance.scan.return_value = mock_scan_result

                result = auditor.check_deprecated_files()

                MockHealth.assert_called_once_with(Path(tmpdir))
                mock_instance.scan.assert_called_once()
                assert isinstance(result, list)

    def test_check_root_clutter_filters_h009_issues_only(self) -> None:
        """check_root_clutter returns only H-009 issues from the health scan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = AuditOrchestrator(workspace_root=tmpdir)

            h009_issue = MagicMock()
            h009_issue.check_id = "H-009"
            h009_issue.path = Path("stray_script.py")

            h006_issue = MagicMock()
            h006_issue.check_id = "H-006"
            h006_issue.path = Path("old_module.py")

            mock_scan_result = MagicMock()
            mock_scan_result.issues = [h009_issue, h006_issue]

            with patch(
                "cortex.orchestrators.core.audit_orchestrator.HealthOrchestrator"
            ) as MockHealth:
                mock_instance = MockHealth.return_value
                mock_instance.scan.return_value = mock_scan_result

                result = auditor.check_root_clutter()

                assert len(result) == 1
                assert result[0].check_id == "H-009"

    def test_check_deprecated_files_filters_h006_issues_only(self) -> None:
        """check_deprecated_files returns only H-006 issues from the health scan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = AuditOrchestrator(workspace_root=tmpdir)

            h006_issue = MagicMock()
            h006_issue.check_id = "H-006"
            h006_issue.path = Path("legacy.py")

            h009_issue = MagicMock()
            h009_issue.check_id = "H-009"
            h009_issue.path = Path("stray.py")

            mock_scan_result = MagicMock()
            mock_scan_result.issues = [h006_issue, h009_issue]

            with patch(
                "cortex.orchestrators.core.audit_orchestrator.HealthOrchestrator"
            ) as MockHealth:
                mock_instance = MockHealth.return_value
                mock_instance.scan.return_value = mock_scan_result

                result = auditor.check_deprecated_files()

                assert len(result) == 1
                assert result[0].check_id == "H-006"

    def test_health_orchestrator_instantiated_with_path_object(self) -> None:
        """HealthOrchestrator receives a Path, not a raw string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = AuditOrchestrator(workspace_root=tmpdir)

            mock_scan_result = MagicMock()
            mock_scan_result.issues = []

            with patch(
                "cortex.orchestrators.core.audit_orchestrator.HealthOrchestrator"
            ) as MockHealth:
                mock_instance = MockHealth.return_value
                mock_instance.scan.return_value = mock_scan_result

                auditor.check_root_clutter()

                call_args = MockHealth.call_args[0][0]
                assert isinstance(call_args, Path), (
                    f"Expected Path, got {type(call_args)}"
                )

    def test_check_root_clutter_raises_without_workspace_root(self) -> None:
        """check_root_clutter raises ValueError when workspace_root is None."""
        auditor = AuditOrchestrator()
        with pytest.raises(ValueError, match="workspace_root"):
            auditor.check_root_clutter()

    def test_check_deprecated_files_raises_without_workspace_root(self) -> None:
        """check_deprecated_files raises ValueError when workspace_root is None."""
        auditor = AuditOrchestrator()
        with pytest.raises(ValueError, match="workspace_root"):
            auditor.check_deprecated_files()


class TestAuditOrchestratorNoDuplication:
    """Confirm AuditOrchestrator does NOT contain its own filesystem walk logic."""

    def test_audit_orchestrator_has_no_internal_root_walk(self) -> None:
        """AuditOrchestrator source does not contain a custom root directory walk."""
        import inspect
        import cortex.orchestrators.core.audit_orchestrator as mod

        source = inspect.getsource(mod)
        # These patterns indicate a reimplemented filesystem walk — forbidden
        forbidden_patterns = [
            "iterdir()",
            "os.listdir",
            "glob('*')",
            'glob("*")',
        ]
        for pattern in forbidden_patterns:
            assert pattern not in source, (
                f"AuditOrchestrator reimplements filesystem walk via '{pattern}'. "
                "Delegate to HealthOrchestrator instead (CORE-035)."
            )


class TestAuditOrchestratorExistingBehaviour:
    """Existing AuditOrchestrator behaviour is preserved (non-regression)."""

    def test_audit_returns_dict_with_mode(self) -> None:
        """audit() returns a dict containing the requested mode."""
        auditor = AuditOrchestrator()
        result = auditor.audit(mode="P0")
        assert result["mode"] == "P0"

    def test_audit_default_mode_is_hexa(self) -> None:
        """audit() defaults to HEXA mode."""
        auditor = AuditOrchestrator()
        result = auditor.audit()
        assert result["mode"] == "HEXA"

    def test_should_pass_all_passing(self) -> None:
        """should_pass returns True when all checks pass."""
        auditor = AuditOrchestrator()
        assert auditor.should_pass({"c1": {"status": "pass"}}) is True

    def test_should_pass_with_failure(self) -> None:
        """should_pass returns False when any check fails."""
        auditor = AuditOrchestrator()
        assert auditor.should_pass({"c1": {"status": "fail"}}) is False

    def test_run_p1_5_checks_returns_five_checks(self) -> None:
        """run_p1_5_checks returns exactly five P1.5 check results."""
        auditor = AuditOrchestrator()
        result = auditor.run_p1_5_checks()
        assert len(result) == 5
        assert all(k.startswith("P1.5-") for k in result)

    def test_generate_report_returns_dict(self) -> None:
        """generate_report returns a dict with expected keys."""
        auditor = AuditOrchestrator()
        report = auditor.generate_report()
        assert "results" in report
        assert "summary" in report
