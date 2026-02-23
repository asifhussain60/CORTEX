"""
cortex/tools/media/media_scanner.py

Recursive media file discovery for :class:`MediaTagCleaner`.

Scans a root directory tree and returns :class:`MediaFile` objects for every
file whose extension is in the supported set (or a custom override).

Default supported extensions::

    .mp4 .m4a .mp3 .flac .ogg .aac .wav .wma .opus .ape .aiff

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-MEDIA-2026-02-23-002
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set


@dataclass
class MediaFile:
    """
    Represents a single discovered media file.

    Attributes:
        path:        Absolute :class:`~pathlib.Path` to the file.
        extension:   Lowercase extension including leading dot (e.g. ``.mp4``).
        folder_name: Name of the immediate parent directory.
    """

    path: Path
    extension: str
    folder_name: str


class MediaScanner:
    """
    Recursively discovers media files under a root directory.

    Attributes:
        root:       Root directory to scan.
        extensions: Set of lowercase extensions to include (dot-prefixed).

    Examples::

        scanner = MediaScanner(Path("Z:/MUSIC/Bollywood"))
        files = scanner.scan()

        # Custom extensions only:
        scanner = MediaScanner(root, extensions={".mp4", ".mp3"})
    """

    DEFAULT_EXTENSIONS: Set[str] = {
        ".mp4",
        ".m4a",
        ".mp3",
        ".flac",
        ".ogg",
        ".aac",
        ".wav",
        ".wma",
        ".opus",
        ".ape",
        ".aiff",
    }

    def __init__(
        self,
        root: Path,
        extensions: Optional[Set[str]] = None,
    ) -> None:
        """
        Initialise a scanner for *root*.

        Args:
            root:       Directory to scan recursively.
            extensions: Override the default extension whitelist.
                        Values must be lowercase and dot-prefixed
                        (e.g. ``{".mp4", ".mp3"}``).
        """
        self.root: Path = root
        self.extensions: Set[str] = (
            {ext.lower() for ext in extensions} if extensions else self.DEFAULT_EXTENSIONS
        )

    def scan(self) -> List[MediaFile]:
        """
        Walk the tree under :attr:`root` and collect matching media files.

        Returns:
            List of :class:`MediaFile` instances, one per matching file.
            The list is sorted by path for deterministic ordering.

        Raises:
            FileNotFoundError: If :attr:`root` does not exist.
        """
        if not self.root.exists():
            raise FileNotFoundError(f"Root directory not found: {self.root}")

        results: List[MediaFile] = []
        for file_path in sorted(self.root.rglob("*")):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lower()
            if ext not in self.extensions:
                continue
            results.append(
                MediaFile(
                    path=file_path,
                    extension=ext,
                    folder_name=file_path.parent.name,
                )
            )
        return results


# AC_COMPLETE: AC-MEDIA-2026-02-23-002 ✅
