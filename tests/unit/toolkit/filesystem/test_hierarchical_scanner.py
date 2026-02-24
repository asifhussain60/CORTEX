"""Tests for HierarchicalScanner — Generic recursive file discovery.

TDD Phase: RED → Tests written before implementation
Authority: phase-toolkit-consolidation.yaml Sub-phase S2
CORE-008: TDD mandatory

AC_START: AC-TOOLKIT-HIERARCHICAL-SCANNER-TEST-001
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Set

import pytest

from cortex.toolkit.filesystem.hierarchical_scanner import (
    HierarchicalScanner,
    ScannedFile,
    OrganizationAdapter,
)


@pytest.fixture
def temp_hierarchy():
    """Create temporary directory hierarchy for testing.
    
    Structure:
        root/
            file1.txt
            file2.mp4
            Studio_A/
                video1.mp4
                video2.mkv
                Collection_X/
                    video3.mp4
            Studio_B/
                video4.avi
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Root level files
        (root / "file1.txt").write_text("content")
        (root / "file2.mp4").write_text("content")
        
        # Studio A with nested collection
        studio_a = root / "Studio_A"
        studio_a.mkdir()
        (studio_a / "video1.mp4").write_text("content")
        (studio_a / "video2.mkv").write_text("content")
        
        collection_x = studio_a / "Collection_X"
        collection_x.mkdir()
        (collection_x / "video3.mp4").write_text("content")
        
        # Studio B
        studio_b = root / "Studio_B"
        studio_b.mkdir()
        (studio_b / "video4.avi").write_text("content")
        
        yield root


class TestHierarchicalScanner:
    """Test HierarchicalScanner initialization and basic functionality."""
    
    def test_scanner_initialization(self, temp_hierarchy: Path):
        """Scanner must initialize with root path and default extensions."""
        scanner = HierarchicalScanner(root=temp_hierarchy)
        
        assert scanner.root == temp_hierarchy
        assert isinstance(scanner.extensions, set)
        assert len(scanner.extensions) > 0
    
    def test_scanner_custom_extensions(self, temp_hierarchy: Path):
        """Scanner must accept custom extension set."""
        custom_exts = {".mp4", ".mkv", ".avi"}
        scanner = HierarchicalScanner(root=temp_hierarchy, extensions=custom_exts)
        
        assert scanner.extensions == custom_exts
    
    def test_scan_discovers_all_files(self, temp_hierarchy: Path):
        """Scanner must discover all files matching extensions."""
        scanner = HierarchicalScanner(
            root=temp_hierarchy,
            extensions={".mp4", ".mkv", ".avi"}
        )
        
        files = scanner.scan()
        
        assert isinstance(files, list)
        assert len(files) == 5  # file2.mp4 + video1.mp4 + video2.mkv + video3.mp4 + video4.avi
        assert all(isinstance(f, ScannedFile) for f in files)
    
    def test_scan_filters_by_extension(self, temp_hierarchy: Path):
        """Scanner must filter files by extension."""
        scanner = HierarchicalScanner(
            root=temp_hierarchy,
            extensions={".txt"}
        )
        
        files = scanner.scan()
        
        assert len(files) == 1
        assert files[0].extension == ".txt"
    
    def test_hierarchy_depth_root_level(self, temp_hierarchy: Path):
        """Root-level files must have hierarchy_depth=1."""
        scanner = HierarchicalScanner(root=temp_hierarchy)
        files = scanner.scan()
        
        root_files = [f for f in files if f.hierarchy_depth == 1]
        assert len(root_files) == 2  # file1.txt, file2.mp4
    
    def test_hierarchy_depth_studio_level(self, temp_hierarchy: Path):
        """Studio-level files must have hierarchy_depth=2."""
        scanner = HierarchicalScanner(
            root=temp_hierarchy,
            extensions={".mp4", ".mkv", ".avi"}
        )
        files = scanner.scan()
        
        studio_files = [f for f in files if f.hierarchy_depth == 2]
        assert len(studio_files) == 3  # Studio_A: video1.mp4 + video2.mkv, Studio_B: video4.avi
    
    def test_hierarchy_depth_nested_collection(self, temp_hierarchy: Path):
        """Nested collection files must have hierarchy_depth=3."""
        scanner = HierarchicalScanner(
            root=temp_hierarchy,
            extensions={".mp4"}
        )
        files = scanner.scan()
        
        nested_files = [f for f in files if f.hierarchy_depth == 3]
        assert len(nested_files) == 1  # Collection_X/video3.mp4
    
    def test_organization_name_extraction(self, temp_hierarchy: Path):
        """Scanner must extract organization name from parent directory."""
        scanner = HierarchicalScanner(
            root=temp_hierarchy,
            extensions={".mp4"}
        )
        files = scanner.scan()
        
        studio_a_files = [f for f in files if f.organization == "Studio_A"]
        assert len(studio_a_files) >= 1  # At least video1.mp4
    
    def test_folder_name_tracking(self, temp_hierarchy: Path):
        """Scanner must track immediate parent folder name."""
        scanner = HierarchicalScanner(root=temp_hierarchy)
        files = scanner.scan()
        
        assert all(isinstance(f.folder_name, str) for f in files)
        assert any(f.folder_name == "Collection_X" for f in files)
    
    def test_filename_stem_extraction(self, temp_hierarchy: Path):
        """Scanner must extract filename without extension."""
        scanner = HierarchicalScanner(
            root=temp_hierarchy,
            extensions={".mp4"}
        )
        files = scanner.scan()
        
        stems = {f.filename_stem for f in files}
        assert "video1" in stems
        assert "video3" in stems


