"""Unit tests for TieredRouter

Tests cover:
- Tier 1-4 classification accuracy
- Cache functionality
- Regex fallback
- Telemetry accuracy tracking
- Performance benchmarks

Author: Asif Hussain
Phase: 01 of CORTEX Evolution v3.9
"""

import pytest
import time
from datetime import datetime
from src.operations.modules.routing.tiered_router import (
    TieredRouter,
    RoutingDecision,
    RoutingTelemetry,
    OperationTier,
    RegexFallback
)


class TestTieredRouter:
    """Test TieredRouter classification."""
    
    def test_tier_1_classification_help(self):
        """Test Tier 1: help command."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("help")
        
        assert decision.tier == 1
        assert decision.execution_method == "instant"
        assert decision.estimated_time == "<2s"
        assert decision.requires_planning == False
        assert decision.confidence > 0.7
    
    def test_tier_1_classification_healthcheck(self):
        """Test Tier 1: healthcheck command."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("healthcheck")
        
        assert decision.tier == 1
        assert decision.execution_method == "instant"
        assert decision.estimated_time == "<2s"
    
    def test_tier_1_classification_align(self):
        """Test Tier 1: align command."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("align")
        
        assert decision.tier == 1
        assert decision.execution_method == "instant"
    
    def test_tier_2_classification_typo_fix(self):
        """Test Tier 2: typo fix."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("fix typo in config.py")
        
        assert decision.tier == 2
        assert decision.execution_method == "lightweight"
        assert decision.estimated_time == "<10s"
        assert decision.requires_planning == False
    
    def test_tier_2_classification_docstring(self):
        """Test Tier 2: add docstring."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("add docstring to function")
        
        assert decision.tier == 2
        assert decision.execution_method == "lightweight"
    
    def test_tier_3_classification_feature(self):
        """Test Tier 3: add feature."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("add user authentication feature")
        
        assert decision.tier == 3
        assert decision.execution_method == "documented"
        assert decision.estimated_time == "10-60min"
        assert decision.requires_planning == True
    
    def test_tier_3_classification_ado_story(self):
        """Test Tier 3: plan ADO story."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("plan ado story")
        
        assert decision.tier == 3
        assert decision.requires_planning == True
    
    def test_tier_4_classification_redesign(self):
        """Test Tier 4: redesign system."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("redesign database architecture")
        
        assert decision.tier == 4
        assert decision.execution_method == "complex"
        assert decision.estimated_time == ">1h"
        assert decision.requires_planning == True
    
    def test_tier_4_classification_ado_feature(self):
        """Test Tier 4: plan ADO feature."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        decision = router.route("plan ado feature")
        
        assert decision.tier == 4
        assert decision.requires_planning == True
    
    def test_cache_hit(self):
        """Test cache retrieval for known operations."""
        router = TieredRouter(llm_client=None, cache_enabled=True)
        
        # First call (cache miss)
        decision1 = router.route("help")
        assert decision1.cache_hit == False
        
        # Second call (should hit cache)
        decision2 = router.route("help")
        assert decision2.cache_hit == True
        assert decision1.tier == decision2.tier
        
        # Verify telemetry
        metrics = router.get_telemetry()
        assert metrics['cache_hit_rate'] == 0.5  # 1 hit out of 2 calls
    
    def test_cache_disabled(self):
        """Test routing with cache disabled."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        
        decision1 = router.route("help")
        decision2 = router.route("help")
        
        assert decision1.cache_hit == False
        assert decision2.cache_hit == False
    
    def test_cache_ttl_expiry(self):
        """Test cache TTL expiration."""
        router = TieredRouter(llm_client=None, cache_enabled=True, cache_ttl_seconds=0.1)
        
        # First call
        decision1 = router.route("help")
        assert decision1.cache_hit == False
        
        # Wait for cache to expire
        time.sleep(0.2)
        
        # Second call (cache expired, should be miss)
        decision2 = router.route("help")
        assert decision2.cache_hit == False
    
    def test_context_handling(self):
        """Test routing with context."""
        router = TieredRouter(llm_client=None, cache_enabled=False)
        context = {"files_affected": 5, "complexity": "high"}
        
        decision = router.route("refactor code", context=context)
        
        assert decision.tier >= 2  # Should not be instant
        assert isinstance(decision.reasoning, str)
    
    def test_performance_under_50ms_cached(self):
        """Test performance: cached operations <50ms."""
        router = TieredRouter(llm_client=None, cache_enabled=True)
        
        # Warm up cache
        router.route("help")
        
        # Measure cached performance
        start = time.perf_counter()
        router.route("help")
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert elapsed_ms < 50, f"Cached routing took {elapsed_ms:.2f}ms (expected <50ms)"


