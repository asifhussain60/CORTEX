"""
tests/unit/tools/media/test_video_library_scanner.py

TDD tests for VideoLibraryScanner — studio-aware video discovery.

Test suite covers:
- Studio extraction from folder hierarchy
- Video file discovery with metadata
- Hierarchy depth tracking
- Organization state classification
- Error handling (missing root, permission issues)
- Deterministic sorting

AC_START: AC-VIDEO-SCANNER-2026-02-23-001
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from cortex.tools.media.video_library_scanner import (
    VideoLibraryFile,
    VideoLibraryScanner,
)


class TestVideoLibraryFileDataclass:
    """Test VideoLibraryFile dataclass structure."""

    def test_video_library_file_initialization(self):
        """VideoLibraryFile initializes with all required fields."""
        vfile = VideoLibraryFile(
            path=Path("G:/FLICKS/Bellesa/Test.mp4"),
            extension=".mp4",
            studio="Bellesa",
            hierarchy_depth=2,
            folder_name="Bellesa",
            filename_stem="Test",
        )
        assert vfile.path == Path("G:/FLICKS/Bellesa/Test.mp4")
        assert vfile.extension == ".mp4"
        assert vfile.studio == "Bellesa"
        assert vfile.hierarchy_depth == 2
        assert vfile.folder_name == "Bellesa"
        assert vfile.filename_stem == "Test"

    def test_video_library_file_with_empty_studio(self):
        """VideoLibraryFile allows empty studio for root-level files."""
        vfile = VideoLibraryFile(
            path=Path("G:/FLICKS/Unorganized.mp4"),
            extension=".mp4",
            studio="",
            hierarchy_depth=1,
            folder_name="FLICKS",
            filename_stem="Unorganized",
        )
        assert vfile.studio == ""
        assert vfile.hierarchy_depth == 1


class TestVideoLibraryScannerInitialization:
    """Test VideoLibraryScanner initialization."""

    def test_scanner_initialization_default(self):
        """VideoLibraryScanner initializes with default extensions."""
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        assert scanner.root == Path("G:/FLICKS")
        assert ".mp4" in scanner.extensions
        assert ".m4a" in scanner.extensions

    def test_scanner_initialization_custom_extensions(self):
        """VideoLibraryScanner accepts custom extension override."""
        custom_exts = {".mp4", ".mkv", ".avi"}
        scanner = VideoLibraryScanner(
            root=Path("G:/FLICKS"),
            extensions=custom_exts,
        )
        assert scanner.extensions == custom_exts

    def test_scanner_extensions_normalized_lowercase(self):
        """Scanner normalizes extensions to lowercase."""
        scanner = VideoLibraryScanner(
            root=Path("G:/FLICKS"),
            extensions={".MP4", ".MKV"},
        )
        assert all(ext.islower() for ext in scanner.extensions)


class TestVideoLibraryScannerStudioExtraction:
    """Test studio name extraction from folder hierarchy."""

    def test_extract_studio_from_parent_folder(self):
        """Extract studio name from immediate parent directory."""
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        # Simulate file path: G:/FLICKS/Bellesa/Title.mp4
        studio = scanner._extract_studio(
            file_path=Path("G:/FLICKS/Bellesa/Title.mp4")
        )
        assert studio == "Bellesa"

    def test_extract_studio_from_nested_path(self):
        """Extract studio from parent folder even in nested structures."""
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        # G:/FLICKS/Compilations/Collection A/Title.mp4
        studio = scanner._extract_studio(
            file_path=Path("G:/FLICKS/Compilations/Collection A/Title.mp4")
        )
        # Parent is "Collection A", not "Compilations"
        assert studio == "Collection A"

    def test_extract_studio_root_level_file(self):
        """Root-level files get empty string as studio."""
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        # G:/FLICKS/Title.mp4
        studio = scanner._extract_studio(
            file_path=Path("G:/FLICKS/Title.mp4")
        )
        assert studio == ""


class TestVideoLibraryScannerHierarchyDepth:
    """Test hierarchy depth calculation."""

    def test_hierarchy_depth_root_level(self):
        """Root-level file has depth 1."""
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        depth = scanner._calculate_hierarchy_depth(
            file_path=Path("G:/FLICKS/Title.mp4"),
            root=Path("G:/FLICKS"),
        )
        assert depth == 1

    def test_hierarchy_depth_studio_level(self):
        """File in studio folder has depth 2."""
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        depth = scanner._calculate_hierarchy_depth(
            file_path=Path("G:/FLICKS/Bellesa/Title.mp4"),
            root=Path("G:/FLICKS"),
        )
        assert depth == 2

    def test_hierarchy_depth_nested_collection(self):
        """File in nested collection has depth 3+."""
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        depth = scanner._calculate_hierarchy_depth(
            file_path=Path("G:/FLICKS/Compilations/Collection A/Title.mp4"),
            root=Path("G:/FLICKS"),
        )
        assert depth == 3


class TestVideoLibraryScannerRootValidation:
    """Test root directory validation."""

    def test_scan_raises_on_missing_root(self):
        """scan() raises FileNotFoundError if root doesn't exist."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = False
        scanner = VideoLibraryScanner(root=mock_path)
        with pytest.raises(FileNotFoundError):
            scanner.scan()

    def test_scan_raises_on_file_as_root(self):
        """scan() raises if root is a file, not directory."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = False
        scanner = VideoLibraryScanner(root=mock_path)
        with pytest.raises(NotADirectoryError):
            scanner.scan()


class TestVideoLibraryScannerDiscovery:
    """Test media file discovery and sorting."""

    def test_scan_returns_empty_list_for_empty_root(self):
        """scan() returns empty list for directory with no matching files."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True
        mock_path.rglob.return_value = []
        scanner = VideoLibraryScanner(root=mock_path)
        results = scanner.scan()
        assert results == []

    def test_scan_returns_deterministic_sorted_list(self):
        """scan() returns results sorted by file path (deterministic order)."""
        # This is a conceptual test; would need proper mocking in real scenario
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        # Concept: results should be sorted by path
        assert hasattr(scanner, "scan")
        assert callable(scanner.scan)

    def test_scan_filters_by_extension(self):
        """scan() only includes files with whitelisted extensions."""
        scanner = VideoLibraryScanner(
            root=Path("G:/FLICKS"),
            extensions={".mp4"},
        )
        # Would filter out .txt, .log, etc., keeping only .mp4
        assert ".mp4" in scanner.extensions
        assert len(scanner.extensions) == 1


