# AC_START: AC-WAVE-4-S1-001
"""
Test suite for ENH-087 Track 2: Intelligent Response Routing.

Tests intelligent response routing based on context analysis,
pattern matching, and template selection optimization.

Module: tests/unit/orchestrators/test_intelligent_response_routing.py
Authority: WAVE-4 Stage 1 - ENH-087 Track 2
Coverage Target: ≥98%
"""

import pytest
from typing import Dict, Any, List
from dataclasses import dataclass

# Import modules to test (will be created)
from cortex.orchestrators.core.intelligent_response_router import (
    IntelligentResponseRouter,
    ContextAnalysisResult,
    PatternMatchResult,
    TemplateSelectionResult,
    RoutingContext,
)


@dataclass
class MockRoutingContext:
    """Mock routing context for testing."""
    intent_type: str
    user_query: str
    domain: str
    complexity: int
    user_preferences: Dict[str, Any]


class TestContextAnalysis:
    """Test suite for context analysis (8 tests)."""

    def test_analyze_simple_query(self):
        """Context analysis should handle simple queries."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="IMPLEMENT",
            user_query="implement login feature",
            domain="authentication",
            complexity=3,
            user_preferences={}
        )
        
        result = router.analyze_context(context)
        
        assert result.confidence > 0.7
        assert result.context_type in ["simple", "moderate", "complex"]
        assert len(result.key_factors) > 0

    def test_analyze_complex_query(self):
        """Context analysis should identify complex queries."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="REFACTOR",
            user_query="refactor master orchestrator with strategy pattern",
            domain="core",
            complexity=8,
            user_preferences={"verbose": True}
        )
        
        result = router.analyze_context(context)
        
        assert result.context_type == "complex"
        assert result.confidence > 0.8

    def test_analyze_with_user_preferences(self):
        """Context analysis should incorporate user preferences."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="ANALYZE",
            user_query="analyze code quality",
            domain="quality",
            complexity=5,
            user_preferences={"format": "concise", "show_metrics": True}
        )
        
        result = router.analyze_context(context)
        
        assert "user_preferences" in result.metadata
        assert result.metadata["user_preferences"]["format"] == "concise"

    def test_analyze_empty_query(self):
        """Context analysis should handle empty queries gracefully."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="QUERY",
            user_query="",
            domain="unknown",
            complexity=1,
            user_preferences={}
        )
        
        result = router.analyze_context(context)
        
        assert result.confidence < 0.5
        assert result.context_type == "simple"

    def test_analyze_domain_specific_context(self):
        """Context analysis should recognize domain-specific patterns."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="IMPLEMENT",
            user_query="implement security audit trail",
            domain="security",
            complexity=7,
            user_preferences={}
        )
        
        result = router.analyze_context(context)
        
        assert "security" in result.key_factors
        assert result.confidence > 0.75

    def test_analyze_with_confidence_factors(self):
        """Context analysis should provide confidence breakdown."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="FIX",
            user_query="fix race condition",
            domain="concurrency",
            complexity=6,
            user_preferences={}
        )
        
        result = router.analyze_context(context)
        
        assert "confidence_factors" in result.metadata
        assert len(result.metadata["confidence_factors"]) > 0

    def test_analyze_intent_alignment(self):
        """Context analysis should check intent-domain alignment."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="IMPLEMENT",
            user_query="analyze existing code",  # Misaligned
            domain="analysis",
            complexity=4,
            user_preferences={}
        )
        
        result = router.analyze_context(context)
        
        assert "intent_mismatch" in result.warnings

    def test_analyze_complexity_threshold(self):
        """Context analysis should flag high complexity."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="REFACTOR",
            user_query="refactor entire orchestrator architecture",
            domain="architecture",
            complexity=10,
            user_preferences={}
        )
        
        result = router.analyze_context(context)
        
        assert result.context_type == "complex"
        assert "high_complexity" in result.warnings


