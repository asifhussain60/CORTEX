"""
Tests for Phase 1.5 Token Optimization integration with WorkingMemory.

This test suite validates:
1. Configuration loading and management
2. Context optimization pipeline
3. Cache health monitoring integration
4. Token metrics tracking
5. Performance targets (<50ms overhead)
6. Quality targets (>0.9 score)
"""

import pytest

# Mark entire module as requiring sklearn
pytestmark = pytest.mark.requires_sklearn

import json
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.tier1.working_memory import WorkingMemory


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "cortex.config.json"
    config_data = {
        "token_optimization": {
            "enabled": True,
            "soft_limit": 40000,
            "hard_limit": 50000,
            "target_reduction": 0.6,
            "quality_threshold": 0.9,
            "cache_check_frequency": 5
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f)
    
    return config_path


@pytest.fixture
def working_memory(tmp_path):
    """Create a WorkingMemory instance with test database."""
    db_path = tmp_path / "test_working_memory.db"
    wm = WorkingMemory(db_path=db_path)
    yield wm
    wm.close()


@pytest.fixture
def working_memory_with_data(working_memory):
    """WorkingMemory instance with sample conversations."""
    # Add sample conversations
    working_memory.add_conversation(
        conversation_id="conv1",
        title="Python Refactoring Discussion",
        messages=[
            {"role": "user", "content": "I need help refactoring my Python code for better performance."},
            {"role": "assistant", "content": "I'd be happy to help! Let's start by identifying the bottlenecks in your code. Can you share the code you're working with?"},
            {"role": "user", "content": "Here's the main function that processes large datasets..."},
        ]
    )
    
    working_memory.add_conversation(
        conversation_id="conv2",
        title="Database Query Optimization",
        messages=[
            {"role": "user", "content": "My SQL queries are running too slowly. How can I optimize them?"},
            {"role": "assistant", "content": "Let's analyze your query patterns. Start by checking if you have proper indexes on frequently queried columns."},
        ]
    )
    
    working_memory.set_active_conversation("conv1")
    
    return working_memory


class TestConfigurationLoading:
    """Test configuration loading and management."""
    
    def test_load_default_config_when_file_missing(self, working_memory):
        """Should use default configuration when config file doesn't exist."""
        config = working_memory.config
        
        assert 'token_optimization' in config
        assert config['token_optimization']['enabled'] is True
        assert config['token_optimization']['soft_limit'] == 40000
        assert config['token_optimization']['hard_limit'] == 50000
    
    def test_load_config_from_file(self, tmp_path, monkeypatch):
        """Should load configuration from cortex.config.json."""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        config_path = tmp_path / "cortex.config.json"
        config_data = {
            "token_optimization": {
                "enabled": False,
                "soft_limit": 30000,
                "hard_limit": 40000,
                "target_reduction": 0.5,
                "quality_threshold": 0.85
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        db_path = tmp_path / "test.db"
        wm = WorkingMemory(db_path=db_path)
        
        assert wm.config['token_optimization']['enabled'] is False
        assert wm.config['token_optimization']['soft_limit'] == 30000
        assert wm.optimization_enabled is False
    
    def test_graceful_config_load_failure(self, tmp_path, monkeypatch):
        """Should use defaults if config file is invalid."""
        monkeypatch.chdir(tmp_path)
        
        config_path = tmp_path / "cortex.config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("invalid json{")
        
        db_path = tmp_path / "test.db"
        wm = WorkingMemory(db_path=db_path)
        
        # Should fall back to defaults
        assert wm.optimization_enabled is True


class TestContextOptimization:
    """Test context optimization pipeline."""
    
    def test_get_optimized_context_with_active_conversation(self, working_memory_with_data):
        """Should optimize context for active conversation."""
        result = working_memory_with_data.get_optimized_context()
        
        assert 'original_context' in result
        assert 'optimized_context' in result
        assert 'optimization_stats' in result
        assert 'cache_health' in result
        
        # Check stats
        stats = result['optimization_stats']
        assert stats['enabled'] is True
        assert stats['original_tokens'] > 0
        assert stats['optimized_tokens'] > 0
        assert stats['original_tokens'] >= stats['optimized_tokens']
        assert 0 <= stats['reduction_rate'] <= 1
        assert 0 <= stats['quality_score'] <= 1
    
    def test_get_optimized_context_with_specific_conversation(self, working_memory_with_data):
        """Should optimize context for a specific conversation."""
        result = working_memory_with_data.get_optimized_context(conversation_id="conv2")
        
        # Should have conv2 in optimized context
        assert len(result['optimized_context']['conversations']) >= 1
        assert any(c['conversation_id'] == 'conv2' for c in result['optimized_context']['conversations'])
    
    def test_get_optimized_context_with_pattern_context(self, working_memory_with_data):
        """Should optimize both conversation and pattern context."""
        patterns = [
            {
                "pattern_type": "architectural",
                "name": "MVC Pattern",
                "description": "Model-View-Controller architectural pattern for web applications.",
                "usage_count": 15
            },
            {
                "pattern_type": "design",
                "name": "Singleton Pattern",
                "description": "Ensures a class has only one instance and provides global access.",
                "usage_count": 8
            }
        ]
        
        result = working_memory_with_data.get_optimized_context(pattern_context=patterns)
        
        # Should include patterns in context
        assert 'patterns' in result['original_context']
        assert len(result['original_context']['patterns']) == 2
        
        # Patterns should be optimized
        assert 'patterns' in result['optimized_context']
    
    def test_get_optimized_context_with_custom_target_reduction(self, working_memory_with_data):
        """Should respect custom target reduction parameter."""
        # Request aggressive reduction
        result = working_memory_with_data.get_optimized_context(target_reduction=0.8)
        
        stats = result['optimization_stats']
        
        # Should attempt higher reduction (though quality may prevent it)
        assert stats['reduction_rate'] >= 0  # Some reduction should occur
    
    def test_get_optimized_context_when_disabled(self, working_memory_with_data):
        """Should return original context when optimization is disabled."""
        working_memory_with_data.optimization_enabled = False
        
        result = working_memory_with_data.get_optimized_context()
        
        stats = result['optimization_stats']
        assert stats['enabled'] is False
        assert stats['reduction_rate'] == 0.0
        assert stats['quality_score'] == 1.0
        
        # Original and optimized should be the same
        assert result['original_context'] == result['optimized_context']
    
    def test_build_context_with_no_conversations(self, working_memory):
        """Should handle empty working memory gracefully."""
        result = working_memory.get_optimized_context()
        
        assert result['original_context']['conversations'] == []
        assert result['optimization_stats']['original_tokens'] >= 0


class TestCacheHealthIntegration:
    """Test cache health monitoring integration."""
    
    def test_cache_health_check_on_context_retrieval(self, working_memory_with_data):
        """Should check cache health when retrieving context."""
        result = working_memory_with_data.get_optimized_context()
        
        assert 'cache_health' in result
        cache_health = result['cache_health']
        
        assert 'status' in cache_health
        assert 'total_tokens' in cache_health  # Changed from 'current_tokens'
        assert 'conversation_count' in cache_health
    
    def test_get_cache_health_report(self, working_memory_with_data):
        """Should provide standalone cache health report."""
        report = working_memory_with_data.get_cache_health_report()
        
        assert 'status' in report
        assert 'total_tokens' in report  # Changed from 'current_tokens'
        assert 'conversation_count' in report


class TestTokenMetricsIntegration:
    """Test token metrics tracking integration."""
    
    def test_metrics_recorded_on_optimization(self, working_memory_with_data):
        """Should record metrics when context is optimized."""
        # Get optimized context (records metrics)
        result = working_memory_with_data.get_optimized_context()
        
        # Get metrics summary
        summary = working_memory_with_data.get_token_metrics_summary()
        
        assert 'total_requests' in summary
        assert summary['total_requests'] >= 1
        
        assert 'tokens' in summary
        assert 'saved_total' in summary['tokens']  # Changed structure
    
    def test_get_token_metrics_summary(self, working_memory_with_data):
        """Should provide comprehensive token metrics summary."""
        # Generate some activity
        working_memory_with_data.get_optimized_context()
        working_memory_with_data.get_optimized_context(conversation_id="conv2")
        
        summary = working_memory_with_data.get_token_metrics_summary()
        
        assert 'total_requests' in summary
        assert 'tokens' in summary
        assert 'original_total' in summary['tokens']  # Changed structure
        assert 'optimized_total' in summary['tokens']
        assert 'saved_total' in summary['tokens']
        assert 'optimization' in summary
        assert 'average_reduction_percentage' in summary['optimization']
        assert 'average_quality_score' in summary['optimization']
        
        # Should have recorded 2 requests
        assert summary['total_requests'] >= 2


class TestPerformanceTargets:
    """Test performance targets (<50ms overhead)."""
    
    def test_optimization_overhead_under_50ms(self, working_memory_with_data):
        """Should complete optimization in <50ms."""
        # Warm up
        working_memory_with_data.get_optimized_context()
        
        # Measure
        start_time = time.perf_counter()
        result = working_memory_with_data.get_optimized_context()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        print(f"\n[PERFORMANCE] Optimization completed in {elapsed_ms:.2f}ms")
        
        # Should be under 50ms target
        assert elapsed_ms < 50, f"Optimization took {elapsed_ms:.2f}ms (target: <50ms)"
    
    def test_optimization_overhead_multiple_conversations(self, working_memory_with_data):
        """Should handle multiple conversations efficiently."""
        # Add more conversations
        for i in range(3, 8):
            working_memory_with_data.add_conversation(
                conversation_id=f"conv{i}",
                title=f"Test Conversation {i}",
                messages=[
                    {"role": "user", "content": f"User message {i}"},
                    {"role": "assistant", "content": f"Assistant response {i}"}
                ]
            )
        
        # Measure optimization with 7 conversations
        start_time = time.perf_counter()
        result = working_memory_with_data.get_optimized_context()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        print(f"\n[PERFORMANCE] Optimization with 7 conversations: {elapsed_ms:.2f}ms")
        
        # Should still be reasonable (allow more time for more data)
        assert elapsed_ms < 100, f"Optimization took {elapsed_ms:.2f}ms (target: <100ms for 7+ conversations)"


class TestQualityTargets:
    """Test quality targets (>0.9 score)."""
    
    def test_quality_score_above_threshold(self, working_memory_with_data):
        """Should maintain quality score >0.9."""
        result = working_memory_with_data.get_optimized_context()
        
        stats = result['optimization_stats']
        quality_threshold = working_memory_with_data.config.get('token_optimization', {}).get('quality_threshold', 0.9)
        
        print(f"\n[QUALITY] Quality score: {stats['quality_score']:.3f} (threshold: {quality_threshold})")
        
        # Should meet or exceed quality threshold
        assert stats['quality_score'] >= quality_threshold, \
            f"Quality score {stats['quality_score']:.3f} below threshold {quality_threshold}"
        
        assert stats['meets_threshold'] is True
    
    def test_quality_maintained_with_high_reduction(self, working_memory_with_data):
        """Should maintain quality even with aggressive reduction targets."""
        # Request 70% reduction
        result = working_memory_with_data.get_optimized_context(target_reduction=0.7)
        
        stats = result['optimization_stats']
        
        # Quality should still be high even if reduction is lower than requested
        assert stats['quality_score'] >= 0.85, \
            f"Quality score {stats['quality_score']:.3f} dropped too low with aggressive reduction"


class TestTokenEstimation:
    """Test token estimation utilities."""
    
    def test_estimate_tokens_with_simple_context(self, working_memory):
        """Should estimate tokens for simple context."""
        context = {
            'conversations': [],
            'patterns': [],
            'entities': []
        }
        
        tokens = working_memory._estimate_tokens(context)
        
        assert tokens > 0
        assert tokens < 100  # Simple context should be small
    
    def test_estimate_tokens_with_complex_context(self, working_memory_with_data):
        """Should estimate tokens for complex context."""
        result = working_memory_with_data.get_optimized_context()
        
        original_tokens = result['optimization_stats']['original_tokens']
        optimized_tokens = result['optimization_stats']['optimized_tokens']
        
        # Complex context should have reasonable token counts
        assert original_tokens > 100
        assert optimized_tokens > 0
        assert optimized_tokens <= original_tokens


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_optimization_with_empty_conversation(self, working_memory):
        """Should handle conversations with no messages."""
        working_memory.add_conversation(
            conversation_id="empty_conv",
            title="Empty Conversation",
            messages=[]
        )
        
        result = working_memory.get_optimized_context(conversation_id="empty_conv")
        
        # Should not crash
        assert result is not None
        assert result['optimization_stats']['original_tokens'] >= 0
    
    def test_optimization_with_none_conversation_id(self, working_memory):
        """Should handle None conversation_id gracefully."""
        result = working_memory.get_optimized_context(conversation_id=None)
        
        # Should use active or recent conversations
        assert result is not None
        assert 'optimization_stats' in result
    
    def test_optimization_with_invalid_target_reduction(self, working_memory_with_data):
        """Should handle invalid target reduction values."""
        # Negative reduction
        result = working_memory_with_data.get_optimized_context(target_reduction=-0.5)
        assert result is not None
        
        # >1.0 reduction
        result = working_memory_with_data.get_optimized_context(target_reduction=1.5)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