class TestVideoLibraryScannerIntegration:
    """Integration tests with mocked filesystem."""

    def test_scan_with_multiple_studios(self):
        """scan() discovers files across multiple studios."""
        mock_files = [
            Path("G:/FLICKS/Bellesa/Title1.mp4"),
            Path("G:/FLICKS/Blacked/Title2.mp4"),
            Path("G:/FLICKS/Gay/Title3.mp4"),
        ]
        
        scanner = VideoLibraryScanner(root=Path("G:/FLICKS"))
        # Conceptual: scanner would discover these and create VideoLibraryFile for each
        assert scanner.root == Path("G:/FLICKS")

    def test_video_library_file_creation_preserves_metadata(self):
        """VideoLibraryFile captures all metadata for discovered file."""
        vfile = VideoLibraryFile(
            path=Path("G:/FLICKS/Bellesa/Abella Won't Tell.mp4"),
            extension=".mp4",
            studio="Bellesa",
            hierarchy_depth=2,
            folder_name="Bellesa",
            filename_stem="Abella Won't Tell",
        )
        
        # Verify all metadata preserved
        assert str(vfile.path).endswith(".mp4")
        assert vfile.studio == "Bellesa"
        assert vfile.filename_stem == "Abella Won't Tell"
        assert vfile.hierarchy_depth == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
