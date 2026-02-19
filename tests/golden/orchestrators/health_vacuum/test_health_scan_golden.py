"""Golden Tests — HealthOrchestrator (GH-001 .. GH-010)

Each test is end-to-end: build workspace → scan → assert findings + audit log.

Phase: PHASE-51
CORE: CORE-008 (TDD), CORE-055 (golden test tier contract)
"""

from pathlib import Path
from typing import List

import pytest

from cortex.orchestrators.health.models import IssueFile, ScanResult


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Minimal workspace with various health issues baked in."""
    # Normal Python file
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "cortex" / "good_module.py").write_text("def hello():\n    pass\n")

    # --- H-001: Screaming case file ---
    (tmp_path / "AUDIT_REPORT.txt").write_text("old report\n")

    # --- H-002: Empty file ---
    (tmp_path / "empty.py").write_text("")

    # --- H-003: Orphaned directory ---
    (tmp_path / "orphaned_dir").mkdir()

    # --- H-005: Duplicate content ---
    (tmp_path / "cortex" / "util_a.py").write_text("# shared logic\nx = 1\n")
    (tmp_path / "cortex" / "util_b.py").write_text("# shared logic\nx = 1\n")

    # --- H-006: Deprecated marker ---
    (tmp_path / "cortex" / "old_module.py").write_text(
        "# DEPRECATED: remove after phase-99\ndef old():\n    pass\n"
    )

    # --- H-007: Markdown in wrong location ---
    (tmp_path / "cortex" / "RANDOM_NOTES.md").write_text("# random\n")

    # --- H-008: Naming violation (Python file with kebab) ---
    (tmp_path / "cortex" / "my-module.py").write_text("x = 1\n")

    # --- H-009: Root violations ---
    (tmp_path / "scratch_notes.txt").write_text("some scratch\n")

    # Standard root files (protected)
    (tmp_path / "README.md").write_text("# Project\n")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    (tmp_path / "conftest.py").write_text("")
    (tmp_path / ".gitignore").write_text("__pycache__/\n")

    return tmp_path


def _find_issues(result: ScanResult, check_id: str) -> List[IssueFile]:
    """Filter scan results to a specific check_id."""
    return [i for i in result.issues if i.check_id == check_id]


class TestGH001ScreamingCase:
    """GH-001: Screaming-case files detected with recommended kebab name."""

    def test_screaming_file_detected(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-001")
        assert len(issues) >= 1
        paths = {str(i.path) for i in issues}
        assert any("AUDIT_REPORT" in p for p in paths)

    def test_screaming_has_suggested_fix(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        issues = _find_issues(result, "H-001")
        for issue in issues:
            assert issue.suggested_fix is not None


class TestGH002EmptyFiles:
    """GH-002: Empty files detected (excluding __init__.py / .gitkeep)."""

    def test_empty_file_detected(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-002")
        assert len(issues) >= 1
        paths = {str(i.path) for i in issues}
        assert any("empty.py" in p for p in paths)

    def test_init_not_flagged(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-002")
        paths = {str(i.path) for i in issues}
        assert not any("__init__.py" in p for p in paths)


class TestGH003OrphanedDirectories:
    """GH-003: Orphaned (empty) directories detected."""

    def test_orphaned_dir_detected(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-003")
        assert len(issues) >= 1
        paths = {str(i.path) for i in issues}
        assert any("orphaned_dir" in p for p in paths)


class TestGH005DuplicateContent:
    """GH-005: Duplicate content detected via MD5 hash."""

    def test_duplicates_found(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-005")
        assert len(issues) >= 1


class TestGH006DeprecatedMarkers:
    """GH-006: Files with DEPRECATED markers detected."""

    def test_deprecated_detected(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-006")
        assert len(issues) >= 1
        paths = {str(i.path) for i in issues}
        assert any("old_module.py" in p for p in paths)


class TestGH007MarkdownLocation:
    """GH-007: Markdown files in wrong location detected."""

    def test_markdown_in_source_dir(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-007")
        assert len(issues) >= 1
        paths = {str(i.path) for i in issues}
        assert any("RANDOM_NOTES" in p for p in paths)


class TestGH008NamingViolations:
    """GH-008: Non-snake_case Python files or non-kebab-case others detected."""

    def test_python_kebab_detected(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-008")
        assert len(issues) >= 1
        paths = {str(i.path) for i in issues}
        assert any("my-module.py" in p for p in paths)


class TestGH009RootViolations:
    """GH-009: Files in project root that don't belong there."""

    def test_scratch_file_flagged(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-009")
        assert len(issues) >= 1
        paths = {str(i.path) for i in issues}
        assert any("scratch_notes.txt" in p for p in paths)

    def test_protected_files_not_flagged(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        issues = _find_issues(result, "H-009")
        paths = {str(i.path) for i in issues}
        # Protected files must NOT appear
        assert not any("README.md" in p for p in paths)
        assert not any("pyproject.toml" in p for p in paths)
        assert not any("conftest.py" in p for p in paths)


class TestGH010AggregatedReport:
    """GH-010: All findings aggregated into unified ScanResult."""

    def test_health_score_below_100(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()

        assert result.total_issues > 0
        assert result.health_score < 100.0

    def test_scan_result_serialisable(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        d = result.to_dict()
        assert "health_score" in d
        assert "issues" in d
        assert isinstance(d["issues"], list)