class TestScannedFile:
    """Test ScannedFile dataclass."""
    
    def test_scanned_file_creation(self):
        """ScannedFile must be creatable with required fields."""
        file = ScannedFile(
            path=Path("/test/file.mp4"),
            extension=".mp4",
            organization="Studio",
            hierarchy_depth=2,
            folder_name="Studio",
            filename_stem="file"
        )
        
        assert file.path == Path("/test/file.mp4")
        assert file.extension == ".mp4"
        assert file.organization == "Studio"
        assert file.hierarchy_depth == 2
    
    def test_scanned_file_equality(self):
        """ScannedFile instances with same path must be equal."""
        file1 = ScannedFile(
            path=Path("/test/file.mp4"),
            extension=".mp4",
            organization="Studio",
            hierarchy_depth=2,
            folder_name="Studio",
            filename_stem="file"
        )
        file2 = ScannedFile(
            path=Path("/test/file.mp4"),
            extension=".mp4",
            organization="Studio",
            hierarchy_depth=2,
            folder_name="Studio",
            filename_stem="file"
        )
        
        assert file1 == file2


class TestOrganizationAdapter:
    """Test OrganizationAdapter protocol."""
    
    def test_adapter_protocol_exists(self):
        """OrganizationAdapter protocol must be importable."""
        assert OrganizationAdapter is not None
    
    def test_adapter_detect_organization_method(self):
        """OrganizationAdapter must define detect_organization method."""
        # This will be implemented in GREEN phase
        # Protocol should require: detect_organization(path: Path, folder_name: str) -> str
        pass


class TestScannerWithAdapter:
    """Test HierarchicalScanner with custom OrganizationAdapter."""
    
    def test_scanner_accepts_adapter(self, temp_hierarchy: Path):
        """Scanner must accept custom organization adapter."""
        # Custom adapter will be provided in GREEN phase
        # For now, test that parameter exists
        scanner = HierarchicalScanner(
            root=temp_hierarchy,
            adapter=None  # Will be replaced with actual adapter
        )
        
        assert scanner is not None
    
    def test_adapter_overrides_default_detection(self, temp_hierarchy: Path):
        """Custom adapter must override default organization detection."""
        # Will be implemented in GREEN phase
        # Adapter should transform "Studio_A" → "StudioA" or similar
        pass


# AC_COMPLETE: AC-TOOLKIT-HIERARCHICAL-SCANNER-TEST-001 ✅ Tests written (RED phase)
