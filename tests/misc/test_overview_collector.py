"""
Tests for Overview Collector - Dashboard Overview Tab

Tests data aggregation, orchestration, and JSON generation.
Following TDD: RED → GREEN → REFACTOR cycle.

Author: Asif Hussain
Created: 2025-12-06
Phase: RED (Write Failing Tests)
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestOverviewCollector:
    """Test suite for OverviewCollector class."""
    
    def test_overview_collector_initialization(self):
        """Test OverviewCollector can be instantiated."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        collector = OverviewCollector("/fake/path")
        assert collector is not None
        assert collector.repo_path == "/fake/path"
    
    @patch('src.dashboard.data.overview_collector.Path')
    def test_collect_aggregates_all_sources(self, mock_path):
        """Test collect() aggregates data from all sources."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        # Mock file existence and content
        mock_path.return_value.exists.return_value = True
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "overall_health_score": 92,
                "metrics": {"code_quality_score": 88}
            })
            
            collector = OverviewCollector("/fake/path")
            result = collector.collect()
            
            assert result is not None
            assert "project_name" in result
            assert "overall_health" in result
    
    def test_load_health_data(self):
        """Test loading health-data.json."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        collector = OverviewCollector("/fake/path")
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "overall_health_score": 92,
                "metrics": {"code_quality_score": 88}
            })
            
            data = collector._load_health_data()
            
            assert data["overall_health_score"] == 92
    
    def test_load_security_data(self):
        """Test loading security.json."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        collector = OverviewCollector("/fake/path")
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "overall_score": 96,
                "vulnerabilities": {"critical": 0}
            })
            
            data = collector._load_security_data()
            
            assert data["overall_score"] == 96
    
    def test_load_tech_stack_data(self):
        """Test loading tech-stack.json."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        collector = OverviewCollector("/fake/path")
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "languages": [{"name": "Python", "percentage": 75}]
            })
            
            data = collector._load_tech_stack_data()
            
            assert len(data["languages"]) == 1
    
    def test_missing_file_returns_empty_dict(self):
        """Test missing files return empty dict instead of crashing."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        collector = OverviewCollector("/fake/path")
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            data = collector._load_health_data()
            assert data == {}
    
    def test_schema_compliance(self):
        """Test output conforms to overview schema."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "overall_health_score": 92
            })
            
            collector = OverviewCollector("/fake/path")
            result = collector.collect()
            
            # Check required top-level fields
            assert "project_name" in result
            assert "overall_health" in result
            assert "key_metrics" in result
            assert "health_categories" in result
            assert "composition" in result
    
    def test_health_score_calculator_integration(self):
        """Test integration with HealthScoreCalculator."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "metrics": {
                    "code_quality_score": 88,
                    "security_score": 96,
                    "test_score": 82,
                    "documentation_score": 75
                }
            })
            
            collector = OverviewCollector("/fake/path")
            result = collector.collect()
            
            # Should calculate overall health from category scores
            assert "overall_health" in result
            assert "score" in result["overall_health"]
    
    def test_trend_analyzer_integration(self):
        """Test integration with TrendAnalyzer."""
        from src.dashboard.data.overview_collector import OverviewCollector
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "overall_health_score": 92
            })
            
            collector = OverviewCollector("/fake/path")
            
            # Mock previous snapshot
            collector._load_previous_snapshot = Mock(return_value={
                "overall_health_score": 88
            })
            
            result = collector.collect()
            
            # Should include trend information
            assert "overall_health" in result
            assert "trend" in result["overall_health"]
    
    def test_performance_under_one_second(self):
        """Test collection completes in <1 second."""
        import time
        from src.dashboard.data.overview_collector import OverviewCollector
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({})
            
            collector = OverviewCollector("/fake/path")
            
            start = time.time()
            result = collector.collect()
            duration = time.time() - start
            
            assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
