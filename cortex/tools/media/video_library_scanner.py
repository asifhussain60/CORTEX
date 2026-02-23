"""
cortex/tools/media/video_library_scanner.py

Recursive video file discovery for PLEX library organization.

Extends :class:`MediaScanner` to handle video-specific folder hierarchies
organized by studio. Detects studio name from parent directory and tracks
hierarchy depth for organizational classification.

Example::

    scanner = VideoLibraryScanner(Path("G:/FLICKS"))
    videos = scanner.scan()
    
    for video in videos:
        print(f"{video.studio}: {video.filename_stem} (depth={video.hierarchy_depth})")

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-VIDEO-SCANNER-2026-02-23-001
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from cortex.tools.media.media_scanner import MediaFile, MediaScanner


@dataclass
class VideoLibraryFile:
    """
    Represents a discovered video file with studio metadata.

    Extends :class:`MediaFile` with studio-specific hierarchical information.

    Attributes:
        path:            Absolute :class:`~pathlib.Path` to the video file.
        extension:       Lowercase extension including dot (e.g. ``.mp4``).
        studio:          Studio folder name (parent directory name), or empty
                         string if file is at root level.
        hierarchy_depth: Nesting depth from root: 1 (root-level), 2 (studio
                         level), 3+ (nested collections).
        folder_name:     Immediate parent directory name.
        filename_stem:   Filename without extension.
    """

    path: Path
    extension: str
    studio: str
    hierarchy_depth: int
    folder_name: str
    filename_stem: str


class VideoLibraryScanner(MediaScanner):
    """
    Recursively discovers video files under a FLICKS-style library hierarchy.

    Extends :class:`MediaScanner` to extract studio name (from parent folder)
    and track hierarchy depth. Classifies files as organized (studio-level)
    or backlog (root-level or unorganized).

    Attributes:
        root:        Root directory (typically ``G:/FLICKS``).
        extensions:  Set of supported video extensions (inherits defaults from
                     parent class).

    Examples::

        scanner = VideoLibraryScanner(Path("G:/FLICKS"))
        videos = scanner.scan()
        
        bellesa_videos = [v for v in videos if v.studio == "Bellesa"]
        organized_videos = [v for v in videos if v.hierarchy_depth >= 2]
        backlog_videos = [v for v in videos if v.hierarchy_depth == 1]
    """

    DEFAULT_EXTENSIONS: Set[str] = {
        ".mp4",
        ".m4a",
        ".mkv",
        ".avi",
        ".mov",
        ".flv",
        ".wmv",
        ".webm",
        ".3gp",
        ".ts",
        ".m3u8",
    }

    def __init__(
        self,
        root: Path,
        extensions: Optional[Set[str]] = None,
    ) -> None:
        """
        Initialize a video library scanner.

        Args:
            root:       Root directory to scan (e.g. ``G:/FLICKS``).
            extensions: Override the default video extension whitelist.
                        Must be lowercase with dot prefix.
        """
        super().__init__(root=root, extensions=extensions or self.DEFAULT_EXTENSIONS)

    def scan(self) -> List[VideoLibraryFile]:
        """
        Scan root directory tree and return video files with studio metadata.

        Returns:
            List of :class:`VideoLibraryFile`, one per discovered video file,
            sorted by path (deterministic order).

        Raises:
            FileNotFoundError: If :attr:`root` does not exist.
            NotADirectoryError: If :attr:`root` is not a directory.
        """
        if not self.root.exists():
            raise FileNotFoundError(f"Root directory not found: {self.root}")

        if not self.root.is_dir():
            raise NotADirectoryError(f"Root must be a directory: {self.root}")

        results: List[VideoLibraryFile] = []

        for file_path in sorted(self.root.rglob("*")):
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            if ext not in self.extensions:
                continue

            # Extract studio from parent folder
            studio = self._extract_studio(file_path)

            # Calculate hierarchy depth
            depth = self._calculate_hierarchy_depth(file_path, self.root)

            # Filename stem (without extension)
            stem = file_path.stem

            # Folder name (immediate parent)
            folder_name = file_path.parent.name

            video_file = VideoLibraryFile(
                path=file_path,
                extension=ext,
                studio=studio,
                hierarchy_depth=depth,
                folder_name=folder_name,
                filename_stem=stem,
            )
            results.append(video_file)

        return results

    def _extract_studio(self, file_path: Path) -> str:
        """
        Extract studio name from immediate parent directory.

        For files at root level (``G:/FLICKS/file.mp4``), returns empty string.
        For files in studio folder (``G:/FLICKS/Bellesa/file.mp4``), returns
        ``Bellesa``.

        Args:
            file_path: Full path to video file.

        Returns:
            Studio name, or empty string if file is at root.
        """
        parent = file_path.parent
        root_parent = self.root

        # If parent is root, return empty (root-level file)
        if parent == root_parent:
            return ""

        # Return immediate parent folder name (studio)
        return parent.name

    def _calculate_hierarchy_depth(
        self,
        file_path: Path,
        root: Path,
    ) -> int:
        """
        Calculate folder nesting depth from root.

        Returns:
            1 for root-level files, 2 for studio-level, 3+ for nested collections.
        """
        try:
            # Compute relative path depth
            rel_path = file_path.relative_to(root)
            # Number of parents = depth
            depth = len(rel_path.parents)
            return depth
        except ValueError:
            # file_path is not under root
            return 1


# AC_COMPLETE: AC-VIDEO-SCANNER-2026-02-23-001 ✅
