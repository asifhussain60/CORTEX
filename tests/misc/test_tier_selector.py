"""
Tests for Tier Selector - Response Templates v4.0

Validates tier selection logic for all 4 tiers + success template.
Target: 20+ test cases covering all decision paths.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import yaml

from src.templates.tier_selector import TierSelector
from src.templates.types import ResponseTier, TemplateContext


@pytest.fixture
def template_config():
    """Load response-templates-v4.yaml for testing"""
    config_path = Path("cortex-brain/response-templates-v4.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def tier_selector(template_config):
    """Create TierSelector instance"""
    return TierSelector(template_config)


class TestTier1Instant:
    """Test TIER 1 (INSTANT) selection - factual queries <50 tokens"""
    
    def test_factual_query_with_question_word(self, tier_selector):
        """Test factual query with question word triggers TIER 1"""
        context = TemplateContext(
            operation="query",
            request="what files are in src/utils/?",
            is_factual_query=True,
            estimated_tokens=20,
            requires_explanation=False
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.INSTANT
    
    def test_how_many_query(self, tier_selector):
        """Test 'how many' quantitative query triggers TIER 1"""
        context = TemplateContext(
            operation="query",
            request="how many lines in this file?",
            is_factual_query=True,
            estimated_tokens=10,
            requires_explanation=False
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.INSTANT
    
    def test_where_query(self, tier_selector):
        """Test 'where' location query triggers TIER 1"""
        context = TemplateContext(
            operation="query",
            request="where is the configuration file?",
            is_factual_query=True,
            estimated_tokens=30,
            requires_explanation=False
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.INSTANT
    
    def test_which_query(self, tier_selector):
        """Test 'which' selection query triggers TIER 1"""
        context = TemplateContext(
            operation="query",
            request="which orchestrator handles cleanup?",
            is_factual_query=True,
            estimated_tokens=25,
            requires_explanation=False
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.INSTANT
    
    def test_factual_without_question_word(self, tier_selector):
        """Test factual query without question word still triggers TIER 1"""
        context = TemplateContext(
            operation="lookup",
            request="list all brain tiers",
            is_factual_query=True,
            estimated_tokens=40,
            requires_explanation=False
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.INSTANT
    
    def test_rejects_if_explanation_needed(self, tier_selector):
        """Test TIER 1 rejected if explanation required"""
        context = TemplateContext(
            operation="query",
            request="what is lazy loading?",
            is_factual_query=True,
            estimated_tokens=30,
            requires_explanation=True  # This triggers TIER 2+
        )
        tier = tier_selector.select_tier(context)
        assert tier != ResponseTier.INSTANT  # Should be TIER 2 or higher


class TestTier2Focused:
    """Test TIER 2 (FOCUSED) selection - single concepts 50-200 tokens"""
    
    def test_concept_explanation(self, tier_selector):
        """Test concept explanation triggers TIER 2"""
        context = TemplateContext(
            operation="explain",
            request="explain lazy loading",
            is_single_concept=True,
            estimated_tokens=120,
            requires_explanation=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.FOCUSED
    
    def test_difference_query(self, tier_selector):
        """Test 'difference between X and Y' triggers TIER 2"""
        context = TemplateContext(
            operation="explain",
            request="what's the difference between Tier 1 and Tier 2?",
            is_single_concept=True,
            estimated_tokens=150,
            requires_explanation=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.FOCUSED
    
    def test_how_does_it_work(self, tier_selector):
        """Test 'how does X work' triggers TIER 2"""
        context = TemplateContext(
            operation="explain",
            request="how does namespace isolation work?",
            is_single_concept=True,
            estimated_tokens=180,
            requires_explanation=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.FOCUSED
    
    def test_simple_configuration(self, tier_selector):
        """Test simple configuration guidance triggers TIER 2"""
        context = TemplateContext(
            operation="configure",
            request="how to enable debug logging?",
            is_single_concept=True,
            estimated_tokens=100,
            requires_explanation=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.FOCUSED
    
    def test_token_range_boundary_low(self, tier_selector):
        """Test TIER 2 lower boundary (50 tokens)"""
        context = TemplateContext(
            operation="explain",
            request="explain FIFO queue",
            is_single_concept=True,
            estimated_tokens=50,
            requires_explanation=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.FOCUSED
    
    def test_token_range_boundary_high(self, tier_selector):
        """Test TIER 2 upper boundary (200 tokens)"""
        context = TemplateContext(
            operation="explain",
            request="explain brain architecture",
            is_single_concept=True,
            estimated_tokens=200,
            requires_explanation=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.FOCUSED


class TestTier3Structured:
    """Test TIER 3 (STRUCTURED) selection - multi-faceted 200-600 tokens"""
    
    def test_feature_implementation(self, tier_selector):
        """Test feature implementation triggers TIER 3"""
        context = TemplateContext(
            operation="implement",
            request="implement user authentication",
            requires_multiple_aspects=True,
            estimated_tokens=400,
            has_modifications=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.STRUCTURED
    
    def test_analysis_task(self, tier_selector):
        """Test analysis task triggers TIER 3"""
        context = TemplateContext(
            operation="analyze",
            request="analyze test coverage",
            requires_multiple_aspects=True,
            estimated_tokens=350,
            has_technical_depth=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.STRUCTURED
    
    def test_architecture_review(self, tier_selector):
        """Test architecture review triggers TIER 3"""
        context = TemplateContext(
            operation="review",
            request="review API design",
            requires_multiple_aspects=True,
            estimated_tokens=500,
            has_architecture=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.STRUCTURED
    
    def test_token_range_mid(self, tier_selector):
        """Test TIER 3 mid-range (400 tokens)"""
        context = TemplateContext(
            operation="implement",
            request="add caching layer",
            requires_multiple_aspects=True,
            estimated_tokens=400,
            has_modifications=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.STRUCTURED


class TestTier4Comprehensive:
    """Test TIER 4 (COMPREHENSIVE) selection - complex operations 600+ tokens"""
    
    def test_complex_operation(self, tier_selector):
        """Test complex multi-phase operation triggers TIER 4"""
        context = TemplateContext(
            operation="maintenance",
            request="run system maintenance",
            estimated_tokens=800,
            has_modifications=True,
            has_technical_depth=True,
            has_architecture=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.COMPREHENSIVE
    
    def test_planning_workflow(self, tier_selector):
        """Test planning workflow triggers TIER 4"""
        context = TemplateContext(
            operation="plan",
            request="plan feature implementation",
            estimated_tokens=1000,
            has_architecture=True,
            requires_multiple_aspects=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.COMPREHENSIVE
    
    def test_high_token_count(self, tier_selector):
        """Test high token count (1000+) triggers TIER 4"""
        context = TemplateContext(
            operation="migrate",
            request="migrate database schema",
            estimated_tokens=1200,
            has_modifications=True,
            has_risks=True
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.COMPREHENSIVE
    
    def test_default_fallback(self, tier_selector):
        """Test default fallback to TIER 4 for ambiguous cases"""
        context = TemplateContext(
            operation="unknown",
            request="do something complex",
            estimated_tokens=0  # Unknown complexity
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.COMPREHENSIVE


class TestSuccessTemplate:
    """Test success template override (special case)"""
    
    def test_success_overrides_tier_selection(self, tier_selector):
        """Test success conditions override normal tier selection"""
        context = TemplateContext(
            operation="maintenance",
            request="run system maintenance",
            all_work_complete=True,
            no_errors=True,
            no_user_action_required=True,
            estimated_tokens=100  # Would normally be TIER 2
        )
        tier = tier_selector.select_tier(context)
        assert tier == ResponseTier.COMPREHENSIVE  # Success always uses TIER 4
    
    def test_success_requires_all_conditions(self, tier_selector):
        """Test success requires all 3 conditions to be True"""
        # Missing no_user_action_required
        context = TemplateContext(
            operation="test",
            request="run tests",
            all_work_complete=True,
            no_errors=True,
            no_user_action_required=False,  # Missing this
            estimated_tokens=100
        )
        tier = tier_selector.select_tier(context)
        # Should not trigger success template, fall through to normal selection
        assert tier != ResponseTier.COMPREHENSIVE or not (
            context.all_work_complete and 
            context.no_errors and 
            not context.no_user_action_required
        )


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_token_estimate(self, tier_selector):
        """Test handling of zero token estimate"""
        context = TemplateContext(
            operation="unknown",
            request="do something",
            estimated_tokens=0
        )
        tier = tier_selector.select_tier(context)
        # Should default to TIER 4
        assert tier == ResponseTier.COMPREHENSIVE
    
    def test_empty_request(self, tier_selector):
        """Test handling of empty request"""
        context = TemplateContext(
            operation="test",
            request="",
            estimated_tokens=50
        )
        tier = tier_selector.select_tier(context)
        # Should handle gracefully (default to TIER 4)
        assert tier == ResponseTier.COMPREHENSIVE
    
    def test_exact_boundary_50_tokens(self, tier_selector):
        """Test exact boundary at 50 tokens (TIER 1/2 boundary)"""
        context = TemplateContext(
            operation="query",
            request="what is the answer?",
            is_factual_query=True,
            estimated_tokens=50,
            requires_explanation=False
        )
        tier = tier_selector.select_tier(context)
        # 50 tokens is TIER 1 upper limit OR TIER 2 lower limit
        assert tier in [ResponseTier.INSTANT, ResponseTier.FOCUSED]
    
    def test_exact_boundary_200_tokens(self, tier_selector):
        """Test exact boundary at 200 tokens (TIER 2/3 boundary)"""
        context = TemplateContext(
            operation="explain",
            request="explain something moderately complex",
            is_single_concept=True,
            estimated_tokens=200,
            requires_explanation=True
        )
        tier = tier_selector.select_tier(context)
        # 200 tokens is TIER 2 upper limit OR TIER 3 lower limit
        assert tier in [ResponseTier.FOCUSED, ResponseTier.STRUCTURED]
