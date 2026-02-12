"""
Tests for Platform Output Formatter (AC-ENH054-002)

Tests Windows CP1252 compatibility and ASCII/emoji fallback.
"""

import platform
import pytest
from unittest.mock import patch, MagicMock

from cortex.common.platform_output import (
    PlatformOutputFormatter,
    OutputLevel,
    success, error, warning, info, critical, fix, start, complete
)


# AC_START: AC-ENH054-002
# Description: Test Windows CP1252 encoding compatibility layer
# Requirements: Platform detection, ASCII fallback, emoji support


class TestPlatformDetection:
    """Test platform and encoding detection"""
    
    def test_creates_formatter_instance(self):
        """Test creating formatter instance"""
        formatter = PlatformOutputFormatter()
        assert formatter is not None
        assert hasattr(formatter, 'use_ascii')
    
    @patch('platform.system', return_value='Windows')
    @patch('sys.stdout')
    def test_detects_windows_cp1252(self, mock_stdout, mock_platform):
        """Test detecting Windows CP1252 encoding"""
        mock_stdout.encoding = 'cp1252'
        formatter = PlatformOutputFormatter()
        assert formatter.use_ascii is True
    
    @patch('platform.system', return_value='Darwin')  # macOS
    @patch('sys.stdout')
    def test_detects_macos_utf8(self, mock_stdout, mock_platform):
        """Test detecting macOS UTF-8 encoding"""
        mock_stdout.encoding = 'utf-8'
        formatter = PlatformOutputFormatter()
        assert formatter.use_ascii is False
    
    @patch('platform.system', return_value='Linux')
    @patch('sys.stdout')
    def test_detects_linux_utf8(self, mock_stdout, mock_platform):
        """Test detecting Linux UTF-8 encoding"""
        mock_stdout.encoding = 'utf-8'
        formatter = PlatformOutputFormatter()
        assert formatter.use_ascii is False
    
    def test_force_ascii_mode(self):
        """Test forcing ASCII mode"""
        formatter = PlatformOutputFormatter(force_ascii=True)
        assert formatter.use_ascii is True
    
    def test_force_emoji_mode(self):
        """Test forcing emoji mode"""
        formatter = PlatformOutputFormatter(force_ascii=False)
        assert formatter.use_ascii is False


class TestASCIIFormatting:
    """Test ASCII-only output formatting"""
    
    def setup_method(self):
        """Setup ASCII-only formatter"""
        self.formatter = PlatformOutputFormatter(force_ascii=True)
    
    def test_success_ascii(self):
        """Test success message with ASCII"""
        result = self.formatter.success("Test passed")
        assert result == "[OK] Test passed"
        assert "✅" not in result
    
    def test_error_ascii(self):
        """Test error message with ASCII"""
        result = self.formatter.error("Test failed")
        assert result == "[FAIL] Test failed"
        assert "❌" not in result
    
    def test_warning_ascii(self):
        """Test warning message with ASCII"""
        result = self.formatter.warning("Warning message")
        assert result == "[WARN] Warning message"
        assert "⚠️" not in result
    
    def test_info_ascii(self):
        """Test info message with ASCII"""
        result = self.formatter.info("Info message")
        assert result == "[INFO] Info message"
        assert "ℹ️" not in result
    
    def test_critical_ascii(self):
        """Test critical message with ASCII"""
        result = self.formatter.critical("Critical issue")
        assert result == "[CRIT] Critical issue"
        assert "🔴" not in result
    
    def test_fix_ascii(self):
        """Test fix message with ASCII"""
        result = self.formatter.fix("Applying fix")
        assert result == "[FIX] Applying fix"
        assert "🔧" not in result
    
    def test_start_ascii(self):
        """Test start message with ASCII"""
        result = self.formatter.start("Starting process")
        assert result == "[START] Starting process"
        assert "🚀" not in result
    
    def test_complete_ascii(self):
        """Test completion message with ASCII"""
        result = self.formatter.complete("Process completed")
        assert result == "[DONE] Process completed"
        assert "🎯" not in result


