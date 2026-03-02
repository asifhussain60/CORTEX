"""Orphaned Test Cleaner — Cleans up misplaced test files from tests/ root.

Detects and removes/relocates test files from the tests/ root folder that:
1. Should be in a proper subdirectory (unit/, integration/, etc.)
2. Are phase-specific test files (e.g., phase_26_*.py)
3. Are ad-hoc test files not imported by other tests

Safety:
- Preserves conftest.py and __init__.py
- Checks for imports before deletion
- Age-aware with minimum threshold

AC-ID: AC-VAC-TESTS-001
Authority: Phase 104 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set
import ast
import re

from .base import Analysis, CleanerInterface, Report, RollbackResult


class OrphanedTestCleaner(CleanerInterface):
    """Cleaner for orphaned and misplaced test files."""

    # Files that must NEVER be deleted from tests/ root
    PROTECTED_FILES: Set[str] = {
        "conftest.py",
        "__init__.py",
        "pytest.ini",
        "baseline.json",
    }

    # Patterns indicating phase-specific or temporary tests
    TEMP_PATTERNS: List[str] = [
        r"^phase[-_]?\d+.*\.py$",           # phase_26_*, phase-53-*
        r"^test_temp[-_].*\.py$",            # test_temp_*
        r"^conftest_.*\.py$",                # conftest_optimize.py
    ]

    # Patterns for tests that should be in subdirectories
    MISPLACED_PATTERNS: List[str] = [
        r"^test_.*\.py$",                    # All test_*.py files
    ]

    # Proper test subdirectories
    PROPER_SUBDIRS: Set[str] = {
        "unit",
        "integration",
        "e2e",
        "performance",
        "golden",
        "regression",
        "contracts",
    }

    # Minimum age in days before cleanup
    MIN_AGE_DAYS: int = 14

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize orphaned test cleaner.

        Args:
            config: Configuration with repo_root and options
        """
        super().__init__(config)
        self.repo_root = Path(config.get("repo_root", "."))
        self.tests_dir = self.repo_root / "tests"
        self.min_age_days = config.get("min_age_days", self.MIN_AGE_DAYS)
        self.dry_run = config.get("dry_run", False)
        self.relocate_mode = config.get("relocate_mode", False)  # Move instead of delete

        # Compile patterns
        self._temp_patterns = [re.compile(p, re.IGNORECASE) for p in self.TEMP_PATTERNS]
        self._misplaced_patterns = [re.compile(p, re.IGNORECASE) for p in self.MISPLACED_PATTERNS]

    @property
    def name(self) -> str:
        """Get cleaner name."""
        return "OrphanedTestCleaner"

    @property
    def version(self) -> str:
        """Get cleaner version."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Get cleaner domain."""
        return "orphaned_tests"

    def _is_protected(self, filename: str) -> bool:
        """Check if file is protected from cleanup.

        Args:
            filename: File name to check

        Returns:
            True if protected
        """
        return filename in self.PROTECTED_FILES

    def _is_temp_test(self, filename: str) -> bool:
        """Check if file matches temporary test patterns.

        Args:
            filename: File name to check

        Returns:
            True if temporary/phase-specific
        """
        for pattern in self._temp_patterns:
            if pattern.match(filename):
                return True
        return False

    def _is_misplaced_test(self, filename: str) -> bool:
        """Check if file is a test that should be in subdirectory.

        Args:
            filename: File name to check

        Returns:
            True if misplaced test
        """
        for pattern in self._misplaced_patterns:
            if pattern.match(filename):
                return True
        return False

    def _get_file_age_days(self, file_path: Path) -> int:
        """Get file age in days.

        Args:
            file_path: Path to file

        Returns:
            Age in days
        """
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - mtime
            return age.days
        except OSError:
            return 0

    def _is_imported_elsewhere(self, file_path: Path) -> bool:
        """Check if file is imported by other test files.

        Args:
            file_path: Path to file

        Returns:
            True if imported elsewhere
        """
        module_name = file_path.stem

        # Search for imports in tests directory
        for test_file in self.tests_dir.rglob("*.py"):
            if test_file == file_path:
                continue

            try:
                content = test_file.read_text()

                # Quick string check first
                if module_name not in content:
                    continue

                # Parse AST for accurate import detection
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if module_name in alias.name:
                                    return True
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and module_name in node.module:
                                return True
                except SyntaxError:
                    # If we can't parse, fall back to string search
                    import_patterns = [
                        f"import {module_name}",
                        f"from {module_name}",
                        f"from tests.{module_name}",
                        f"from .{module_name}",
                    ]
                    if any(p in content for p in import_patterns):
                        return True

            except (OSError, UnicodeDecodeError):
                continue

        return False

    def _suggest_target_dir(self, filename: str, file_path: Path) -> str:
        """Suggest target subdirectory for misplaced test.

        Args:
            filename: Test file name
            file_path: Full path to file

        Returns:
            Suggested subdirectory name
        """
        # Try to infer from file content
        try:
            content = file_path.read_text()

            # Check for integration markers
            if "integration" in content.lower() or "@pytest.mark.integration" in content:
                return "integration"

            # Check for e2e markers
            if "e2e" in content.lower() or "end-to-end" in content.lower():
                return "e2e"

            # Check for performance markers
            if "benchmark" in content.lower() or "@pytest.mark.slow" in content:
                return "performance"

            # Default to unit
            return "unit"

        except (OSError, UnicodeDecodeError):
            return "unit"

    def analyze(self) -> Analysis:
        """Analyze tests/ root for orphaned files.

        Returns:
            Analysis with detected orphaned tests
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        issues: List[Dict[str, Any]] = []
        files_scanned = 0

        if not self.tests_dir.exists():
            logs.append(f"Tests directory not found: {self.tests_dir}")
            return Analysis(
                cleaner_id=self.name,
                timestamp=timestamp,
                files_scanned=0,
                issues_found=0,
                plan={"issues": []},
                logs=logs,
            )

        logs.append(f"Scanning tests root: {self.tests_dir}")

        # Only scan root level (not subdirectories)
        for test_file in self.tests_dir.iterdir():
            if not test_file.is_file():
                continue

            if not test_file.suffix == ".py":
                continue

            files_scanned += 1
            filename = test_file.name

            # Skip protected files
            if self._is_protected(filename):
                logs.append(f"Protected: {filename}")
                continue

            # Determine issue type
            is_temp = self._is_temp_test(filename)
            is_misplaced = self._is_misplaced_test(filename)

            if not is_temp and not is_misplaced:
                continue

            # Check age for temp files
            age_days = self._get_file_age_days(test_file)
            if is_temp and age_days < self.min_age_days:
                logs.append(f"Too young ({age_days}d): {filename}")
                continue

            # Check if imported elsewhere
            if self._is_imported_elsewhere(test_file):
                logs.append(f"Imported elsewhere: {filename}")
                continue

            # Determine action
            if is_temp:
                action = "delete"
                reason = f"Phase-specific test, {age_days} days old"
            else:
                action = "relocate" if self.relocate_mode else "delete"
                target_dir = self._suggest_target_dir(filename, test_file)
                reason = f"Misplaced test, should be in tests/{target_dir}/"

            issues.append({
                "type": "temp_test" if is_temp else "misplaced_test",
                "path": str(test_file),
                "filename": filename,
                "age_days": age_days,
                "size_bytes": test_file.stat().st_size,
                "action": action,
                "target_dir": target_dir if not is_temp else None,
                "reason": reason,
            })
            logs.append(f"Candidate ({action}): {filename}")

        return Analysis(
            cleaner_id=self.name,
            timestamp=timestamp,
            files_scanned=files_scanned,
            issues_found=len(issues),
            plan={"issues": issues},
            logs=logs,
        )

    def execute(self, plan: Any) -> Report:
        """Execute cleanup of orphaned tests.

        Args:
            plan: Execution plan (either Analysis object or dict with issues)

        Returns:
            Report with cleanup results
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        actions_taken: List[Dict[str, Any]] = []
        errors: List[str] = []

        # Handle both Analysis object and dict
        if hasattr(plan, 'plan'):
            # It's an Analysis object
            issues = plan.plan.get("issues", [])
        elif isinstance(plan, dict):
            # It's the plan dict directly
            issues = plan.get("issues", [])
        else:
            issues = []

        for issue in issues:
            file_path = Path(issue["path"])
            action = issue["action"]

            try:
                if action == "delete":
                    if self.dry_run:
                        logs.append(f"[DRY RUN] Would delete: {file_path.name}")
                    else:
                        file_path.unlink()
                        logs.append(f"Deleted: {file_path.name}")

                    actions_taken.append({
                        "action": "delete",
                        "path": str(file_path),
                        "dry_run": self.dry_run,
                    })

                elif action == "relocate":
                    target_dir = self.tests_dir / issue.get("target_dir", "unit")
                    target_path = target_dir / file_path.name

                    if self.dry_run:
                        logs.append(f"[DRY RUN] Would move: {file_path.name} → {target_dir.name}/")
                    else:
                        target_dir.mkdir(parents=True, exist_ok=True)
                        file_path.rename(target_path)
                        logs.append(f"Moved: {file_path.name} → {target_dir.name}/")

                    actions_taken.append({
                        "action": "relocate",
                        "source": str(file_path),
                        "target": str(target_path),
                        "dry_run": self.dry_run,
                    })

            except Exception as e:
                error_msg = f"Failed to {action} {file_path.name}: {e}"
                errors.append(error_msg)
                logs.append(f"ERROR: {error_msg}")

        deleted = len([a for a in actions_taken if a["action"] == "delete" and not a.get("dry_run")])
        relocated = len([a for a in actions_taken if a["action"] == "relocate" and not a.get("dry_run")])

        status = "SUCCESS" if len(errors) == 0 else ("PARTIAL" if (deleted + relocated) > 0 else "FAILED")

        return Report(
            cleaner_id=self.name,
            timestamp=timestamp,
            status=status,
            actions_taken=len(actions_taken),
            changes={"deleted": deleted, "relocated": relocated},
            errors=errors,
            logs=logs,
        )

    def rollback(self, report: Report) -> RollbackResult:
        """Rollback is not supported.

        Args:
            report: Report from execute

        Returns:
            RollbackResult indicating not supported
        """
        return RollbackResult(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            status="FAILED",
            files_restored=0,
            errors=["Rollback not supported. Use git to restore deleted files."],
        )
