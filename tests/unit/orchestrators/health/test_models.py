"""Unit Tests — models.py

Phase: PHASE-51
CORE: CORE-008 (TDD — tests first)
"""

from pathlib import Path


class TestScanResult:
    """ScanResult — aggregated output from HealthOrchestrator.scan()."""

    def test_construction(self) -> None:
        from cortex.orchestrators.health.models import ScanResult

        result = ScanResult(workspace_root=Path("/tmp/test"))
        assert result.workspace_root == Path("/tmp/test")
        assert result.issues == []
        assert result.health_score == 100.0

    def test_recount(self) -> None:
        from cortex.orchestrators.health.models import (
            ScanResult,
            IssueFile,
            IssueSeverity,
        )

        result = ScanResult(workspace_root=Path("/tmp/test"))
        result.issues.append(
            IssueFile(
                check_id="H-001",
                path=Path("foo.txt"),
                severity=IssueSeverity.HIGH,
                description="screaming case",
                suggested_fix="rename to foo.txt",
            )
        )
        result.recount()
        assert result.total_issues == 1
        assert result.high_issues == 1
        assert result.health_score < 100.0


class TestIssueFile:
    """IssueFile — single health finding."""

    def test_to_dict(self) -> None:
        from cortex.orchestrators.health.models import IssueFile, IssueSeverity

        issue = IssueFile(
            check_id="H-001",
            path=Path("FOO.txt"),
            severity=IssueSeverity.HIGH,
            description="Screaming case",
            suggested_fix="rename to foo.txt",
        )
        d = issue.to_dict()
        assert d["check_id"] == "H-001"
        assert d["path"] == "FOO.txt"
        assert d["severity"] == "high"

    def test_category_optional(self) -> None:
        from cortex.orchestrators.health.models import IssueFile, IssueSeverity

        issue = IssueFile(
            check_id="H-002",
            path=Path("empty.py"),
            severity=IssueSeverity.LOW,
            description="empty file",
        )
        assert issue.category is None


class TestOperationResult:
    """OperationResult — single vacuum operation."""

    def test_success(self) -> None:
        from cortex.orchestrators.health.models import OperationResult

        op = OperationResult(
            op_type="rename",
            source=Path("FOO.txt"),
            destination=Path("foo.txt"),
            success=True,
        )
        assert op.success is True
        assert op.error is None

    def test_failure(self) -> None:
        from cortex.orchestrators.health.models import OperationResult

        op = OperationResult(
            op_type="delete",
            source=Path("protected.py"),
            success=False,
            error="File is protected",
        )
        assert op.success is False
        assert "protected" in op.error


class TestVacuumReport:
    """VacuumReport — aggregated vacuum results."""

    def test_construction(self) -> None:
        from cortex.orchestrators.health.models import VacuumReport

        report = VacuumReport()
        assert report.operations == []
        assert report.total_operations == 0
        assert report.successful_operations == 0

    def test_add_operation(self) -> None:
        from cortex.orchestrators.health.models import VacuumReport, OperationResult

        report = VacuumReport()
        report.operations.append(
            OperationResult(
                op_type="rename",
                source=Path("FOO.txt"),
                destination=Path("foo.txt"),
                success=True,
            )
        )
        report.recount()
        assert report.total_operations == 1
        assert report.successful_operations == 1


class TestNamingViolation:
    """NamingViolation — returned by classify_naming_violation."""

    def test_construction(self) -> None:
        from cortex.orchestrators.health.models import NamingViolation

        v = NamingViolation(
            original_name="my-module.py",
            suggested_name="my_module.py",
            violation_type="non_snake_case",
        )
        assert v.original_name == "my-module.py"
        assert v.suggested_name == "my_module.py"
        assert v.violation_type == "non_snake_case"