class TestEmojiFormatting:
    """Test emoji output formatting"""
    
    def setup_method(self):
        """Setup emoji formatter"""
        self.formatter = PlatformOutputFormatter(force_ascii=False)
    
    def test_success_emoji(self):
        """Test success message with emoji"""
        result = self.formatter.success("Test passed")
        assert result == "✅ Test passed"
        assert "[OK]" not in result
    
    def test_error_emoji(self):
        """Test error message with emoji"""
        result = self.formatter.error("Test failed")
        assert result == "❌ Test failed"
        assert "[FAIL]" not in result
    
    def test_warning_emoji(self):
        """Test warning message with emoji"""
        result = self.formatter.warning("Warning message")
        assert result == "⚠️ Warning message"
        assert "[WARN]" not in result
    
    def test_fix_emoji(self):
        """Test fix message with emoji"""
        result = self.formatter.fix("Applying fix")
        assert result == "🔧 Applying fix"
        assert "[FIX]" not in result


class TestModuleLevelFunctions:
    """Test module-level convenience functions"""
    
    def test_success_function(self):
        """Test module-level success()"""
        result = success("Test passed")
        assert "Test passed" in result
        # Contains either emoji or ASCII
        assert ("✅" in result) or ("[OK]" in result)
    
    def test_error_function(self):
        """Test module-level error()"""
        result = error("Test failed")
        assert "Test failed" in result
        assert ("❌" in result) or ("[FAIL]" in result)
    
    def test_warning_function(self):
        """Test module-level warning()"""
        result = warning("Warning message")
        assert "Warning message" in result
        assert ("⚠️" in result) or ("[WARN]" in result)
    
    def test_info_function(self):
        """Test module-level info()"""
        result = info("Info message")
        assert "Info message" in result
        assert ("ℹ️" in result) or ("[INFO]" in result)


class TestEncodingInfo:
    """Test encoding information reporting"""
    
    def test_get_encoding_info(self):
        """Test getting encoding info"""
        formatter = PlatformOutputFormatter()
        info_dict = formatter.get_encoding_info()
        
        # Check required keys
        assert "platform" in info_dict
        assert "stdout_encoding" in info_dict
        assert "mode" in info_dict
        assert "reason" in info_dict
        
        # Check values are strings
        assert isinstance(info_dict["platform"], str)
        assert isinstance(info_dict["stdout_encoding"], str)
        assert info_dict["mode"] in ["ASCII", "UTF-8"]
    
    def test_encoding_info_ascii_mode(self):
        """Test encoding info in ASCII mode"""
        formatter = PlatformOutputFormatter(force_ascii=True)
        info_dict = formatter.get_encoding_info()
        
        assert info_dict["mode"] == "ASCII"
    
    def test_encoding_info_emoji_mode(self):
        """Test encoding info in emoji mode"""
        formatter = PlatformOutputFormatter(force_ascii=False)
        info_dict = formatter.get_encoding_info()
        
        assert info_dict["mode"] == "UTF-8"


class TestWindowsCompatibility:
    """Test Windows-specific compatibility scenarios"""
    
    @patch('platform.system', return_value='Windows')
    @patch('sys.stdout')
    def test_windows_with_cp1252_uses_ascii(self, mock_stdout, mock_platform):
        """Test Windows with CP1252 uses ASCII"""
        mock_stdout.encoding = 'cp1252'
        formatter = PlatformOutputFormatter()
        
        result = formatter.success("Test")
        assert "[OK]" in result
        assert "✅" not in result
    
    @patch('platform.system', return_value='Windows')
    @patch('sys.stdout')
    def test_windows_with_windows1252_uses_ascii(self, mock_stdout, mock_platform):
        """Test Windows with windows-1252 uses ASCII"""
        mock_stdout.encoding = 'windows-1252'
        formatter = PlatformOutputFormatter()
        
        result = formatter.success("Test")
        assert "[OK]" in result
    
    @patch('platform.system', return_value='Windows')
    @patch('sys.stdout')
    def test_windows_fallback_when_encoding_unknown(self, mock_stdout, mock_platform):
        """Test Windows defaults to ASCII when encoding unknown"""
        # Simulate missing encoding attribute
        del mock_stdout.encoding
        formatter = PlatformOutputFormatter()
        
        # Windows should default to ASCII for safety
        # Note: When encoding check fails, we catch AttributeError and default to True
        assert formatter.use_ascii is True


# AC_COMPLETE: AC-ENH054-002 [OK] 28/28 tests PASSING
# Platform detection: PASS
# ASCII formatting: PASS
# Emoji formatting: PASS
# Windows CP1252 compatibility: PASS
# Module-level functions: PASS
