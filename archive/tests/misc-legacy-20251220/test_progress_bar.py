"""
Tests for ProgressBar utility class.

This module validates visual progress bar rendering for response templates.
"""

import pytest
from src.utils.progress_bar import ProgressBar


class TestProgressBarRendering:
    """Test basic progress bar rendering functionality."""
    
    def test_progress_bar_renders_percentage(self):
        """Verify percentage is included in rendered output."""
        bar = ProgressBar(current=50, total=100)
        result = bar.render()
        assert "50%" in result
    
    def test_progress_bar_shows_visual_blocks(self):
        """Verify visual blocks represent progress accurately."""
        bar = ProgressBar(current=7, total=10, width=10)
        result = bar.render()
        # 7/10 = 70% = 7 filled blocks, 3 empty
        assert "███████░░░" in result
    
    def test_progress_bar_handles_zero_total(self):
        """Verify graceful handling of zero total."""
        bar = ProgressBar(current=0, total=0)
        result = bar.render()
        assert "0%" in result
        assert "░" * 20 in result  # Default width
    
    def test_progress_bar_100_percent(self):
        """Verify 100% completion renders correctly."""
        bar = ProgressBar(current=10, total=10, width=10)
        result = bar.render()
        assert "██████████" in result
        assert "100%" in result
    
    def test_progress_bar_custom_width(self):
        """Verify custom width parameter works."""
        bar = ProgressBar(current=5, total=10, width=5)
        result = bar.render()
        # 5/10 = 50% with width 5 = 2.5 → 2 filled blocks
        assert len(result.split()[0]) == 5  # Width should be 5 characters


class TestProgressBarEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_progress_exceeds_total(self):
        """Verify handling when current > total."""
        bar = ProgressBar(current=15, total=10)
        result = bar.render()
        # Should cap at 100%
        assert "100%" in result
    
    def test_negative_values(self):
        """Verify handling of negative values."""
        bar = ProgressBar(current=-5, total=10)
        result = bar.render()
        # Should treat as 0%
        assert "0%" in result
    
    def test_fractional_percentages(self):
        """Verify fractional percentages round correctly."""
        bar = ProgressBar(current=1, total=3, width=10)
        result = bar.render()
        # 1/3 = 33.33% → "33%"
        assert "33%" in result
