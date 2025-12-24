"""
Tests for Aggressive File Sweeper Plugin (Recycle Bin Mode)

Tests file classification, Recycle Bin execution, whitelist protection,
and integration with cleanup orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.plugins.sweeper_plugin import (
    SweeperPlugin,
    FileCategory,
    FileClassification
)


class TestSweeperPlugin:
    """Test sweeper plugin functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create directory structure
        (temp_dir / "src").mkdir()
        (temp_dir / "tests").mkdir()
        (temp_dir / "cortex-brain").mkdir()
        (temp_dir / "cortex-brain" / "sweeper-logs").mkdir()
        (temp_dir / "docs").mkdir()
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sweeper(self):
        """Create sweeper plugin instance"""
        plugin = SweeperPlugin()
        plugin.initialize()
        return plugin
    
    def test_plugin_metadata(self, sweeper):
        """Test plugin metadata is correct"""
        assert sweeper.metadata.plugin_id == "sweeper"
        assert sweeper.metadata.name == "File Sweeper"
        assert sweeper.metadata.version == "1.0.0"
    
    def test_classification_backup_files(self, sweeper, temp_workspace):
        """Test classification of backup files"""
        sweeper.workspace_root = temp_workspace
        
        # Create backup files
        backup_files = [
            temp_workspace / "file-BACKUP-001.md",
            temp_workspace / "notes.backup.txt",
            temp_workspace / "data.bak",
            temp_workspace / "config-OLD-v1.yaml"
        ]
        
        for f in backup_files:
            f.write_text("backup content")
        
        # Classify each file
        for backup_file in backup_files:
            classification = sweeper._classify_file(backup_file)
            assert classification.category == FileCategory.BACKUP
            assert classification.action == "delete"
    
    def test_classification_dated_duplicates(self, sweeper, temp_workspace):
        """Test classification of dated duplicate files"""
        sweeper.workspace_root = temp_workspace
        
        # Create dated duplicates
        dated_files = [
            temp_workspace / "report.2024-11-10.md",
            temp_workspace / "notes.20241110.txt",
            temp_workspace / "data.2024-01-15.json"
        ]
        
        for f in dated_files:
            f.write_text("dated content")
        
        # Classify each file
        for dated_file in dated_files:
            classification = sweeper._classify_file(dated_file)
            assert classification.category == FileCategory.DUPLICATE
            assert classification.action == "delete"
    
    def test_classification_session_reports(self, sweeper, temp_workspace):
        """Test classification of session reports"""
        sweeper.workspace_root = temp_workspace
        
        # Create old session report (40 days old)
        old_session = temp_workspace / "SESSION-2024-10-01.md"
        old_session.write_text("old session")
        
        # Set modification time to 40 days ago
        old_time = (datetime.now() - timedelta(days=40)).timestamp()
        old_session.touch()
        import os
        os.utime(old_session, (old_time, old_time))
        
        classification = sweeper._classify_file(old_session)
        assert classification.category == FileCategory.SESSION
        assert classification.action == "delete"
        assert classification.age_days >= 30
    
    def test_classification_reference_docs(self, sweeper, temp_workspace):
        """Test classification of reference documentation"""
        sweeper.workspace_root = temp_workspace
        
        # Create old reference docs (70 days old)
        old_ref = temp_workspace / "API-REFERENCE.md"
        old_ref.write_text("old reference")
        
        # Set modification time to 70 days ago
        old_time = (datetime.now() - timedelta(days=70)).timestamp()
        old_ref.touch()
        import os
        os.utime(old_ref, (old_time, old_time))
        
        classification = sweeper._classify_file(old_ref)
        assert classification.category == FileCategory.REFERENCE
        assert classification.action == "delete"
        assert classification.age_days >= 60
    
    def test_classification_temp_files(self, sweeper, temp_workspace):
        """Test classification of temporary files"""
        sweeper.workspace_root = temp_workspace
        
        temp_files = [
            temp_workspace / "data.tmp",
            temp_workspace / "cache.temp",
            temp_workspace / "output.pyc"
        ]
        
        for f in temp_files:
            f.write_text("temp content")
        
        for temp_file in temp_files:
            classification = sweeper._classify_file(temp_file)
            assert classification.category in [FileCategory.TEMP, FileCategory.CACHE]
            assert classification.action == "delete"
    
    def test_protected_directories(self, sweeper, temp_workspace):
        """Test that protected directories are respected"""
        sweeper.workspace_root = temp_workspace
        sweeper._set_default_protections()
        
        # Create backup file in protected directory
        protected_file = temp_workspace / "src" / "backup.bak"
        protected_file.write_text("protected backup")
        
        # Should be protected
        assert sweeper._is_protected(protected_file)
    
    def test_protected_patterns(self, sweeper, temp_workspace):
        """Test that protected patterns are respected"""
        sweeper.workspace_root = temp_workspace
        sweeper._set_default_protections()
        
        # Create files matching protected patterns
        protected_files = [
            temp_workspace / "main.py",
            temp_workspace / "config.yaml",
            temp_workspace / "data.json",
            temp_workspace / "README.md"
        ]
        
        for f in protected_files:
            f.write_text("protected content")
        
        for protected_file in protected_files:
            assert sweeper._is_protected(protected_file)
    
    @patch('src.plugins.sweeper_plugin.send2trash')
    def test_deletion_execution(self, mock_send2trash, sweeper, temp_workspace):
        """Test Recycle Bin execution"""
        sweeper.workspace_root = temp_workspace
        
        # Create files to delete
        delete_files = [
            temp_workspace / "backup.bak",
            temp_workspace / "temp.tmp",
            temp_workspace / "cache.pyc"
        ]
        
        for f in delete_files:
            f.write_text("delete me")
        
        # Classify files
        classifications = []
        for f in delete_files:
            classifications.append(sweeper._classify_file(f))
        
        # Execute deletions (mocked)
        sweeper._execute_deletions(classifications)
        
        # Verify send2trash was called
        assert mock_send2trash.call_count == 3
        
        # Verify stats
        assert sweeper.stats.files_deleted == 3
    
    @patch('src.plugins.sweeper_plugin.send2trash')
    def test_audit_log_creation(self, mock_send2trash, sweeper, temp_workspace):
        """Test that audit log is created with Recycle Bin info"""
        sweeper.workspace_root = temp_workspace
        
        # Create and delete a file
        test_file = temp_workspace / "test.bak"
        test_file.write_text("test")
        
        classification = sweeper._classify_file(test_file)
        sweeper._execute_deletions([classification])
        
        # Save audit log
        sweeper._save_audit_log()
        
        # Verify audit log exists
        log_dir = temp_workspace / "cortex-brain" / "sweeper-logs"
        log_files = list(log_dir.glob("sweeper-*.json"))
        
        assert len(log_files) > 0
        
        # Verify log content includes recycle bin info
        import json
        with open(log_files[0], 'r') as f:
            log_data = json.load(f)
        
        assert log_data["mode"] == "recycle_bin"
        assert log_data["recoverable"] is True
        assert "recovery_instructions" in log_data
    
    @patch('src.plugins.sweeper_plugin.send2trash')
    def test_full_execution(self, mock_send2trash, sweeper, temp_workspace):
        """Test full sweeper execution with Recycle Bin"""
        # Create test files
        files_to_create = [
            ("backup.bak", "delete"),
            ("temp.tmp", "delete"),
            ("important.py", "keep"),  # Protected pattern
            ("README.md", "keep"),  # Protected pattern
        ]
        
        for filename, _ in files_to_create:
            (temp_workspace / filename).write_text("content")
        
        # Execute sweeper
        result = sweeper.execute({"workspace_root": str(temp_workspace)})
        
        # Verify execution success
        assert result["success"] is True
        assert result["stats"]["files_deleted"] == 2  # backup.bak and temp.tmp
        
        # Verify send2trash was called
        assert mock_send2trash.call_count == 2
        
        # Verify protected files were NOT sent to trash
        called_paths = [str(call[0][0]) for call in mock_send2trash.call_args_list]
        assert not any("important.py" in path for path in called_paths)
        assert not any("README.md" in path for path in called_paths)
    
    def test_no_backup_creation(self, sweeper, temp_workspace):
        """Test that no backup/manifest files are created"""
        sweeper.workspace_root = temp_workspace
        
        # Create and delete a file
        test_file = temp_workspace / "test.bak"
        test_file.write_text("test")
        
        classification = sweeper._classify_file(test_file)
        sweeper._execute_deletions([classification])
        
        # Verify no .backup or manifest files created
        all_files = list(temp_workspace.rglob("*"))
        backup_files = [f for f in all_files if ".backup" in f.name or "manifest" in f.name.lower()]
        
        # Only audit log should exist, no other backup files
        assert len(backup_files) == 0
    
    @patch('src.plugins.sweeper_plugin.send2trash')
    def test_error_handling(self, mock_send2trash, sweeper, temp_workspace):
        """Test error handling for inaccessible files"""
        # Make send2trash raise an exception
        mock_send2trash.side_effect = Exception("Permission denied")
        
        sweeper.workspace_root = temp_workspace
        
        # Create a file classification
        test_file = temp_workspace / "test.bak"
        test_file.write_text("test")
        
        classification = sweeper._classify_file(test_file)
        
        # Try to delete
        sweeper._execute_deletions([classification])
        
        # Should have an error logged
        assert len(sweeper.stats.errors) > 0
        assert "Permission denied" in sweeper.stats.errors[0]
    
    def test_scan_and_classify(self, sweeper, temp_workspace):
        """Test full workspace scanning and classification"""
        # Set workspace root first
        sweeper.workspace_root = temp_workspace
        
        # Create diverse file set
        (temp_workspace / "docs" / "backup.bak").write_text("backup")
        (temp_workspace / "docs" / "notes.md").write_text("notes")
        (temp_workspace / "cortex-brain" / "SESSION-OLD.md").write_text("session")
        (temp_workspace / "temp.tmp").write_text("temp")
        (temp_workspace / "src" / "main.py").write_text("# code")
        
        # Scan and classify
        classifications = sweeper._scan_and_classify()
        
        # Should find some files to classify (excluding protected)
        assert len(classifications) >= 2  # At least backup.bak and temp.tmp
        
        # Verify protected files are not in classifications
        classified_paths = [str(c.path) for c in classifications]
        assert not any("main.py" in p for p in classified_paths)


class TestSweeperIntegration:
    """Integration tests with cleanup orchestrator"""
    
    def test_plugin_registration(self):
        """Test that sweeper can be registered"""
        from src.plugins.sweeper_plugin import register
        
        plugin = register()
        assert plugin is not None
        assert plugin.metadata.plugin_id == "sweeper"
    
    def test_plugin_initialization(self):
        """Test plugin can be initialized"""
        plugin = SweeperPlugin()
        success = plugin.initialize()
        assert success is True
    
    def test_plugin_cleanup(self):
        """Test plugin cleanup"""
        plugin = SweeperPlugin()
        plugin.initialize()
        success = plugin.cleanup()
        assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
