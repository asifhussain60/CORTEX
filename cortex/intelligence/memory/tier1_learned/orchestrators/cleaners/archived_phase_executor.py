"""Archived Phase Executor Cleaner — Cleans up old completed phase executors.

Detects and removes completed phase executor scripts from archived/ folders that are:
1. Located in phase_executors/archived/ directory
2. Older than 90 days (allows rollback period)
3. Already committed to git

Safety:
- Git-aware: Won't delete files with uncommitted changes
- Age-aware: 90-day minimum threshold
- Location-aware: ONLY targets archived/ subdirectories

AC-ID: AC-VAC-ARCHIVED-001
Authority: Phase 104 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set
import re
import subprocess

from .base import Analysis, CleanerInterface, Report, RollbackResult


class ArchivedPhaseExecutorCleaner(CleanerInterface):
    """Cleaner for archived/completed phase executor scripts."""

    # Directories containing archived executors
    ARCHIVED_DIRS: List[str] = [
        "cortex/phase_executors/archived",
    ]

    # Patterns for archived phase executor files
    ARCHIVED_PATTERNS: List[str] = [
        r"^execute_phase_\d+.*\.py$",        # execute_phase_49_complete.py
        r"^phase[-_]?\d+[-_].*\.py$",         # phase-81-*, phase25_*
    ]

    # Files that must NEVER be deleted (if any exist)
    PROTECTED_FILES: Set[str] = {
        "__init__.py",
        "README.md",
    }

    # Minimum age in days before cleanup (90 days = ~3 months rollback period)
    MIN_AGE_DAYS: int = 90

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize archived phase executor cleaner.

        Args:
            config: Configuration with repo_root and optional min_age_days
        """
        super().__init__(config)
        self.repo_root = Path(config.get("repo_root", "."))
        self.min_age_days = config.get("min_age_days", self.MIN_AGE_DAYS)
        self.dry_run = config.get("dry_run", False)

        # Compile patterns for efficiency
        self._archived_patterns = [re.compile(p, re.IGNORECASE) for p in self.ARCHIVED_PATTERNS]

    @property
    def name(self) -> str:
        """Get cleaner name."""
        return "ArchivedPhaseExecutorCleaner"

    @property
    def version(self) -> str:
        """Get cleaner version."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Get cleaner domain."""
        return "archived_phase_executors"

    def _is_archived_executor(self, filename: str) -> bool:
        """Check if filename matches archived executor pattern.

        Args:
            filename: Name of the file to check

        Returns:
            True if file matches archived executor pattern
        """
        return any(pattern.match(filename) for pattern in self._archived_patterns)

    def _is_old_enough(self, file_path: Path) -> bool:
        """Check if file is older than minimum age threshold.

        Args:
            file_path: Path to the file

        Returns:
            True if file is old enough to be cleaned
        """
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - mtime
            return age.days >= self.min_age_days
        except (OSError, IOError):
            return False

    def _has_uncommitted_changes(self, file_path: Path) -> bool:
        """Check if file has uncommitted changes in git.

        Args:
            file_path: Path to the file

        Returns:
            True if file has uncommitted changes
        """
        try:
            rel_path = file_path.relative_to(self.repo_root)
            result = subprocess.run(
                ["git", "status", "--porcelain", str(rel_path)],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=5,
            )
            # If output is empty, file has no uncommitted changes
            return bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
            # If we can't determine git status, assume uncommitted (safe default)
            return True

    def _get_file_age_days(self, file_path: Path) -> int:
        """Get file age in days.

        Args:
            file_path: Path to the file

        Returns:
            Age in days, or -1 if cannot determine
        """
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - mtime
            return age.days
        except (OSError, IOError):
            return -1

    def analyze(self) -> Analysis:
        """Analyze archived directories for cleanup candidates.

        Returns:
            Analysis with cleanup plan
        """
        logs: List[str] = []
        files_scanned = 0
        cleanup_candidates: List[Dict[str, Any]] = []

        for archived_dir in self.ARCHIVED_DIRS:
            dir_path = self.repo_root / archived_dir

            if not dir_path.exists():
                logs.append(f"Directory not found: {archived_dir}")
                continue

            logs.append(f"Scanning: {archived_dir}")

            for file_path in dir_path.iterdir():
                if not file_path.is_file():
                    continue

                files_scanned += 1
                filename = file_path.name

                # Skip protected files
                if filename in self.PROTECTED_FILES:
                    logs.append(f"  Protected: {filename}")
                    continue

                # Check if matches archived executor pattern
                if not self._is_archived_executor(filename):
                    continue

                # Check age threshold
                age_days = self._get_file_age_days(file_path)
                if age_days < self.min_age_days:
                    logs.append(f"  Too recent ({age_days}d): {filename}")
                    continue

                # Check for uncommitted changes
                if self._has_uncommitted_changes(file_path):
                    logs.append(f"  Uncommitted changes: {filename}")
                    continue

                # Candidate for cleanup
                cleanup_candidates.append({
                    "path": str(file_path),
                    "filename": filename,
                    "age_days": age_days,
                    "action": "delete",
                    "reason": f"Archived executor ({age_days} days old)",
                })
                logs.append(f"  ✓ Candidate: {filename} ({age_days}d old)")

        return Analysis(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            files_scanned=files_scanned,
            issues_found=len(cleanup_candidates),
            plan={"issues": cleanup_candidates},
            logs=logs,
        )

    def execute(self, plan: Any) -> Report:
        """Execute cleanup of archived phase executors.

        Args:
            plan: Analysis object or plan dict from analyze()

        Returns:
            Report of actions taken
        """
        # Handle both Analysis objects and dict plans
        if hasattr(plan, 'plan'):
            issues = plan.plan.get("issues", [])
        elif isinstance(plan, dict):
            issues = plan.get("issues", [])
        else:
            issues = []

        logs: List[str] = []
        errors: List[str] = []
        deleted_count = 0
        deleted_files: List[str] = []

        for issue in issues:
            file_path = Path(issue["path"])
            filename = issue["filename"]

            if self.dry_run:
                logs.append(f"[DRY RUN] Would delete: {filename}")
                deleted_count += 1
                continue

            try:
                # Store file info for potential rollback
                deleted_files.append(str(file_path))

                # Delete the file
                file_path.unlink()
                deleted_count += 1
                logs.append(f"Deleted: {filename}")

            except OSError as e:
                errors.append(f"Failed to delete {filename}: {e}")

        status = "SUCCESS" if not errors else ("PARTIAL" if deleted_count > 0 else "FAILED")

        return Report(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            status=status,
            actions_taken=deleted_count,
            changes={"deleted": deleted_count},
            errors=errors,
            logs=logs,
        )

    def rollback(self, report: Report) -> RollbackResult:
        """Rollback is not supported for deleted files.

        Args:
            report: Report from previous execution

        Returns:
            RollbackResult indicating rollback not supported
        """
        return RollbackResult(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            status="FAILED",
            files_restored=0,
            errors=["Rollback not supported for deleted files. Use git to restore."],
        )
