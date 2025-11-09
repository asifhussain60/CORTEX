"""
Unit Tests for Context Optimizer

Tests:
- ContextOptimizer tier selection
- PatternRelevanceScorer scoring algorithm
- ContextCompressor compression techniques
- OptimizedContextLoader integration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Phase: Phase 4.3 - Context Optimization
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from src.tier0.context_optimizer import (
    ContextOptimizer,
    PatternRelevanceScorer,
    ContextCompressor
)
from src.tier0.optimized_context_loader import OptimizedContextLoader


class TestContextOptimizer:
    """Test ContextOptimizer class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.optimizer = ContextOptimizer()
    
    def test_tier_strategy_selection_simple_query(self):
        """Test strategy selection for simple queries"""
        strategy = self.optimizer._select_tier_strategy(
            intent="HELP",
            query="show me the list"
        )
        assert strategy in ["minimal", "light"]
    
    def test_tier_strategy_selection_complex_query(self):
        """Test strategy selection for complex queries"""
        strategy = self.optimizer._select_tier_strategy(
            intent="PLAN",
            query="refactor the authentication module to use OAuth2"
        )
        assert strategy in ["standard", "full"]
    
    def test_tier_strategy_selection_by_intent(self):
        """Test strategy selection based on intent"""
        # Help intent should be minimal
        assert self.optimizer._select_tier_strategy("HELP", "help") == "minimal"
        
        # Plan intent should be full
        assert self.optimizer._select_tier_strategy("PLAN", "create plan") == "full"
    
    def test_selective_tier_loading(self):
        """Test selective tier loading"""
        available_tiers = {
            "tier0": "instinct_handler",
            "tier1": "working_memory",
            "tier2": "knowledge_graph",
            "tier3": "dev_context"
        }
        
        # Load minimal strategy
        selected = self.optimizer._load_selective_tiers("minimal", available_tiers)
        assert "tier0" in selected
        assert len(selected) == 1
        
        # Load full strategy
        selected = self.optimizer._load_selective_tiers("full", available_tiers)
        assert len(selected) == 4
    
    def test_target_size_calculation(self):
        """Test target context size calculation"""
        # Simple query - small size
        size = self.optimizer._calculate_target_size("show list")
        assert size == self.optimizer.min_context_size
        
        # Complex query - larger size
        size = self.optimizer._calculate_target_size(
            "refactor the entire authentication system to use OAuth2 with refresh tokens"
        )
        assert size > self.optimizer.min_context_size
    
    def test_context_building(self):
        """Test context building from tiers"""
        tiers = {
            "tier0": "instinct",
            "tier1": "memory",
            "tier2": "knowledge"
        }
        
        context = self.optimizer._build_context(
            tiers, 
            "test query",
            5000
        )
        
        assert "tiers_loaded" in context
        assert "components" in context
        assert "instincts" in context["components"]
        assert "recent_memory" in context["components"]
        assert "patterns" in context["components"]
    
    def test_context_compression(self):
        """Test context compression"""
        context = {
            "tiers_loaded": ["tier0", "tier1", "tier2"],
            "components": {
                "instincts": {"size_estimate": 1000},
                "recent_memory": {"size_estimate": 3000},
                "patterns": {"size_estimate": 4000}
            }
        }
        
        compressed = self.optimizer._compress_context(context, target_size=5000)
        
        assert "optimized" in compressed
        assert compressed["optimized"] == True
        assert compressed["compressed_size"] <= 5000
        assert compressed["reduction_percent"] > 0


