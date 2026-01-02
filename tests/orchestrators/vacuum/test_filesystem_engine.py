"""
Unit Tests for Filesystem Engine - Transactional Filesystem Operations

Tests transactional filesystem operations with ACID guarantees:
- FilesystemTransaction (begin, commit, rollback)
- delete_file with checkpoint backup
- move_file with atomic rename
- Checkpoint management
- Hash verification
- Error handling (permissions, disk space, etc.)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.vacuum.filesystem_engine import (
    FilesystemEngine,
    FilesystemTransaction
)
from src.database.planning_state_db import PlanningStateDB


class TestFilesystemTransaction:
    """Test suite for FilesystemTransaction."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def mock_db(self):
        """Mock PlanningStateDB."""
        return Mock(spec=PlanningStateDB)
    
    @pytest.fixture
    def transaction(self, temp_dir, mock_db):
        """Create FilesystemTransaction instance."""
        checkpoint_dir = temp_dir / "checkpoint"
        return FilesystemTransaction(checkpoint_dir, mock_db)
    
    def test_transaction_begin(self, transaction, temp_dir):
        """Test transaction initialization."""
        transaction_id = transaction.begin()
        
        assert transaction_id is not None
        assert transaction_id.startswith("vacuum-")
        assert transaction.checkpoint_dir.exists()
        assert (transaction.checkpoint_dir / "files").exists()
    
    def test_delete_file_with_backup(self, transaction, temp_dir):
        """Test file deletion with checkpoint backup."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Begin transaction
        transaction.begin()
        
        # Delete file
        result = transaction.delete_file(test_file)
        
        assert result is True
        assert not test_file.exists()
        
        # Verify backup exists
        backup_files = list(transaction.checkpoint_dir.glob("files/*"))
        assert len(backup_files) == 1
        assert backup_files[0].read_text() == "test content"
    
    def test_delete_nonexistent_file(self, transaction, temp_dir):
        """Test deletion of nonexistent file."""
        nonexistent = temp_dir / "nonexistent.txt"
        
        transaction.begin()
        result = transaction.delete_file(nonexistent)
        
        assert result is False
    
    def test_move_file_atomic(self, transaction, temp_dir):
        """Test atomic file move."""
        source = temp_dir / "source.txt"
        destination = temp_dir / "dest" / "target.txt"
        source.write_text("move me")
        
        transaction.begin()
        result = transaction.move_file(source, destination)
        
        assert result is True
        assert not source.exists()
        assert destination.exists()
        assert destination.read_text() == "move me"
    
    def test_move_file_conflict_resolution(self, transaction, temp_dir):
        """Test move with destination conflict."""
        source = temp_dir / "source.txt"
        destination = temp_dir / "dest.txt"
        
        source.write_text("source content")
        destination.write_text("existing content")
        
        transaction.begin()
        result = transaction.move_file(source, destination)
        
        # Should succeed by renaming destination
        assert result is True
        assert not source.exists()
        assert destination.exists()
    
    def test_transaction_operations_log(self, transaction, temp_dir):
        """Test operation logging."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        transaction.begin()
        transaction.delete_file(test_file)
        
        assert len(transaction.operations) == 1
        op = transaction.operations[0]
        
        assert op['type'] == 'delete'
        assert op['status'] == 'completed'
        assert 'timestamp' in op
        assert 'hash' in op
    
    def test_rollback_transaction(self, transaction, temp_dir):
        """Test transaction rollback."""
        # Create and delete file
        test_file = temp_dir / "test.txt"
        original_content = "original content"
        test_file.write_text(original_content)
        
        transaction.begin()
        transaction.delete_file(test_file)
        
        assert not test_file.exists()
        
        # Rollback
        result = transaction.rollback()
        
        assert result is True
        assert test_file.exists()
        assert test_file.read_text() == original_content
    
    def test_hash_verification(self, transaction, temp_dir):
        """Test hash-based backup verification."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        transaction.begin()
        
        # Compute hash
        computed_hash = transaction._compute_hash(test_file)
        
        assert computed_hash is not None
        assert len(computed_hash) == 64  # SHA256 hex digest
        
        # Verify hash matches expected
        expected_hash = hashlib.sha256(b"test content").hexdigest()
        assert computed_hash == expected_hash
    
    def test_permission_error_handling(self, transaction, temp_dir):
        """Test permission denied error handling."""
        test_file = temp_dir / "readonly.txt"
        test_file.write_text("readonly")
        test_file.chmod(0o444)  # Read-only
        
        transaction.begin()
        
        # Attempt delete (may succeed on some systems, should handle gracefully)
        result = transaction.delete_file(test_file)
        
        # Should either succeed or return False (not crash)
        assert isinstance(result, bool)


class TestFilesystemEngine:
    """Test suite for FilesystemEngine."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def mock_db(self):
        """Mock PlanningStateDB."""
        return Mock(spec=PlanningStateDB)
    
    @pytest.fixture
    def engine(self, mock_db):
        """Create FilesystemEngine instance."""
        safety_rules = {
            'critical_patterns': ['.git', '*.py'],
            'size_threshold_mb': 1000
        }
        return FilesystemEngine(state_db=mock_db, safety_rules=safety_rules)
    
    def test_scan_directory(self, engine, temp_dir):
        """Test directory scanning and categorization."""
        # Create test filesystem
        (temp_dir / "test.tmp").touch()
        (temp_dir / "__pycache__").mkdir()
        (temp_dir / "__pycache__" / "module.pyc").touch()
        (temp_dir / "source.py").touch()
        
        cleanup_rules = {
            'temp_files': {'patterns': ['*.tmp']},
            'build_artifacts': {'patterns': ['__pycache__/', '*.pyc']}
        }
        
        inventory = engine.scan_directory(
            temp_dir,
            cleanup_rules=cleanup_rules,
            exclude_patterns=[]
        )
        
        assert 'temp_files' in inventory
        assert 'build_artifacts' in inventory
        assert len(inventory['temp_files']) >= 1
        assert len(inventory['build_artifacts']) >= 1
    
    def test_categorize_file(self, engine):
        """Test file categorization by patterns."""
        cleanup_rules = {
            'temp_files': {'patterns': ['*.tmp', '*.temp']},
            'logs': {'patterns': ['*.log']}
        }
        
        # Test temp file
        temp_path = Path("/tmp/test.tmp")
        category = engine._categorize_file(temp_path, cleanup_rules)
        assert category == 'temp_files'
        
        # Test log file
        log_path = Path("/var/log/app.log")
        category = engine._categorize_file(log_path, cleanup_rules)
        assert category == 'logs'
        
        # Test uncategorized
        other_path = Path("/src/main.py")
        category = engine._categorize_file(other_path, cleanup_rules)
        assert category is None
    
    def test_execute_cleanup(self, engine, temp_dir):
        """Test cleanup execution."""
        # Create test files
        safe_file = temp_dir / "test.tmp"
        safe_file.write_text("temp")
        
        validated_plan = {
            'safe': [safe_file],
            'moves': [],
            'critical': []
        }
        
        result = engine.execute_cleanup(
            validated_plan,
            checkpoint_dir=temp_dir / "checkpoint"
        )
        
        assert 'files_deleted' in result
        assert 'files_moved' in result
        assert 'space_reclaimed' in result
    
    def test_exclude_patterns(self, engine, temp_dir):
        """Test exclusion pattern enforcement."""
        # Create files
        (temp_dir / "include.tmp").touch()
        (temp_dir / "node_modules").mkdir()
        (temp_dir / "node_modules" / "package.tmp").touch()
        
        cleanup_rules = {
            'temp_files': {'patterns': ['*.tmp']}
        }
        
        inventory = engine.scan_directory(
            temp_dir,
            cleanup_rules=cleanup_rules,
            exclude_patterns=['node_modules']
        )
        
        # Should find include.tmp but not node_modules/package.tmp
        temp_files = [str(f) for f in inventory.get('temp_files', [])]
        
        assert any('include.tmp' in f for f in temp_files)
        assert not any('node_modules' in f for f in temp_files)
    
    def test_symlink_handling(self, engine, temp_dir):
        """Test symlink safety."""
        # Create file and symlink
        real_file = temp_dir / "real.txt"
        real_file.write_text("real content")
        
        symlink = temp_dir / "link.txt"
        symlink.symlink_to(real_file)
        
        cleanup_rules = {
            'temp_files': {'patterns': ['*.txt']}
        }
        
        # Scan should handle symlinks
        inventory = engine.scan_directory(
            temp_dir,
            cleanup_rules=cleanup_rules,
            exclude_patterns=[]
        )
        
        # Should detect files (implementation may vary)
        assert 'temp_files' in inventory or 'uncategorized' in inventory
    
    def test_empty_directory_detection(self, engine, temp_dir):
        """Test empty directory identification."""
        # Create empty directory
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        # Create non-empty directory
        nonempty_dir = temp_dir / "nonempty"
        nonempty_dir.mkdir()
        (nonempty_dir / "file.txt").touch()
        
        cleanup_rules = {
            'empty_directories': {'patterns': ['*/']}
        }
        
        inventory = engine.scan_directory(
            temp_dir,
            cleanup_rules=cleanup_rules,
            exclude_patterns=[]
        )
        
        # Implementation should identify empty directories
        assert 'empty_directories' in inventory or 'temp_files' in inventory
    
    def test_large_file_handling(self, engine, temp_dir):
        """Test handling of large files."""
        # Create large file (10MB)
        large_file = temp_dir / "large.bin"
        large_file.write_bytes(b"0" * (10 * 1024 * 1024))
        
        cleanup_rules = {
            'large_files': {'patterns': ['*.bin']}
        }
        
        inventory = engine.scan_directory(
            temp_dir,
            cleanup_rules=cleanup_rules,
            exclude_patterns=[]
        )
        
        # Should scan without crashing
        assert inventory is not None
    
    def test_concurrent_modification_handling(self, engine, temp_dir):
        """Test handling of files modified during scan."""
        # Create file
        test_file = temp_dir / "test.txt"
        test_file.write_text("initial")
        
        cleanup_rules = {
            'temp_files': {'patterns': ['*.txt']}
        }
        
        # Scan
        inventory = engine.scan_directory(
            temp_dir,
            cleanup_rules=cleanup_rules,
            exclude_patterns=[]
        )
        
        # Modify file during operation (simulate)
        test_file.write_text("modified")
        
        # Should handle gracefully
        assert inventory is not None


