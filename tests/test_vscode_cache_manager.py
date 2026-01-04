"""
Unit Tests for VSCodeCacheManager - CORTEX v5.0

Author: Asif Hussain
Created: January 4, 2026
Part of: CORTEX-5.0 Sub-Plan C50-00D
"""

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from datetime import datetime

from src.operations.utilities.vscode_cache_manager import (
    VSCodeCacheManager,
    optimize_pre_flight,
    run_full_cleanup,
    check_cache_health
)


class TestVSCodeCacheManager(unittest.TestCase):
    """Test suite for VSCodeCacheManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "enabled": True,
            "pre_flight": {
                "enabled": True,
                "clear_copilot_chat": True,
                "log_metrics": False  # Disable for tests
            },
            "thresholds": {
                "copilot_chat_mb": 100,
                "extension_vsix_mb": 500
            }
        }
        self.manager = VSCodeCacheManager(config=self.config)
    
    def test_initialization(self):
        """Test VSCodeCacheManager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.config["enabled"], True)
        self.assertIn(self.manager.platform, ["Windows", "Darwin", "Linux"])
        self.assertIsInstance(self.manager.paths, dict)
    
    def test_default_config(self):
        """Test default configuration when none provided."""
        manager = VSCodeCacheManager()
        self.assertTrue(manager.config["enabled"])
        self.assertTrue(manager.config["pre_flight"]["enabled"])
        self.assertEqual(manager.config["thresholds"]["copilot_chat_mb"], 100)
    
    def test_path_resolution_mac(self):
        """Test path resolution for macOS."""
        with patch('platform.system', return_value='Darwin'):
            manager = VSCodeCacheManager()
            paths = manager.paths
            self.assertIn("copilot_chat", paths)
            copilot_path = str(paths["copilot_chat"])
            self.assertIn("Library/Application Support", copilot_path)
    
    def test_path_resolution_windows(self):
        """Test path resolution for Windows."""
        with patch('platform.system', return_value='Windows'):
            with patch.dict('os.environ', {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'}):
                manager = VSCodeCacheManager()
                paths = manager.paths
                self.assertIn("copilot_chat", paths)
                copilot_path = str(paths["copilot_chat"])
                self.assertIn("AppData", copilot_path)
    
    def test_path_resolution_linux(self):
        """Test path resolution for Linux."""
        with patch('platform.system', return_value='Linux'):
            manager = VSCodeCacheManager()
            paths = manager.paths
            self.assertIn("copilot_chat", paths)
            copilot_path = str(paths["copilot_chat"])
            self.assertIn(".config", copilot_path)
    
    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists', return_value=True)
    def test_pre_flight_optimize_success(self, mock_exists, mock_rmtree):
        """Test successful pre-flight optimization."""
        with patch.object(self.manager, '_get_dir_size', return_value=104857600):  # 100MB
            result = self.manager.pre_flight_optimize(dry_run=False)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["operation"], "pre_flight_optimize")
            self.assertIn("cache_cleared", result)
            self.assertEqual(len(result["errors"]), 0)
            mock_rmtree.assert_called()
    
    @patch('pathlib.Path.exists', return_value=True)
    def test_pre_flight_optimize_dry_run(self, mock_exists):
        """Test pre-flight optimization in dry-run mode."""
        with patch.object(self.manager, '_get_dir_size', return_value=52428800):  # 50MB
            result = self.manager.pre_flight_optimize(dry_run=True)
            
            self.assertTrue(result["success"])
            self.assertTrue(result["dry_run"])
            self.assertIn("copilot_chat", result["cache_cleared"])
            cache_info = result["cache_cleared"]["copilot_chat"]
            self.assertEqual(cache_info["size_before_mb"], 50.0)
            self.assertEqual(cache_info["freed_mb"], 0.0)  # Dry run doesn't free
    
    @patch('pathlib.Path.exists', return_value=False)
    def test_pre_flight_optimize_no_cache(self, mock_exists):
        """Test pre-flight optimization when cache doesn't exist."""
        result = self.manager.pre_flight_optimize()
        
        self.assertTrue(result["success"])
        self.assertIn("copilot_chat", result["cache_cleared"])
        self.assertFalse(result["cache_cleared"]["copilot_chat"]["exists"])
    
    def test_pre_flight_optimize_disabled(self):
        """Test pre-flight optimization when disabled in config."""
        self.manager.config["pre_flight"]["enabled"] = False
        result = self.manager.pre_flight_optimize()
        
        self.assertTrue(result["success"])
        self.assertIn("skipped", result)
    
    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists', return_value=True)
    def test_full_cleanup(self, mock_exists, mock_rmtree):
        """Test full cleanup operation."""
        with patch.object(self.manager, '_get_dir_size', return_value=209715200):  # 200MB
            result = self.manager.full_cleanup(dry_run=False)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["operation"], "full_cleanup")
            self.assertGreater(result["total_freed_mb"], 0)
            # Should attempt to clear all paths
            self.assertEqual(mock_rmtree.call_count, len(self.manager.paths))
    
    @patch('pathlib.Path.exists', return_value=True)
    def test_health_check(self, mock_exists):
        """Test cache health check."""
        with patch.object(self.manager, '_get_dir_size', return_value=157286400):  # 150MB
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_mtime = datetime.now().timestamp()
                
                result = self.manager.health_check()
                
                self.assertIn("caches", result)
                self.assertIn("overall_status", result)
                self.assertIn("total_size_mb", result)
                
                # Check copilot_chat status
                if "copilot_chat" in result["caches"]:
                    cache_info = result["caches"]["copilot_chat"]
                    self.assertIn("size_mb", cache_info)
                    self.assertIn("status", cache_info)
    
    @patch('pathlib.Path.exists', return_value=False)
    def test_health_check_clean_system(self, mock_exists):
        """Test health check on clean system (no caches)."""
        result = self.manager.health_check()
        
        self.assertEqual(result["overall_status"], "✅ Healthy")
        self.assertEqual(result["total_size_mb"], 0.0)
        
        # All caches should report as clean
        for cache_name, cache_info in result["caches"].items():
            self.assertFalse(cache_info["exists"])
            self.assertEqual(cache_info["status"], "✅ Clean")
    
    def test_get_dir_size(self):
        """Test directory size calculation."""
        # Create mock file structure
        mock_files = [
            MagicMock(is_file=Mock(return_value=True), stat=Mock(return_value=MagicMock(st_size=1024))),
            MagicMock(is_file=Mock(return_value=True), stat=Mock(return_value=MagicMock(st_size=2048))),
            MagicMock(is_file=Mock(return_value=False))  # Directory
        ]
        
        with patch('pathlib.Path.rglob', return_value=mock_files):
            size = self.manager._get_dir_size(Path("/fake/path"))
            self.assertEqual(size, 3072)  # 1024 + 2048
    
    @patch('pathlib.Path.rglob', side_effect=PermissionError("Access denied"))
    def test_get_dir_size_permission_error(self, mock_rglob):
        """Test graceful handling of permission errors."""
        size = self.manager._get_dir_size(Path("/restricted/path"))
        self.assertEqual(size, 0)  # Should return 0, not raise exception
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_log_metrics(self, mock_mkdir, mock_file):
        """Test metrics logging."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "operation": "test",
            "success": True
        }
        
        self.manager._log_metrics(results)
        
        mock_mkdir.assert_called_once()
        mock_file.assert_called_once()
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("test", written_data)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    @patch('src.operations.utilities.vscode_cache_manager.VSCodeCacheManager')
    def test_optimize_pre_flight(self, mock_manager_class):
        """Test optimize_pre_flight convenience function."""
        mock_manager = Mock()
        mock_manager.pre_flight_optimize.return_value = {"success": True}
        mock_manager_class.return_value = mock_manager
        
        result = optimize_pre_flight()
        
        self.assertTrue(result["success"])
        mock_manager.pre_flight_optimize.assert_called_once()
    
    @patch('src.operations.utilities.vscode_cache_manager.VSCodeCacheManager')
    def test_full_cache_cleanup(self, mock_manager_class):
        """Test run_full_cleanup convenience function."""
        mock_manager = Mock()
        mock_manager.full_cleanup.return_value = {"success": True, "total_freed_mb": 250.0}
        mock_manager_class.return_value = mock_manager
        
        result = run_full_cleanup(dry_run=True)
        
        self.assertTrue(result["success"])
        mock_manager.full_cleanup.assert_called_once_with(dry_run=True)
    
    @patch('src.operations.utilities.vscode_cache_manager.VSCodeCacheManager')
    def test_cache_health_check(self, mock_manager_class):
        """Test check_cache_health convenience function."""
        mock_manager = Mock()
        mock_manager.health_check.return_value = {"overall_status": "✅ Healthy"}
        mock_manager_class.return_value = mock_manager
        
        result = check_cache_health()
        
        self.assertIn("overall_status", result)
        mock_manager.health_check.assert_called_once()
    
    @patch('src.operations.utilities.vscode_cache_manager.VSCodeCacheManager', side_effect=Exception("Init failed"))
    def test_optimize_pre_flight_error_handling(self, mock_manager_class):
        """Test error handling in convenience functions."""
        result = optimize_pre_flight()
        
        self.assertTrue(result["success"])  # Non-blocking
        self.assertIn("error", result)


class TestCrossCompatibility(unittest.TestCase):
    """Test cross-platform compatibility."""
    
    def test_all_platforms_have_paths(self):
        """Test that all platforms have cache path definitions."""
        required_caches = ["copilot_chat", "extension_vsix", "general_cache", "cached_data"]
        
        for platform in ["Windows", "Darwin", "Linux"]:
            self.assertIn(platform, VSCodeCacheManager.CACHE_PATHS)
            platform_paths = VSCodeCacheManager.CACHE_PATHS[platform]
            
            for cache_name in required_caches:
                self.assertIn(cache_name, platform_paths)
                self.assertIsInstance(platform_paths[cache_name], str)
                self.assertGreater(len(platform_paths[cache_name]), 0)


if __name__ == '__main__':
    unittest.main()
