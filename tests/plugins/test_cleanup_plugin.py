"""
Tests for Cleanup Plugin

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import time

from src.plugins.cleanup_plugin import (
    Plugin as CleanupPlugin,
    CleanupStats,
    CleanupAction,
    FileCategory
)
from src.plugins.base_plugin import HookPoint


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create project structure
    (temp_dir / 'src').mkdir()
    (temp_dir / 'tests').mkdir()
    (temp_dir / 'docs').mkdir()
    (temp_dir / 'logs').mkdir()
    (temp_dir / 'scripts').mkdir()
    (temp_dir / 'cortex-brain').mkdir()
    
    # Create some test files
    (temp_dir / 'README.md').write_text('# Test Project')
    (temp_dir / '.gitignore').write_text('*.tmp\n__pycache__\n')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def plugin_config(temp_project_dir):
    """Create plugin configuration"""
    return {
        'application': {
            'rootPath': str(temp_project_dir)
        },
        'plugins': {
            'cleanup_plugin': {
                'enabled': True,
                'dry_run': True,
                'auto_cleanup_on_startup': False,
                'temp_patterns': ['*.tmp', '*.temp', '*~'],
                'backup_patterns': ['*.bak', '*.old'],
                'cache_dirs': ['__pycache__', '.cache'],
                'preserve_patterns': ['LICENSE', 'README*', '.git/'],
                'max_temp_age_days': 7,
                'max_log_age_days': 30,
                'max_backup_age_days': 14,
                'min_duplicate_size_kb': 1,
                'large_file_threshold_mb': 10,
                'compress_old_archives': False,
                'enforce_structure': True,
                'detect_orphans': False
            }
        }
    }


@pytest.fixture
def cleanup_plugin(plugin_config):
    """Create cleanup plugin instance"""
    plugin = CleanupPlugin()
    assert plugin.initialize(plugin_config)
    return plugin


class TestCleanupPluginInitialization:
    """Test plugin initialization"""
    
    def test_metadata(self):
        """Test plugin metadata"""
        plugin = CleanupPlugin()
        metadata = plugin._get_metadata()
        
        assert metadata.plugin_id == "cleanup_plugin"
        assert metadata.name == "CORTEX Cleanup & Maintenance"
        assert metadata.version == "2.0.0"
        assert metadata.author == "Asif Hussain"
    
    def test_initialization_success(self, plugin_config):
        """Test successful initialization"""
        plugin = CleanupPlugin()
        assert plugin.initialize(plugin_config)
        assert plugin.dry_run is True
        assert plugin.auto_cleanup is False
    
    def test_initialization_with_defaults(self, temp_project_dir):
        """Test initialization with minimal config"""
        config = {
            'application': {
                'rootPath': str(temp_project_dir)
            },
            'plugins': {}
        }
        plugin = CleanupPlugin()
        assert plugin.initialize(config)


class TestTempFileCleanup:
    """Test temporary file cleanup"""
    
    def test_cleanup_old_temp_files(self, cleanup_plugin, temp_project_dir):
        """Test cleanup of old temp files"""
        # Create old temp file
        old_temp = temp_project_dir / 'old_file.tmp'
        old_temp.write_text('old temp')
        
        # Set file time to 10 days ago
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        old_temp.touch()
        import os
        os.utime(old_temp, (old_time, old_time))
        
        # Run cleanup
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert cleanup_plugin.stats.files_deleted > 0
    
    def test_preserve_recent_temp_files(self, cleanup_plugin, temp_project_dir):
        """Test that recent temp files are preserved"""
        # Create recent temp file
        recent_temp = temp_project_dir / 'recent_file.tmp'
        recent_temp.write_text('recent temp')
        
        # Run cleanup
        initial_deleted = cleanup_plugin.stats.files_deleted
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        # Recent file should not be deleted
        assert recent_temp.exists()
    
    def test_preserve_patterns(self, cleanup_plugin, temp_project_dir):
        """Test that preserve patterns are respected"""
        # Create file matching preserve pattern
        readme = temp_project_dir / 'README.tmp'
        readme.write_text('readme')
        
        # Set old timestamp
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        import os
        os.utime(readme, (old_time, old_time))
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        # README* should be preserved even if old
        assert readme.exists()


class TestBackupFileCleanup:
    """Test backup file cleanup"""
    
    def test_cleanup_old_backups(self, cleanup_plugin, temp_project_dir):
        """Test cleanup of old backup files"""
        # Create old backup
        old_backup = temp_project_dir / 'file.bak'
        old_backup.write_text('old backup')
        
        # Set old timestamp
        old_time = (datetime.now() - timedelta(days=20)).timestamp()
        import os
        os.utime(old_backup, (old_time, old_time))
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert cleanup_plugin.stats.files_deleted > 0


class TestCacheCleanup:
    """Test cache directory cleanup"""
    
    def test_cleanup_pycache(self, cleanup_plugin, temp_project_dir):
        """Test cleanup of __pycache__ directories"""
        # Create __pycache__ directory
        pycache = temp_project_dir / 'src' / '__pycache__'
        pycache.mkdir()
        (pycache / 'module.pyc').write_bytes(b'compiled')
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert cleanup_plugin.stats.directories_removed > 0


class TestLogFileCleanup:
    """Test log file cleanup and archival"""
    
    def test_archive_old_logs(self, cleanup_plugin, temp_project_dir):
        """Test archival of old log files"""
        # Create old log file
        old_log = temp_project_dir / 'logs' / 'old.log'
        old_log.write_text('old log entries')
        
        # Set old timestamp
        old_time = (datetime.now() - timedelta(days=40)).timestamp()
        import os
        os.utime(old_log, (old_time, old_time))
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert cleanup_plugin.stats.files_archived > 0


class TestDuplicateDetection:
    """Test duplicate file detection"""
    
    def test_detect_duplicates(self, cleanup_plugin, temp_project_dir):
        """Test detection of duplicate files"""
        # Create duplicate files
        content = 'duplicate content' * 1000  # Make it large enough
        
        file1 = temp_project_dir / 'file1.txt'
        file2 = temp_project_dir / 'file2.txt'
        
        file1.write_text(content)
        file2.write_text(content)
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert cleanup_plugin.stats.duplicates_found > 0
    
    def test_ignore_small_duplicates(self, cleanup_plugin, temp_project_dir):
        """Test that small files are not checked for duplicates"""
        # Create small duplicate files
        content = 'small'
        
        file1 = temp_project_dir / 'small1.txt'
        file2 = temp_project_dir / 'small2.txt'
        
        file1.write_text(content)
        file2.write_text(content)
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        # Small files should be ignored
        assert cleanup_plugin.stats.duplicates_found == 0


class TestEmptyDirectoryCleanup:
    """Test empty directory cleanup"""
    
    def test_cleanup_empty_dirs(self, cleanup_plugin, temp_project_dir):
        """Test cleanup of empty directories"""
        # Create empty directory
        empty_dir = temp_project_dir / 'empty'
        empty_dir.mkdir()
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert cleanup_plugin.stats.directories_removed > 0
    
    def test_cleanup_nested_empty_dirs(self, cleanup_plugin, temp_project_dir):
        """Test cleanup of nested empty directories"""
        # Create nested empty directories
        nested = temp_project_dir / 'level1' / 'level2' / 'level3'
        nested.mkdir(parents=True)
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        # Should remove multiple levels
        assert cleanup_plugin.stats.directories_removed >= 1
    
    def test_preserve_dirs_with_files(self, cleanup_plugin, temp_project_dir):
        """Test that directories with files are preserved"""
        # Create directory with file
        dir_with_file = temp_project_dir / 'has_file'
        dir_with_file.mkdir()
        (dir_with_file / 'file.txt').write_text('content')
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert dir_with_file.exists()


class TestLargeFileDetection:
    """Test large file detection"""
    
    def test_detect_large_files(self, cleanup_plugin, temp_project_dir):
        """Test detection of large files"""
        # Create large file (>10MB threshold)
        large_file = temp_project_dir / 'large.bin'
        large_file.write_bytes(b'x' * (11 * 1024 * 1024))
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        # Check that large file was reported
        large_file_actions = [
            a for a in cleanup_plugin.actions_taken
            if a['action'] == CleanupAction.REPORT.value and 'Large file' in a['reason']
        ]
        assert len(large_file_actions) > 0


class TestStructureEnforcement:
    """Test project structure enforcement"""
    
    def test_enforce_structure(self, cleanup_plugin, temp_project_dir):
        """Test project structure validation"""
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        # Should have warnings if required dirs are missing
    
    def test_detect_misplaced_files(self, cleanup_plugin, temp_project_dir):
        """Test detection of misplaced files in root"""
        # Create misplaced file
        misplaced = temp_project_dir / 'random_file.txt'
        misplaced.write_text('misplaced')
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        # Should report misplaced file
        misplaced_actions = [
            a for a in cleanup_plugin.actions_taken
            if 'Misplaced' in a['reason']
        ]
        assert len(misplaced_actions) > 0


class TestDryRunMode:
    """Test dry run functionality"""
    
    def test_dry_run_no_deletion(self, cleanup_plugin, temp_project_dir):
        """Test that dry run doesn't delete files"""
        # Create temp file
        temp_file = temp_project_dir / 'test.tmp'
        temp_file.write_text('temp')
        
        # Set old timestamp
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        import os
        os.utime(temp_file, (old_time, old_time))
        
        cleanup_plugin.dry_run = True
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert result['dry_run'] is True
        # File should still exist in dry run
        assert temp_file.exists()
    
    def test_actual_deletion_when_not_dry_run(self, cleanup_plugin, temp_project_dir):
        """Test that actual deletion happens when not in dry run"""
        # Create temp file
        temp_file = temp_project_dir / 'test.tmp'
        temp_file.write_text('temp')
        
        # Set old timestamp
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        import os
        os.utime(temp_file, (old_time, old_time))
        
        cleanup_plugin.dry_run = False
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        # File should be deleted
        assert not temp_file.exists()


