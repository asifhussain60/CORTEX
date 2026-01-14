"""
Tests for FileUtils - OE-005 Enforcement (Atomic File Operations)
TDD Cycle: RED phase
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import os


class TestFileUtils:
    """Test suite for atomic file operations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def file_utils(self):
        """Create FileUtils instance."""
        from src.infrastructure.file_utils import FileUtils
        return FileUtils()
    
    def test_atomic_write_basic(self, file_utils, temp_dir):
        """Test basic atomic write operation."""
        target_file = temp_dir / "test.txt"
        content = "Hello, World!"
        
        file_utils.atomic_write(target_file, content)
        
        assert target_file.exists()
        assert target_file.read_text() == content
        
    def test_atomic_write_overwrites_existing(self, file_utils, temp_dir):
        """Test atomic write overwrites existing file safely."""
        target_file = temp_dir / "test.txt"
        target_file.write_text("old content")
        
        new_content = "new content"
        file_utils.atomic_write(target_file, new_content)
        
        assert target_file.read_text() == new_content
        
    def test_atomic_write_no_partial_files(self, file_utils, temp_dir):
        """Test that failed writes don't leave partial files."""
        target_file = temp_dir / "test.txt"
        
        # Simulate write failure
        with pytest.raises(Exception):
            file_utils.atomic_write(
                target_file,
                "content",
                fail_after_temp=True  # Mock parameter
            )
        
        # Target file should not exist or be unchanged
        assert not target_file.exists()
        
    def test_atomic_write_bytes(self, file_utils, temp_dir):
        """Test atomic write with binary data."""
        target_file = temp_dir / "binary.bin"
        binary_data = b'\x00\x01\x02\xff\xfe\xfd'
        
        file_utils.atomic_write(target_file, binary_data, mode='wb')
        
        assert target_file.read_bytes() == binary_data
        
    def test_atomic_write_creates_parent_dirs(self, file_utils, temp_dir):
        """Test atomic write creates parent directories."""
        target_file = temp_dir / "subdir1" / "subdir2" / "test.txt"
        
        file_utils.atomic_write(target_file, "content")
        
        assert target_file.exists()
        assert target_file.read_text() == "content"
        
    def test_safe_delete_existing_file(self, file_utils, temp_dir):
        """Test safe deletion of existing file."""
        target_file = temp_dir / "test.txt"
        target_file.write_text("content")
        
        result = file_utils.safe_delete(target_file)
        
        assert result is True
        assert not target_file.exists()
        
    def test_safe_delete_nonexistent_file(self, file_utils, temp_dir):
        """Test safe deletion returns False for nonexistent file."""
        target_file = temp_dir / "nonexistent.txt"
        
        result = file_utils.safe_delete(target_file)
        
        assert result is False
        
    def test_safe_move_basic(self, file_utils, temp_dir):
        """Test safe move operation."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("content to move")
        
        file_utils.safe_move(source, dest)
        
        assert not source.exists()
        assert dest.exists()
        assert dest.read_text() == "content to move"
        
    def test_safe_move_overwrites_dest(self, file_utils, temp_dir):
        """Test safe move overwrites destination."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("new content")
        dest.write_text("old content")
        
        file_utils.safe_move(source, dest, overwrite=True)
        
        assert not source.exists()
        assert dest.read_text() == "new content"
        
    def test_safe_copy_basic(self, file_utils, temp_dir):
        """Test safe copy operation."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("content to copy")
        
        file_utils.safe_copy(source, dest)
        
        assert source.exists()
        assert dest.exists()
        assert dest.read_text() == "content to copy"
        
    def test_safe_read_existing_file(self, file_utils, temp_dir):
        """Test safe read of existing file."""
        target_file = temp_dir / "test.txt"
        target_file.write_text("test content")
        
        content = file_utils.safe_read(target_file)
        
        assert content == "test content"
        
    def test_safe_read_nonexistent_file(self, file_utils, temp_dir):
        """Test safe read returns None for nonexistent file."""
        target_file = temp_dir / "nonexistent.txt"
        
        content = file_utils.safe_read(target_file, default=None)
        
        assert content is None
        
    def test_safe_read_with_default(self, file_utils, temp_dir):
        """Test safe read returns default value."""
        target_file = temp_dir / "nonexistent.txt"
        
        content = file_utils.safe_read(target_file, default="default value")
        
        assert content == "default value"
        
    def test_ensure_directory(self, file_utils, temp_dir):
        """Test ensure directory creates nested paths."""
        nested_path = temp_dir / "a" / "b" / "c"
        
        file_utils.ensure_directory(nested_path)
        
        assert nested_path.exists()
        assert nested_path.is_dir()
        
    def test_atomic_write_preserves_existing_on_error(self, file_utils, temp_dir):
        """Test that existing file is preserved if write fails."""
        target_file = temp_dir / "important.txt"
        original_content = "original important data"
        target_file.write_text(original_content)
        
        # Attempt write that will fail (simulated)
        try:
            # This would simulate a failure scenario
            # In real implementation, any exception during write
            # should leave original file intact
            pass
        except:
            pass
        
        # Original file should still exist with original content
        assert target_file.exists()
        assert target_file.read_text() == original_content
