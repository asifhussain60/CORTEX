"""
Tests for DuplicateDetector - TDD RED Phase

Tests duplicate detection in planning artifacts.

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path
import hashlib

from src.workflows.duplicate_detector import (
    DuplicateDetector,
    DuplicateGroup,
    ResolutionStrategy
)


@pytest.fixture
def detector(tmp_path):
    """Fixture for DuplicateDetector."""
    return DuplicateDetector(root_directory=tmp_path)


@pytest.fixture
def sample_files_with_duplicates(tmp_path):
    """Create sample files with duplicates."""
    # Original file
    original = tmp_path / "plan-v1.yaml"
    original.write_text("plan_id: test\ntitle: Test Plan\ncontent: original")
    
    # Exact duplicate (same content)
    duplicate1 = tmp_path / "plan-v1-copy.yaml"
    duplicate1.write_text("plan_id: test\ntitle: Test Plan\ncontent: original")
    
    # Near duplicate (similar content)
    duplicate2 = tmp_path / "plan-v2.yaml"
    duplicate2.write_text("plan_id: test\ntitle: Test Plan\ncontent: modified slightly")
    
    # Unique file
    unique = tmp_path / "other-plan.yaml"
    unique.write_text("plan_id: other\ntitle: Other Plan\ncontent: completely different")
    
    return tmp_path


class TestDuplicateDetectorInit:
    """Test duplicate detector initialization."""
    
    def test_detector_initialization(self, detector):
        """Test detector can be initialized."""
        assert detector is not None
        assert detector.root_directory.exists()
    
    def test_detector_validates_directory(self, tmp_path):
        """Test detector validates directory existence."""
        nonexistent = tmp_path / "nonexistent"
        
        with pytest.raises(ValueError):
            DuplicateDetector(root_directory=nonexistent)


class TestDuplicateFinding:
    """Test finding duplicates."""
    
    def test_find_exact_duplicates(self, detector, sample_files_with_duplicates):
        """Test finding exact content duplicates."""
        detector.root_directory = sample_files_with_duplicates
        
        duplicates = detector.find_duplicates()
        
        assert isinstance(duplicates, list)
        assert len(duplicates) >= 1  # Should find at least one duplicate group
        
        # Check first group has exact duplicates
        exact_group = next((g for g in duplicates if len(g.files) >= 2), None)
        assert exact_group is not None
    
    def test_find_duplicates_by_content_hash(self, detector, tmp_path):
        """Test finding duplicates using content hash."""
        # Create files with same content
        file1 = tmp_path / "file1.yaml"
        file1.write_text("identical content")
        
        file2 = tmp_path / "file2.yaml"
        file2.write_text("identical content")
        
        detector.root_directory = tmp_path
        duplicates = detector.find_duplicates()
        
        assert len(duplicates) >= 1
        assert len(duplicates[0].files) == 2
    
    def test_find_duplicates_by_filename_similarity(self, detector, tmp_path):
        """Test finding duplicates by similar filenames."""
        # Create files with similar names
        file1 = tmp_path / "PLAN-2025-12-14-feature.yaml"
        file1.write_text("content1")
        
        file2 = tmp_path / "PLAN-2025-12-14-feature-v2.yaml"
        file2.write_text("content2")
        
        detector.root_directory = tmp_path
        duplicates = detector.find_duplicates(check_filename_similarity=True)
        
        # Should detect similar filenames
        assert isinstance(duplicates, list)
    
    def test_find_no_duplicates(self, detector, tmp_path):
        """Test when no duplicates exist."""
        # Create unique files
        file1 = tmp_path / "file1.yaml"
        file1.write_text("unique content 1")
        
        file2 = tmp_path / "file2.yaml"
        file2.write_text("unique content 2")
        
        detector.root_directory = tmp_path
        duplicates = detector.find_duplicates()
        
        assert isinstance(duplicates, list)
        assert len(duplicates) == 0


class TestDuplicateGrouping:
    """Test grouping duplicates."""
    
    def test_group_by_content_hash(self, detector, sample_files_with_duplicates):
        """Test grouping files by content hash."""
        detector.root_directory = sample_files_with_duplicates
        
        groups = detector.group_by_hash()
        
        assert isinstance(groups, dict)
        # Should have groups for identical content
        duplicate_groups = [g for g in groups.values() if len(g) > 1]
        assert len(duplicate_groups) >= 1
    
    def test_duplicate_group_metadata(self, detector, sample_files_with_duplicates):
        """Test duplicate group contains metadata."""
        detector.root_directory = sample_files_with_duplicates
        
        duplicates = detector.find_duplicates()
        
        if duplicates:
            group = duplicates[0]
            assert isinstance(group, DuplicateGroup)
            assert hasattr(group, 'files')
            assert hasattr(group, 'hash')
            assert len(group.files) >= 2


class TestDuplicateResolution:
    """Test duplicate resolution strategies."""
    
    def test_resolve_keep_newest(self, detector, tmp_path):
        """Test keep newest resolution strategy."""
        # Create files with different timestamps
        import time
        
        file1 = tmp_path / "file1.yaml"
        file1.write_text("duplicate")
        time.sleep(0.01)  # Small delay
        
        file2 = tmp_path / "file2.yaml"
        file2.write_text("duplicate")
        
        detector.root_directory = tmp_path
        duplicates = detector.find_duplicates()
        
        if duplicates:
            result = detector.resolve_duplicates(
                duplicates[0],
                strategy=ResolutionStrategy.KEEP_NEWEST
            )
            
            assert result.kept_file is not None
            assert result.removed_files is not None
    
    def test_resolve_keep_largest(self, detector, tmp_path):
        """Test keep largest resolution strategy."""
        # Create files with different sizes
        file1 = tmp_path / "file1.yaml"
        file1.write_text("small")
        
        file2 = tmp_path / "file2.yaml"
        file2.write_text("small content but larger file size")
        
        detector.root_directory = tmp_path
        
        # Should keep larger file
        # (Implementation will handle this)
    
    def test_resolve_manual(self, detector, tmp_path):
        """Test manual resolution strategy."""
        file1 = tmp_path / "file1.yaml"
        file1.write_text("duplicate")
        
        file2 = tmp_path / "file2.yaml"
        file2.write_text("duplicate")
        
        detector.root_directory = tmp_path
        duplicates = detector.find_duplicates()
        
        if duplicates:
            # Manual should not delete anything automatically
            result = detector.resolve_duplicates(
                duplicates[0],
                strategy=ResolutionStrategy.MANUAL
            )
            
            assert result.action == "manual_review"


class TestDuplicateArchiving:
    """Test archiving duplicate files."""
    
    def test_move_duplicates_to_archive(self, detector, sample_files_with_duplicates):
        """Test moving duplicate files to archive folder."""
        detector.root_directory = sample_files_with_duplicates
        
        duplicates = detector.find_duplicates()
        
        if duplicates:
            archive_path = detector.archive_duplicates(duplicates[0])
            
            assert archive_path.exists()
            assert archive_path.name == "duplicates"
            assert archive_path.parent == sample_files_with_duplicates
    
    def test_generate_duplicate_manifest(self, detector, sample_files_with_duplicates):
        """Test generating manifest of duplicates."""
        detector.root_directory = sample_files_with_duplicates
        
        duplicates = detector.find_duplicates()
        
        if duplicates:
            manifest = detector.generate_duplicate_manifest(duplicates)
            
            assert isinstance(manifest, dict)
            assert "duplicates_found" in manifest
            assert "total_groups" in manifest


class TestDuplicateReporting:
    """Test duplicate detection reporting."""
    
    def test_generate_duplicate_report(self, detector, sample_files_with_duplicates):
        """Test generating duplicate detection report."""
        detector.root_directory = sample_files_with_duplicates
        
        duplicates = detector.find_duplicates()
        
        report = detector.generate_report(duplicates)
        
        assert isinstance(report, str)
        assert "Duplicate" in report or "duplicate" in report.lower()
    
    def test_report_includes_statistics(self, detector, sample_files_with_duplicates):
        """Test report includes statistics."""
        detector.root_directory = sample_files_with_duplicates
        
        duplicates = detector.find_duplicates()
        report = detector.generate_report(duplicates)
        
        # Should include counts
        assert any(char.isdigit() for char in report)


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_directory(self, detector):
        """Test detector handles empty directory."""
        duplicates = detector.find_duplicates()
        
        assert isinstance(duplicates, list)
        assert len(duplicates) == 0
    
    def test_single_file(self, detector, tmp_path):
        """Test detector handles single file."""
        file1 = tmp_path / "single.yaml"
        file1.write_text("content")
        
        detector.root_directory = tmp_path
        duplicates = detector.find_duplicates()
        
        assert len(duplicates) == 0
    
    def test_binary_files_skipped(self, detector, tmp_path):
        """Test detector skips binary files."""
        # Create binary file
        binary = tmp_path / "image.png"
        binary.write_bytes(b'\x89PNG\r\n\x1a\n')
        
        # Create text file
        text = tmp_path / "plan.yaml"
        text.write_text("content")
        
        detector.root_directory = tmp_path
        duplicates = detector.find_duplicates()
        
        # Should only process text files
        assert isinstance(duplicates, list)


class TestIntegration:
    """Integration tests."""
    
    def test_full_duplicate_workflow(self, detector, sample_files_with_duplicates):
        """Test complete duplicate detection and resolution workflow."""
        detector.root_directory = sample_files_with_duplicates
        
        # 1. Find duplicates
        duplicates = detector.find_duplicates()
        assert len(duplicates) >= 1
        
        # 2. Generate report
        report = detector.generate_report(duplicates)
        assert len(report) > 0
        
        # 3. Resolve (manual review)
        if duplicates:
            result = detector.resolve_duplicates(
                duplicates[0],
                strategy=ResolutionStrategy.MANUAL
            )
            assert result is not None