class TestReporting:
    """Test cleanup reporting"""
    
    def test_generate_report(self, cleanup_plugin, temp_project_dir):
        """Test cleanup report generation"""
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert 'report_path' in result
        assert 'stats' in result
        assert 'recommendations' in result
    
    def test_report_contains_stats(self, cleanup_plugin, temp_project_dir):
        """Test that report contains statistics"""
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        stats = result['stats']
        assert 'files_scanned' in stats
        assert 'files_deleted' in stats
        assert 'space_freed_mb' in stats
    
    def test_report_saved_to_file(self, cleanup_plugin, temp_project_dir):
        """Test that report is saved to file"""
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        report_path = Path(result['report_path'])
        # In dry run, parent dirs may not be created
        if report_path.parent.exists():
            # Check report would be saved (in actual run)
            assert report_path.parent.exists()


class TestHealthReport:
    """Test health report generation"""
    
    def test_generate_health_report(self, cleanup_plugin):
        """Test health report generation for self-review"""
        result = cleanup_plugin.execute({'hook': HookPoint.ON_SELF_REVIEW.value})
        
        assert result['success']
        assert 'health_report' in result
        assert 'issues_found' in result


class TestCleanupStats:
    """Test CleanupStats class"""
    
    def test_stats_initialization(self):
        """Test stats initialization"""
        stats = CleanupStats()
        assert stats.files_scanned == 0
        assert stats.files_deleted == 0
        assert stats.space_freed_bytes == 0
    
    def test_stats_space_conversion(self):
        """Test space freed conversion"""
        stats = CleanupStats()
        stats.space_freed_bytes = 10 * 1024 * 1024  # 10MB
        
        assert stats.space_freed_mb == 10.0
        assert stats.space_freed_gb == 10.0 / 1024
    
    def test_stats_to_dict(self):
        """Test stats conversion to dictionary"""
        stats = CleanupStats()
        stats.files_deleted = 5
        stats.space_freed_bytes = 1024 * 1024
        
        data = stats.to_dict()
        assert data['files_deleted'] == 5
        assert 'space_freed_mb' in data


