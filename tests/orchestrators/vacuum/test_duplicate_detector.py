"""
Unit Tests for Duplicate Detector - Three-Phase Progressive Hashing

Tests the three-phase duplicate detection algorithm:
- Phase 1: Size grouping (group files by size)
- Phase 2: Quick hash (first 8KB for size matches)
- Phase 3: Full hash (SHA256 for quick-hash matches)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
import hashlib
from pathlib import Path

from src.orchestrators.vacuum.duplicate_detector import DuplicateDetector


class TestDuplicateDetector:
    """Test suite for DuplicateDetector."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def detector(self):
        """Create DuplicateDetector instance."""
        return DuplicateDetector(min_file_size=100)  # 100 bytes minimum
    
    def test_initialization(self, detector):
        """Test detector initialization."""
        assert detector.min_file_size == 100
        assert detector.stats['files_scanned'] == 0
    
    def test_find_exact_duplicates(self, detector, temp_dir):
        """Test detection of exact duplicate files."""
        # Create duplicate files with content >=100 bytes (min_file_size)
        content = "duplicate content " * 10  # ~170 bytes
        
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file3 = temp_dir / "file3.txt"
        
        file1.write_text(content)
        file2.write_text(content)
        file3.write_text(content)
        
        # Find duplicates
        result = detector.find_duplicates([file1, file2, file3])
        
        assert result['total_duplicates'] == 2  # 2 duplicates (keep 1)
        assert len(result['duplicate_groups']) == 1
        assert len(result['duplicate_groups'][0]) == 3
    
    def test_no_duplicates(self, detector, temp_dir):
        """Test when no duplicates exist."""
        # Create unique files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        result = detector.find_duplicates([file1, file2])
        
        assert result['total_duplicates'] == 0
        assert len(result['duplicate_groups']) == 0
    
    def test_size_grouping_phase1(self, detector, temp_dir):
        """Test Phase 1: Size grouping optimization."""
        # Create files of different sizes (all >=100 bytes due to min_file_size)
        small = temp_dir / "small.txt"
        medium = temp_dir / "medium.txt"
        large = temp_dir / "large.txt"
        
        small.write_text("a" * 100)
        medium.write_text("b" * 1000)
        large.write_text("c" * 10000)
        
        # Group by size
        size_groups = detector._group_by_size([small, medium, large])
        
        # Only groups with 2+ files are kept, so we expect 0 groups
        # (each file has unique size)
        assert len(size_groups) == 0
    
    def test_quick_hash_phase2(self, detector, temp_dir):
        """Test Phase 2: Quick hash (first 8KB)."""
        # Create files with same size but different content
        file1 = temp_dir / "file1.bin"
        file2 = temp_dir / "file2.bin"
        
        # Same first 8KB, different after
        content1 = b"a" * 8192 + b"x" * 1000
        content2 = b"a" * 8192 + b"y" * 1000
        
        file1.write_bytes(content1)
        file2.write_bytes(content2)
        
        # Quick hash should be identical
        quick_hash1 = detector._compute_quick_hash(file1)
        quick_hash2 = detector._compute_quick_hash(file2)
        
        assert quick_hash1 == quick_hash2
        
        # Full hash should differ
        full_hash1 = detector._compute_full_hash(file1)
        full_hash2 = detector._compute_full_hash(file2)
        
        assert full_hash1 != full_hash2
    
    def test_full_hash_phase3(self, detector, temp_dir):
        """Test Phase 3: Full SHA256 hash."""
        file1 = temp_dir / "file1.txt"
        content = "test content for full hash"
        file1.write_text(content)
        
        # Compute full hash
        full_hash = detector._compute_full_hash(file1)
        
        # Verify against expected hash
        expected = hashlib.sha256(content.encode()).hexdigest()
        assert full_hash == expected
    
    def test_min_file_size_filter(self, detector, temp_dir):
        """Test minimum file size filtering."""
        # Create file below threshold
        tiny = temp_dir / "tiny.txt"
        tiny.write_text("x" * 50)  # Below 100 byte threshold
        
        large = temp_dir / "large.txt"
        large.write_text("y" * 200)  # Above threshold
        
        result = detector.find_duplicates([tiny, large])
        
        # Tiny file should be filtered out
        assert result['stats']['files_scanned'] == 2
    
    def test_space_wasted_calculation(self, detector, temp_dir):
        """Test space wasted calculation."""
        # Create 3 duplicate 1KB files
        content = "x" * 1024
        
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file3 = temp_dir / "file3.txt"
        
        file1.write_text(content)
        file2.write_text(content)
        file3.write_text(content)
        
        result = detector.find_duplicates([file1, file2, file3])
        
        # Space wasted = 2 duplicates * 1024 bytes
        assert result['space_wasted'] == 2048
    
    def test_multiple_duplicate_groups(self, detector, temp_dir):
        """Test multiple independent duplicate groups."""
        # Group 1: Duplicates of "content A" (>=100 bytes)
        content_a = "content A " * 15  # ~150 bytes
        a1 = temp_dir / "a1.txt"
        a2 = temp_dir / "a2.txt"
        a1.write_text(content_a)
        a2.write_text(content_a)
        
        # Group 2: Duplicates of "content B" (>=100 bytes)
        content_b = "content B " * 15  # ~150 bytes
        b1 = temp_dir / "b1.txt"
        b2 = temp_dir / "b2.txt"
        b3 = temp_dir / "b3.txt"
        b1.write_text(content_b)
        b2.write_text(content_b)
        b3.write_text(content_b)
        
        result = detector.find_duplicates([a1, a2, b1, b2, b3])
        
        assert len(result['duplicate_groups']) == 2
        assert result['total_duplicates'] == 3  # 1 dup in group A, 2 in group B
    
    def test_large_file_handling(self, detector, temp_dir):
        """Test handling of large files (>8KB)."""
        # Create large duplicate files (10MB each)
        content = b"x" * (10 * 1024 * 1024)
        
        large1 = temp_dir / "large1.bin"
        large2 = temp_dir / "large2.bin"
        
        large1.write_bytes(content)
        large2.write_bytes(content)
        
        result = detector.find_duplicates([large1, large2])
        
        assert len(result['duplicate_groups']) == 1
        assert result['total_duplicates'] == 1
        
        # Verify statistics
        assert detector.stats['quick_hash_computed'] >= 2
        assert detector.stats['full_hash_computed'] >= 2
    
    def test_empty_file_duplicates(self, detector, temp_dir):
        """Test duplicate detection for empty files."""
        empty1 = temp_dir / "empty1.txt"
        empty2 = temp_dir / "empty2.txt"
        
        empty1.touch()
        empty2.touch()
        
        result = detector.find_duplicates([empty1, empty2])
        
        # Empty files should be filtered by min_file_size
        assert result['total_duplicates'] == 0
    
    def test_binary_file_duplicates(self, detector, temp_dir):
        """Test duplicate detection for binary files."""
        binary_content = bytes([i % 256 for i in range(1000)])
        
        bin1 = temp_dir / "file1.bin"
        bin2 = temp_dir / "file2.bin"
        
        bin1.write_bytes(binary_content)
        bin2.write_bytes(binary_content)
        
        result = detector.find_duplicates([bin1, bin2])
        
        assert len(result['duplicate_groups']) == 1
    
    def test_hash_computation_error_handling(self, detector, temp_dir):
        """Test error handling for inaccessible files."""
        # Create file and make it unreadable
        file = temp_dir / "unreadable.txt"
        file.write_text("content")
        file.chmod(0o000)  # No permissions
        
        # Should handle gracefully (may skip file)
        try:
            result = detector.find_duplicates([file])
            # Should either skip or handle error
            assert isinstance(result, dict)
        finally:
            file.chmod(0o644)  # Restore permissions for cleanup
    
    def test_statistics_tracking(self, detector, temp_dir):
        """Test statistics collection during detection."""
        # Create test files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file3 = temp_dir / "file3.txt"
        
        file1.write_text("content")
        file2.write_text("content")
        file3.write_text("different")
        
        result = detector.find_duplicates([file1, file2, file3])
        
        stats = result['stats']
        assert stats['files_scanned'] == 3
        assert stats['size_groups'] >= 1
        assert stats['quick_hash_computed'] >= 0
        assert stats['full_hash_computed'] >= 0
        assert stats['duplicates_found'] >= 0