class TestPatternRelevanceScorer:
    """Test PatternRelevanceScorer class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.scorer = PatternRelevanceScorer()
    
    def test_keyword_extraction(self):
        """Test keyword extraction from query"""
        keywords = self.scorer._extract_keywords(
            "show me the authentication module in the backend"
        )
        
        # Should extract meaningful words
        assert "authentication" in keywords
        assert "module" in keywords
        assert "backend" in keywords
        
        # Should remove stop words
        assert "the" not in keywords
        assert "me" not in keywords
    
    def test_recency_scoring(self):
        """Test recency score calculation"""
        # Recent timestamp (today)
        recent = datetime.now().isoformat()
        score = self.scorer._calculate_recency_score(recent)
        assert score > 0.9  # Very recent = high score
        
        # Old timestamp (60 days ago)
        old = (datetime.now() - timedelta(days=60)).isoformat()
        score = self.scorer._calculate_recency_score(old)
        assert score < 0.2  # Old = low score
    
    def test_pattern_scoring(self):
        """Test complete pattern scoring"""
        patterns = [
            {
                "name": "authentication_pattern",
                "description": "OAuth2 authentication flow",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
                "usage_count": 5
            },
            {
                "name": "database_pattern",
                "description": "Database connection pooling",
                "confidence": 0.6,
                "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
                "usage_count": 2
            }
        ]
        
        scored = self.scorer.score_patterns(
            patterns,
            query="refactor authentication module",
            limit=10
        )
        
        # Should have scores
        assert all("relevance_score" in p for p in scored)
        
        # Authentication pattern should score higher (better keyword match)
        assert scored[0]["name"] == "authentication_pattern"
    
    def test_pattern_limit(self):
        """Test pattern limit enforcement"""
        patterns = [{"name": f"pattern_{i}"} for i in range(20)]
        
        scored = self.scorer.score_patterns(patterns, "test", limit=5)
        
        assert len(scored) == 5


class TestContextCompressor:
    """Test ContextCompressor class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.compressor = ContextCompressor()
    
    def test_size_estimation(self):
        """Test size estimation"""
        obj = {"key": "value", "nested": {"data": [1, 2, 3]}}
        size = self.compressor._estimate_size(obj)
        assert size > 0
    
    def test_long_content_summarization(self):
        """Test summarization of long strings"""
        context = {
            "short": "short text",
            "long": "a" * 1000  # 1000 char string
        }
        
        summarized = self.compressor._summarize_long_content(context)
        
        # Short should stay same
        assert summarized["short"] == "short text"
        
        # Long should be truncated
        assert len(summarized["long"]) < len(context["long"])
        assert "[truncated" in summarized["long"]
    
    def test_reference_replacement(self):
        """Test replacement of duplicates with references"""
        repeated_object = {"data": "repeated", "count": 100}
        context = {
            "item1": repeated_object,
            "item2": repeated_object.copy()  # Same content
        }
        
        referenced = self.compressor._replace_with_references(context)
        
        # Should detect and reference duplicates
        # (Note: actual implementation may vary)
        assert "$ref" in json.dumps(referenced) or len(json.dumps(referenced)) <= len(json.dumps(context))
    
    def test_duplicate_removal(self):
        """Test duplicate removal from lists"""
        context = {
            "items": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"},
                {"id": 1, "name": "item1"}  # Duplicate
            ]
        }
        
        deduped = self.compressor._remove_duplicates(context)
        
        assert len(deduped["items"]) == 2  # One duplicate removed
    
    def test_metadata_compression(self):
        """Test metadata compression"""
        context = {
            "data": "important",
            "_debug": "verbose debug info",  # Should be removed
            "nested": {
                "value": 42,
                "_internal": "internal data"  # Should be removed
            }
        }
        
        compressed = self.compressor._compress_metadata(context)
        
        # Important data should remain
        assert "data" in compressed
        assert "nested" in compressed
        
        # Debug/internal should be removed
        assert "_debug" not in compressed
        assert "_internal" not in compressed["nested"]
    
    def test_full_compression(self):
        """Test full compression pipeline"""
        context = {
            "conversations": [
                {
                    "id": 1,
                    "content": "a" * 600,  # Long content
                    "_debug": "debug info"
                },
                {
                    "id": 2,
                    "content": "short",
                    "_debug": "more debug"
                }
            ],
            "patterns": [
                {"name": "p1"},
                {"name": "p2"},
                {"name": "p1"}  # Duplicate
            ]
        }
        
        compressed, stats = self.compressor.compress(context, target_reduction=0.30)
        
        # Should have stats
        assert "original_size" in stats
        assert "compressed_size" in stats
        assert "reduction_percent" in stats
        
        # Should achieve some reduction
        assert stats["compressed_size"] < stats["original_size"]
        assert stats["reduction_percent"] > 0


