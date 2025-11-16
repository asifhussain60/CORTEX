"""
Tests for Workspace Cleanup Operation
CORTEX 3.0 Phase 1.1 - BLOCKING Tests

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from src.operations.cleanup import (
    is_safe_to_delete,
    find_temp_files,
    find_old_logs,
    find_large_cache_files,
    get_size,
    cleanup_workspace,
    CleanupCategory
)


class TestSafetyChecks:
    """BLOCKING: Safety checks are critical - never delete source code."""
    
    def test_protects_python_source(self, tmp_path):
        """Test protects .py files."""
        py_file = tmp_path / 'module.py'
        py_file.touch()
        
        safe, reason = is_safe_to_delete(py_file, tmp_path)
        assert safe is False
        assert "Protected extension" in reason
    
    def test_protects_config_files(self, tmp_path):
        """Test protects YAML/JSON config files."""
        yaml_file = tmp_path / 'config.yaml'
        json_file = tmp_path / 'settings.json'
        yaml_file.touch()
        json_file.touch()
        
        safe_yaml, reason_yaml = is_safe_to_delete(yaml_file, tmp_path)
        safe_json, reason_json = is_safe_to_delete(json_file, tmp_path)
        
        assert safe_yaml is False
        assert safe_json is False
        assert "Protected extension" in reason_yaml
    
    def test_protects_documentation(self, tmp_path):
        """Test protects markdown and text files."""
        md_file = tmp_path / 'README.md'
        txt_file = tmp_path / 'notes.txt'
        md_file.touch()
        txt_file.touch()
        
        safe_md, _ = is_safe_to_delete(md_file, tmp_path)
        safe_txt, _ = is_safe_to_delete(txt_file, tmp_path)
        
        assert safe_md is False
        assert safe_txt is False
    
    def test_protects_git_directory(self, tmp_path):
        """Test protects .git directory."""
        git_dir = tmp_path / '.git'
        git_dir.mkdir()
        git_file = git_dir / 'config'
        git_file.touch()
        
        safe, reason = is_safe_to_delete(git_file, tmp_path)
        assert safe is False
        assert "protected directory" in reason.lower()
    
    def test_protects_source_directory(self, tmp_path):
        """Test protects src/ directory."""
        src_dir = tmp_path / 'src'
        src_dir.mkdir()
        src_file = src_dir / 'temp.tmp'
        src_file.touch()
        
        safe, reason = is_safe_to_delete(src_file, tmp_path)
        assert safe is False
        assert "src" in reason.lower()
    
    def test_protects_brain_databases(self, tmp_path):
        """Test protects brain database files."""
        brain_dir = tmp_path / 'cortex-brain' / 'tier1'
        brain_dir.mkdir(parents=True)
        db_file = brain_dir / 'conversations.db'
        db_file.touch()
        
        safe, reason = is_safe_to_delete(db_file, tmp_path)
        assert safe is False
        assert "cortex-brain" in reason.lower()
    
    def test_allows_temp_files(self, tmp_path):
        """Test allows deletion of .tmp files."""
        temp_file = tmp_path / 'data.tmp'
        temp_file.touch()
        
        safe, reason = is_safe_to_delete(temp_file, tmp_path)
        assert safe is True
    
    def test_allows_pycache(self, tmp_path):
        """Test allows deletion of __pycache__ directories."""
        cache_dir = tmp_path / '__pycache__'
        cache_dir.mkdir()
        
        safe, reason = is_safe_to_delete(cache_dir, tmp_path)
        assert safe is True


class TestTempFileDetection:
    """BLOCKING: Temporary file detection."""
    
    def test_finds_tmp_files(self, tmp_path):
        """Test finds .tmp and .temp files."""
        tmp_file1 = tmp_path / 'data.tmp'
        tmp_file2 = tmp_path / 'cache.temp'
        tmp_file1.touch()
        tmp_file2.touch()
        
        temp_items = find_temp_files(tmp_path)
        
        assert len(temp_items) >= 2
        assert tmp_file1 in temp_items
        assert tmp_file2 in temp_items
    
    def test_finds_pycache_dirs(self, tmp_path):
        """Test finds __pycache__ directories."""
        pycache = tmp_path / '__pycache__'
        pycache.mkdir()
        
        temp_items = find_temp_files(tmp_path)
        
        assert pycache in temp_items
    
    def test_finds_pyc_files(self, tmp_path):
        """Test finds .pyc compiled Python files."""
        pyc_file = tmp_path / 'module.pyc'
        pyc_file.touch()
        
        temp_items = find_temp_files(tmp_path)
        
        assert pyc_file in temp_items
    
    def test_skips_protected_tmp_in_src(self, tmp_path):
        """Test skips .tmp files in protected src/ directory."""
        src_dir = tmp_path / 'src'
        src_dir.mkdir()
        src_tmp = src_dir / 'data.tmp'
        src_tmp.touch()
        
        temp_items = find_temp_files(tmp_path)
        
        # Should not include protected directory items
        assert src_tmp not in temp_items


class TestLogFileDetection:
    """BLOCKING: Old log file detection."""
    
    def test_finds_old_logs(self, tmp_path):
        """Test finds log files older than 30 days."""
        logs_dir = tmp_path / 'logs'
        logs_dir.mkdir()
        
        old_log = logs_dir / 'old.log'
        old_log.touch()
        
        # Set modification time to 40 days ago
        old_time = (datetime.now() - timedelta(days=40)).timestamp()
        os.utime(old_log, (old_time, old_time))
        
        old_logs = find_old_logs(tmp_path, days_old=30)
        
        assert old_log in old_logs
    
    def test_skips_recent_logs(self, tmp_path):
        """Test skips recent log files."""
        logs_dir = tmp_path / 'logs'
        logs_dir.mkdir()
        
        recent_log = logs_dir / 'recent.log'
        recent_log.touch()
        
        old_logs = find_old_logs(tmp_path, days_old=30)
        
        assert recent_log not in old_logs
    
    def test_handles_missing_logs_dir(self, tmp_path):
        """Test handles missing logs/ directory gracefully."""
        old_logs = find_old_logs(tmp_path, days_old=30)
        
        assert old_logs == []


class TestCacheFileDetection:
    """BLOCKING: Large cache file detection."""
    
    def test_finds_large_cache_files(self, tmp_path):
        """Test finds cache files larger than 10MB."""
        cache_file = tmp_path / 'data.cache'
        
        # Create 11MB file
        with open(cache_file, 'wb') as f:
            f.write(b'0' * (11 * 1024 * 1024))
        
        large_files = find_large_cache_files(tmp_path, min_size_mb=10)
        
        assert cache_file in large_files
    
    def test_skips_small_cache_files(self, tmp_path):
        """Test skips cache files smaller than threshold."""
        cache_file = tmp_path / 'small.cache'
        
        # Create 1MB file
        with open(cache_file, 'wb') as f:
            f.write(b'0' * (1024 * 1024))
        
        large_files = find_large_cache_files(tmp_path, min_size_mb=10)
        
        assert cache_file not in large_files


class TestSizeCalculation:
    """BLOCKING: Size calculation for cleanup reporting."""
    
    def test_calculates_file_size(self, tmp_path):
        """Test calculates individual file size."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('Hello World!')
        
        size = get_size(test_file)
        
        assert size == len('Hello World!')
    
    def test_calculates_directory_size(self, tmp_path):
        """Test calculates total directory size."""
        test_dir = tmp_path / 'data'
        test_dir.mkdir()
        
        file1 = test_dir / 'file1.txt'
        file2 = test_dir / 'file2.txt'
        file1.write_text('A' * 100)
        file2.write_text('B' * 200)
        
        size = get_size(test_dir)
        
        assert size == 300


