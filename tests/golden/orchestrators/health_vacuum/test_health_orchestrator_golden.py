"""
Golden Tests: HealthOrchestrator — Phase 48
Scenarios GH-001 to GH-007

TDD: RED phase — these tests drive the implementation.
Authority: Phase 48, CORE-008, CORE-028, CORE-002
"""

import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile
import os


# ===========================================================================
# FIXTURES
# ===========================================================================


@pytest.fixture
def tmp_repo(tmp_path):
    """Create a temporary repo structure for testing."""
    (tmp_path / "cortex").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "_workspaces").mkdir()
    (tmp_path / "scripts").mkdir()
    return tmp_path


@pytest.fixture
def health_orchestrator(tmp_repo):
    """Instantiate HealthOrchestrator pointed at temp repo."""
    from cortex.orchestrators.support.health_orchestrator import HealthOrchestrator
    return HealthOrchestrator(workspace_root=tmp_repo)


# ===========================================================================
# GH-001: Screaming Case Detection
# ===========================================================================


class TestScreamingCaseDetection:
    """GH-001: Files with 3+ consecutive uppercase chars flagged."""

    def test_detects_screaming_case_txt(self, tmp_repo, health_orchestrator):
        """WAVE-1-CERTIFICATE.txt → screaming_case issue."""
        f = tmp_repo / "WAVE-1-CERTIFICATE.txt"
        f.write_text("content")

        result = health_orchestrator.scan()

        assert result.screaming_case.count >= 1
        paths = [i.path for i in result.screaming_case.files]
        assert any("WAVE-1-CERTIFICATE.txt" in p for p in paths)

    def test_detects_multiple_screaming_files(self, tmp_repo, health_orchestrator):
        """GH-001: Two screaming case files → count == 2."""
        (tmp_repo / "TEST-FILE.txt").write_text("a")
        (tmp_repo / "WAVE-1-CERT.txt").write_text("b")

        result = health_orchestrator.scan()

        assert result.screaming_case.count >= 2

    def test_screaming_file_has_recommended_name(self, tmp_repo, health_orchestrator):
        """GH-001: Each screaming issue carries recommended kebab name."""
        (tmp_repo / "AUDIT-REPORT.txt").write_text("x")

        result = health_orchestrator.scan()
        issue = next(
            i for i in result.screaming_case.files if "AUDIT-REPORT" in i.path
        )

        assert issue.recommended_name == "audit-report.txt"
        assert issue.action == "rename"

    def test_lowercase_files_not_flagged(self, tmp_repo, health_orchestrator):
        """GH-001: lowercase-file.txt → not flagged."""
        (tmp_repo / "lowercase-file.txt").write_text("ok")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.screaming_case.files]
        assert not any("lowercase-file.txt" in p for p in paths)


# ===========================================================================
# GH-002: Empty Files Detection
# ===========================================================================


class TestEmptyFileDetection:
    """GH-002: Zero-byte files flagged (excluding .gitkeep)."""

    def test_detects_empty_python_file(self, tmp_repo, health_orchestrator):
        """GH-002: Empty .py file flagged."""
        (tmp_repo / "cortex" / "stub.py").write_text("")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.empty_files.files]
        assert any("stub.py" in p for p in paths)

    def test_gitkeep_not_flagged(self, tmp_repo, health_orchestrator):
        """GH-002: .gitkeep exempted from empty file check."""
        (tmp_repo / ".gitkeep").write_text("")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.empty_files.files]
        assert not any(".gitkeep" in p for p in paths)

    def test_non_empty_file_not_flagged(self, tmp_repo, health_orchestrator):
        """GH-002: File with content not flagged."""
        (tmp_repo / "cortex" / "real.py").write_text("# real content\ndef foo(): pass")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.empty_files.files]
        assert not any("real.py" in p for p in paths)


# ===========================================================================
# GH-003: Orphaned Directory Detection
# ===========================================================================


class TestOrphanedDirectoryDetection:
    """GH-003: Empty directories flagged as orphaned."""

    def test_detects_empty_directory(self, tmp_repo, health_orchestrator):
        """GH-003: Empty dir → orphaned_directories issue."""
        empty_dir = tmp_repo / "cortex" / "wiring" / "specs"
        empty_dir.mkdir(parents=True)

        result = health_orchestrator.scan()

        dirs = [d.path for d in result.orphaned_directories.directories]
        assert any("specs" in d for d in dirs)

    def test_non_empty_directory_not_flagged(self, tmp_repo, health_orchestrator):
        """GH-003: Dir with children → not flagged."""
        d = tmp_repo / "cortex" / "active"
        d.mkdir(parents=True)
        (d / "file.py").write_text("content")

        result = health_orchestrator.scan()

        dirs = [p.path for p in result.orphaned_directories.directories]
        assert not any("active" in p for p in dirs)


