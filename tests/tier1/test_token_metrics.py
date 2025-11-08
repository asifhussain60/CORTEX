"""
Tests for Token Metrics Collector
Phase 1.5: Token Optimization System
"""

import pytest
import os
import json
from datetime import datetime
from unittest.mock import Mock, MagicMock
from pathlib import Path
from src.tier1.token_metrics import TokenMetricsCollector, TokenMetricsFormatter


class TestTokenMetricsCollector:
    """Test Token Metrics Collector functionality."""
    
    @pytest.fixture
    def mock_working_memory(self):
        """Create mock working memory."""
        mock = Mock()
        mock.db_path = Path("test.db")
        mock.get_recent_conversations = Mock(return_value=[])
        return mock
    
    @pytest.fixture
    def collector(self, mock_working_memory):
        """Create collector instance."""
        return TokenMetricsCollector(mock_working_memory)
    
    # ========== Basic Functionality Tests ==========
    
    def test_collector_initialization(self, collector):
        """Test collector initializes correctly."""
        assert collector.COST_PER_TOKEN == 0.000003
        assert collector._session_tokens_original == 0
        assert collector._session_tokens_optimized == 0
        assert collector._request_count == 0
        assert len(collector._requests) == 0
    
    def test_record_request_basic(self, collector):
        """Test recording a basic request."""
        collector.record_request(
            original_tokens=25_000,
            optimized_tokens=10_000,
            optimization_method="ml_compression",
            quality_score=0.95
        )
        
        assert collector._session_tokens_original == 25_000
        assert collector._session_tokens_optimized == 10_000
        assert collector._request_count == 1
        assert len(collector._requests) == 1
        
        request = collector._requests[0]
        assert request["original_tokens"] == 25_000
        assert request["optimized_tokens"] == 10_000
        assert request["tokens_saved"] == 15_000
        assert request["reduction_percentage"] == 60.0
        assert request["optimization_method"] == "ml_compression"
        assert request["quality_score"] == 0.95
    
    def test_record_multiple_requests(self, collector):
        """Test recording multiple requests."""
        for i in range(5):
            collector.record_request(
                original_tokens=20_000 + (i * 1_000),
                optimized_tokens=8_000 + (i * 400),
                optimization_method=f"method_{i}"
            )
        
        assert collector._request_count == 5
        assert len(collector._requests) == 5
        assert collector._session_tokens_original > 100_000
        assert collector._session_tokens_optimized > 40_000
    
    def test_record_request_invalidates_cache(self, collector):
        """Test that recording request invalidates metrics cache."""
        # Get metrics (caches result)
        collector.get_current_metrics()
        assert collector._metrics_cache is not None
        
        # Record request
        collector.record_request(1000, 500)
        
        # Cache should be invalidated
        assert collector._metrics_cache is None
    
    # ========== Metrics Calculation Tests ==========
    
    def test_get_current_metrics_structure(self, collector):
        """Test current metrics structure."""
        metrics = collector.get_current_metrics()
        
        # Session tracking
        assert "session_id" in metrics
        assert "session_start" in metrics
        assert "session_duration_seconds" in metrics
        assert "session_duration_minutes" in metrics
        
        # Token metrics
        assert "session_tokens_original" in metrics
        assert "session_tokens_optimized" in metrics
        assert "session_tokens_saved" in metrics
        assert "cache_tokens" in metrics
        
        # Cost metrics
        assert "session_cost_original_usd" in metrics
        assert "session_cost_optimized_usd" in metrics
        assert "session_cost_saved_usd" in metrics
        
        # Optimization metrics
        assert "optimization_percentage" in metrics
        assert "request_count" in metrics
        assert "average_tokens_per_request" in metrics
        
        # Memory metrics
        assert "conversation_count" in metrics
        assert "pattern_count" in metrics
        assert "tier1_bytes" in metrics
        assert "tier1_mb" in metrics
    
    def test_optimization_percentage_calculation(self, collector):
        """Test optimization percentage calculation."""
        collector.record_request(10_000, 4_000)  # 60% reduction
        
        metrics = collector.get_current_metrics()
        assert metrics["optimization_percentage"] == 60.0
    
    def test_cost_calculation(self, collector):
        """Test cost calculation."""
        collector.record_request(10_000, 4_000)
        
        metrics = collector.get_current_metrics()
        
        # 10,000 * 0.000003 = $0.03
        assert abs(metrics["session_cost_original_usd"] - 0.03) < 0.001
        
        # 4,000 * 0.000003 = $0.012
        assert abs(metrics["session_cost_optimized_usd"] - 0.012) < 0.001
        
        # Saved: $0.018
        assert abs(metrics["session_cost_saved_usd"] - 0.018) < 0.001
    
    def test_average_tokens_per_request(self, collector):
        """Test average tokens per request calculation."""
        collector.record_request(10_000, 4_000)
        collector.record_request(20_000, 8_000)
        collector.record_request(30_000, 12_000)
        
        metrics = collector.get_current_metrics()
        
        # Total optimized: 24,000 / 3 requests = 8,000
        assert metrics["average_tokens_per_request"] == 8_000
    
    def test_zero_requests_metrics(self, collector):
        """Test metrics with zero requests."""
        metrics = collector.get_current_metrics()
        
        assert metrics["request_count"] == 0
        assert metrics["optimization_percentage"] == 0.0
        assert metrics["average_tokens_per_request"] == 0
    
    def test_cache_utilization_calculation(self, collector, mock_working_memory):
        """Test cache utilization calculation."""
        # Mock conversations with known token count
        mock_working_memory.get_recent_conversations.return_value = [
            {
                "messages": [
                    {"content": "A" * 40_000}  # 10,000 tokens
                ]
            }
        ]
        
        metrics = collector.get_current_metrics(force_refresh=True)
        
        # 10,000 / 40,000 = 25%
        assert abs(metrics["cache_utilization_percentage"] - 25.0) < 1.0
    
    def test_cache_status_determination(self, collector, mock_working_memory):
        """Test cache status determination."""
        # OK status (< 30k tokens)
        mock_working_memory.get_recent_conversations.return_value = [
            {"messages": [{"content": "A" * 40_000}]}  # ~10k tokens
        ]
        metrics = collector.get_current_metrics(force_refresh=True)
        assert metrics["cache_status"] == "OK"
        
        # ELEVATED status (30k-40k)
        mock_working_memory.get_recent_conversations.return_value = [
            {"messages": [{"content": "A" * 120_000}]}  # ~30k tokens
        ]
        metrics = collector.get_current_metrics(force_refresh=True)
        assert metrics["cache_status"] == "ELEVATED"
    
    def test_metrics_caching(self, collector):
        """Test metrics caching behavior."""
        # First call
        metrics1 = collector.get_current_metrics()
        cache_time1 = collector._cache_timestamp
        
        # Second call within TTL (should use cache)
        metrics2 = collector.get_current_metrics()
        cache_time2 = collector._cache_timestamp
        
        assert metrics1 == metrics2
        assert cache_time1 == cache_time2
    
    def test_force_refresh_bypasses_cache(self, collector):
        """Test force refresh bypasses cache."""
        # First call (caches)
        metrics1 = collector.get_current_metrics()
        cache_time1 = collector._cache_timestamp
        
        # Force refresh
        metrics2 = collector.get_current_metrics(force_refresh=True)
        cache_time2 = collector._cache_timestamp
        
        assert cache_time2 > cache_time1
    
    # ========== Session Summary Tests ==========
    
    def test_get_session_summary(self, collector):
        """Test session summary generation."""
        collector.record_request(10_000, 4_000, quality_score=0.95)
        collector.record_request(20_000, 8_000, quality_score=0.92)
        
        summary = collector.get_session_summary()
        
        assert "session_id" in summary
        assert "session_duration" in summary
        assert "total_requests" in summary
        assert "tokens" in summary
        assert "cost" in summary
        assert "optimization" in summary
        assert "memory" in summary
    
    def test_session_summary_best_worst_reduction(self, collector):
        """Test best/worst reduction tracking in summary."""
        collector.record_request(10_000, 4_000)  # 60% reduction
        collector.record_request(20_000, 16_000)  # 20% reduction
        collector.record_request(15_000, 3_000)  # 80% reduction
        
        summary = collector.get_session_summary()
        
        best = summary["optimization"]["best_reduction"]
        worst = summary["optimization"]["worst_reduction"]
        
        assert best["reduction_percentage"] == 80.0
        assert worst["reduction_percentage"] == 20.0
    
    def test_session_summary_average_quality(self, collector):
        """Test average quality score in summary."""
        collector.record_request(10_000, 4_000, quality_score=0.95)
        collector.record_request(20_000, 8_000, quality_score=0.90)
        collector.record_request(15_000, 6_000, quality_score=0.85)
        
        summary = collector.get_session_summary()
        
        avg_quality = summary["optimization"]["average_quality_score"]
        assert abs(avg_quality - 0.90) < 0.01  # (0.95 + 0.90 + 0.85) / 3
    
    # ========== Request History Tests ==========
    
    def test_get_request_history_all(self, collector):
        """Test getting full request history."""
        for i in range(5):
            collector.record_request(10_000, 5_000)
        
        history = collector.get_request_history()
        
        assert len(history) == 5
        assert all("timestamp" in r for r in history)
        assert all("request_number" in r for r in history)
    
    def test_get_request_history_limited(self, collector):
        """Test getting limited request history."""
        for i in range(10):
            collector.record_request(10_000, 5_000)
        
        history = collector.get_request_history(limit=3)
        
        assert len(history) == 3
        # Should return most recent
        assert history[-1]["request_number"] == 10
    
    # ========== Export/Import Tests ==========
    
    def test_export_session_data(self, collector, tmp_path):
        """Test exporting session data to JSON."""
        collector.record_request(10_000, 4_000, quality_score=0.95)
        
        output_path = tmp_path / "test_export.json"
        result_path = collector.export_session_data(output_path)
        
        assert result_path.exists()
        
        with open(result_path) as f:
            data = json.load(f)
        
        assert "session_summary" in data
        assert "current_metrics" in data
        assert "request_history" in data
        assert len(data["request_history"]) == 1
    
    def test_export_default_path(self, collector):
        """Test export with default path."""
        collector.record_request(10_000, 4_000)
        
        result_path = collector.export_session_data()
        
        assert result_path.exists()
        assert "cortex-metrics-" in str(result_path)
        assert result_path.suffix == ".json"
        
        # Cleanup
        result_path.unlink()
    
    # ========== Session Management Tests ==========
    
    def test_reset_session(self, collector):
        """Test resetting session."""
        # Record some data
        collector.record_request(10_000, 4_000)
        collector.record_request(20_000, 8_000)
        
        old_session_id = collector._session_id
        
        # Reset
        collector.reset_session()
        
        assert collector._session_id != old_session_id
        assert collector._request_count == 0
        assert len(collector._requests) == 0
        assert collector._session_tokens_original == 0
        assert collector._session_tokens_optimized == 0


