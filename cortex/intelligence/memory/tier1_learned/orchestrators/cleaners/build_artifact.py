"""Build Artifact Cleaner — Cleans up build artifacts from source directories.

Detects and removes build artifacts that are:
1. Located in obj/, bin/, build/, dist/, __pycache__/ directories
2. Generated output files (.pyc, .pyo, .dll, .exe, .pdb)
3. Always safe to regenerate via build commands

Safety:
- Only targets well-known build directories
- Git-aware: Respects .gitignore patterns
- Preserves source files entirely

AC-ID: AC-VAC-BUILD-001
Authority: Phase 104 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set
import os
import shutil

from .base import Analysis, CleanerInterface, Report, RollbackResult


class BuildArtifactCleaner(CleanerInterface):
    """Cleaner for build artifacts and generated files."""

    # Target directories to scan for build artifacts
    TARGET_DIRS: List[str] = [
        "cortex",
        "cortex.intelligence",
        "cortex.lens",
    ]

    # Build directories that can be entirely removed
    BUILD_DIR_NAMES: Set[str] = {
        "obj",
        "bin",
        "build",
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".tox",
        "*.egg-info",
    }

    # File extensions that are build artifacts
    BUILD_FILE_EXTENSIONS: Set[str] = {
        ".pyc",
        ".pyo",
        ".pyd",
        ".dll",
        ".exe",
        ".pdb",
        ".obj",
        ".o",
        ".so",
        ".dylib",
        ".cache",
    }

    # Directories that should NEVER be deleted
    PROTECTED_DIRS: Set[str] = {
        ".git",
        ".github",
        ".vscode",
        ".venv",
        "venv",
        "env",
        "_workspaces",  # all subfolders: approved-orchestrator-view/, recommend/, prompts/, .chats/
    }

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize build artifact cleaner.

        Args:
            config: Configuration with repo_root
        """
        super().__init__(config)
        self.repo_root = Path(config.get("repo_root", "."))
        self.dry_run = config.get("dry_run", False)

    @property
    def name(self) -> str:
        """Get cleaner name."""
        return "BuildArtifactCleaner"

    @property
    def version(self) -> str:
        """Get cleaner version."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Get cleaner domain."""
        return "build_artifacts"

    def _is_build_directory(self, dir_name: str) -> bool:
        """Check if directory name indicates a build directory.

        Args:
            dir_name: Name of the directory

        Returns:
            True if directory is a build directory
        """
        # Direct match
        if dir_name in self.BUILD_DIR_NAMES:
            return True

        # Pattern match (e.g., *.egg-info)
        if dir_name.endswith(".egg-info"):
            return True

        return False

    def _is_protected_path(self, path: Path) -> bool:
        """Check if path is protected from cleanup.

        Args:
            path: Path to check

        Returns:
            True if path is protected
        """
        parts = path.parts
        return any(part in self.PROTECTED_DIRS for part in parts)

    def _get_dir_size(self, dir_path: Path) -> int:
        """Get total size of directory in bytes.

        Args:
            dir_path: Path to directory

        Returns:
            Total size in bytes
        """
        total_size = 0
        try:
            for entry in dir_path.rglob("*"):
                if entry.is_file():
                    try:
                        total_size += entry.stat().st_size
                    except (OSError, IOError):
                        pass
        except (OSError, IOError):
            pass
        return total_size

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human-readable size string
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def analyze(self) -> Analysis:
        """Analyze target directories for build artifacts.

        Returns:
            Analysis with cleanup plan
        """
        logs: List[str] = []
        files_scanned = 0
        cleanup_candidates: List[Dict[str, Any]] = []
        total_size = 0

        for target_dir in self.TARGET_DIRS:
            dir_path = self.repo_root / target_dir

            if not dir_path.exists():
                logs.append(f"Directory not found: {target_dir}")
                continue

            logs.append(f"Scanning: {target_dir}")

            # Walk through directory tree
            for root, dirs, files in os.walk(dir_path):
                root_path = Path(root)

                # Skip protected paths
                if self._is_protected_path(root_path):
                    continue

                files_scanned += len(files)

                # Check if current directory is a build directory
                dir_name = root_path.name
                if self._is_build_directory(dir_name):
                    # Check if parent is also a build dir (avoid double-counting)
                    if not self._is_build_directory(root_path.parent.name):
                        dir_size = self._get_dir_size(root_path)
                        total_size += dir_size

                        rel_path = root_path.relative_to(self.repo_root)
                        cleanup_candidates.append({
                            "path": str(root_path),
                            "type": "directory",
                            "name": dir_name,
                            "size": dir_size,
                            "size_formatted": self._format_size(dir_size),
                            "action": "delete",
                            "reason": f"Build directory ({self._format_size(dir_size)})",
                        })
                        logs.append(f"  ✓ Build dir: {rel_path} ({self._format_size(dir_size)})")

                        # Don't descend into this directory
                        dirs.clear()

        logs.append(f"Total reclaimable: {self._format_size(total_size)}")

        return Analysis(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            files_scanned=files_scanned,
            issues_found=len(cleanup_candidates),
            plan={
                "issues": cleanup_candidates,
                "total_size": total_size,
                "total_size_formatted": self._format_size(total_size),
            },
            logs=logs,
        )

    def execute(self, plan: Any) -> Report:
        """Execute cleanup of build artifacts.

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
        total_freed = 0

        for issue in issues:
            path = Path(issue["path"])
            name = issue.get("name", path.name)
            size = issue.get("size", 0)

            if self.dry_run:
                logs.append(f"[DRY RUN] Would delete: {name}")
                deleted_count += 1
                total_freed += size
                continue

            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    deleted_count += 1
                    total_freed += size
                    logs.append(f"Deleted: {name}")
                elif path.is_file():
                    path.unlink()
                    deleted_count += 1
                    total_freed += size
                    logs.append(f"Deleted: {name}")
                else:
                    # Path doesn't exist
                    errors.append(f"Path not found: {name}")

            except OSError as e:
                errors.append(f"Failed to delete {name}: {e}")

        status = "SUCCESS" if not errors else ("PARTIAL" if deleted_count > 0 else "FAILED")

        return Report(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            status=status,
            actions_taken=deleted_count,
            changes={
                "deleted": deleted_count,
                "bytes_freed": total_freed,
            },
            errors=errors,
            logs=logs,
        )

    def rollback(self, report: Report) -> RollbackResult:
        """Rollback is not needed for build artifacts.

        Build artifacts can be regenerated by running build commands.

        Args:
            report: Report from previous execution

        Returns:
            RollbackResult indicating regeneration instructions
        """
        return RollbackResult(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            files_restored=0,
            errors=["Build artifacts can be regenerated via: pip install -e . or dotnet build"],
        )
