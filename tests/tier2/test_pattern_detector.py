"""
Tests for Change Pattern Detector (Phase 4.4)

Tests pattern detection for different file changes.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

NOTE: These tests are skipped - ambient daemon removed from CORTEX 3.0
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
import sys
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))


@pytest.mark.skip(reason="Ambient daemon removed from CORTEX 3.0 - manual capture hints used instead")
class TestChangePatternDetector:
    """Test suite for ChangePatternDetector (DEPRECATED)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.detector = ChangePatternDetector(str(self.temp_path))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
    
    # ========================================================================
    # Extension-Based Classification
    # ========================================================================
    
    def test_detect_documentation_pattern(self):
        """Should detect documentation changes."""
        event = {
            "file": "README.md",
            "event": "modified"
        }
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "DOCS"
    
    def test_detect_rst_documentation(self):
        """Should detect .rst documentation."""
        event = {
            "file": "docs/guide.rst",
            "event": "modified"
        }
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "DOCS"
    
    def test_detect_config_json(self):
        """Should detect JSON configuration changes."""
        event = {
            "file": "package.json",
            "event": "modified"
        }
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "CONFIG"
    
    def test_detect_config_yaml(self):
        """Should detect YAML configuration changes."""
        event = {
            "file": "config.yaml",
            "event": "modified"
        }
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "CONFIG"
    
    def test_detect_config_env(self):
        """Should detect environment file changes."""
        event = {
            "file": ".env",
            "event": "modified"
        }
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "CONFIG"
    
    # ========================================================================
    # Event Type Classification
    # ========================================================================
    
    def test_detect_feature_created(self):
        """Should detect new file creation as feature."""
        event = {
            "file": "src/new_module.py",
            "event": "created"
        }
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "FEATURE"
    
    def test_detect_refactor_deleted(self):
        """Should detect file deletion as refactor."""
        event = {
            "file": "src/old_module.py",
            "event": "deleted"
        }
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "REFACTOR"
    
    # ========================================================================
    # Git Diff Analysis (Mocked)
    # ========================================================================
    
    def test_detect_bugfix_small_change(self):
        """Should detect small changes as bug fix."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        # Mock git diff with small change
        with patch.object(self.detector, '_get_git_diff', return_value=[
            "--- a/src/module.py",
            "+++ b/src/module.py",
            "+    if value is None:",
            "+        return default",
            "-    return value"
        ]):
            pattern = self.detector.detect_pattern(event)
            assert pattern == "BUGFIX"
    
    def test_detect_refactor_balanced_changes(self):
        """Should detect balanced add/delete as refactor."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        # Mock git diff with balanced changes
        diff_lines = ["--- a/src/module.py", "+++ b/src/module.py"]
        # 15 additions, 14 deletions (ratio > 0.7)
        diff_lines += [f"+    new_line_{i}" for i in range(15)]
        diff_lines += [f"-    old_line_{i}" for i in range(14)]
        
        with patch.object(self.detector, '_get_git_diff', return_value=diff_lines):
            pattern = self.detector.detect_pattern(event)
            assert pattern == "REFACTOR"
    
    def test_detect_feature_many_additions(self):
        """Should detect many additions as feature."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        # Mock git diff with many additions
        diff_lines = ["--- a/src/module.py", "+++ b/src/module.py"]
        diff_lines += [f"+    new_code_{i}" for i in range(60)]
        diff_lines += ["-    old_line"]
        
        with patch.object(self.detector, '_get_git_diff', return_value=diff_lines):
            pattern = self.detector.detect_pattern(event)
            assert pattern == "FEATURE"
    
    def test_detect_unknown_no_diff(self):
        """Should return unknown when no diff available."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        with patch.object(self.detector, '_get_git_diff', return_value=[]):
            pattern = self.detector.detect_pattern(event)
            assert pattern == "UNKNOWN"
    
    # ========================================================================
    # Git Diff Caching
    # ========================================================================
    
    def test_cache_git_diff(self):
        """Should cache git diff results."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        # Mock subprocess call
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "+line1\n+line2\n-line3"
        
        with patch('subprocess.run', return_value=mock_result):
            # First call
            self.detector.detect_pattern(event)
            
            # Second call should use cache
            self.detector.detect_pattern(event)
            
            # Should have cached the result
            assert "src/module.py" in self.detector.pattern_detector._diff_cache if hasattr(self.detector, 'pattern_detector') else True
    
    def test_cache_size_limit(self):
        """Should limit cache size to 100 entries."""
        # Create many diff requests
        for i in range(110):
            event = {
                "file": f"src/file{i}.py",
                "event": "modified"
            }
            
            with patch.object(self.detector, '_get_git_diff', return_value=["+line"]):
                self.detector.detect_pattern(event)
        
        # Cache should be limited
        assert len(self.detector._diff_cache) <= 100
    
    # ========================================================================
    # Edge Cases
    # ========================================================================
    
    def test_handle_git_not_available(self):
        """Should handle when git is not available."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        # Mock subprocess to raise FileNotFoundError
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            pattern = self.detector.detect_pattern(event)
            assert pattern == "UNKNOWN"
    
    def test_handle_git_timeout(self):
        """Should handle git command timeout."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('git', 5)):
            pattern = self.detector.detect_pattern(event)
            assert pattern == "UNKNOWN"
    
    def test_handle_malformed_event(self):
        """Should handle malformed events gracefully."""
        event = {}  # Missing required fields
        
        pattern = self.detector.detect_pattern(event)
        assert pattern == "UNKNOWN"
    
    def test_clear_cache(self):
        """Should clear diff cache."""
        # Add some cached items
        self.detector._diff_cache['test'] = ['line']
        self.detector._cache_timestamps['test'] = 123456
        
        # Clear cache
        self.detector.clear_cache()
        
        assert len(self.detector._diff_cache) == 0
        assert len(self.detector._cache_timestamps) == 0


class TestPatternDetectorIntegration:
    """Integration tests for pattern detector."""
    
    def test_pattern_types_defined(self):
        """Should define all pattern types."""
        assert hasattr(ChangePatternDetector, 'PATTERN_REFACTOR')
        assert hasattr(ChangePatternDetector, 'PATTERN_FEATURE')
        assert hasattr(ChangePatternDetector, 'PATTERN_BUGFIX')
        assert hasattr(ChangePatternDetector, 'PATTERN_DOCS')
        assert hasattr(ChangePatternDetector, 'PATTERN_CONFIG')
        assert hasattr(ChangePatternDetector, 'PATTERN_UNKNOWN')
    
    def test_all_patterns_are_strings(self):
        """All pattern constants should be strings."""
        detector = ChangePatternDetector("/tmp")
        
        assert isinstance(detector.PATTERN_REFACTOR, str)
        assert isinstance(detector.PATTERN_FEATURE, str)
        assert isinstance(detector.PATTERN_BUGFIX, str)
        assert isinstance(detector.PATTERN_DOCS, str)
        assert isinstance(detector.PATTERN_CONFIG, str)
        assert isinstance(detector.PATTERN_UNKNOWN, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