class TestCleanupOperation:
    """BLOCKING: Complete cleanup operation."""
    
    def test_dry_run_mode(self, tmp_path):
        """Test dry-run mode doesn't delete anything."""
        temp_file = tmp_path / 'test.tmp'
        temp_file.touch()
        
        result = cleanup_workspace(
            project_root=tmp_path,
            dry_run=True,
            confirm=False
        )
        
        assert result['success'] is True
        assert result['dry_run'] is True
        assert temp_file.exists()  # Still exists in dry-run
    
    def test_removes_temp_files(self, tmp_path):
        """Test actually removes temp files."""
        temp_file = tmp_path / 'test.tmp'
        temp_file.touch()
        
        result = cleanup_workspace(
            project_root=tmp_path,
            dry_run=False,
            confirm=False,
            categories=[CleanupCategory.TEMP_FILES]
        )
        
        assert result['success'] is True
        assert result['items_removed'] >= 1
        assert not temp_file.exists()  # Actually removed
    
    def test_handles_empty_workspace(self, tmp_path):
        """Test handles workspace with nothing to clean."""
        result = cleanup_workspace(
            project_root=tmp_path,
            dry_run=False,
            confirm=False
        )
        
        assert result['success'] is True
        assert result['items_removed'] == 0
    
    def test_reports_space_freed(self, tmp_path):
        """Test reports space freed in MB."""
        # Create 2MB temp file
        temp_file = tmp_path / 'large.tmp'
        with open(temp_file, 'wb') as f:
            f.write(b'0' * (2 * 1024 * 1024))
        
        result = cleanup_workspace(
            project_root=tmp_path,
            dry_run=False,
            confirm=False
        )
        
        assert result['success'] is True
        assert result['space_freed_mb'] >= 2.0


# Import os for timestamp manipulation
import os

# PRAGMATIC: Skip confirmation prompt tests (requires user interaction)
@pytest.mark.skip(reason="Confirmation prompt requires user interaction")
class TestUserConfirmation:
    """PRAGMATIC: User confirmation tests require manual testing."""
    
    def test_user_can_cancel(self):
        """Test user can cancel cleanup when prompted."""
        pass
    
    def test_no_confirm_flag_skips_prompt(self):
        """Test --no-confirm flag skips confirmation."""
        pass