class TestPatternMatching:
    """Test suite for pattern matching (10 tests)."""

    def test_match_simple_pattern(self):
        """Pattern matching should identify simple patterns."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="simple",
            confidence=0.85,
            key_factors=["implement", "feature"],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert result.matched_patterns is not None
        assert len(result.matched_patterns) > 0
        assert result.confidence > 0.7

    def test_match_complex_pattern(self):
        """Pattern matching should handle complex patterns."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="complex",
            confidence=0.9,
            key_factors=["refactor", "strategy", "pattern"],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert len(result.matched_patterns) > 0
        assert result.best_match is not None

    def test_match_with_domain_patterns(self):
        """Pattern matching should recognize domain-specific patterns."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="moderate",
            confidence=0.8,
            key_factors=["security", "audit", "logging"],
            metadata={"domain": "security"},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert any("security" in p.lower() for p in result.matched_patterns)

    def test_match_intent_patterns(self):
        """Pattern matching should align with intent types."""
        router = IntelligentResponseRouter()
        
        for intent in ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE"]:
            context_result = ContextAnalysisResult(
                context_type="moderate",
                confidence=0.8,
                key_factors=[intent.lower()],
                metadata={"intent": intent},
                warnings=[]
            )
            
            result = router.match_patterns(context_result)
            
            assert result.confidence > 0.6
            assert len(result.matched_patterns) > 0

    def test_match_pattern_confidence_scoring(self):
        """Pattern matching should provide confidence scores."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="moderate",
            confidence=0.85,
            key_factors=["implement", "api", "endpoint"],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert "pattern_scores" in result.metadata
        assert all(0 <= score <= 1 for score in result.metadata["pattern_scores"].values())

    def test_match_no_patterns_found(self):
        """Pattern matching should handle no matches gracefully."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="simple",
            confidence=0.4,
            key_factors=[],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert len(result.matched_patterns) == 0
        assert result.best_match is None
        assert result.confidence < 0.5

    def test_match_multiple_patterns(self):
        """Pattern matching should rank multiple matches."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="complex",
            confidence=0.9,
            key_factors=["implement", "test", "refactor", "optimize"],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert len(result.matched_patterns) >= 2
        assert result.best_match == result.matched_patterns[0]

    def test_match_pattern_similarity(self):
        """Pattern matching should use similarity scoring."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="moderate",
            confidence=0.8,
            key_factors=["refactoring", "improvement"],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        # Should match "refactor" pattern (similar to "refactoring")
        assert any("refactor" in p.lower() for p in result.matched_patterns)

    def test_match_pattern_fallback(self):
        """Pattern matching should provide fallback patterns."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="simple",
            confidence=0.6,
            key_factors=["unknown"],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert "fallback_patterns" in result.metadata

    def test_match_pattern_metadata(self):
        """Pattern matching should include pattern metadata."""
        router = IntelligentResponseRouter()
        
        context_result = ContextAnalysisResult(
            context_type="moderate",
            confidence=0.85,
            key_factors=["implement", "feature"],
            metadata={},
            warnings=[]
        )
        
        result = router.match_patterns(context_result)
        
        assert "pattern_metadata" in result.metadata
        assert result.best_match is not None


class TestTemplateSelection:
    """Test suite for template selection optimization (7 tests)."""

    def test_select_template_for_simple_context(self):
        """Template selection should choose simple templates for simple contexts."""
        router = IntelligentResponseRouter()
        
        pattern_result = PatternMatchResult(
            matched_patterns=["implement_feature"],
            best_match="implement_feature",
            confidence=0.85,
            metadata={"context_type": "simple"},
            warnings=[]
        )
        
        result = router.select_template(pattern_result)
        
        assert result.template_id is not None
        assert "simple" in result.template_id or result.complexity_level == "simple"

    def test_select_template_for_complex_context(self):
        """Template selection should choose detailed templates for complex contexts."""
        router = IntelligentResponseRouter()
        
        pattern_result = PatternMatchResult(
            matched_patterns=["refactor_architecture", "implement_pattern"],
            best_match="refactor_architecture",
            confidence=0.9,
            metadata={"context_type": "complex"},
            warnings=[]
        )
        
        result = router.select_template(pattern_result)
        
        assert result.complexity_level in ["complex", "detailed"]

    def test_select_template_with_preferences(self):
        """Template selection should respect user preferences."""
        router = IntelligentResponseRouter()
        
        pattern_result = PatternMatchResult(
            matched_patterns=["analyze_code"],
            best_match="analyze_code",
            confidence=0.8,
            metadata={"user_preferences": {"format": "concise"}},
            warnings=[]
        )
        
        result = router.select_template(pattern_result)
        
        assert "concise" in result.template_attributes

    def test_select_template_optimization(self):
        """Template selection should optimize for performance."""
        router = IntelligentResponseRouter()
        
        pattern_result = PatternMatchResult(
            matched_patterns=["quick_fix"],
            best_match="quick_fix",
            confidence=0.75,
            metadata={},
            warnings=[]
        )
        
        result = router.select_template(pattern_result)
        
        assert result.optimization_applied
        assert "performance" in result.metadata

    def test_select_template_fallback(self):
        """Template selection should provide fallback templates."""
        router = IntelligentResponseRouter()
        
        pattern_result = PatternMatchResult(
            matched_patterns=[],
            best_match=None,
            confidence=0.4,
            metadata={},
            warnings=[]
        )
        
        result = router.select_template(pattern_result)
        
        assert result.template_id is not None  # Fallback template
        assert result.is_fallback

    def test_select_template_caching(self):
        """Template selection should cache frequently used templates."""
        router = IntelligentResponseRouter()
        
        pattern_result = PatternMatchResult(
            matched_patterns=["implement_feature"],
            best_match="implement_feature",
            confidence=0.85,
            metadata={},
            warnings=[]
        )
        
        # First call
        result1 = router.select_template(pattern_result)
        
        # Second call (should be cached)
        result2 = router.select_template(pattern_result)
        
        assert result1.template_id == result2.template_id
        assert "cache_hit" in result2.metadata

    def test_select_template_metadata(self):
        """Template selection should include template metadata."""
        router = IntelligentResponseRouter()
        
        pattern_result = PatternMatchResult(
            matched_patterns=["implement_api"],
            best_match="implement_api",
            confidence=0.88,
            metadata={"domain": "api"},
            warnings=[]
        )
        
        result = router.select_template(pattern_result)
        
        assert "template_metadata" in result.metadata
        assert result.template_id is not None


