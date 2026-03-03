"""
CORTEX Toolkit - Cleanup Module

Consolidates markdown vacuum and debug marker cleanup scripts.

**Consolidated Scripts:**
- scripts/run_vacuum.py
- scripts/vacuum-runner.py
- .cortex-runtime/phase-80-root-cleanup.py
- cortex/debugging/debug_decorator.py (cleanup functions)

**Authority:** Phase 90 S-90-05
"""
# CORE-035 — domain-scoped; class name appropriate for this module

# AC_START: AC-P90-004
# Description: Cleanup module for markdown vacuum and debug marker removal

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional
import shutil


class CleanupOperation(Enum):
    """Types of cleanup operations."""
    VACUUM_MARKDOWN = "vacuum_markdown"
    REMOVE_DEBUG_MARKERS = "remove_debug_markers"
    ARCHIVE_FILES = "archive_files"
    REMOVE_TEMP_FILES = "remove_temp_files"


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    operation: CleanupOperation
    file_path: Path
    success: bool
    message: str
    archived_to: Optional[Path] = None


class CleanupManager:
    """
    Manages cleanup operations for CORTEX workspace.

    Consolidates:
    - Markdown sprawl detection and archival (vacuum)
    - Debug marker removal (CORTEX_DEBUG cleanup)
    - Temporary file cleanup
    - Archive management

    Attributes:
        workspace_root: Root directory of CORTEX workspace
        dry_run: If True, report what would be done without making changes
    """

    # Markdown patterns to detect sprawl
    MARKDOWN_SPRAWL_PATTERNS = [
        "*-summary.md",
        "*-report.md",
        "*-analysis.md",
        "*-plan.md",
        "*-notes.md",
    ]

    # Directories to exclude from vacuum
    EXCLUDE_DIRS = {
        "docs",
        "cortex-docs",
        ".github",
        "_archives",
        "node_modules",
        ".git",
    }

    def __init__(
        self,
        workspace_root: Path,
        dry_run: bool = False
    ) -> None:
        """
        Initialize CleanupManager.

        Args:
            workspace_root: Root directory of workspace
            dry_run: If True, simulate operations without making changes
        """
        self.workspace_root = Path(workspace_root)
        self.dry_run = dry_run

    def scan_markdown_sprawl(self) -> List[CleanupResult]:
        """
        Scan workspace for markdown sprawl.

        Returns:
            List of CleanupResult objects for detected sprawl files
        """
        results = []

        for pattern in self.MARKDOWN_SPRAWL_PATTERNS:
            for file_path in self.workspace_root.rglob(pattern):
                # Skip excluded directories
                if any(exclude in file_path.parts for exclude in self.EXCLUDE_DIRS):
                    continue

                results.append(
                    CleanupResult(
                        operation=CleanupOperation.VACUUM_MARKDOWN,
                        file_path=file_path,
                        success=True,
                        message=f"Detected markdown sprawl: {file_path.name}"
                    )
                )

        return results

    def scan_debug_markers(self) -> List[CleanupResult]:
        """
        Scan workspace for CORTEX_DEBUG markers.

        Returns:
            List of CleanupResult objects for files with debug markers
        """
        results = []

        # Search Python files for CORTEX_DEBUG markers
        for file_path in self.workspace_root.rglob("*.py"):
            # Skip excluded directories
            if any(exclude in file_path.parts for exclude in self.EXCLUDE_DIRS):
                continue

            try:
                content = file_path.read_text()
                if "CORTEX_DEBUG" in content:
                    marker_count = content.count("CORTEX_DEBUG")
                    results.append(
                        CleanupResult(
                            operation=CleanupOperation.REMOVE_DEBUG_MARKERS,
                            file_path=file_path,
                            success=True,
                            message=f"Found {marker_count} debug markers"
                        )
                    )
            except Exception as e:
                results.append(
                    CleanupResult(
                        operation=CleanupOperation.REMOVE_DEBUG_MARKERS,
                        file_path=file_path,
                        success=False,
                        message=f"Error scanning file: {e}"
                    )
                )

        return results

    def vacuum_markdown_files(
        self,
        files: Optional[List[Path]] = None,
        archive_dir: Optional[Path] = None
    ) -> List[CleanupResult]:
        """
        Vacuum (archive) markdown files.

        Args:
            files: List of files to vacuum (if None, uses scan_markdown_sprawl)
            archive_dir: Directory to archive files to (default: _archives/markdown)

        Returns:
            List of CleanupResult objects
        """
        if files is None:
            scan_results = self.scan_markdown_sprawl()
            files = [r.file_path for r in scan_results if r.success]

        if archive_dir is None:
            archive_dir = self.workspace_root / "_archives" / "markdown"

        results = []

        for file_path in files:
            try:
                if self.dry_run:
                    results.append(
                        CleanupResult(
                            operation=CleanupOperation.VACUUM_MARKDOWN,
                            file_path=file_path,
                            success=True,
                            message=f"Would archive {file_path.name} to {archive_dir}",
                            archived_to=archive_dir / file_path.name
                        )
                    )
                else:
                    # Create archive directory if needed
                    archive_dir.mkdir(parents=True, exist_ok=True)

                    # Move file to archive
                    archived_path = archive_dir / file_path.name
                    shutil.move(str(file_path), str(archived_path))

                    results.append(
                        CleanupResult(
                            operation=CleanupOperation.VACUUM_MARKDOWN,
                            file_path=file_path,
                            success=True,
                            message=f"Archived {file_path.name}",
                            archived_to=archived_path
                        )
                    )
            except Exception as e:
                results.append(
                    CleanupResult(
                        operation=CleanupOperation.VACUUM_MARKDOWN,
                        file_path=file_path,
                        success=False,
                        message=f"Error archiving file: {e}"
                    )
                )

        return results

    def remove_debug_markers(
        self,
        file_path: Path
    ) -> CleanupResult:
        """
        Remove CORTEX_DEBUG markers from a file.

        Args:
            file_path: Path to file to clean

        Returns:
            CleanupResult object
        """
        try:
            content = file_path.read_text()
            original_lines = content.split('\n')

            # Remove lines containing CORTEX_DEBUG
            cleaned_lines = [
                line for line in original_lines
                if "CORTEX_DEBUG" not in line
            ]

            removed_count = len(original_lines) - len(cleaned_lines)

            if self.dry_run:
                return CleanupResult(
                    operation=CleanupOperation.REMOVE_DEBUG_MARKERS,
                    file_path=file_path,
                    success=True,
                    message=f"Would remove {removed_count} debug markers"
                )
            else:
                # Write cleaned content
                file_path.write_text('\n'.join(cleaned_lines))

                return CleanupResult(
                    operation=CleanupOperation.REMOVE_DEBUG_MARKERS,
                    file_path=file_path,
                    success=True,
                    message=f"Removed {removed_count} debug markers"
                )
        except Exception as e:
            return CleanupResult(
                operation=CleanupOperation.REMOVE_DEBUG_MARKERS,
                file_path=file_path,
                success=False,
                message=f"Error removing markers: {e}"
            )

    def generate_report(
        self,
        results: List[CleanupResult]
    ) -> str:
        """
        Generate cleanup summary report.

        Args:
            results: List of CleanupResult objects

        Returns:
            Formatted report string
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        by_operation = {}
        for result in results:
            op = result.operation.value
            if op not in by_operation:
                by_operation[op] = {"success": 0, "failed": 0}

            if result.success:
                by_operation[op]["success"] += 1
            else:
                by_operation[op]["failed"] += 1

        report_lines = [
            "Cleanup Summary",
            "=" * 50,
            f"Total operations: {total}",
            f"Successful: {successful}",
            f"Failed: {failed}",
            "",
            "By Operation:",
        ]

        for op, counts in by_operation.items():
            report_lines.append(
                f"  {op}: {counts['success']} successful, {counts['failed']} failed"
            )

        if failed > 0:
            report_lines.append("")
            report_lines.append("Failed Operations:")
            for result in results:
                if not result.success:
                    report_lines.append(f"  - {result.file_path.name}: {result.message}")

        return "\n".join(report_lines)

# AC_COMPLETE: AC-P90-004 ✅ Cleanup module with vacuum + debug marker removal
