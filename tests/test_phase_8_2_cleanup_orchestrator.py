"""
Phase 8.1.2: Integration Cleanup Orchestrator Tests (TDD RED Phase)

Tests for the actual integration cleanup implementation:
- File detection (obsolete tests, old backups, temporary files)
- Dry-run vs live mode execution
- Profile levels (quick, standard, comprehensive)
- Error handling and recovery
- Cleanup metrics and reporting

Author: Asif Hussain
Date: December 2, 2025
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrators.phase8_operation_handler import Phase8OperationHandler


class TestIntegrationCleanupOrchestrator:
    """Test actual integration cleanup orchestration."""
    
    @pytest.fixture
    def temp_brain(self, tmp_path):
        """Create temporary brain structure for testing."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        # Create standard brain structure
        (brain_path / "documents" / "reports").mkdir(parents=True)
        (brain_path / "backups").mkdir(parents=True)
        (brain_path / "cache").mkdir(parents=True)
        
        # Create some obsolete files to clean
        (brain_path / "backups" / "old-backup-2024-01-01.db").write_text("old backup")
        (brain_path / "cache" / "temp-file.tmp").write_text("temp")
        (brain_path / "documents" / "reports" / "old-report.md").write_text("# Old Report")
        
        return brain_path
    
    def test_cleanup_detects_obsolete_files(self, temp_brain):
        """
        RED TEST: Verify cleanup detects files to remove.
        
        Should detect:
        - Old backups (>30 days)
        - Temporary cache files
        - Obsolete test files
        - Deprecated documentation
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {'dry_run': True, 'profile': 'standard'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert 'files found' in result.lower() or 'items detected' in result.lower(), \
            "Should report number of files detected for cleanup"
        assert 'backup' in result.lower() or 'cache' in result.lower(), \
            "Should mention types of files detected"
    
    def test_dry_run_does_not_modify_files(self, temp_brain):
        """
        RED TEST: Verify dry-run mode doesn't actually delete files.
        
        Should:
        - Report what would be deleted
        - Not actually delete any files
        - Preserve all file contents
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        backup_file = temp_brain / "backups" / "old-backup-2024-01-01.db"
        original_content = backup_file.read_text()
        
        context = {'dry_run': True, 'profile': 'comprehensive'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert backup_file.exists(), "Dry-run should not delete files"
        assert backup_file.read_text() == original_content, \
            "Dry-run should not modify file contents"
        assert 'would' in result.lower() or 'dry run' in result.lower(), \
            "Output should use conditional language"
    
    def test_live_mode_actually_removes_files(self, temp_brain):
        """
        RED TEST: Verify live mode actually deletes files.
        
        Should:
        - Delete obsolete files
        - Preserve important files
        - Return summary of deletions
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        backup_file = temp_brain / "backups" / "old-backup-2024-01-01.db"
        important_file = temp_brain / "documents" / "reports" / "old-report.md"
        
        context = {'dry_run': False, 'profile': 'quick'}
        
        # Mock confirmation to avoid user input
        with patch('builtins.input', return_value='yes'):
            # Act
            result = handler.handle_integration_cleanup(context)
        
        # Assert - OLD backups should be removed
        assert not backup_file.exists(), \
            "Live mode should delete old backup files"
        
        # Important files should be preserved (reports are kept in quick profile)
        # This will fail in RED phase - we'll implement preservation logic in GREEN
    
    def test_quick_profile_minimal_cleanup(self, temp_brain):
        """
        RED TEST: Verify quick profile only removes obvious obsolete files.
        
        Quick profile should:
        - Remove temp files
        - Remove very old backups (>90 days)
        - Preserve recent files
        - Complete in <30 seconds
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        
        # Create files with different ages
        temp_file = temp_brain / "cache" / "temp.tmp"
        temp_file.write_text("temp")
        
        recent_backup = temp_brain / "backups" / "backup-2024-12-01.db"
        recent_backup.write_text("recent")
        
        context = {'dry_run': True, 'profile': 'quick'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert 'quick' in result.lower(), "Should acknowledge quick profile"
        assert 'temp' in result.lower() or 'cache' in result.lower(), \
            "Should mention temp/cache cleanup"
        # Quick profile should NOT mention comprehensive cleanup
        assert 'documentation consolidation' not in result.lower(), \
            "Quick profile should skip heavy operations"
    
    def test_standard_profile_balanced_cleanup(self, temp_brain):
        """
        RED TEST: Verify standard profile performs balanced cleanup.
        
        Standard profile should:
        - Remove obsolete files (>30 days)
        - Clean backup archives
        - Consolidate similar files
        - Complete in <5 minutes
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {'dry_run': True, 'profile': 'standard'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert 'standard' in result.lower(), "Should acknowledge standard profile"
        assert any(word in result.lower() for word in ['backup', 'cache', 'obsolete']), \
            "Should mention multiple cleanup categories"
    
    def test_comprehensive_profile_deep_cleanup(self, temp_brain):
        """
        RED TEST: Verify comprehensive profile performs thorough cleanup.
        
        Comprehensive profile should:
        - All standard cleanup
        - Optimize database files
        - Consolidate documentation
        - Archive old reports
        - May take 10+ minutes
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {'dry_run': True, 'profile': 'comprehensive'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert 'comprehensive' in result.lower(), \
            "Should acknowledge comprehensive profile"
        assert any(word in result.lower() for word in 
                   ['optimize', 'consolidate', 'archive']), \
            "Should mention advanced operations"
    
    def test_cleanup_generates_metrics(self, temp_brain):
        """
        RED TEST: Verify cleanup generates useful metrics.
        
        Should report:
        - Files scanned
        - Files to remove
        - Space to free (MB)
        - Execution time
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {'dry_run': True, 'profile': 'standard'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert 'files' in result.lower(), "Should mention file count"
        assert any(unit in result.lower() for unit in ['mb', 'kb', 'space']), \
            "Should mention space savings"
    
    def test_cleanup_preserves_critical_files(self, temp_brain):
        """
        RED TEST: Verify cleanup never touches critical files.
        
        Critical files (must preserve):
        - brain-protection-rules.yaml
        - response-templates.yaml
        - Active database files (tier1, tier2, tier3)
        - Current VERSION file
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        
        # Create critical files
        critical_files = [
            temp_brain / "brain-protection-rules.yaml",
            temp_brain / "response-templates.yaml",
            temp_brain / "tier1" / "working_memory.db",
        ]
        
        for f in critical_files:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("critical data")
        
        context = {'dry_run': False, 'profile': 'comprehensive'}
        
        # Mock confirmation
        with patch('builtins.input', return_value='yes'):
            # Act
            result = handler.handle_integration_cleanup(context)
        
        # Assert
        for f in critical_files:
            assert f.exists(), f"Critical file should never be deleted: {f.name}"
    
    def test_cleanup_handles_missing_directories(self, temp_brain):
        """
        RED TEST: Verify cleanup handles missing directories gracefully.
        
        Should:
        - Not fail if optional directories missing
        - Create directories if needed
        - Log warnings for unexpected missing dirs
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        
        # Remove optional directory
        shutil.rmtree(temp_brain / "cache")
        
        context = {'dry_run': True, 'profile': 'standard'}
        
        # Act & Assert - should not raise exception
        try:
            result = handler.handle_integration_cleanup(context)
            assert True, "Should handle missing directories gracefully"
        except Exception as e:
            pytest.fail(f"Cleanup should not fail on missing directories: {e}")
    
    def test_cleanup_rollback_on_error(self, temp_brain):
        """
        RED TEST: Verify cleanup rolls back on error.
        
        If cleanup fails midway:
        - Should restore deleted files from backup
        - Should log error details
        - Should return error status
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        test_file = temp_brain / "backups" / "test-backup.db"
        test_file.write_text("important data")
        
        context = {'dry_run': False, 'profile': 'standard'}
        
        # Mock a failure during cleanup
        with patch('builtins.input', return_value='yes'):
            with patch.object(Path, 'unlink', side_effect=PermissionError("Mock error")):
                # Act
                result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert 'error' in result.lower() or 'failed' in result.lower(), \
            "Should report error status"
        # File should still exist due to rollback
        assert test_file.exists(), \
            "Should preserve files if cleanup fails"


class TestCleanupMetrics:
    """Test cleanup metrics and reporting."""
    
    @pytest.fixture
    def temp_brain(self, tmp_path):
        """Create temporary brain with files of known sizes."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        backups = brain_path / "backups"
        backups.mkdir()
        
        # Create files with specific sizes for metric testing
        (backups / "large-backup.db").write_bytes(b'x' * (5 * 1024 * 1024))  # 5 MB
        (backups / "small-backup.db").write_bytes(b'x' * 1024)  # 1 KB
        
        return brain_path
    
    def test_metrics_calculate_space_savings(self, temp_brain):
        """
        RED TEST: Verify metrics accurately calculate space to free.
        
        Should:
        - Sum file sizes correctly
        - Convert to appropriate units (KB/MB/GB)
        - Round to 2 decimal places
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {'dry_run': True, 'profile': 'comprehensive'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        # Should report ~5 MB of space (from large-backup.db)
        assert '5' in result and 'mb' in result.lower(), \
            "Should report approximately 5 MB of space savings"
    
    def test_metrics_track_file_categories(self, temp_brain):
        """
        RED TEST: Verify metrics break down files by category.
        
        Categories:
        - Backups
        - Cache
        - Temporary files
        - Documentation
        - Logs
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        
        # Add files from different categories
        (temp_brain / "cache").mkdir()
        (temp_brain / "cache" / "temp.tmp").write_text("temp")
        (temp_brain / "logs").mkdir()
        (temp_brain / "logs" / "old.log").write_text("log")
        
        context = {'dry_run': True, 'profile': 'comprehensive'}
        
        # Act
        result = handler.handle_integration_cleanup(context)
        
        # Assert
        assert 'backup' in result.lower(), "Should mention backup files"
        assert 'cache' in result.lower() or 'temp' in result.lower(), \
            "Should mention cache/temp files"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
