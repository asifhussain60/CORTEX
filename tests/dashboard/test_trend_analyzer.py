"""
Tests for Trend Analyzer - Dashboard Overview Tab

Tests trend detection, snapshot comparison, and trend classification logic.
Following TDD: RED → GREEN → REFACTOR cycle.

Author: Asif Hussain
Created: 2025-12-06
Phase: RED (Write Failing Tests)
"""

import pytest
from datetime import datetime, timedelta


class TestTrendAnalyzer:
    """Test suite for TrendAnalyzer class."""
    
    def test_trend_analyzer_initialization(self):
        """Test TrendAnalyzer can be instantiated."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        assert analyzer is not None
    
    def test_analyze_trend_improving(self):
        """Test trend classification as improving when delta > +2.0."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        current_value = 85.0
        previous_value = 80.0
        
        trend = analyzer.analyze_trend(current_value, previous_value)
        
        assert trend == "improving"
    
    def test_analyze_trend_stable(self):
        """Test trend classification as stable when -2.0 <= delta <= +2.0."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        # Test upper boundary (delta = +2.0)
        trend1 = analyzer.analyze_trend(82.0, 80.0)
        assert trend1 == "stable"
        
        # Test lower boundary (delta = -2.0)
        trend2 = analyzer.analyze_trend(78.0, 80.0)
        assert trend2 == "stable"
        
        # Test middle (delta = +1.0)
        trend3 = analyzer.analyze_trend(81.0, 80.0)
        assert trend3 == "stable"
    
    def test_analyze_trend_declining(self):
        """Test trend classification as declining when delta < -2.0."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        current_value = 75.0
        previous_value = 80.0
        
        trend = analyzer.analyze_trend(current_value, previous_value)
        
        assert trend == "declining"
    
    def test_analyze_trend_no_previous_data(self):
        """Test trend returns N/A when no previous data available."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        current_value = 85.0
        previous_value = None
        
        trend = analyzer.analyze_trend(current_value, previous_value)
        
        assert trend == "N/A"
    
    def test_compare_snapshots_basic(self):
        """Test basic snapshot comparison with all metrics."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        current_snapshot = {
            "overall_health_score": 92,
            "code_quality_score": 88,
            "security_score": 96,
            "test_score": 82
        }
        
        previous_snapshot = {
            "overall_health_score": 88,
            "code_quality_score": 85,
            "security_score": 96,
            "test_score": 78
        }
        
        trends = analyzer.compare_snapshots(current_snapshot, previous_snapshot)
        
        assert trends["overall_health_score"] == "improving"  # +4
        assert trends["code_quality_score"] == "improving"    # +3
        assert trends["security_score"] == "stable"           # 0
        assert trends["test_score"] == "improving"            # +4
    
    def test_compare_snapshots_missing_metrics(self):
        """Test snapshot comparison handles missing metrics gracefully."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        current_snapshot = {
            "overall_health_score": 92,
            "code_quality_score": 88
        }
        
        previous_snapshot = {
            "overall_health_score": 88
        }
        
        trends = analyzer.compare_snapshots(current_snapshot, previous_snapshot)
        
        assert trends["overall_health_score"] == "improving"
        assert trends["code_quality_score"] == "N/A"  # Not in previous
    
    def test_compare_snapshots_no_previous(self):
        """Test snapshot comparison when no previous snapshot exists."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        current_snapshot = {
            "overall_health_score": 92,
            "code_quality_score": 88
        }
        
        trends = analyzer.compare_snapshots(current_snapshot, None)
        
        assert all(trend == "N/A" for trend in trends.values())
    
    def test_edge_case_exact_threshold_boundaries(self):
        """Test exact threshold boundaries for trend classification."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        # Delta = +2.0 exactly (should be stable)
        assert analyzer.analyze_trend(82.0, 80.0) == "stable"
        
        # Delta = +2.1 (should be improving)
        assert analyzer.analyze_trend(82.1, 80.0) == "improving"
        
        # Delta = -2.0 exactly (should be stable)
        assert analyzer.analyze_trend(78.0, 80.0) == "stable"
        
        # Delta = -2.1 (should be declining)
        assert analyzer.analyze_trend(77.9, 80.0) == "declining"
    
    def test_trend_with_zero_values(self):
        """Test trend analysis with zero values."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        # From 0 to positive
        assert analyzer.analyze_trend(5.0, 0.0) == "improving"
        
        # From positive to 0
        assert analyzer.analyze_trend(0.0, 5.0) == "declining"
        
        # Both zero
        assert analyzer.analyze_trend(0.0, 0.0) == "stable"
    
    def test_trend_with_negative_values(self):
        """Test trend analysis with negative values."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        # From -10 to -5 (improvement)
        assert analyzer.analyze_trend(-5.0, -10.0) == "improving"
        
        # From -5 to -10 (decline)
        assert analyzer.analyze_trend(-10.0, -5.0) == "declining"
    
    def test_calculate_delta(self):
        """Test delta calculation between two values."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        # Positive delta
        delta1 = analyzer.calculate_delta(85.0, 80.0)
        assert delta1 == 5.0
        
        # Negative delta
        delta2 = analyzer.calculate_delta(75.0, 80.0)
        assert delta2 == -5.0
        
        # Zero delta
        delta3 = analyzer.calculate_delta(80.0, 80.0)
        assert delta3 == 0.0
    
    def test_calculate_delta_no_previous(self):
        """Test delta calculation when no previous value exists."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        delta = analyzer.calculate_delta(85.0, None)
        assert delta is None
    
    def test_get_trend_indicator_symbols(self):
        """Test getting visual trend indicator symbols."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        assert analyzer.get_trend_indicator("improving") == "↑"
        assert analyzer.get_trend_indicator("stable") == "→"
        assert analyzer.get_trend_indicator("declining") == "↓"
        assert analyzer.get_trend_indicator("N/A") == "—"
        assert analyzer.get_trend_indicator("unknown") == "—"  # Fallback
    
    def test_batch_analyze_multiple_metrics(self):
        """Test analyzing trends for multiple metrics at once."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        metrics = {
            "health": (92, 88),      # +4, improving
            "quality": (85, 84),     # +1, stable
            "security": (96, 96),    # 0, stable
            "tests": (80, 85),       # -5, declining
            "docs": (75, None)       # None, N/A
        }
        
        trends = analyzer.batch_analyze(metrics)
        
        assert trends["health"] == "improving"
        assert trends["quality"] == "stable"
        assert trends["security"] == "stable"
        assert trends["tests"] == "declining"
        assert trends["docs"] == "N/A"
    
    def test_confidence_score_for_trends(self):
        """Test confidence scoring for trend accuracy."""
        from src.dashboard.data.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        
        # High confidence (large delta)
        confidence1 = analyzer.calculate_confidence(10.0)
        assert confidence1 >= 0.9
        
        # Medium confidence (moderate delta)
        confidence2 = analyzer.calculate_confidence(3.0)
        assert 0.6 <= confidence2 < 0.9
        
        # Low confidence (small delta near threshold)
        confidence3 = analyzer.calculate_confidence(2.1)
        assert 0.3 <= confidence3 < 0.6
        
        # Very low confidence (at threshold)
        confidence4 = analyzer.calculate_confidence(2.0)
        assert confidence4 < 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