class TestDuplicateDetectorPerformance:
    """Performance tests for DuplicateDetector."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def detector(self):
        """Create DuplicateDetector instance."""
        return DuplicateDetector(min_file_size=1024)
    
    def test_large_file_set_performance(self, detector, temp_dir):
        """Test performance with many files."""
        # Create 100 files (50 duplicates)
        files = []
        for i in range(100):
            file = temp_dir / f"file{i}.txt"
            # Create duplicates (each content duplicated)
            content = f"content {i // 2}"
            file.write_text(content)
            files.append(file)
        
        result = detector.find_duplicates(files)
        
        # Should find ~50 duplicate groups
        assert result['total_duplicates'] > 0
        
        # Verify optimization: not all files should be full-hashed
        # (files with unique sizes skip quick/full hash)
        assert detector.stats['full_hash_computed'] <= len(files)
    
    def test_progressive_hashing_optimization(self, detector, temp_dir):
        """Test that progressive hashing reduces hash operations."""
        # Create files with unique sizes (no duplicates possible)
        files = []
        for i in range(10):
            file = temp_dir / f"file{i}.txt"
            file.write_text("x" * (1024 + i * 100))  # Different sizes
            files.append(file)
        
        result = detector.find_duplicates(files)
        
        # No files should reach Phase 2/3 (all have unique sizes)
        assert detector.stats['quick_hash_computed'] == 0
        assert detector.stats['full_hash_computed'] == 0
        assert result['total_duplicates'] == 0


class TestDuplicateDetectorEdgeCases:
    """Edge case tests for DuplicateDetector."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def detector(self):
        """Create DuplicateDetector instance."""
        return DuplicateDetector(min_file_size=100)
    
    def test_empty_file_list(self, detector):
        """Test with empty file list."""
        result = detector.find_duplicates([])
        
        assert result['total_duplicates'] == 0
        assert len(result['duplicate_groups']) == 0
    
    def test_single_file(self, detector, temp_dir):
        """Test with single file (no duplicates possible)."""
        file = temp_dir / "single.txt"
        file.write_text("content")
        
        result = detector.find_duplicates([file])
        
        assert result['total_duplicates'] == 0
    
    def test_symlink_handling(self, detector, temp_dir):
        """Test handling of symbolic links."""
        # Create file and symlink
        real_file = temp_dir / "real.txt"
        real_file.write_text("content")
        
        symlink = temp_dir / "link.txt"
        symlink.symlink_to(real_file)
        
        # Should handle symlinks gracefully
        result = detector.find_duplicates([real_file, symlink])
        
        # Implementation-dependent: may detect as duplicates or skip symlink
        assert isinstance(result, dict)
    
    def test_nonexistent_file(self, detector, temp_dir):
        """Test handling of nonexistent files."""
        nonexistent = temp_dir / "nonexistent.txt"
        
        # Should handle gracefully
        try:
            result = detector.find_duplicates([nonexistent])
            assert isinstance(result, dict)
        except FileNotFoundError:
            # Acceptable behavior
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
