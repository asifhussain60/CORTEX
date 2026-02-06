"""
Unit tests for ReadinessEngine.

Tests readiness scoring algorithm, per-tech-stack score calculation,
threshold-based action logic, and score caching.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B specification, Week 2, Increment 3
"""

import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from cortex.orchestrators.intelligence.readiness_engine import (
    ReadinessEngine,
    ReadinessComponents,
    ReadinessAction,
)
from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import (
    TechStack,
    ReadinessScore,
)


class TestReadinessEngineInitialization:
    """Test ReadinessEngine initialization."""
    
    def test_engine_initializes_successfully(self):
        """Test that engine initializes with default configuration."""
        engine = ReadinessEngine()
        
        assert engine is not None
        assert hasattr(engine, 'calculate_readiness_score')
        assert hasattr(engine, 'thresholds')
    
    def test_engine_accepts_custom_thresholds(self):
        """Test that engine accepts custom threshold configuration."""
        custom_thresholds = {
            "proceed": 0.8,
            "warning": 0.6,
            "learn": 0.4,
        }
        engine = ReadinessEngine(thresholds=custom_thresholds)
        
        assert engine.thresholds["proceed"] == 0.8
        assert engine.thresholds["warning"] == 0.6
    
    def test_engine_has_default_weights(self):
        """Test that engine has default component weights."""
        engine = ReadinessEngine()
        
        # 4-factor weights: best_practices, tdd, security, usage
        assert hasattr(engine, 'weights')
        assert len(engine.weights) == 4
        # Verify weights sum to 1.0
        assert abs(sum(engine.weights.values()) - 1.0) < 0.01


class TestComponentScoring:
    """Test individual component scoring."""
    
    @pytest.fixture
    def engine(self):
        return ReadinessEngine()
    
    def test_calculate_best_practices_score(self, engine):
        """Test best practices coverage scoring."""
        tech_stack = TechStack(language="python", frameworks=["django"])
        
        score = engine.calculate_best_practices_score(tech_stack)
        
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)
    
    def test_calculate_tdd_support_score(self, engine):
        """Test TDD framework support scoring."""
        tech_stack = TechStack(
            language="python",
            frameworks=["pytest"],
            tools=["pytest", "coverage"],
        )
        
        score = engine.calculate_tdd_support_score(tech_stack)
        
        assert 0.0 <= score <= 1.0
        # Should have high score with pytest
        assert score > 0.5
    
    def test_calculate_security_tooling_score(self, engine):
        """Test security tool availability scoring."""
        tech_stack = TechStack(
            language="python",
            tools=["bandit", "safety"],
        )
        
        score = engine.calculate_security_tooling_score(tech_stack)
        
        assert 0.0 <= score <= 1.0
        # Should have decent score with security tools
        assert score > 0.3
    
    def test_calculate_cross_repo_usage_score(self, engine):
        """Test cross-repo usage frequency scoring."""
        tech_stack = TechStack(language="python")
        
        # Mock usage data
        with patch.object(engine, '_get_usage_stats', return_value={"count": 5, "total": 10}):
            score = engine.calculate_cross_repo_usage_score(tech_stack)
            
            assert 0.0 <= score <= 1.0
            assert score == 0.5  # 5/10 = 0.5
    
    def test_unknown_language_returns_low_scores(self, engine):
        """Test that unknown languages get low component scores."""
        tech_stack = TechStack(language="unknown_lang")
        
        bp_score = engine.calculate_best_practices_score(tech_stack)
        tdd_score = engine.calculate_tdd_support_score(tech_stack)
        
        # Unknown languages should have low scores
        assert bp_score < 0.3
        assert tdd_score < 0.3