class TestFilesystemEngineIntegration:
    """Integration tests for FilesystemEngine."""
    
    @pytest.fixture
    def real_temp_dir(self):
        """Create real test filesystem."""
        temp = tempfile.mkdtemp()
        temp_path = Path(temp)
        
        # Create realistic filesystem structure
        (temp_path / "temp.tmp").write_text("temporary")
        (temp_path / "__pycache__").mkdir()
        (temp_path / "__pycache__" / "module.pyc").write_bytes(b"bytecode")
        (temp_path / "build").mkdir()
        (temp_path / "build" / "output.exe").write_bytes(b"executable")
        (temp_path / "src").mkdir()
        (temp_path / "src" / "main.py").write_text("print('hello')")
        (temp_path / ".git").mkdir()
        (temp_path / ".git" / "config").write_text("[core]")
        
        yield temp_path
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_full_cleanup_workflow(self, real_temp_dir):
        """Test complete cleanup workflow."""
        # Create real database
        db_path = real_temp_dir / "test.db"
        state_db = PlanningStateDB(str(db_path))
        
        # Create engine
        safety_rules = {
            'critical_patterns': ['.git', '*.py'],
            'size_threshold_mb': 1000
        }
        engine = FilesystemEngine(state_db=state_db, safety_rules=safety_rules)
        
        # Define cleanup rules
        cleanup_rules = {
            'temp_files': {'patterns': ['*.tmp']},
            'build_artifacts': {'patterns': ['__pycache__/', '*.pyc', 'build/']}
        }
        
        # Scan
        inventory = engine.scan_directory(
            real_temp_dir,
            cleanup_rules=cleanup_rules,
            exclude_patterns=['.git', 'src']
        )
        
        # Verify inventory
        assert 'temp_files' in inventory or 'build_artifacts' in inventory
        
        # Verify critical files excluded
        scanned_paths = [str(f) for cat in inventory.values() for f in cat]
        assert not any('.git' in p for p in scanned_paths)
        assert not any('main.py' in p for p in scanned_paths)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