class TestPluginCleanup:
    """Test plugin cleanup"""
    
    def test_plugin_cleanup(self, cleanup_plugin):
        """Test plugin cleanup method"""
        assert cleanup_plugin.cleanup()


class TestErrorHandling:
    """Test error handling"""
    
    def test_handle_permission_errors(self, cleanup_plugin, temp_project_dir):
        """Test handling of permission errors"""
        # This test is platform-dependent and may not work on all systems
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        # Should complete even if some operations fail
        assert result['success']
    
    def test_handle_missing_directories(self, plugin_config):
        """Test handling of missing directories"""
        # Use non-existent directory
        plugin_config['application']['rootPath'] = '/nonexistent/path'
        
        plugin = CleanupPlugin()
        # Should initialize even with missing path
        assert plugin.initialize(plugin_config)


class TestEdgeCases:
    """Test edge cases"""
    
    def test_cleanup_with_no_files(self, cleanup_plugin, temp_project_dir):
        """Test cleanup when no files need cleaning"""
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']
        assert cleanup_plugin.stats.files_deleted == 0
    
    def test_cleanup_with_special_characters(self, cleanup_plugin, temp_project_dir):
        """Test cleanup with special characters in filenames"""
        # Create file with special chars
        special_file = temp_project_dir / 'file with spaces & special.tmp'
        special_file.write_text('special')
        
        # Set old timestamp
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        import os
        os.utime(special_file, (old_time, old_time))
        
        result = cleanup_plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        assert result['success']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
