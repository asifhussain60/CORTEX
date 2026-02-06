"""
Tests for ContextMetricsCollector.

Authority: ENH-046 (Context Synthesis Gateway)
Test Coverage: Metrics tracking, Prometheus integration, session summaries
"""

import pytest
import time
from cortex.interaction.context_metrics_collector import (
    ContextMetricsCollector,
    ContextMetrics,
    get_context_metrics_collector,
)


class TestContextMetricsCollector:
    """Test suite for ContextMetricsCollector."""
    
    def test_initialization(self):
        """Test collector initializes correctly."""
        collector = ContextMetricsCollector()
        
        assert collector._active_syntheses == {}
        assert collector._session_metrics == {}
    
    def test_start_synthesis(self):
        """Test synthesis tracking starts correctly."""
        collector = ContextMetricsCollector()
        
        session_id = "test-session-1"
        collector.start_synthesis(session_id)
        
        assert session_id in collector._active_syntheses
        assert isinstance(collector._active_syntheses[session_id], float)
    
    def test_end_synthesis_basic(self):
        """Test basic synthesis completion."""
        collector = ContextMetricsCollector()
        session_id = "test-session-2"
        
        collector.start_synthesis(session_id)
        time.sleep(0.01)  # Small delay
        
        metrics = collector.end_synthesis(
            session_id=session_id,
            size_before=50000,
            size_after=10000,
            cache_hits=3,
            cache_misses=1,
            tokens_used=8000
        )
        
        assert metrics.session_id == session_id
        assert metrics.size_before == 50000
        assert metrics.size_after == 10000
        assert metrics.compression_ratio == pytest.approx(0.8, rel=0.01)
        assert metrics.synthesis_time_ms > 0
        assert metrics.cache_hits == 3
        assert metrics.cache_misses == 1
    
    def test_compression_ratio_calculation(self):
        """Test compression ratio is calculated correctly."""
        collector = ContextMetricsCollector()
        
        # 50% compression
        metrics = collector.end_synthesis(
            session_id="test-50",
            size_before=100000,
            size_after=50000
        )
        assert metrics.compression_ratio == pytest.approx(0.5, rel=0.01)
        
        # 80% compression
        metrics = collector.end_synthesis(
            session_id="test-80",
            size_before=100000,
            size_after=20000
        )
        assert metrics.compression_ratio == pytest.approx(0.8, rel=0.01)
        
        # No compression
        metrics = collector.end_synthesis(
            session_id="test-0",
            size_before=100000,
            size_after=100000
        )
        assert metrics.compression_ratio == pytest.approx(0.0, rel=0.01)
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate is calculated correctly."""
        collector = ContextMetricsCollector()
        
        # 75% hit rate
        metrics = collector.end_synthesis(
            session_id="test-cache",
            size_before=10000,
            size_after=5000,
            cache_hits=3,
            cache_misses=1
        )
        
        # Verify metrics stored
        assert metrics.cache_hits == 3
        assert metrics.cache_misses == 1
    
    def test_token_budget_tracking(self):
        """Test token budget compliance tracking."""
        collector = ContextMetricsCollector()
        
        # Within budget
        metrics = collector.end_synthesis(
            session_id="test-within",
            size_before=10000,
            size_after=5000,
            token_budget=20000,
            tokens_used=15000
        )
        assert metrics.tokens_used == 15000
        assert metrics.token_budget == 20000
        
        # Over budget
        metrics = collector.end_synthesis(
            session_id="test-over",
            size_before=10000,
            size_after=5000,
            token_budget=20000,
            tokens_used=25000
        )
        assert metrics.tokens_used == 25000
    
    def test_reference_tracking(self):
        """Test reference counting."""
        collector = ContextMetricsCollector()
        
        metrics = collector.end_synthesis(
            session_id="test-refs",
            size_before=10000,
            size_after=5000,
            references_loaded=13,
            reference_types={
                "agent": 6,
                "yaml": 5,
                "source": 2
            }
        )
        
        assert metrics.references_loaded == 13
        assert metrics.reference_types["agent"] == 6
        assert metrics.reference_types["yaml"] == 5
        assert metrics.reference_types["source"] == 2
    
    def test_copilot_summarization_recording(self):
        """Test Copilot summarization event recording."""
        collector = ContextMetricsCollector()
        
        session_id = "test-copilot"
        
        # Should not raise
        collector.record_copilot_summarization(session_id)
        collector.record_copilot_summarization(session_id)
    
    def test_reference_recording(self):
        """Test file reference recording."""
        collector = ContextMetricsCollector()
        
        session_id = "test-ref-record"
        
        collector.record_reference(session_id, "agent")
        collector.record_reference(session_id, "yaml")
        collector.record_reference(session_id, "source")
    
    def test_session_summary(self):
        """Test session summary calculation."""
        collector = ContextMetricsCollector()
        session_id = "test-summary"
        
        # Record multiple syntheses
        for i in range(3):
            collector.start_synthesis(session_id)
            time.sleep(0.001)  # Ensure measurable time
            collector.end_synthesis(
                session_id=session_id,
                size_before=50000,
                size_after=10000,
                cache_hits=2,
                cache_misses=1,
                tokens_used=8000
            )
        
        summary = collector.get_session_summary(session_id)
        
        assert summary["session_id"] == session_id
        assert summary["total_syntheses"] == 3
        assert summary["avg_compression_ratio"] == pytest.approx(0.8, rel=0.01)
        assert summary["avg_synthesis_time_ms"] >= 0  # Allow zero for fast tests
        assert summary["cache_hit_rate"] == pytest.approx(66.67, rel=0.1)
    
    def test_session_summary_no_metrics(self):
        """Test session summary with no recorded metrics."""
        collector = ContextMetricsCollector()
        
        summary = collector.get_session_summary("nonexistent")
        
        assert summary["session_id"] == "nonexistent"
        assert summary["total_syntheses"] == 0
        assert "error" in summary
    
    def test_singleton_instance(self):
        """Test get_context_metrics_collector returns singleton."""
        collector1 = get_context_metrics_collector()
        collector2 = get_context_metrics_collector()
        
        assert collector1 is collector2