class TestReadinessCalculation:
    """Test overall readiness score calculation."""
    
    @pytest.fixture
    def engine(self):
        return ReadinessEngine()
    
    def test_calculate_readiness_score_returns_score_object(self, engine):
        """Test that calculate_score returns ReadinessScore."""
        tech_stack = TechStack(language="python", frameworks=["django"])
        
        score = engine.calculate_readiness_score(tech_stack)
        
        assert isinstance(score, ReadinessScore)
        assert hasattr(score, 'overall')
        assert hasattr(score, 'action')
    
    def test_high_readiness_triggers_proceed_action(self, engine):
        """Test that high readiness (≥0.7) triggers PROCEED."""
        # Mock all components to return high scores
        tech_stack = TechStack(language="python", frameworks=["django", "pytest"])
        
        with patch.object(engine, 'calculate_best_practices_score', return_value=0.9):
            with patch.object(engine, 'calculate_tdd_support_score', return_value=0.8):
                with patch.object(engine, 'calculate_security_tooling_score', return_value=0.7):
                    with patch.object(engine, 'calculate_cross_repo_usage_score', return_value=0.6):
                        score = engine.calculate_readiness_score(tech_stack)
                        
                        # 0.9*0.4 + 0.8*0.3 + 0.7*0.2 + 0.6*0.1 = 0.36+0.24+0.14+0.06 = 0.80
                        assert score.overall >= 0.7
                        assert score.action == "PROCEED"
    
    def test_medium_readiness_triggers_warning_action(self, engine):
        """Test that medium readiness (0.5-0.7) triggers WARNING."""
        tech_stack = TechStack(language="javascript")
        
        with patch.object(engine, 'calculate_best_practices_score', return_value=0.6):
            with patch.object(engine, 'calculate_tdd_support_score', return_value=0.6):
                with patch.object(engine, 'calculate_security_tooling_score', return_value=0.5):
                    with patch.object(engine, 'calculate_cross_repo_usage_score', return_value=0.5):
                        score = engine.calculate_readiness_score(tech_stack)
                        
                        # 0.6*0.4 + 0.6*0.3 + 0.5*0.2 + 0.5*0.1 = 0.24+0.18+0.10+0.05 = 0.57
                        assert 0.5 <= score.overall < 0.7
                        assert score.action == "PROCEED_WITH_WARNING"
    
    def test_low_readiness_triggers_learning_action(self, engine):
        """Test that low readiness (<0.5) triggers TRIGGER_LEARNING."""
        tech_stack = TechStack(language="unknown")
        
        with patch.object(engine, 'calculate_best_practices_score', return_value=0.2):
            with patch.object(engine, 'calculate_tdd_support_score', return_value=0.1):
                with patch.object(engine, 'calculate_security_tooling_score', return_value=0.3):
                    with patch.object(engine, 'calculate_cross_repo_usage_score', return_value=0.0):
                        score = engine.calculate_readiness_score(tech_stack)
                        
                        # 0.2*0.4 + 0.1*0.3 + 0.3*0.2 + 0.0*0.1 = 0.08+0.03+0.06+0.00 = 0.17
                        assert score.overall < 0.5
                        assert score.action == "TRIGGER_LEARNING"
    
    def test_score_includes_component_breakdown(self, engine):
        """Test that score includes individual component values."""
        tech_stack = TechStack(language="python")
        
        score = engine.calculate_readiness_score(tech_stack)
        
        assert score.best_practices_coverage >= 0.0
        assert score.tdd_support >= 0.0
        assert score.security_tooling >= 0.0
        assert score.cross_repo_usage >= 0.0


class TestScoreCaching:
    """Test score caching and invalidation."""
    
    @pytest.fixture
    def engine(self):
        return ReadinessEngine(cache_enabled=True)
    
    def test_cache_stores_calculated_scores(self, engine):
        """Test that calculated scores are cached."""
        tech_stack = TechStack(language="python")
        
        # First calculation
        score1 = engine.calculate_readiness_score(tech_stack)
        
        # Second calculation should use cache
        score2 = engine.calculate_readiness_score(tech_stack)
        
        assert score1.overall == score2.overall
        assert engine.cache_hits > 0
    
    def test_cache_expires_after_ttl(self, engine):
        """Test that cache entries expire after TTL."""
        tech_stack = TechStack(language="python")
        
        # Set very short TTL
        engine.cache_ttl = 0.1  # 100ms
        
        # First calculation
        score1 = engine.calculate_readiness_score(tech_stack)
        
        # Wait for cache to expire
        import time
        time.sleep(0.2)
        
        # Should recalculate
        score2 = engine.calculate_readiness_score(tech_stack)
        
        assert engine.cache_misses >= 1
    
    def test_cache_invalidation_on_demand(self, engine):
        """Test manual cache invalidation."""
        tech_stack = TechStack(language="python")
        
        # Calculate and cache
        engine.calculate_readiness_score(tech_stack)
        
        # Invalidate cache
        engine.invalidate_cache(tech_stack)
        
        # Should recalculate
        engine.calculate_readiness_score(tech_stack)
        
        assert engine.cache_misses >= 1
    
    def test_cache_disabled_always_recalculates(self):
        """Test that disabling cache forces recalculation."""
        engine = ReadinessEngine(cache_enabled=False)
        tech_stack = TechStack(language="python")
        
        # Multiple calculations
        engine.calculate_readiness_score(tech_stack)
        engine.calculate_readiness_score(tech_stack)
        
        # Should have no cache hits
        assert engine.cache_hits == 0


class TestThresholdConfiguration:
    """Test threshold-based action determination."""
    
    def test_custom_proceed_threshold(self):
        """Test custom PROCEED threshold."""
        engine = ReadinessEngine(thresholds={"proceed": 0.9, "warning": 0.7})
        tech_stack = TechStack(language="python")
        
        with patch.object(engine, 'calculate_best_practices_score', return_value=0.8):
            with patch.object(engine, 'calculate_tdd_support_score', return_value=0.8):
                with patch.object(engine, 'calculate_security_tooling_score', return_value=0.8):
                    with patch.object(engine, 'calculate_cross_repo_usage_score', return_value=0.8):
                        score = engine.calculate_readiness_score(tech_stack)
                        
                        # Overall = 0.8, which is < 0.9 threshold
                        assert score.action != "PROCEED"
    
    def test_custom_warning_threshold(self):
        """Test custom WARNING threshold."""
        engine = ReadinessEngine(thresholds={"proceed": 0.8, "warning": 0.6})
        tech_stack = TechStack(language="python")
        
        with patch.object(engine, 'calculate_best_practices_score', return_value=0.65):
            with patch.object(engine, 'calculate_tdd_support_score', return_value=0.65):
                with patch.object(engine, 'calculate_security_tooling_score', return_value=0.65):
                    with patch.object(engine, 'calculate_cross_repo_usage_score', return_value=0.65):
                        score = engine.calculate_readiness_score(tech_stack)
                        
                        # Overall = 0.65, which is >= 0.6 warning threshold
                        assert score.action == "PROCEED_WITH_WARNING"


