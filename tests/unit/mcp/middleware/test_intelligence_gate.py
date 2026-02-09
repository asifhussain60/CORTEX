"""
Unit tests for IntelligenceGate middleware.

CORE Rules:
- CORE-008: TDD (tests before code) ✅
- CORE-011: Type hints ✅
- CORE-012: Docstrings ✅
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from cortex.mcp.middleware.intelligence_gate import (
    IntelligenceGate,
    IntelligenceContextCache,
)
from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
)


class TestIntelligenceContextCache:
    """Test IntelligenceContextCache class."""

    def test_cache_is_fresh_immediately_after_creation(self):
        """Fresh cache should return is_fresh=True."""
        mock_context = MagicMock(spec=UnifiedIntelligenceContext)
        cache = IntelligenceContextCache(context=mock_context, created_at=time.time())

        assert cache.is_fresh() is True
        assert cache.is_stale() is False

    def test_cache_becomes_stale_after_ttl(self):
        """Cache should become stale after TTL expires."""
        mock_context = MagicMock(spec=UnifiedIntelligenceContext)
        past_time = time.time() - 400  # 400 seconds ago (> 300s TTL)
        cache = IntelligenceContextCache(
            context=mock_context, created_at=past_time, ttl_seconds=300
        )

        assert cache.is_stale() is True
        assert cache.is_fresh() is False

    def test_custom_ttl(self):
        """Cache should respect custom TTL."""
        mock_context = MagicMock(spec=UnifiedIntelligenceContext)
        past_time = time.time() - 60
        cache = IntelligenceContextCache(
            context=mock_context, created_at=past_time, ttl_seconds=100
        )

        assert cache.is_stale() is True

        # With longer TTL, should not be stale
        cache2 = IntelligenceContextCache(
            context=mock_context, created_at=past_time, ttl_seconds=1000
        )
        assert cache2.is_fresh() is True


class TestIntelligenceGate:
    """Test IntelligenceGate middleware."""

    @pytest.fixture
    def gate(self):
        """Create gate with mocked synthesis engine."""
        gate = IntelligenceGate(cache_ttl_seconds=300)
        # Mock the synthesis engine
        gate.synthesis_engine = MagicMock()
        return gate

    @pytest.fixture
    def mock_context(self):
        """Create mock UnifiedIntelligenceContext."""
        ctx = MagicMock(spec=UnifiedIntelligenceContext)
        ctx.coverage_score = 0.95
        ctx.knowledge_layers = {"company": {}, "domain": {}, "cortex": {}}
        return ctx

    def test_gate_initialization(self, gate):
        """Gate should initialize with empty cache."""
        assert gate.cache == {}
        assert gate.stats["total_requests"] == 0
        assert gate.cache_ttl == 300

    def test_process_request_with_provided_context(self, gate, mock_context):
        """Gate should use provided context (from CCL or decorator)."""
        kwargs = {"unified_intelligence": mock_context}
        result = gate.process_request("cortex_process_request", kwargs)

        assert result["unified_intelligence"] == mock_context
        assert gate.stats["total_requests"] == 1
        # Should not synthesize if already provided
        gate.synthesis_engine.synthesize_unified_context.assert_not_called()

    def test_process_request_synthesizes_when_missing(self, gate, mock_context):
        """Gate should synthesize context when not provided."""
        gate.synthesis_engine.synthesize_unified_context.return_value = mock_context

        kwargs = {"operation": "IMPLEMENT", "target": "test.py"}
        result = gate.process_request("cortex_process_request", kwargs)

        assert "unified_intelligence" in result
        assert result["unified_intelligence"] == mock_context
        gate.synthesis_engine.synthesize_unified_context.assert_called_once()

    def test_process_request_caching(self, gate, mock_context):
        """Gate should cache synthesized contexts."""
        gate.synthesis_engine.synthesize_unified_context.return_value = mock_context

        # First request should synthesize
        kwargs1 = {
            "operation": "IMPLEMENT",
            "target": "test.py",
            "request_id": "req-123",
        }
        result1 = gate.process_request("cortex_process_request", kwargs1)

        assert len(gate.cache) == 1
        assert gate.stats["cache_misses"] == 1
        gate.synthesis_engine.reset_mock()

        # Second request with same key should use cache
        kwargs2 = {
            "operation": "IMPLEMENT",
            "target": "test.py",
            "request_id": "req-123",
        }
        result2 = gate.process_request("cortex_process_request", kwargs2)

        assert result2["unified_intelligence"] == mock_context
        assert gate.stats["cache_hits"] == 1
        # Should not synthesize again
        gate.synthesis_engine.synthesize_unified_context.assert_not_called()

    def test_process_request_synthesis_failure_blocks(self, gate):
        """Gate should block if synthesis fails."""
        gate.synthesis_engine.synthesize_unified_context.side_effect = ValueError(
            "Synthesis failed"
        )

        kwargs = {"operation": "IMPLEMENT", "target": "test.py"}

        with pytest.raises(ValueError) as exc_info:
            gate.process_request("cortex_process_request", kwargs)

        assert "Intelligence synthesis required" in str(exc_info.value)
        assert gate.stats["synthesis_failures"] == 1

    def test_callable_interface(self, gate, mock_context):
        """Gate should be callable as middleware."""
        gate.synthesis_engine.synthesize_unified_context.return_value = mock_context

        kwargs = {"operation": "IMPLEMENT"}
        result = gate("cortex_process_request", kwargs)

        assert "unified_intelligence" in result

    def test_get_stats(self, gate, mock_context):
        """Gate should provide accurate statistics."""
        gate.synthesis_engine.synthesize_unified_context.return_value = mock_context

        # Make some requests
        kwargs = {"operation": "IMPLEMENT", "request_id": "req-1"}
        gate.process_request("tool1", kwargs)
        gate.process_request("tool1", kwargs)  # Cache hit

        stats = gate.get_stats()

        assert stats["total_requests"] == 2
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1
        assert stats["cache_hit_rate"] == 0.5

    def test_clear_cache(self, gate, mock_context):
        """Gate should clear cache."""
        gate.synthesis_engine.synthesize_unified_context.return_value = mock_context

        # Fill cache
        for i in range(3):
            kwargs = {"operation": "IMPLEMENT", "request_id": f"req-{i}"}
            gate.process_request("tool", kwargs)

        assert len(gate.cache) == 3

        # Clear
        cleared = gate.clear_cache()

        assert cleared == 3
        assert len(gate.cache) == 0

    def test_cleanup_stale(self, gate, mock_context):
        """Gate should clean up stale cache entries."""
        gate.synthesis_engine.synthesize_unified_context.return_value = mock_context

        # Add fresh entries
        for i in range(2):
            cache_key = f"key-{i}"
            gate.cache[cache_key] = IntelligenceContextCache(
                context=mock_context, created_at=time.time(), ttl_seconds=300
            )

        # Add stale entries
        for i in range(2, 4):
            cache_key = f"key-{i}"
            gate.cache[cache_key] = IntelligenceContextCache(
                context=mock_context,
                created_at=time.time() - 400,
                ttl_seconds=300,
            )

        # Cleanup
        cleaned = gate.cleanup_stale()

        assert cleaned == 2
        assert len(gate.cache) == 2


class TestIntelligenceGateIntegration:
    """Integration tests for IntelligenceGate."""

    @pytest.mark.integration
    def test_e2e_enforcement_multiple_tools(self):
        """E2E: Multiple tools should all receive intelligence context."""
        gate = IntelligenceGate()
        gate.synthesis_engine = MagicMock()

        mock_context = MagicMock(spec=UnifiedIntelligenceContext)
        mock_context.coverage_score = 0.95
        gate.synthesis_engine.synthesize_unified_context.return_value = mock_context

        # Simulate multiple tool calls
        tools = [
            "cortex_process_request",
            "cortex_lens_analyze",
            "cortex_total_recall",
        ]

        for tool in tools:
            kwargs = {"operation": "ANALYZE"}
            result = gate.process_request(tool, kwargs)
            assert "unified_intelligence" in result

        assert gate.stats["total_requests"] == 3
        # Each tool is different, so all should be misses
        assert gate.stats["cache_misses"] == 3