# ===========================================================================
# GH-004: Wrong References Detection
# ===========================================================================


class TestWrongReferencesDetection:
    """GH-004: Stale module paths flagged for replacement."""

    def test_detects_cortex_brain_import(self, tmp_repo, health_orchestrator):
        """GH-004: 'from cortex_brain import' → wrong_references issue."""
        f = tmp_repo / "cortex" / "some_module.py"
        f.write_text("from cortex_brain import something\n")

        result = health_orchestrator.scan()

        assert result.wrong_references.count >= 1
        issue = next(
            i for i in result.wrong_references.files if "some_module.py" in i.path
        )
        assert "cortex_brain" in issue.old_ref
        assert "cortex_intelligence" in issue.new_ref
        assert issue.action == "fix"

    def test_correct_reference_not_flagged(self, tmp_repo, health_orchestrator):
        """GH-004: 'from cortex_intelligence import' → not flagged."""
        f = tmp_repo / "cortex" / "correct.py"
        f.write_text("from cortex_intelligence import something\n")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.wrong_references.files]
        assert not any("correct.py" in p for p in paths)


# ===========================================================================
# GH-005: Invalid Markdown Location
# ===========================================================================


class TestInvalidMarkdownLocation:
    """GH-005: Markdown outside allowed paths flagged (CORE-002)."""

    def test_detects_md_in_cortex_subdir(self, tmp_repo, health_orchestrator):
        """GH-005: cortex/agents/REPORT.md → invalid_markdown issue."""
        agents_dir = tmp_repo / "cortex" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "REPORT.md").write_text("# report")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.invalid_markdown.files]
        assert any("REPORT.md" in p for p in paths)

    def test_root_readme_allowed(self, tmp_repo, health_orchestrator):
        """GH-005: README.md at root is always allowed."""
        (tmp_repo / "README.md").write_text("# CORTEX")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.invalid_markdown.files]
        assert not any("README.md" in p for p in paths)

    def test_docs_subdir_allowed(self, tmp_repo, health_orchestrator):
        """GH-005: docs/**/*.md is always allowed."""
        docs = tmp_repo / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "guide.md").write_text("# Guide")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.invalid_markdown.files]
        assert not any("guide.md" in p for p in paths)


# ===========================================================================
# GH-006: Protected Files Never Flagged
# ===========================================================================


class TestProtectedFilesRespected:
    """GH-006: Protected files never appear in any issue category."""

    def test_readme_not_flagged_for_markdown(self, tmp_repo, health_orchestrator):
        """GH-006: README.md protected from invalid_markdown."""
        (tmp_repo / "README.md").write_text("# CORTEX")

        result = health_orchestrator.scan()

        all_paths = [i.path for i in result.invalid_markdown.files]
        assert not any("README.md" in p for p in all_paths)

    def test_pytest_ini_not_flagged(self, tmp_repo, health_orchestrator):
        """GH-006: pytest.ini protected from all checks."""
        (tmp_repo / "pytest.ini").write_text("[pytest]")

        result = health_orchestrator.scan()

        assert result.issues_for_path("pytest.ini") == []


# ===========================================================================
# GH-007: _workspaces Exception
# ===========================================================================


class TestWorkspacesException:
    """GH-007: _workspaces/ directory fully excluded from all checks."""

    def test_screaming_case_in_workspaces_ignored(self, tmp_repo, health_orchestrator):
        """GH-007: SCREAMING.md in _workspaces not flagged."""
        ws = tmp_repo / "_workspaces"
        ws.mkdir(exist_ok=True)
        (ws / "SCREAMING-CASE.md").write_text("# chat")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.screaming_case.files]
        assert not any("_workspaces" in p for p in paths)

    def test_invalid_md_in_workspaces_ignored(self, tmp_repo, health_orchestrator):
        """GH-007: .md in _workspaces not flagged for CORE-002."""
        ws = tmp_repo / "_workspaces"
        ws.mkdir(exist_ok=True)
        (ws / "chat01.md").write_text("# chat")

        result = health_orchestrator.scan()

        paths = [i.path for i in result.invalid_markdown.files]
        assert not any("_workspaces" in p for p in paths)