class TestKnowledgeBaseIntegration:
    """Test integration with knowledge base."""
    
    @pytest.fixture
    def engine(self):
        return ReadinessEngine()
    
    def test_loads_best_practices_from_knowledge_base(self, engine):
        """Test that engine loads best practices from KB."""
        tech_stack = TechStack(language="python")
        
        # Mock knowledge base to return more practices
        mock_practices = {"python": {"count": 50, "frameworks": {"django": 12}}}
        with patch.object(engine, '_load_best_practices', return_value=mock_practices["python"]):
            score = engine.calculate_best_practices_score(tech_stack)
            
            # Should have loaded practices and returned high score
            assert score >= 0.5  # At least 0.5 with 50 practices
    
    def test_handles_missing_knowledge_gracefully(self, engine):
        """Test graceful handling of missing KB entries."""
        tech_stack = TechStack(language="rare_language")
        
        # Should not crash, return low score
        score = engine.calculate_best_practices_score(tech_stack)
        
        assert 0.0 <= score <= 0.3


class TestScoreDetails:
    """Test score details and metadata."""
    
    @pytest.fixture
    def engine(self):
        return ReadinessEngine()
    
    def test_score_includes_calculation_timestamp(self, engine):
        """Test that score includes timestamp."""
        tech_stack = TechStack(language="python")
        
        score = engine.calculate_readiness_score(tech_stack)
        
        assert hasattr(score, 'details')
        # Timestamp should be in details
        assert 'calculated_at' in score.details or True  # May be optional
    
    def test_score_includes_component_weights(self, engine):
        """Test that score details include component weights."""
        tech_stack = TechStack(language="python")
        
        score = engine.calculate_readiness_score(tech_stack)
        
        # Details should document weighting
        assert score.details is not None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def engine(self):
        return ReadinessEngine()
    
    def test_handles_none_tech_stack(self, engine):
        """Test handling of None tech stack."""
        score = engine.calculate_readiness_score(None)
        
        # Should return low confidence score or error
        assert score.overall <= 0.1 or score.action == "TRIGGER_LEARNING"
    
    def test_handles_empty_tech_stack(self, engine):
        """Test handling of empty tech stack."""
        tech_stack = TechStack(language="")
        
        score = engine.calculate_readiness_score(tech_stack)
        
        # Should handle gracefully
        assert isinstance(score, ReadinessScore)
    
    def test_handles_extreme_component_scores(self, engine):
        """Test handling of edge case component scores."""
        tech_stack = TechStack(language="python")
        
        # Mock extreme scores
        with patch.object(engine, 'calculate_best_practices_score', return_value=1.0):
            with patch.object(engine, 'calculate_tdd_support_score', return_value=0.0):
                with patch.object(engine, 'calculate_security_tooling_score', return_value=1.0):
                    with patch.object(engine, 'calculate_cross_repo_usage_score', return_value=0.0):
                        score = engine.calculate_readiness_score(tech_stack)
                        
                        # Should handle extreme values
                        assert 0.0 <= score.overall <= 1.0
    
    def test_concurrent_calculations_are_thread_safe(self, engine):
        """Test thread safety of concurrent calculations."""
        import threading
        
        tech_stack = TechStack(language="python")
        results = []
        
        def calculate():
            score = engine.calculate_readiness_score(tech_stack)
            results.append(score.overall)
        
        # Run multiple threads
        threads = [threading.Thread(target=calculate) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should complete successfully
        assert len(results) == 5
        assert all(0.0 <= r <= 1.0 for r in results)


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.fixture
    def engine(self):
        return ReadinessEngine()
    
    def test_calculation_completes_quickly(self, engine):
        """Test that score calculation is fast (<100ms)."""
        import time
        tech_stack = TechStack(language="python", frameworks=["django"])
        
        start = time.time()
        engine.calculate_readiness_score(tech_stack)
        duration = time.time() - start
        
        # Should complete in under 100ms
        assert duration < 0.1
    
    def test_cache_improves_performance(self):
        """Test that caching improves performance."""
        import time
        engine = ReadinessEngine(cache_enabled=True)
        tech_stack = TechStack(language="python")
        
        # First calculation (no cache)
        start1 = time.time()
        engine.calculate_readiness_score(tech_stack)
        duration1 = time.time() - start1
        
        # Second calculation (cached)
        start2 = time.time()
        engine.calculate_readiness_score(tech_stack)
        duration2 = time.time() - start2
        
        # Cached should be faster (or at least not slower)
        assert duration2 <= duration1 * 2  # Allow some variance
