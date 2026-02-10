"""
Tests for Hot Path Analyzer

Validates identification of frequently executed code paths from test execution data.

Author: CORTEX Architect  
Phase: Phase 66 S4
"""

import pytest
from typing import Dict, Any, List


class TestHotPathAnalyzer:
    """Test suite for hot path analysis"""
    
    def test_identify_frequently_executed_paths(self):
        """Test identifying frequently executed code paths"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {"file": "cortex/orchestrators/master.py", "function": "process_request", "call_count": 150},
            {"file": "cortex/models/phase.py", "function": "validate", "call_count": 200},
            {"file": "cortex/utils/helper.py", "function": "format_output", "call_count": 50}
        ]
        
        analyzer = HotPathAnalyzer()
        hot_paths = analyzer.identify_frequently_executed_paths(execution_data, threshold=100)
        
        assert len(hot_paths) == 2  # Only process_request and validate
        assert all(p["call_count"] >= 100 for p in hot_paths)
        assert any(p["function"] == "process_request" for p in hot_paths)
    
    def test_rank_by_execution_frequency(self):
        """Test ranking paths by execution frequency"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {"file": "a.py", "function": "func_a", "call_count": 10},
            {"file": "b.py", "function": "func_b", "call_count": 100},
            {"file": "c.py", "function": "func_c", "call_count": 50}
        ]
        
        analyzer = HotPathAnalyzer()
        ranked = analyzer.rank_by_execution_frequency(execution_data)
        
        assert len(ranked) == 3
        assert ranked[0]["function"] == "func_b"  # Highest count first
        assert ranked[0]["rank"] == 1
        assert ranked[1]["function"] == "func_c"
        assert ranked[2]["function"] == "func_a"
    
    def test_identify_performance_bottlenecks(self):
        """Test identifying performance bottlenecks from duration data"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {"file": "a.py", "function": "slow_func", "call_count": 10, "total_duration": 15.0},
            {"file": "b.py", "function": "fast_func", "call_count": 100, "total_duration": 1.0},
            {"file": "c.py", "function": "medium_func", "call_count": 50, "total_duration": 5.0}
        ]
        
        analyzer = HotPathAnalyzer()
        bottlenecks = analyzer.identify_performance_bottlenecks(execution_data, threshold_ms=1000)
        
        assert len(bottlenecks) >= 1
        # slow_func: 15s total, avg 1.5s per call = bottleneck
        assert any(b["function"] == "slow_func" for b in bottlenecks)
    
    def test_calculate_hot_path_score(self):
        """Test calculating hot path score (frequency + duration)"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        path_data = {
            "call_count": 100,
            "total_duration": 10.0,
            "file": "cortex/core.py"
        }
        
        analyzer = HotPathAnalyzer()
        score = analyzer.calculate_hot_path_score(path_data)
        
        assert score > 0
        assert isinstance(score, float)
        # Score should combine frequency and duration
    
    def test_aggregate_by_module(self):
        """Test aggregating hot paths by module"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {"file": "cortex/orchestrators/master.py", "function": "func1", "call_count": 100},
            {"file": "cortex/orchestrators/intent.py", "function": "func2", "call_count": 50},
            {"file": "cortex/models/phase.py", "function": "func3", "call_count": 75}
        ]
        
        analyzer = HotPathAnalyzer()
        by_module = analyzer.aggregate_by_module(execution_data)
        
        assert "cortex/orchestrators" in by_module
        assert "cortex/models" in by_module
        assert by_module["cortex/orchestrators"]["total_calls"] == 150  # 100 + 50
    
    def test_identify_critical_paths(self):
        """Test identifying critical paths (hot + important)"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {"file": "cortex/security/auth.py", "function": "authenticate", "call_count": 200},
            {"file": "cortex/utils/helper.py", "function": "log", "call_count": 500},
            {"file": "cortex/core/processor.py", "function": "process", "call_count": 150}
        ]
        
        analyzer = HotPathAnalyzer()
        critical = analyzer.identify_critical_paths(execution_data, min_calls=100)
        
        # All three meet frequency threshold, but security + core should be prioritized
        assert len(critical) >= 2
        assert any("security" in c["file"] or "core" in c["file"] for c in critical)
    
    def test_detect_call_patterns(self):
        """Test detecting common call patterns"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        call_sequences = [
            ["func_a", "func_b", "func_c"],
            ["func_a", "func_b", "func_c"],
            ["func_a", "func_b", "func_d"],
            ["func_a", "func_b", "func_c"]
        ]
        
        analyzer = HotPathAnalyzer()
        patterns = analyzer.detect_call_patterns(call_sequences)
        
        assert len(patterns) >= 1
        # Should detect ["func_a", "func_b", "func_c"] as common pattern (3 occurrences)
        top_pattern = patterns[0]
        assert top_pattern["frequency"] == 3
    
    def test_build_execution_heatmap(self):
        """Test building execution heatmap for visualization"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {"file": "a.py", "line": 10, "execution_count": 100},
            {"file": "a.py", "line": 11, "execution_count": 95},
            {"file": "a.py", "line": 15, "execution_count": 50},
            {"file": "b.py", "line": 20, "execution_count": 200}
        ]
        
        analyzer = HotPathAnalyzer()
        heatmap = analyzer.build_execution_heatmap(execution_data)
        
        assert "a.py" in heatmap
        assert "b.py" in heatmap
        assert heatmap["a.py"][10] == 100
        assert heatmap["b.py"][20] == 200
    
    def test_identify_optimization_candidates(self):
        """Test identifying code that would benefit from optimization"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {
                "file": "cortex/processor.py",
                "function": "heavy_computation",
                "call_count": 1000,
                "avg_duration": 0.5,
                "complexity": 15  # McCabe complexity
            },
            {
                "file": "cortex/helper.py",
                "function": "simple_func",
                "call_count": 10,
                "avg_duration": 0.001,
                "complexity": 2
            }
        ]
        
        analyzer = HotPathAnalyzer()
        candidates = analyzer.identify_optimization_candidates(execution_data)
        
        assert len(candidates) >= 1
        # heavy_computation: high frequency + high duration + high complexity
        assert any(c["function"] == "heavy_computation" for c in candidates)


class TestHotPathAnalyzerIntegration:
    """Integration tests for hot path analyzer"""
    
    def test_end_to_end_hot_path_analysis(self):
        """Test complete hot path analysis workflow"""
        from cortex_lens.runtime_correlation.hot_path_analyzer import HotPathAnalyzer
        
        execution_data = [
            {"file": "cortex/orchestrators/master.py", "function": "process", "call_count": 500, "total_duration": 10.0},
            {"file": "cortex/models/phase.py", "function": "validate", "call_count": 300, "total_duration": 3.0},
            {"file": "cortex/utils/logger.py", "function": "log", "call_count": 1000, "total_duration": 1.0},
            {"file": "cortex/security/auth.py", "function": "check", "call_count": 400, "total_duration": 8.0}
        ]
        
        analyzer = HotPathAnalyzer()
        
        # Identify hot paths
        hot_paths = analyzer.identify_frequently_executed_paths(execution_data, threshold=250)
        assert len(hot_paths) == 4  # All meet threshold
        
        # Rank by frequency
        ranked = analyzer.rank_by_execution_frequency(execution_data)
        assert ranked[0]["function"] == "log"  # Highest count
        
        # Find bottlenecks (adjust threshold for test data)
        bottlenecks = analyzer.identify_performance_bottlenecks(execution_data, threshold_ms=15)
        assert len(bottlenecks) >= 2  # process and check both have 20ms avg
        
        # Critical paths
        critical = analyzer.identify_critical_paths(execution_data, min_calls=300)
        assert any("security" in c["file"] for c in critical)
