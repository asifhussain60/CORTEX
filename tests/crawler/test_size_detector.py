"""
Tests for CORTEX Size Detection Engine

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.crawler.size_detector import (
    SizeDetector,
    SizeCategory,
    SizeEstimate
)


@pytest.fixture
def temp_codebase():
    """Create temporary codebase with known structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create small Python files
        (Path(tmpdir) / "src").mkdir()
        (Path(tmpdir) / "src" / "main.py").write_text("print('hello')\n" * 100)  # ~1400 bytes
        (Path(tmpdir) / "src" / "utils.py").write_text("def helper(): pass\n" * 50)  # ~700 bytes
        
        # Create medium C# file
        (Path(tmpdir) / "app.cs").write_text("// Comment\n" * 1000)  # ~12000 bytes
        
        # Create directory to skip
        (Path(tmpdir) / "node_modules").mkdir()
        (Path(tmpdir) / "node_modules" / "lib.js").write_text("x" * 10000)
        
        yield tmpdir


class TestSizeDetector:
    """Test size detection functionality"""
    
    def test_detect_small_codebase(self, temp_codebase):
        """Test detection of small codebase"""
        detector = SizeDetector()
        estimate = detector.detect(temp_codebase)
        
        # Should find 3 files (main.py, utils.py, app.cs)
        # Should skip node_modules
        assert estimate.total_files == 3
        assert estimate.size_category == SizeCategory.SMALL
        assert estimate.estimated_loc < 50_000
        assert estimate.detection_time_ms < 30_000  # Under 30 seconds
    
    def test_skip_directories(self, temp_codebase):
        """Test that common directories are skipped"""
        detector = SizeDetector()
        estimate = detector.detect(temp_codebase)
        
        # node_modules file should not be counted
        assert estimate.total_files == 3  # Not 4
    
    def test_file_breakdown_by_extension(self, temp_codebase):
        """Test file breakdown by extension"""
        detector = SizeDetector()
        estimate = detector.detect(temp_codebase)
        
        # Should have counts for .py and .cs
        assert '.py' in estimate.file_breakdown
        assert estimate.file_breakdown['.py'] == 2
        assert '.cs' in estimate.file_breakdown
        assert estimate.file_breakdown['.cs'] == 1
    
    def test_largest_files_tracking(self, temp_codebase):
        """Test that largest files are tracked"""
        detector = SizeDetector()
        estimate = detector.detect(temp_codebase)
        
        assert len(estimate.largest_files) > 0
        # Largest should be app.cs (~12KB)
        largest_path, largest_loc = estimate.largest_files[0]
        assert 'app.cs' in largest_path
        assert largest_loc > 100  # Should estimate >100 LOC
    
    def test_size_categorization(self):
        """Test size category assignment"""
        detector = SizeDetector()
        
        # Test each category threshold
        assert detector._categorize_size(10_000) == SizeCategory.SMALL
        assert detector._categorize_size(100_000) == SizeCategory.MEDIUM
        assert detector._categorize_size(500_000) == SizeCategory.LARGE
        assert detector._categorize_size(1_500_000) == SizeCategory.MASSIVE
    
    def test_strategy_recommendations(self):
        """Test that strategies are recommended correctly"""
        detector = SizeDetector()
        
        strategies = detector.STRATEGIES
        assert strategies[SizeCategory.SMALL] == "Full Analysis"
        assert strategies[SizeCategory.MEDIUM] == "Chunked Analysis"
        assert strategies[SizeCategory.LARGE] == "Sampling + Chunking (20% sample)"
        assert strategies[SizeCategory.MASSIVE] == "Intelligent Sampling (5% sample)"
    
    def test_loc_estimation_accuracy(self):
        """Test LOC estimation from file size"""
        detector = SizeDetector()
        
        # 4000 bytes / 40 bytes per line = 100 LOC
        assert detector._estimate_loc(4000) == 100
        
        # Very small files should still estimate at least 1 LOC
        assert detector._estimate_loc(10) == 1
    
    def test_timeout_detection(self):
        """Test timeout mechanism"""
        detector = SizeDetector(timeout_seconds=1)
        
        # Start timing
        detector.start_time = detector.start_time or detector.start_time
        import time
        detector.start_time = time.time() - 2  # Simulate 2 seconds elapsed
        
        assert detector._is_timeout() is True
    
    def test_format_estimate_output(self, temp_codebase):
        """Test formatted output for user display"""
        detector = SizeDetector()
        estimate = detector.detect(temp_codebase)
        
        formatted = detector.format_estimate(estimate)
        
        # Should contain key information
        assert "Detected codebase size" in formatted
        assert "Strategy:" in formatted
        assert "Detection time:" in formatted
        assert "Files analyzed:" in formatted
    
    def test_invalid_path_handling(self):
        """Test handling of invalid paths"""
        detector = SizeDetector()
        
        with pytest.raises(ValueError, match="Path does not exist"):
            detector.detect("Z:\\definitely\\nonexistent\\path\\12345")
    
    def test_custom_extensions_filter(self, temp_codebase):
        """Test detection with custom extension filter"""
        detector = SizeDetector()
        
        # Only analyze Python files
        estimate = detector.detect(temp_codebase, extensions=['.py'])
        
        assert estimate.total_files == 2  # Only main.py and utils.py
        assert '.cs' not in estimate.file_breakdown or estimate.file_breakdown['.cs'] == 0
    
    def test_detection_time_tracking(self, temp_codebase):
        """Test that detection time is tracked"""
        detector = SizeDetector()
        estimate = detector.detect(temp_codebase)
        
        # Detection time should be reasonable
        assert estimate.detection_time_ms > 0
        assert estimate.detection_time_ms < 5000  # Under 5 seconds for small test


class TestSizeEstimate:
    """Test SizeEstimate dataclass"""
    
    def test_estimate_structure(self):
        """Test that estimate contains all required fields"""
        estimate = SizeEstimate(
            total_files=100,
            estimated_loc=50000,
            size_category=SizeCategory.MEDIUM,
            file_breakdown={'.py': 50, '.cs': 50},
            largest_files=[("test.py", 1000)],
            detection_time_ms=500.0,
            recommended_strategy="Chunked Analysis"
        )
        
        assert estimate.total_files == 100
        assert estimate.estimated_loc == 50000
        assert estimate.size_category == SizeCategory.MEDIUM
        assert estimate.recommended_strategy == "Chunked Analysis"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
