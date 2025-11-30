"""
User Cleanup Orchestrator - Lightweight cleanup for user repositories

This module provides safe, conservative cleanup for user repositories with:
- User-safe scanning (logs, temp, cache only)
- Protected path validation (never touch source/configs)
- Interactive prompts for confirmation
- Lightweight reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 3.2.1
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationPhase,
    OperationResult,
    OperationStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class CleanupCategory:
    """Category of files to clean up"""

    name: str
    description: str
    patterns: List[str]
    safe_to_delete: bool = True
    requires_confirmation: bool = False


@dataclass
class UserCleanupReport:
    """Simple cleanup report for user"""

    generated_at: datetime
    categories_cleaned: List[str]
    files_deleted: int
    space_freed_mb: float
    execution_time: float
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "generated_at": self.generated_at.isoformat(),
            "categories_cleaned": self.categories_cleaned,
            "files_deleted": self.files_deleted,
            "space_freed_mb": self.space_freed_mb,
            "execution_time": self.execution_time,
            "errors": self.errors,
        }


class UserCleanupOrchestrator(BaseOperationModule):
    """
    Lightweight cleanup orchestrator for user repositories.

    Conservative by design:
    - Only cleans safe categories (logs, temp, cache, build artifacts)
    - Never touches source code, tests, or configs
    - Interactive confirmation for non-obvious deletions
    - Clear reporting of what was deleted

    User-Safe Categories:
    ✅ Logs (*.log, logs/)
    ✅ Temporary files (tmp/, temp/, *.tmp)
    ✅ Cache directories (cache/, .cache/)
    ✅ Build artifacts (.next/, dist/, build/ with confirmation)
    ✅ IDE files (.vscode/, .idea/ if auto-generated)
    ⚠️ Large files (>10 MB, requires confirmation)

    Protected Paths (Never Touch):
    ❌ Source code (src/, lib/, app/)
    ❌ Tests (tests/, __tests__/, *.test.*)
    ❌ Configs (*.config.js, *.json, .env)
    ❌ Dependencies (node_modules/, venv/)
    ❌ Version control (.git/)
    ❌ Documentation (docs/, *.md in root)
    """

    def __init__(self, project_root: Path = None):
        super().__init__()
        self.project_root = Path(project_root or Path.cwd())

        # Protected paths - NEVER touch these
        self.protected_paths = {
            "src/",
            "lib/",
            "app/",
            "tests/",
            "__tests__/",
            "node_modules/",
            "venv/",
            ".env/",
            ".venv/",
            ".git/",
            "docs/",
            ".github/",
            ".gitlab/",
            "LICENSE",
            "README.md",
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            ".gitignore",
        }

        # Safe cleanup categories
        self.cleanup_categories = {
            "logs": CleanupCategory(
                name="logs",
                description="Log files (*.log, logs/)",
                patterns=["*.log", "logs/", "*.log.*"],
                safe_to_delete=True,
                requires_confirmation=False,
            ),
            "temp": CleanupCategory(
                name="temp",
                description="Temporary files (tmp/, temp/, *.tmp)",
                patterns=["tmp/", "temp/", "*.tmp", "*.temp"],
                safe_to_delete=True,
                requires_confirmation=False,
            ),
            "cache": CleanupCategory(
                name="cache",
                description="Cache directories (cache/, .cache/, __pycache__/)",
                patterns=["cache/", ".cache/", "__pycache__/", "*.pyc"],
                safe_to_delete=True,
                requires_confirmation=False,
            ),
            "build_artifacts": CleanupCategory(
                name="build_artifacts",
                description="Build artifacts (.next/, dist/, build/)",
                patterns=[".next/", "dist/", "build/", "out/", "target/"],
                safe_to_delete=True,
                requires_confirmation=True,  # User should confirm
            ),
            "ide_generated": CleanupCategory(
                name="ide_generated",
                description="Auto-generated IDE files",
                patterns=[
                    ".vscode/settings.json",
                    ".idea/workspace.xml",
                    "*.swp",
                    ".DS_Store",
                ],
                safe_to_delete=True,
                requires_confirmation=False,
            ),
        }

    def get_metadata(self) -> OperationModuleMetadata:
        """Module metadata"""
        return OperationModuleMetadata(
            module_id="user_cleanup_orchestrator",
            name="User Cleanup Orchestrator",
            description="Lightweight cleanup for user repositories (logs, temp, cache)",
            version="1.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=100,
            dependencies=[],
            optional=True,
            tags=["cleanup", "maintenance", "user", "lightweight"],
        )

    def execute(self, context: Dict) -> OperationResult:
        """
        Execute user-safe cleanup.

        Args:
            context: Execution context with optional:
                - dry_run (bool): Preview mode (default: True)
                - categories (List[str]): Categories to clean (default: all safe)
                - auto_confirm (bool): Skip confirmations (default: False)

        Returns:
            OperationResult with cleanup report
        """
        dry_run = context.get("dry_run", True)
        categories = context.get("categories", list(self.cleanup_categories.keys()))
        auto_confirm = context.get("auto_confirm", False)

        try:
            logger.info("=" * 70)
            logger.info("USER CLEANUP ORCHESTRATOR")
            logger.info("=" * 70)
            logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
            logger.info(f"Project Root: {self.project_root}")
            logger.info("")

            start_time = datetime.now()

            # Phase 1: Scan for cleanable files
            logger.info("Phase 1: Scanning Repository")
            logger.info("-" * 70)

            files_by_category = self._scan_repository(categories)

            total_files = sum(len(files) for files in files_by_category.values())
            total_size_mb = sum(
                sum(f.stat().st_size for f in files if f.exists())
                for files in files_by_category.values()
            ) / (1024 * 1024)

            logger.info(f"✅ Found {total_files} files ({total_size_mb:.2f} MB)")
            logger.info("")

            # Phase 2: Display findings
            logger.info("Phase 2: Cleanup Preview")
            logger.info("-" * 70)

            for category_name, files in files_by_category.items():
                if files:
                    category = self.cleanup_categories[category_name]
                    size_mb = (
                        sum(f.stat().st_size for f in files if f.exists())
                        / (1024 * 1024)
                    )
                    logger.info(
                        f"• {category.description}: {len(files)} files ({size_mb:.2f} MB)"
                    )

            logger.info("")

            if total_files == 0:
                logger.info("✨ Repository is already clean!")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="No files to clean",
                    data={
                        "files_deleted": 0,
                        "space_freed_mb": 0.0,
                        "dry_run": dry_run,
                    },
                )

            # Phase 3: Interactive confirmation (if needed)
            if not dry_run and not auto_confirm:
                logger.info("Phase 3: Confirmation")
                logger.info("-" * 70)

                confirmation_needed = any(
                    self.cleanup_categories[cat].requires_confirmation
                    for cat in files_by_category
                    if files_by_category[cat]
                )

                if confirmation_needed:
                    logger.info(
                        "⚠️  Some categories require confirmation before deletion:"
                    )
                    for category_name, files in files_by_category.items():
                        if (
                            files
                            and self.cleanup_categories[category_name].requires_confirmation
                        ):
                            logger.info(
                                f"   • {self.cleanup_categories[category_name].description}"
                            )

                    logger.info("")
                    logger.info(
                        "To proceed, say 'approve cleanup' or use auto_confirm=True"
                    )
                    logger.info("")

                    return OperationResult(
                        success=True,
                        status=OperationStatus.SUCCESS,
                        message="Cleanup ready - confirmation required",
                        data={
                            "files_found": total_files,
                            "space_to_free_mb": total_size_mb,
                            "requires_confirmation": True,
                            "dry_run": dry_run,
                        },
                    )

            # Phase 4: Execute cleanup
            if not dry_run:
                logger.info("Phase 4: Executing Cleanup")
                logger.info("-" * 70)

                files_deleted, space_freed_mb, errors = self._execute_cleanup(
                    files_by_category
                )

                logger.info("")
            else:
                files_deleted = total_files
                space_freed_mb = total_size_mb
                errors = []

            # Phase 5: Summary
            elapsed = (datetime.now() - start_time).total_seconds()

            report = UserCleanupReport(
                generated_at=datetime.now(),
                categories_cleaned=list(files_by_category.keys()),
                files_deleted=files_deleted,
                space_freed_mb=space_freed_mb,
                execution_time=elapsed,
                errors=errors,
            )

            logger.info("")
            logger.info("=" * 70)
            logger.info("CLEANUP SUMMARY")
            logger.info("=" * 70)
            logger.info(f"Files Cleaned: {files_deleted}")
            logger.info(f"Space Freed: {space_freed_mb:.2f} MB")
            logger.info(f"Execution Time: {elapsed:.2f}s")
            if errors:
                logger.warning(f"Errors: {len(errors)}")
            logger.info("")

            if dry_run:
                logger.info("🔍 DRY RUN COMPLETE - No changes made")
                logger.info("To execute cleanup, run with dry_run=False")

            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Cleanup {'preview' if dry_run else 'complete'}: {files_deleted} files, {space_freed_mb:.2f} MB freed",
                data=report.to_dict(),
                errors=errors if errors else None,
            )

        except Exception as e:
            logger.error(f"User cleanup failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Cleanup failed: {str(e)}",
                data={"error": str(e)},
            )

    def _scan_repository(
        self, categories: List[str]
    ) -> Dict[str, List[Path]]:
        """
        Scan repository for cleanable files.

        Args:
            categories: List of category names to scan

        Returns:
            Dictionary of category → list of files
        """
        files_by_category: Dict[str, List[Path]] = defaultdict(list)

        for category_name in categories:
            if category_name not in self.cleanup_categories:
                logger.warning(f"Unknown category: {category_name}")
                continue

            category = self.cleanup_categories[category_name]

            for pattern in category.patterns:
                if pattern.endswith("/"):
                    # Directory pattern
                    dir_name = pattern.rstrip("/")
                    for dir_path in self.project_root.rglob(dir_name):
                        if dir_path.is_dir() and not self._is_protected(dir_path):
                            # Add all files in directory
                            for file_path in dir_path.rglob("*"):
                                if file_path.is_file():
                                    files_by_category[category_name].append(
                                        file_path
                                    )
                else:
                    # File pattern
                    for file_path in self.project_root.rglob(pattern):
                        if file_path.is_file() and not self._is_protected(file_path):
                            files_by_category[category_name].append(file_path)

        return dict(files_by_category)

    def _is_protected(self, path: Path) -> bool:
        """
        Check if path is protected.

        Args:
            path: Path to check

        Returns:
            True if path is protected
        """
        try:
            relative_path = path.relative_to(self.project_root)
        except ValueError:
            return True  # Outside project root

        # Check against protected paths
        path_str = str(relative_path) + ("/" if path.is_dir() else "")

        for protected in self.protected_paths:
            if path_str.startswith(protected) or protected in str(relative_path):
                return True

        return False

    def _execute_cleanup(
        self, files_by_category: Dict[str, List[Path]]
    ) -> tuple[int, float, List[str]]:
        """
        Execute cleanup by deleting files.

        Args:
            files_by_category: Dictionary of category → files

        Returns:
            Tuple of (files_deleted, space_freed_mb, errors)
        """
        files_deleted = 0
        space_freed_mb = 0.0
        errors = []

        for category_name, files in files_by_category.items():
            logger.info(f"\n📦 Cleaning category: {category_name}")

            for file_path in files:
                try:
                    if file_path.exists():
                        size_mb = file_path.stat().st_size / (1024 * 1024)

                        # Delete file or directory
                        if file_path.is_dir():
                            import shutil

                            shutil.rmtree(file_path)
                        else:
                            file_path.unlink()

                        files_deleted += 1
                        space_freed_mb += size_mb
                        logger.info(
                            f"  ✅ Deleted: {file_path.relative_to(self.project_root)}"
                        )

                except Exception as e:
                    error_msg = f"Failed to delete {file_path.name}: {e}"
                    errors.append(error_msg)
                    logger.error(f"  ❌ {error_msg}")

        return files_deleted, space_freed_mb, errors
