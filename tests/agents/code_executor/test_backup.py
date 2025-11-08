"""Tests for CodeExecutor backup system."""

import os
import tempfile
from pathlib import Path

from src.cortex_agents.code_executor.backup import BackupManager


class TestBackupManager:
    """Test BackupManager functionality."""
    
    def test_manager_initialization(self):
        """Test manager initializes correctly."""
        mgr = BackupManager()
        assert mgr.operation_id is not None
        assert mgr.backup_dir is None
    
    def test_create_backup_dir(self):
        """Test creating backup directory."""
        mgr = BackupManager()
        backup_dir = mgr.create_backup_dir()
        
        assert backup_dir is not None
        assert os.path.exists(backup_dir)
        assert "cortex_backup" in backup_dir
        
        # Cleanup
        mgr.cleanup()
    
    def test_get_backup_dir_before_creation(self):
        """Test getting backup dir before creation."""
        mgr = BackupManager()
        assert mgr.get_backup_dir() is None
    
    def test_get_backup_dir_after_creation(self):
        """Test getting backup dir after creation."""
        mgr = BackupManager()
        created_dir = mgr.create_backup_dir()
        retrieved_dir = mgr.get_backup_dir()
        
        assert retrieved_dir == created_dir
        
        # Cleanup
        mgr.cleanup()
    
    def test_backup_file(self):
        """Test backing up a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.py")
            content = "test content"
            Path(test_file).write_text(content)
            
            # Backup file
            mgr = BackupManager()
            mgr.create_backup_dir()
            backup_path = mgr.backup_file(test_file)
            
            assert backup_path is not None
            assert os.path.exists(backup_path)
            assert Path(backup_path).read_text() == content
            
            # Cleanup
            mgr.cleanup()
    
    def test_backup_nonexistent_file(self):
        """Test backing up a file that doesn't exist."""
        mgr = BackupManager()
        mgr.create_backup_dir()
        backup_path = mgr.backup_file("/nonexistent/file.py")
        
        assert backup_path is None
        
        # Cleanup
        mgr.cleanup()
    
    def test_backup_without_dir(self):
        """Test backing up without creating backup dir first."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.py")
            Path(test_file).write_text("content")
            
            mgr = BackupManager()
            # Don't create backup dir first
            backup_path = mgr.backup_file(test_file)
            
            # Should auto-create dir
            assert backup_path is not None
            assert os.path.exists(backup_path)
            
            # Cleanup
            mgr.cleanup()
    
    def test_restore_file(self):
        """Test restoring a file from backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create original file
            original_file = os.path.join(tmpdir, "original.py")
            original_content = "original"
            Path(original_file).write_text(original_content)
            
            # Backup it
            mgr = BackupManager()
            mgr.create_backup_dir()
            backup_path = mgr.backup_file(original_file)
            
            # Modify original
            Path(original_file).write_text("modified")
            
            # Restore from backup
            success = mgr.restore_file(backup_path, original_file)
            
            assert success is True
            assert Path(original_file).read_text() == original_content
            
            # Cleanup
            mgr.cleanup()
    
    def test_restore_nonexistent_backup(self):
        """Test restoring from nonexistent backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_file = os.path.join(tmpdir, "original.py")
            
            mgr = BackupManager()
            success = mgr.restore_file("/nonexistent/backup.py", original_file)
            
            assert success is False
    
    def test_rollback_all(self):
        """Test rollback availability check."""
        mgr = BackupManager()
        
        # No backup dir
        assert mgr.rollback_all() is False
        
        # With backup dir
        mgr.create_backup_dir()
        assert mgr.rollback_all() is True
        
        # Cleanup
        mgr.cleanup()
    
    def test_cleanup(self):
        """Test cleanup removes backup directory."""
        mgr = BackupManager()
        backup_dir = mgr.create_backup_dir()
        
        assert os.path.exists(backup_dir)
        
        mgr.cleanup()
        
        # Directory should be removed
        assert not os.path.exists(backup_dir)
    
    def test_multiple_backups(self):
        """Test backing up multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            files = []
            for i in range(3):
                file_path = os.path.join(tmpdir, f"test{i}.py")
                Path(file_path).write_text(f"content{i}")
                files.append(file_path)
            
            # Backup all files
            mgr = BackupManager()
            mgr.create_backup_dir()
            
            backup_paths = []
            for file_path in files:
                backup_path = mgr.backup_file(file_path)
                assert backup_path is not None
                backup_paths.append(backup_path)
            
            # Verify all backups exist
            for backup_path in backup_paths:
                assert os.path.exists(backup_path)
            
            # Cleanup
            mgr.cleanup()