class TestIntegration:
    """Integration tests for full routing pipeline (5 tests)."""

    def test_end_to_end_simple_routing(self):
        """Full routing pipeline for simple query."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="IMPLEMENT",
            user_query="implement login feature",
            domain="authentication",
            complexity=3,
            user_preferences={}
        )
        
        # Full pipeline: analyze -> match -> select
        context_result = router.analyze_context(context)
        pattern_result = router.match_patterns(context_result)
        template_result = router.select_template(pattern_result)
        
        assert template_result.template_id is not None
        assert template_result.confidence > 0.7

    def test_end_to_end_complex_routing(self):
        """Full routing pipeline for complex query."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="REFACTOR",
            user_query="refactor orchestrator with strategy pattern and event bus",
            domain="architecture",
            complexity=9,
            user_preferences={"verbose": True}
        )
        
        context_result = router.analyze_context(context)
        pattern_result = router.match_patterns(context_result)
        template_result = router.select_template(pattern_result)
        
        assert template_result.complexity_level == "complex"
        assert template_result.confidence > 0.8

    def test_end_to_end_with_warnings(self):
        """Full routing pipeline should propagate warnings."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="IMPLEMENT",
            user_query="analyze code",  # Intent mismatch
            domain="analysis",
            complexity=4,
            user_preferences={}
        )
        
        context_result = router.analyze_context(context)
        pattern_result = router.match_patterns(context_result)
        template_result = router.select_template(pattern_result)
        
        # Warnings should propagate through pipeline
        assert len(context_result.warnings) > 0 or len(pattern_result.warnings) > 0

    def test_end_to_end_performance(self):
        """Full routing pipeline should complete quickly."""
        import time
        
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="FIX",
            user_query="fix bug in payment processing",
            domain="payment",
            complexity=6,
            user_preferences={}
        )
        
        start = time.time()
        context_result = router.analyze_context(context)
        pattern_result = router.match_patterns(context_result)
        template_result = router.select_template(pattern_result)
        duration = time.time() - start
        
        assert duration < 0.1  # Should complete in <100ms

    def test_end_to_end_consistency(self):
        """Full routing pipeline should be deterministic."""
        router = IntelligentResponseRouter()
        
        context = RoutingContext(
            intent_type="ANALYZE",
            user_query="analyze code quality metrics",
            domain="quality",
            complexity=5,
            user_preferences={}
        )
        
        # Run twice
        result1_context = router.analyze_context(context)
        result1_pattern = router.match_patterns(result1_context)
        result1_template = router.select_template(result1_pattern)
        
        result2_context = router.analyze_context(context)
        result2_pattern = router.match_patterns(result2_context)
        result2_template = router.select_template(result2_pattern)
        
        assert result1_template.template_id == result2_template.template_id


# AC_COMPLETE: AC-WAVE-4-S1-001 (25 tests - RED phase complete)
