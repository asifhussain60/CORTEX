"""
Tests for cortex.tools.toolkit.cleanup module (Phase 90 S4).

Authority: Phase 90 S-90-05
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from cortex.tools.toolkit.cleanup import (
    CleanupManager,
    CleanupResult,
    CleanupOperation,
)


class TestCleanupManager:
    """Test CleanupManager initialization and basic operations."""

    def test_init_with_workspace_root(self, tmp_path):
        """Test initialization with workspace root."""
        manager = CleanupManager(workspace_root=tmp_path)
        assert manager.workspace_root == tmp_path
        assert manager.dry_run is False

    def test_init_dry_run_mode(self, tmp_path):
        """Test initialization in dry-run mode."""
        manager = CleanupManager(workspace_root=tmp_path, dry_run=True)
        assert manager.dry_run is True

    def test_scan_markdown_sprawl(self, tmp_path):
        """Test scanning for markdown sprawl."""
        # Create test markdown files
        (tmp_path / "test-summary.md").write_text("# Summary")
        (tmp_path / "feature-report.md").write_text("# Report")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "architecture.md").write_text("# Architecture")

        manager = CleanupManager(workspace_root=tmp_path)
        results = manager.scan_markdown_sprawl()

        assert len(results) >= 2  # Should find *-summary.md and *-report.md
        assert any("summary" in r.file_path.name for r in results)

    def test_scan_debug_markers(self, tmp_path):
        """Test scanning for CORTEX_DEBUG markers."""
        # Create test Python file with debug markers
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "# CORTEX_DEBUG: Test marker\n"
            "def test_function():\n"
            "    pass\n"
        )

        manager = CleanupManager(workspace_root=tmp_path)
        results = manager.scan_debug_markers()

        assert len(results) >= 1
        assert any("test_module.py" in str(r.file_path) for r in results)

    def test_vacuum_markdown_files(self, tmp_path):
        """Test markdown file vacuuming."""
        # Create test files
        summary_file = tmp_path / "test-summary.md"
        summary_file.write_text("# Summary")
        archive_dir = tmp_path / "_archives" / "markdown"

        manager = CleanupManager(workspace_root=tmp_path)
        results = manager.vacuum_markdown_files(
            files=[summary_file],
            archive_dir=archive_dir
        )

        assert len(results) == 1
        assert results[0].success is True
        assert archive_dir.exists()
        assert not summary_file.exists()  # Should be moved

    def test_remove_debug_markers_from_file(self, tmp_path):
        """Test removing debug markers from a file."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "# CORTEX_DEBUG: Test marker\n"
            "def test_function():\n"
            "    # CORTEX_DEBUG: Another marker\n"
            "    pass\n"
        )

        manager = CleanupManager(workspace_root=tmp_path)
        result = manager.remove_debug_markers(test_file)

        assert result.success is True
        content = test_file.read_text()
        assert "CORTEX_DEBUG" not in content


class TestCleanupDryRun:
    """Test dry-run mode operations."""

    def test_dry_run_no_file_changes(self, tmp_path):
        """Test dry-run mode doesn't modify files."""
        test_file = tmp_path / "test-summary.md"
        test_file.write_text("# Summary")

        manager = CleanupManager(workspace_root=tmp_path, dry_run=True)
        results = manager.vacuum_markdown_files(files=[test_file])

        assert len(results) == 1
        assert results[0].success is True
        assert test_file.exists()  # Should still exist in dry-run

    def test_dry_run_reports_actions(self, tmp_path):
        """Test dry-run reports what would be done."""
        test_file = tmp_path / "test-summary.md"
        test_file.write_text("# Summary")

        manager = CleanupManager(workspace_root=tmp_path, dry_run=True)
        results = manager.vacuum_markdown_files(files=[test_file])

        assert "would archive" in results[0].message.lower()


class TestCleanupReporting:
    """Test cleanup reporting functionality."""

    def test_generate_cleanup_report(self, tmp_path):
        """Test generating cleanup summary report."""
        manager = CleanupManager(workspace_root=tmp_path)
        
        # Create mock results
        results = [
            CleanupResult(
                operation=CleanupOperation.VACUUM_MARKDOWN,
                file_path=tmp_path / "test-summary.md",
                success=True,
                message="Archived test-summary.md"
            ),
            CleanupResult(
                operation=CleanupOperation.REMOVE_DEBUG_MARKERS,
                file_path=tmp_path / "test_module.py",
                success=True,
                message="Removed 2 debug markers"
            ),
        ]

        report = manager.generate_report(results)
        assert "total operations: 2" in report.lower()
        assert "vacuum" in report.lower()
        assert "remove_debug" in report.lower()

    def test_report_includes_failed_operations(self, tmp_path):
        """Test report includes failed operations."""
        manager = CleanupManager(workspace_root=tmp_path)
        
        results = [
            CleanupResult(
                operation=CleanupOperation.VACUUM_MARKDOWN,
                file_path=tmp_path / "test.md",
                success=False,
                message="Permission denied"
            ),
        ]

        report = manager.generate_report(results)
        assert "failed" in report.lower() or "error" in report.lower()
