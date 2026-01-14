#!/usr/bin/env python3
"""
Unit tests for VS Code Cache Cleaner
Author: Asif Hussain
Date: 2026-01-13

Test Coverage:
- Cross-platform path detection (MAC, WIN, Linux)
- Cache directory enumeration
- Preserved paths validation
- Dry-run simulation
- Size calculation accuracy
"""

import pytest
import platform
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.vscode_cache_cleaner import VSCodeCacheCleaner


class TestVSCodeCacheCleaner:
    """Test suite for VSCodeCacheCleaner"""
    
    def test_initialization(self):
        """Test cleaner initialization"""
        cleaner = VSCodeCacheCleaner()
        assert cleaner.system == platform.system()
        assert cleaner.vscode_base is not None
        assert isinstance(cleaner.vscode_base, Path)
    
    @pytest.mark.cross_platform
    def test_get_vscode_base_path_mac(self):
        """Test VS Code path detection on macOS"""
        with patch('platform.system', return_value='Darwin'):
            cleaner = VSCodeCacheCleaner()
            expected = Path.home() / "Library/Application Support/Code"
            assert cleaner.vscode_base == expected
    
    @pytest.mark.cross_platform
    def test_get_vscode_base_path_windows(self):
        """Test VS Code path detection on Windows"""
        with patch('platform.system', return_value='Windows'):
            with patch.dict('os.environ', {'APPDATA': 'C:\\Users\\TestUser\\AppData\\Roaming'}):
                cleaner = VSCodeCacheCleaner()
                # Use pathlib for cross-platform comparison
                expected_str = "C:/Users/TestUser/AppData/Roaming/Code"
                assert str(cleaner.vscode_base).replace('\\', '/') == expected_str
    
    @pytest.mark.cross_platform
    def test_get_vscode_base_path_linux(self):
        """Test VS Code path detection on Linux"""
        with patch('platform.system', return_value='Linux'):
            cleaner = VSCodeCacheCleaner()
            expected = Path.home() / ".config/Code"
            assert cleaner.vscode_base == expected
    
    def test_get_cache_directories(self):
        """Test cache directory enumeration"""
        cleaner = VSCodeCacheCleaner()
        cache_dirs = cleaner._get_cache_directories()
        
        assert isinstance(cache_dirs, list)
        assert len(cache_dirs) > 0
        
        # Check structure
        for cache_dir in cache_dirs:
            assert 'path' in cache_dir
            assert 'name' in cache_dir
            assert 'description' in cache_dir
            assert isinstance(cache_dir['path'], Path)
        
        # Check expected cache directories
        cache_names = [cd['name'] for cd in cache_dirs]
        assert 'Main Cache' in cache_names
        assert 'Workspace Storage' in cache_names
        assert 'GPU Cache' in cache_names
    
    def test_get_preserved_paths(self):
        """Test preserved paths enumeration"""
        cleaner = VSCodeCacheCleaner()
        preserved = cleaner._get_preserved_paths()
        
        assert isinstance(preserved, list)
        assert len(preserved) > 0
        
        # Check structure
        for preserve_info in preserved:
            assert 'path' in preserve_info
            assert 'name' in preserve_info
            assert 'description' in preserve_info
            assert isinstance(preserve_info['path'], Path)
        
        # Check expected preserved paths
        preserve_names = [p['name'] for p in preserved]
        assert 'User Settings' in preserve_names
        assert 'Extensions' in preserve_names
        assert 'Snippets' in preserve_names
    
    def test_format_size(self):
        """Test size formatting"""
        cleaner = VSCodeCacheCleaner()
        
        assert cleaner._format_size(0) == "0.0 B"
        assert cleaner._format_size(512) == "512.0 B"
        assert cleaner._format_size(1024) == "1.0 KB"
        assert cleaner._format_size(1024 * 1024) == "1.0 MB"
        assert cleaner._format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert cleaner._format_size(1536) == "1.5 KB"
    
    def test_dry_run(self):
        """Test dry-run simulation"""
        cleaner = VSCodeCacheCleaner()
        result = cleaner.dry_run()
        
        assert 'to_clean' in result
        assert 'to_preserve' in result
        assert 'total_size' in result
        assert 'total_size_formatted' in result
        
        assert isinstance(result['to_clean'], list)
        assert isinstance(result['to_preserve'], list)
        assert isinstance(result['total_size'], int)
        assert isinstance(result['total_size_formatted'], str)
    
    @patch('shutil.rmtree')
    @patch('pathlib.Path.unlink')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_clean_success(self, mock_is_dir, mock_exists, mock_unlink, mock_rmtree):
        """Test successful cache cleaning"""
        cleaner = VSCodeCacheCleaner()
        
        # Mock directory size calculation
        with patch.object(cleaner, '_get_directory_size', return_value=1024):
            result = cleaner.clean(dry_run=False)
        
        assert 'cleaned' in result
        assert 'errors' in result
        assert 'size_freed' in result
        assert 'success' in result
        
        assert isinstance(result['cleaned'], list)
        assert result['success'] is True
    
    @patch('shutil.rmtree', side_effect=PermissionError("Permission denied"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_clean_permission_error(self, mock_is_dir, mock_exists, mock_rmtree):
        """Test cleaning with permission errors"""
        cleaner = VSCodeCacheCleaner()
        
        with patch.object(cleaner, '_get_directory_size', return_value=1024):
            result = cleaner.clean(dry_run=False)
        
        assert 'errors' in result
        assert len(result['errors']) > 0
        assert result['success'] is False
    
    def test_report_dry_run(self):
        """Test dry-run report generation"""
        cleaner = VSCodeCacheCleaner()
        report = cleaner.report(dry_run=True)
        
        assert isinstance(report, str)
        assert "DRY RUN" in report
        assert "TO BE CLEANED" in report
        assert "TO BE PRESERVED" in report
        assert "Total size to free" in report
    
    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_report_execution(self, mock_is_dir, mock_exists, mock_rmtree):
        """Test execution report generation"""
        cleaner = VSCodeCacheCleaner()
        
        with patch.object(cleaner, '_get_directory_size', return_value=1024):
            report = cleaner.report(dry_run=False)
        
        assert isinstance(report, str)
        assert "EXECUTION REPORT" in report
        assert "CLEANED" in report or "No cache found" in report
        assert "Size freed" in report
    
    @pytest.mark.cross_platform
    def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility (CORE-005)"""
        # Test on current platform
        cleaner = VSCodeCacheCleaner()
        
        # Verify no hardcoded paths
        base_str = str(cleaner.vscode_base)
        assert '/Users/' not in base_str or platform.system() == 'Darwin'
        assert 'C:\\' not in base_str or platform.system() == 'Windows'
        
        # Verify pathlib usage (CORE-005)
        cache_dirs = cleaner._get_cache_directories()
        for cache_dir in cache_dirs:
            assert isinstance(cache_dir['path'], Path)


@pytest.mark.integration
class TestVSCodeCacheCleanerIntegration:
    """Integration tests for VSCodeCacheCleaner"""
    
    def test_dry_run_real_system(self):
        """Test dry-run on real system (safe, no modifications)"""
        cleaner = VSCodeCacheCleaner()
        result = cleaner.dry_run()
        
        # Should complete without errors
        assert 'to_clean' in result
        assert 'total_size' in result
        
        # Size should be non-negative
        assert result['total_size'] >= 0
    
    def test_report_dry_run_real_system(self):
        """Test dry-run report on real system"""
        cleaner = VSCodeCacheCleaner()
        report = cleaner.report(dry_run=True)
        
        # Should generate valid report
        assert isinstance(report, str)
        assert len(report) > 0
        assert "=" in report  # Header separator


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
