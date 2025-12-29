"""
Safe Cleanup Executor for CORTEX Align Orchestrator

This module safely removes obsolete files with comprehensive safety checks:
- Git working directory validation
- Automatic backup creation
- Test baseline capture before cleanup
- Category-level cleanup with incremental validation
- Automatic rollback on test failure

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from src.operations.modules.realignment.obsolete_code_detector import (
    CleanupPlan,
    ObsoleteCodeDetector
)

logger = logging.getLogger(__name__)


class CleanupCategory(Enum):
    """Categories for incremental cleanup."""
    OBSOLETE_TESTS = "obsolete_tests"
    OBSOLETE_SCRIPTS = "obsolete_scripts"
    OBSOLETE_ORCHESTRATORS = "obsolete_orchestrators"
    DEPRECATED_IMPORTS = "deprecated_imports"  # Not deleted, just flagged


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    category: CleanupCategory
    files_removed: List[Path] = field(default_factory=list)
    files_failed: List[Path] = field(default_factory=list)
    backup_path: Optional[Path] = None
    tests_passed_before: bool = False
    tests_passed_after: bool = False
    rolled_back: bool = False
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if cleanup was successful."""
        return len(self.files_failed) == 0 and not self.rolled_back and self.error is None


@dataclass
class ExecutionReport:
    """Complete execution report."""
    total_files_removed: int = 0
    total_files_failed: int = 0
    categories_completed: List[CleanupCategory] = field(default_factory=list)
    categories_failed: List[CleanupCategory] = field(default_factory=list)
    backup_paths: List[Path] = field(default_factory=list)
    results: List[CleanupResult] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if all cleanup operations succeeded."""
        return len(self.categories_failed) == 0 and self.total_files_failed == 0


class SafeCleanupExecutor:
    """Safely executes cleanup operations with comprehensive safety checks."""
    
    def __init__(self, project_root: Optional[Path] = None, create_backups: bool = True):
        """
        Initialize safe cleanup executor.
        
        Args:
            project_root: Path to CORTEX project root. If None, auto-detects.
            create_backups: Whether to create backups before cleanup
        """
        self.project_root = project_root or self._detect_project_root()
        self.create_backups = create_backups
        self.backup_dir = self.project_root / "cortex-brain" / "backups" / "cleanup"
        self.detector = ObsoleteCodeDetector(project_root=self.project_root)
    
    def _detect_project_root(self) -> Path:
        """Auto-detect CORTEX project root."""
        current = Path.cwd()
        
        if (current / "cortex-operations.yaml").exists():
            return current
        
        for parent in current.parents:
            if (parent / "cortex-operations.yaml").exists():
                return parent
        
        raise FileNotFoundError("Cannot detect CORTEX project root")
    
    def check_git_status(self) -> bool:
        """
        Check if git working directory is clean.
        
        Returns:
            True if working directory is clean, False otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            is_clean = len(result.stdout.strip()) == 0
            
            if not is_clean:
                logger.warning("Git working directory has uncommitted changes")
                logger.info("Run 'git status' to see changes")
            
            return is_clean
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to check git status: {e}")
            return False
        except FileNotFoundError:
            logger.warning("Git not found - skipping git status check")
            return True  # Allow cleanup if git not available
    
    def run_tests(self) -> bool:
        """
        Run test suite to capture baseline.
        
        Returns:
            True if all tests pass, False otherwise
        """
        try:
            logger.info("Running test suite...")
            
            result = subprocess.run(
                ['python3', '-m', 'pytest', 'tests/', '-q', '--tb=no'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            tests_passed = result.returncode == 0
            
            if tests_passed:
                logger.info("✅ All tests passed")
            else:
                logger.warning(f"❌ Tests failed (exit code: {result.returncode})")
                logger.debug(f"Test output:\n{result.stdout}\n{result.stderr}")
            
            return tests_passed
        
        except subprocess.TimeoutExpired:
            logger.error("Test suite timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return False
    
    def create_backup(self, files: List[Path]) -> Path:
        """
        Create backup of files before removal.
        
        Args:
            files: List of files to backup
        
        Returns:
            Path to backup directory
        """
        if not self.create_backups:
            return None
        
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating backup in {backup_path}")
        
        # Copy files to backup
        for file in files:
            if not file.exists():
                continue
            
            # Preserve directory structure
            relative_path = file.relative_to(self.project_root)
            backup_file = backup_path / relative_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file, backup_file)
            logger.debug(f"Backed up: {relative_path}")
        
        logger.info(f"✅ Backup created: {backup_path.relative_to(self.project_root)}")
        return backup_path
    
    def remove_files(self, files: List[Path]) -> tuple[List[Path], List[Path]]:
        """
        Remove files from filesystem.
        
        Args:
            files: List of files to remove
        
        Returns:
            Tuple of (successfully removed files, failed files)
        """
        removed = []
        failed = []
        
        for file in files:
            try:
                if file.exists():
                    file.unlink()
                    removed.append(file)
                    logger.debug(f"Removed: {file.relative_to(self.project_root)}")
                else:
                    logger.warning(f"File not found: {file}")
                    failed.append(file)
            except Exception as e:
                logger.error(f"Failed to remove {file}: {e}")
                failed.append(file)
        
        return removed, failed
    
    def restore_backup(self, backup_path: Path, files: List[Path]) -> bool:
        """
        Restore files from backup.
        
        Args:
            backup_path: Path to backup directory
            files: List of files to restore
        
        Returns:
            True if restore successful, False otherwise
        """
        try:
            logger.info(f"Rolling back - restoring from {backup_path}")
            
            for file in files:
                relative_path = file.relative_to(self.project_root)
                backup_file = backup_path / relative_path
                
                if backup_file.exists():
                    # Ensure parent directory exists
                    file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Restore file
                    shutil.copy2(backup_file, file)
                    logger.debug(f"Restored: {relative_path}")
            
            logger.info("✅ Rollback complete")
            return True
        
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def cleanup_category(
        self,
        category: CleanupCategory,
        files: List[Path],
        run_tests_after: bool = True
    ) -> CleanupResult:
        """
        Clean up files in a specific category with safety checks.
        
        Args:
            category: Category being cleaned
            files: Files to remove
            run_tests_after: Whether to run tests after cleanup
        
        Returns:
            CleanupResult with details
        """
        result = CleanupResult(category=category)
        
        if not files:
            logger.info(f"No files to clean in category: {category.value}")
            result.tests_passed_before = True
            result.tests_passed_after = True
            return result
        
        logger.info(f"Cleaning category: {category.value} ({len(files)} files)")
        
        # Test baseline before cleanup
        if run_tests_after:
            result.tests_passed_before = self.run_tests()
            if not result.tests_passed_before:
                result.error = "Tests failed before cleanup - aborting"
                logger.error(result.error)
                return result
        
        # Create backup
        if self.create_backups:
            result.backup_path = self.create_backup(files)
        
        # Remove files
        removed, failed = self.remove_files(files)
        result.files_removed = removed
        result.files_failed = failed
        
        if failed:
            logger.warning(f"Failed to remove {len(failed)} files")
        
        # Test after cleanup
        if run_tests_after and removed:
            result.tests_passed_after = self.run_tests()
            
            if not result.tests_passed_after:
                logger.error("Tests failed after cleanup - rolling back")
                
                if result.backup_path:
                    self.restore_backup(result.backup_path, removed)
                    result.rolled_back = True
                    result.error = "Tests failed after cleanup - changes rolled back"
                else:
                    result.error = "Tests failed after cleanup - no backup to restore"
        else:
            result.tests_passed_after = True
        
        if result.success:
            logger.info(f"✅ Category {category.value} cleaned successfully")
        else:
            logger.error(f"❌ Category {category.value} cleanup failed")
        
        return result
    
    def execute_cleanup(
        self,
        plan: CleanupPlan,
        dry_run: bool = False,
        skip_git_check: bool = False,
        skip_tests: bool = False
    ) -> ExecutionReport:
        """
        Execute complete cleanup with all safety checks.
        
        Args:
            plan: CleanupPlan with files to remove
            dry_run: If True, preview cleanup without executing
            skip_git_check: Skip git working directory check
            skip_tests: Skip test execution (dangerous!)
        
        Returns:
            ExecutionReport with results
        """
        report = ExecutionReport()
        
        if dry_run:
            logger.info("DRY RUN - No files will be removed")
            logger.info(f"Would remove {plan.total_files} files ({plan.estimated_removal_size_mb:.2f} MB)")
            return report
        
        logger.info("Starting safe cleanup execution")
        logger.info(f"Total files to remove: {plan.total_files}")
        logger.info(f"Estimated size: {plan.estimated_removal_size_mb:.2f} MB")
        
        # Safety check: Git status
        if not skip_git_check and not self.check_git_status():
            logger.error("Aborting: Git working directory not clean")
            logger.info("Commit or stash changes, then run cleanup again")
            return report
        
        # Define cleanup order (safest first)
        cleanup_order = [
            (CleanupCategory.OBSOLETE_SCRIPTS, plan.obsolete_scripts),
            (CleanupCategory.OBSOLETE_TESTS, plan.obsolete_tests),
            (CleanupCategory.OBSOLETE_ORCHESTRATORS, plan.obsolete_orchestrators),
        ]
        
        # Execute cleanup by category
        for category, files in cleanup_order:
            if not files:
                continue
            
            result = self.cleanup_category(
                category=category,
                files=files,
                run_tests_after=not skip_tests
            )
            
            report.results.append(result)
            
            if result.backup_path:
                report.backup_paths.append(result.backup_path)
            
            if result.success:
                report.categories_completed.append(category)
                report.total_files_removed += len(result.files_removed)
            else:
                report.categories_failed.append(category)
                report.total_files_failed += len(result.files_failed)
                
                # Stop on first failure
                logger.error(f"Stopping cleanup due to failure in {category.value}")
                break
        
        # Summary
        if report.success:
            logger.info(f"✅ Cleanup complete: {report.total_files_removed} files removed")
        else:
            logger.error(f"❌ Cleanup failed: {report.total_files_failed} files failed")
        
        return report
    
    def generate_report(self, report: ExecutionReport, dry_run: bool = False) -> str:
        """
        Generate formatted report from execution.
        
        Args:
            report: ExecutionReport to format
            dry_run: Whether this was a dry run
        
        Returns:
            Formatted markdown report
        """
        mode = "DRY RUN" if dry_run else "EXECUTED"
        
        report_lines = [
            f"# Safe Cleanup Report ({mode})",
            "",
            f"**Total Files Removed:** {report.total_files_removed}",
            f"**Total Files Failed:** {report.total_files_failed}",
            f"**Categories Completed:** {len(report.categories_completed)}",
            f"**Categories Failed:** {len(report.categories_failed)}",
            f"**Status:** {'✅ Success' if report.success else '❌ Failed'}",
            "",
        ]
        
        if report.categories_completed:
            report_lines.extend([
                "## ✅ Completed Categories",
                ""
            ])
            
            for result in report.results:
                if result.success:
                    report_lines.append(f"### {result.category.value}")
                    report_lines.append("")
                    report_lines.append(f"- **Files Removed:** {len(result.files_removed)}")
                    report_lines.append(f"- **Tests Before:** {'✅ Pass' if result.tests_passed_before else '❌ Fail'}")
                    report_lines.append(f"- **Tests After:** {'✅ Pass' if result.tests_passed_after else '❌ Fail'}")
                    
                    if result.backup_path:
                        relative_backup = result.backup_path.relative_to(self.project_root)
                        report_lines.append(f"- **Backup:** `{relative_backup}`")
                    
                    report_lines.append("")
                    
                    # List removed files (first 10)
                    if result.files_removed:
                        report_lines.append("**Files Removed:**")
                        for file in result.files_removed[:10]:
                            relative_path = file.relative_to(self.project_root)
                            report_lines.append(f"- `{relative_path}`")
                        
                        if len(result.files_removed) > 10:
                            remaining = len(result.files_removed) - 10
                            report_lines.append(f"- ... and {remaining} more")
                        
                        report_lines.append("")
        
        if report.categories_failed:
            report_lines.extend([
                "## ❌ Failed Categories",
                ""
            ])
            
            for result in report.results:
                if not result.success:
                    report_lines.append(f"### {result.category.value}")
                    report_lines.append("")
                    
                    if result.error:
                        report_lines.append(f"**Error:** {result.error}")
                    
                    if result.rolled_back:
                        report_lines.append("**Status:** Changes rolled back")
                    
                    if result.files_failed:
                        report_lines.append("")
                        report_lines.append(f"**Failed Files:** {len(result.files_failed)}")
                    
                    report_lines.append("")
        
        if report.backup_paths:
            report_lines.extend([
                "## 💾 Backups Created",
                ""
            ])
            
            for backup in report.backup_paths:
                relative_path = backup.relative_to(self.project_root)
                report_lines.append(f"- `{relative_path}`")
            
            report_lines.append("")
        
        report_lines.extend([
            "## 🔧 Next Steps",
            ""
        ])
        
        if dry_run:
            report_lines.extend([
                "This was a dry run. To execute cleanup:",
                "1. Ensure git working directory is clean",
                "2. Run `align cleanup --execute`",
                "3. Tests will run automatically before and after each category",
                ""
            ])
        elif report.success:
            report_lines.extend([
                "1. Run tests to verify system: `pytest tests/`",
                "2. Review git status: `git status`",
                "3. Commit cleanup if tests pass",
                "4. Backups available for rollback if needed",
                ""
            ])
        else:
            report_lines.extend([
                "1. Review error messages above",
                "2. Restore from backup if needed",
                "3. Fix issues and try again",
                ""
            ])
        
        return "\n".join(report_lines)


def main():
    """CLI entry point for safe cleanup."""
    import sys
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Safely clean up obsolete code")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview cleanup without executing'
    )
    parser.add_argument(
        '--skip-git-check',
        action='store_true',
        help='Skip git working directory check'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip test execution (dangerous!)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation (not recommended)'
    )
    
    args = parser.parse_args()
    
    try:
        # Generate cleanup plan
        detector = ObsoleteCodeDetector()
        plan = detector.generate_cleanup_plan()
        
        if plan.total_files == 0:
            print("No obsolete files to clean")
            sys.exit(0)
        
        # Execute cleanup
        executor = SafeCleanupExecutor(create_backups=not args.no_backup)
        report = executor.execute_cleanup(
            plan=plan,
            dry_run=args.dry_run,
            skip_git_check=args.skip_git_check,
            skip_tests=args.skip_tests
        )
        
        # Print report
        print(executor.generate_report(report, dry_run=args.dry_run))
        
        # Exit code
        sys.exit(0 if report.success else 1)
    
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