class TestRegexFallback:
    """Test RegexFallback classifier."""
    
    def test_tier_1_patterns(self):
        """Test Tier 1 pattern matching."""
        fallback = RegexFallback()
        
        assert fallback.classify("help") == 1
        assert fallback.classify("healthcheck") == 1
        assert fallback.classify("version") == 1
        assert fallback.classify("status") == 1
    
    def test_tier_2_patterns(self):
        """Test Tier 2 pattern matching."""
        fallback = RegexFallback()
        
        assert fallback.classify("fix typo in file.py") == 2
        assert fallback.classify("update comment") == 2
        assert fallback.classify("add docstring to function") == 2
    
    def test_tier_3_patterns(self):
        """Test Tier 3 pattern matching."""
        fallback = RegexFallback()
        
        assert fallback.classify("add feature for users") == 3
        assert fallback.classify("implement new function") == 3
        assert fallback.classify("create class for data") == 3
    
    def test_tier_4_patterns(self):
        """Test Tier 4 pattern matching."""
        fallback = RegexFallback()
        
        assert fallback.classify("redesign the system") == 4
        assert fallback.classify("architecture changes needed") == 4
        assert fallback.classify("refactor system completely") == 4
    
    def test_default_tier(self):
        """Test default tier for unknown operations."""
        fallback = RegexFallback()
        
        # Unknown operation should default to Tier 2
        assert fallback.classify("unknown operation xyz") == 2


class TestRoutingTelemetry:
    """Test RoutingTelemetry metrics."""
    
    def test_record_decision(self):
        """Test decision recording."""
        telemetry = RoutingTelemetry()
        
        decision = RoutingDecision(
            tier=1,
            confidence=0.95,
            reasoning="test",
            execution_method="instant",
            estimated_time="<2s",
            requires_planning=False
        )
        
        telemetry.record_decision(decision)
        
        metrics = telemetry.get_metrics()
        assert metrics['total_decisions'] == 1
    
    def test_accuracy_calculation_100_percent(self):
        """Test 100% accuracy calculation."""
        telemetry = RoutingTelemetry()
        
        # 10 correct predictions
        for i in range(10):
            telemetry.record_feedback("operation", expected_tier=1, actual_tier=1)
        
        accuracy = telemetry.calculate_accuracy()
        assert accuracy == 1.0
    
    def test_accuracy_calculation_90_percent(self):
        """Test 90% accuracy calculation."""
        telemetry = RoutingTelemetry()
        
        # 9 correct, 1 incorrect
        for i in range(9):
            telemetry.record_feedback(f"operation_{i}", expected_tier=1, actual_tier=1)
        
        telemetry.record_feedback("operation_9", expected_tier=1, actual_tier=2)
        
        accuracy = telemetry.calculate_accuracy()
        assert accuracy == 0.9
    
    def test_accuracy_calculation_last_n(self):
        """Test accuracy over last N operations."""
        telemetry = RoutingTelemetry()
        
        # Add 200 operations
        for i in range(200):
            expected = 1 if i < 190 else 2  # 95% accuracy
            telemetry.record_feedback(f"op_{i}", expected_tier=expected, actual_tier=1)
        
        # Check last 100 operations (should be different accuracy)
        accuracy_last_100 = telemetry.calculate_accuracy(last_n=100)
        assert accuracy_last_100 == 0.9  # 90/100 correct
    
    def test_tier_distribution(self):
        """Test tier distribution tracking."""
        telemetry = RoutingTelemetry()
        router = TieredRouter(llm_client=None, cache_enabled=False)
        router.telemetry = telemetry
        
        # Route to different tiers
        router.route("help")  # Tier 1
        router.route("fix typo")  # Tier 2
        router.route("add feature")  # Tier 3
        router.route("redesign system")  # Tier 4
        
        metrics = telemetry.get_metrics()
        assert metrics['tier_distribution'][1] == 1
        assert metrics['tier_distribution'][2] == 1
        assert metrics['tier_distribution'][3] == 1
        assert metrics['tier_distribution'][4] == 1
    
    def test_average_confidence(self):
        """Test average confidence calculation."""
        telemetry = RoutingTelemetry()
        
        decision1 = RoutingDecision(
            tier=1, confidence=0.9, reasoning="test",
            execution_method="instant", estimated_time="<2s", requires_planning=False
        )
        decision2 = RoutingDecision(
            tier=2, confidence=0.8, reasoning="test",
            execution_method="lightweight", estimated_time="<10s", requires_planning=False
        )
        
        telemetry.record_decision(decision1)
        telemetry.record_decision(decision2)
        
        metrics = telemetry.get_metrics()
        assert metrics['average_confidence'] == pytest.approx(0.85, rel=0.01)  # (0.9 + 0.8) / 2
    
    def test_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        router = TieredRouter(llm_client=None, cache_enabled=True)
        
        # First call (miss)
        router.route("help")
        
        # Second call (hit)
        router.route("help")
        
        # Third call different operation (miss)
        router.route("status")
        
        metrics = router.get_telemetry()
        assert metrics['cache_hit_rate'] == pytest.approx(1/3, rel=0.01)  # 1 hit out of 3


# Integration test marker (run separately in Phase 16)
@pytest.mark.integration
class TestTieredRouterIntegration:
    """Integration tests for tiered router (Phase 16)."""
    
    def test_end_to_end_tier_1(self):
        """Test complete Tier 1 workflow."""
        pytest.skip("Integration test - deferred to Phase 16")
    
    def test_end_to_end_tier_4(self):
        """Test complete Tier 4 workflow."""
        pytest.skip("Integration test - deferred to Phase 16")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
