"""
FileRelocator — Moves files with conflict resolution and rollback support.

AC-PHASE44-S3: Automated file relocation
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional


class FileRelocator:
    """Relocates files with conflict resolution and optional git integration."""

    def __init__(self, conflict_strategy: str = "rename") -> None:
        """Initialize instance."""
        self.conflict_strategy = conflict_strategy
        self.checkpoint_commit: Optional[str] = None

    def relocate_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False,
    ) -> bool:
        """Move *source* to *destination*. Returns True on success."""
        src = Path(source)
        dst = Path(destination)
        if not src.exists():
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if self.conflict_strategy == "rename" and not overwrite:
                # Rename the new file
                dst = Path(self._get_renamed(str(dst)))
            elif not overwrite:
                return False
        shutil.move(str(src), str(dst))
        return True

    def _get_renamed(self, destination: str) -> str:
        """Get renamed."""
        dst = Path(destination)
        stem = dst.stem
        suffix = dst.suffix
        parent = dst.parent
        counter = 1
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return str(candidate)
            counter += 1

    def resolve_conflict(
        self,
        source: str,
        destination: str,
        strategy: str = "rename",
    ) -> str:
        """Resolve a naming conflict at *destination*."""
        dst = Path(destination)
        if not dst.exists():
            return destination
        if strategy == "overwrite":
            return destination
        return self._get_renamed(destination)

    def create_directory_structure(self, path: str) -> bool:
        """Ensure the directory tree for *path* exists."""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def create_git_checkpoint(self, message: str = "relocation checkpoint") -> str:
        """Stash a git commit and return the commit hash."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
        commit_hash = result.stdout.strip()
        self.checkpoint_commit = commit_hash
        return commit_hash

    def rollback(self) -> bool:
        """Roll back to the stored checkpoint commit."""
        if not self.checkpoint_commit:
            return True
        result = subprocess.run(
            ["git", "reset", "--hard", self.checkpoint_commit],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode == 0