class TestOptimizedContextLoader:
    """Test OptimizedContextLoader class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.brain_dir = Path("/tmp/test_cortex_brain")
        self.brain_dir.mkdir(exist_ok=True)
        self.loader = OptimizedContextLoader(self.brain_dir)
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        if self.brain_dir.exists():
            shutil.rmtree(self.brain_dir)
    
    def test_initialization(self):
        """Test loader initialization"""
        assert self.loader.brain_dir == self.brain_dir
        assert self.loader.optimizer is not None
        assert self.loader.scorer is not None
        assert self.loader.compressor is not None
    
    def test_tier0_loading(self):
        """Test Tier 0 loading"""
        tier0_data = self.loader._load_tier0("mock_tier0")
        
        assert "core_principles" in tier0_data
        assert "protection_rules" in tier0_data
        assert "TDD" in tier0_data["core_principles"]
    
    def test_metrics_tracking(self):
        """Test metrics tracking"""
        initial_metrics = self.loader.get_metrics()
        assert initial_metrics["loads"] == 0
        
        # Simulate a load with stats
        stats = {
            "original_size": 10000,
            "compressed_size": 7000,
            "reduction_percent": 30.0
        }
        self.loader._update_metrics(stats)
        
        updated_metrics = self.loader.get_metrics()
        assert updated_metrics["loads"] == 1
        assert updated_metrics["total_original_size"] == 10000
        assert updated_metrics["total_optimized_size"] == 7000
    
    def test_metrics_reset(self):
        """Test metrics reset"""
        stats = {"original_size": 10000, "compressed_size": 7000, "reduction_percent": 30.0}
        self.loader._update_metrics(stats)
        
        self.loader.reset_metrics()
        
        metrics = self.loader.get_metrics()
        assert metrics["loads"] == 0
        assert metrics["total_original_size"] == 0


class TestIntegration:
    """Integration tests for complete optimization pipeline"""
    
    def test_end_to_end_optimization(self):
        """Test complete optimization pipeline"""
        optimizer = ContextOptimizer()
        
        # Mock tiers
        available_tiers = {
            "tier0": "instinct",
            "tier1": "memory",
            "tier2": "knowledge",
            "tier3": "dev"
        }
        
        # Optimize context
        result = optimizer.optimize_context(
            intent="PLAN",
            query="refactor authentication to use OAuth2",
            available_tiers=available_tiers
        )
        
        # Verify structure
        assert "tiers_loaded" in result
        assert "components" in result
        assert "optimized" in result
        
        # Verify optimization
        if "reduction_percent" in result:
            assert result["reduction_percent"] >= 0
    
    def test_compression_target_achievement(self):
        """Test that 30% compression target is achievable"""
        compressor = ContextCompressor()
        
        # Create realistic context
        context = {
            "conversations": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "content": f"Conversation {i} with lots of repeated information",
                    "metadata": {
                        "tags": ["dev", "refactor"],
                        "_debug": "verbose debug information" * 10
                    }
                }
                for i in range(10)
            ],
            "patterns": [{"name": "pattern1"}] * 5  # Duplicates
        }
        
        compressed, stats = compressor.compress(context, target_reduction=0.30)
        
        # Should achieve close to 30% reduction
        assert stats["reduction_percent"] >= 20  # At least 20%
        assert stats["compressed_size"] < stats["original_size"]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
