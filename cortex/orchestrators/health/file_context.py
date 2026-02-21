"""FileContext — Single Filesystem Snapshot

Performs exactly ONE ``rglob("*")`` walk, caching all file paths, content,
and MD5 hashes.  Agents and orchestrators receive this shared context —
no additional disk traversal required.

Phase: PHASE-51
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set

from .constants import EXCLUDED_DIRS


class FileContext:
    """Immutable snapshot of the workspace filesystem.

    Usage::

        ctx = FileContext.build(Path("/path/to/workspace"))
        for f in ctx.all_files:
            print(ctx.get_content(f))

    Attributes:
        workspace_root: Absolute path of the workspace.
        all_files: Every file discovered (excludes excluded dirs).
        directories: Every directory discovered (excludes excluded dirs).
    """

    __slots__ = (
        "workspace_root",
        "all_files",
        "directories",
        "_content_cache",
        "_hash_cache",
    )

    def __init__(
        self,
        workspace_root: Path,
        all_files: List[Path],
        directories: List[Path],
    ) -> None:
        """Initialize instance."""
        self.workspace_root = workspace_root
        self.all_files = all_files
        self.directories = directories
        self._content_cache: Dict[Path, str] = {}
        self._hash_cache: Dict[Path, str] = {}

    # ── factory ──────────────────────────────────────────────────────────

    @classmethod
    def build(
        cls,
        workspace_root: Path,
        excluded_dirs: FrozenSet[str] | None = None,
    ) -> "FileContext":
        """Build a FileContext with a single ``rglob`` walk.

        Args:
            workspace_root: Root directory to scan.
            excluded_dirs: Directory names to skip.  Defaults to
                :data:`constants.EXCLUDED_DIRS`.

        Returns:
            Populated FileContext.
        """
        exclude = excluded_dirs if excluded_dirs is not None else EXCLUDED_DIRS
        files: List[Path] = []
        dirs: Set[Path] = set()

        for entry in workspace_root.rglob("*"):
            # Check if any parent component is excluded
            if _is_excluded(entry, workspace_root, exclude):
                continue
            if entry.is_file():
                files.append(entry)
                if entry.parent != workspace_root:
                    dirs.add(entry.parent)
            elif entry.is_dir():
                dirs.add(entry)

        return cls(
            workspace_root=workspace_root,
            all_files=sorted(files),
            directories=sorted(dirs),
        )

    # ── cached accessors ─────────────────────────────────────────────────

    def get_content(self, path: Path) -> Optional[str]:
        """Return the text content of *path*, reading at most once.

        Args:
            path: Absolute path to a file.

        Returns:
            File text, or ``None`` if the file is not in the snapshot or
            cannot be decoded.
        """
        if path in self._content_cache:
            return self._content_cache[path]
        if path not in self.all_files:
            return None
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            return None
        self._content_cache[path] = text
        return text

    def get_hash(self, path: Path) -> Optional[str]:
        """Return the MD5 hex-digest of *path*, computing at most once.

        Args:
            path: Absolute path to a file.

        Returns:
            32-character hex string, or ``None`` if unavailable.
        """
        if path in self._hash_cache:
            return self._hash_cache[path]
        if path not in self.all_files:
            return None
        try:
            data = path.read_bytes()
        except OSError:
            return None
        digest = hashlib.md5(data).hexdigest()  # noqa: S324 — non-security use
        self._hash_cache[path] = digest
        return digest

    # ── convenience properties ───────────────────────────────────────────

    @property
    def python_files(self) -> List[Path]:
        """All ``.py`` / ``.pyi`` files."""
        return [f for f in self.all_files if f.suffix in (".py", ".pyi")]

    @property
    def file_count(self) -> int:
        """Total number of files in the snapshot."""
        return len(self.all_files)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _is_excluded(
    entry: Path,
    workspace_root: Path,
    excluded: FrozenSet[str],
) -> bool:
    """Return True if *entry* sits under an excluded directory."""
    try:
        relative = entry.relative_to(workspace_root)
    except ValueError:
        return True
    return any(part in excluded for part in relative.parts)


__all__ = ["FileContext"]