class TestTokenMetricsFormatter:
    """Test Token Metrics Formatter functionality."""
    
    def test_format_tokens(self):
        """Test token formatting."""
        assert TokenMetricsFormatter.format_tokens(1_000) == "1,000"
        assert TokenMetricsFormatter.format_tokens(25_000) == "25,000"
        assert TokenMetricsFormatter.format_tokens(1_234_567) == "1,234,567"
    
    def test_format_cost(self):
        """Test cost formatting."""
        assert TokenMetricsFormatter.format_cost(0.0123) == "$0.0123"
        assert TokenMetricsFormatter.format_cost(1.50) == "$1.5000"
        assert TokenMetricsFormatter.format_cost(0.0001) == "$0.0001"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert TokenMetricsFormatter.format_percentage(60.5) == "60.5%"
        assert TokenMetricsFormatter.format_percentage(99.99) == "100.0%"
        assert TokenMetricsFormatter.format_percentage(0.1) == "0.1%"
    
    def test_format_filesize(self):
        """Test file size formatting."""
        assert TokenMetricsFormatter.format_filesize(500) == "500.0 B"
        assert TokenMetricsFormatter.format_filesize(1024) == "1.0 KB"
        assert TokenMetricsFormatter.format_filesize(1024 * 1024) == "1.0 MB"
        assert TokenMetricsFormatter.format_filesize(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_format_duration(self):
        """Test duration formatting."""
        assert TokenMetricsFormatter.format_duration(30) == "30s"
        assert TokenMetricsFormatter.format_duration(90) == "1.5m"
        assert TokenMetricsFormatter.format_duration(3600) == "1.0h"
        assert TokenMetricsFormatter.format_duration(7200) == "2.0h"
    
    def test_format_metrics_summary(self, monkeypatch):
        """Test metrics summary formatting."""
        metrics = {
            "session_id": "test-session",
            "session_duration_seconds": 300,
            "session_tokens_original": 100_000,
            "session_tokens_optimized": 40_000,
            "session_tokens_saved": 60_000,
            "optimization_percentage": 60.0,
            "session_cost_original_usd": 0.30,
            "session_cost_optimized_usd": 0.12,
            "session_cost_saved_usd": 0.18,
            "conversation_count": 15,
            "pattern_count": 250,
            "tier1_bytes": 1024 * 1024 * 5,  # 5 MB
            "tier2_bytes": 1024 * 1024 * 3,  # 3 MB
            "cache_status": "OK",
            "cache_tokens": 25_000
        }
        
        summary = TokenMetricsFormatter.format_metrics_summary(metrics)
        
        assert "CORTEX Token Metrics" in summary
        assert "test-session" in summary
        assert "100,000" in summary  # Original tokens
        assert "40,000" in summary  # Optimized tokens
        assert "60.0%" in summary  # Reduction
        assert "$0.3000" in summary  # Original cost
        assert "OK" in summary  # Cache status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
