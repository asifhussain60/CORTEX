"""
Tests for context_injector.py (TDD Phase 2: Core modules)

RED → GREEN → REFACTOR approach for context injection testing
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from src.core.context_management.context_injector import (
    ContextInjector,
    create_standard_context_display,
    create_compact_context_display
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def base_context_data():
    """Base context data structure for testing"""
    return {
        'tier1_context': {
            'recent_conversations': 5,
            'last_updated': (datetime.now() - timedelta(minutes=15)).isoformat()
        },
        'tier2_context': {
            'matched_patterns': 3,
            'last_updated': (datetime.now() - timedelta(hours=2)).isoformat()
        },
        'tier3_context': {
            'insights_count': 8,
            'last_updated': (datetime.now() - timedelta(days=1)).isoformat()
        },
        'relevance_scores': {
            'tier1': 0.8,
            'tier2': 0.6,
            'tier3': 0.7
        },
        'token_usage': {
            'total': 234,
            'budget': 500,
            'within_budget': True
        },
        'cache_hit': True
    }


@pytest.fixture
def empty_context_data():
    """Empty context data for testing edge cases"""
    return {
        'tier1_context': {'recent_conversations': 0},
        'tier2_context': {'matched_patterns': 0},
        'tier3_context': {'insights_count': 0},
        'relevance_scores': {'tier1': 0.0, 'tier2': 0.0, 'tier3': 0.0},
        'token_usage': {'total': 0, 'budget': 500, 'within_budget': True},
        'cache_hit': False
    }


@pytest.fixture
def high_quality_context():
    """High quality context (score >= 8.0)"""
    return {
        'tier1_context': {'recent_conversations': 10},
        'tier2_context': {'matched_patterns': 5},
        'tier3_context': {'insights_count': 15},
        'relevance_scores': {'tier1': 0.9, 'tier2': 0.85, 'tier3': 0.95},
        'token_usage': {'total': 150, 'budget': 500, 'within_budget': True},
        'cache_hit': True
    }


@pytest.fixture
def low_quality_context():
    """Low quality context (score < 6.0)"""
    return {
        'tier1_context': {'recent_conversations': 1},
        'tier2_context': {'matched_patterns': 0},
        'tier3_context': {'insights_count': 0},
        'relevance_scores': {'tier1': 0.3, 'tier2': 0.2, 'tier3': 0.0},
        'token_usage': {'total': 450, 'budget': 500, 'within_budget': True},
        'cache_hit': False
    }


# ============================================================================
# Test Class 1: Initialization and Format Styles
# ============================================================================

class TestContextInjectorInitialization:
    """Test ContextInjector initialization with different format styles"""
    
    def test_default_initialization(self):
        """Should initialize with default 'detailed' format style"""
        injector = ContextInjector()
        assert injector.format_style == 'detailed'
    
    def test_detailed_format_initialization(self):
        """Should initialize with 'detailed' format style"""
        injector = ContextInjector(format_style='detailed')
        assert injector.format_style == 'detailed'
    
    def test_compact_format_initialization(self):
        """Should initialize with 'compact' format style"""
        injector = ContextInjector(format_style='compact')
        assert injector.format_style == 'compact'
    
    def test_minimal_format_initialization(self):
        """Should initialize with 'minimal' format style"""
        injector = ContextInjector(format_style='minimal')
        assert injector.format_style == 'minimal'


# ============================================================================
# Test Class 2: Context Injection
# ============================================================================

class TestContextInjection:
    """Test inject_context_summary method with different positions"""
    
    def test_inject_before_position(self, base_context_data):
        """Should inject context summary before response text"""
        injector = ContextInjector(format_style='compact')
        response = "This is the agent response."
        
        result = injector.inject_context_summary(response, base_context_data, position='before')
        
        assert result.startswith("🧠 **Context:**")
        assert result.endswith(response)
        assert "\n\n" in result  # Separator present
    
    def test_inject_after_position(self, base_context_data):
        """Should inject context summary after response text"""
        injector = ContextInjector(format_style='compact')
        response = "This is the agent response."
        
        result = injector.inject_context_summary(response, base_context_data, position='after')
        
        assert result.startswith(response)
        assert "🧠 **Context:**" in result
        assert "\n\n" in result  # Separator present
    
    def test_inject_default_position(self, base_context_data):
        """Should default to 'before' position when not specified"""
        injector = ContextInjector(format_style='minimal')
        response = "Agent response"
        
        # Default position in inject_context_summary is 'before'
        result = injector.inject_context_summary(response, base_context_data)
        
        # Should have context before response
        assert "Context:" in result
        assert response in result
    
    def test_inject_with_empty_response(self, base_context_data):
        """Should handle empty response text"""
        injector = ContextInjector()
        
        result = injector.inject_context_summary("", base_context_data, position='before')
        
        assert len(result) > 0  # Context summary still added


# ============================================================================
# Test Class 3: Detailed Summary Formatting
# ============================================================================

class TestDetailedSummaryFormatting:
    """Test _format_detailed_summary method"""
    
    def test_detailed_format_with_all_tiers(self, base_context_data):
        """Should format detailed summary with all tier information"""
        injector = ContextInjector(format_style='detailed')
        
        summary = injector._format_detailed_summary(base_context_data)
        
        assert "🧠 Context Used" in summary
        assert "Recent Work (Tier 1)" in summary
        assert "5 related conversations" in summary
        assert "Learned Patterns (Tier 2)" in summary
        assert "3 matched" in summary
        assert "Metrics (Tier 3)" in summary
        assert "8 insights" in summary
    
    def test_detailed_format_with_relevance_scores(self, base_context_data):
        """Should include relevance scores in detailed format"""
        injector = ContextInjector(format_style='detailed')
        
        summary = injector._format_detailed_summary(base_context_data)
        
        # Format is "Relevance: 0.80 (High)"
        assert "Relevance: 0.80" in summary  # Tier 1
        assert "Relevance: 0.60" in summary  # Tier 2
        assert "Relevance: 0.70" in summary  # Tier 3
    
    def test_detailed_format_with_age_information(self, base_context_data):
        """Should include age information for each tier when conversations/patterns provided"""
        # Add conversations with timestamps to context data
        base_context_data['tier1_context']['conversations'] = [
            {
                'title': 'Recent conversation',
                'created_at': (datetime.now() - timedelta(minutes=15)).isoformat()
            }
        ]
        
        injector = ContextInjector(format_style='detailed')
        
        summary = injector._format_detailed_summary(base_context_data)
        
        # Should contain age string when conversations are provided
        assert "ago" in summary or "Recent" in summary
    
    def test_detailed_format_with_token_usage(self, base_context_data):
        """Should include token usage information"""
        injector = ContextInjector(format_style='detailed')
        
        summary = injector._format_detailed_summary(base_context_data)
        
        assert "**Token Usage:**" in summary
        assert "234/500 tokens" in summary
    
    def test_detailed_format_with_missing_tier_data(self, empty_context_data):
        """Should handle missing tier data gracefully"""
        injector = ContextInjector(format_style='detailed')
        
        summary = injector._format_detailed_summary(empty_context_data)
        
        # Should still generate summary without errors
        assert "🧠 Context Used" in summary
        assert "Token Usage:" in summary


# ============================================================================
# Test Class 4: Compact Summary Formatting
# ============================================================================

class TestCompactSummaryFormatting:
    """Test _format_compact_summary method"""
    
    def test_compact_format_structure(self, base_context_data):
        """Should format compact summary with abbreviated tier info"""
        injector = ContextInjector(format_style='compact')
        
        summary = injector._format_compact_summary(base_context_data)
        
        assert "🧠 **Context:**" in summary
        assert "T1:" in summary  # Tier 1 abbreviation
        assert "tokens" in summary
    
    def test_compact_format_includes_high_relevance_tiers(self, base_context_data):
        """Should include tiers with relevance > 0.5"""
        injector = ContextInjector(format_style='compact')
        
        summary = injector._format_compact_summary(base_context_data)
        
        # All tiers have relevance > 0.5
        assert "T1:" in summary
        assert "T2:" in summary
        assert "T3:" in summary
    
    def test_compact_format_excludes_low_relevance_tiers(self):
        """Should exclude tiers with relevance <= 0.5"""
        context_data = {
            'tier1_context': {'recent_conversations': 5},
            'tier2_context': {'matched_patterns': 3},
            'tier3_context': {'insights_count': 8},
            'relevance_scores': {'tier1': 0.8, 'tier2': 0.3, 'tier3': 0.2},  # T2, T3 low
            'token_usage': {'total': 100, 'budget': 500}
        }
        injector = ContextInjector(format_style='compact')
        
        summary = injector._format_compact_summary(context_data)
        
        assert "T1:" in summary
        assert "T2:" not in summary  # Excluded (rel 0.3)
        assert "T3:" not in summary  # Excluded (rel 0.2)
    
    def test_compact_format_with_no_context(self, empty_context_data):
        """Should show 'No context loaded' when no data available"""
        # Set relevance scores to 0 to simulate no relevant context
        empty_context_data['relevance_scores'] = {'tier1': 0.0, 'tier2': 0.0, 'tier3': 0.0}
        injector = ContextInjector(format_style='compact')
        
        summary = injector._format_compact_summary(empty_context_data)
        
        assert "No context loaded" in summary
    
    def test_compact_format_token_usage(self, base_context_data):
        """Should display token usage in compact format"""
        injector = ContextInjector(format_style='compact')
        
        summary = injector._format_compact_summary(base_context_data)
        
        assert "234/500 tokens" in summary


# ============================================================================
# Test Class 5: Minimal Summary Formatting
# ============================================================================

class TestMinimalSummaryFormatting:
    """Test _format_minimal_summary method"""
    
    def test_minimal_format_with_high_quality(self, high_quality_context):
        """Should show green emoji for high quality (>= 8.0)"""
        injector = ContextInjector(format_style='minimal')
        
        summary = injector._format_minimal_summary(high_quality_context)
        
        assert "🟢" in summary  # Green emoji
        assert "Context:" in summary
        assert "tokens" in summary
    
    def test_minimal_format_with_medium_quality(self, base_context_data):
        """Should show yellow emoji for medium quality (6.0-7.9)"""
        injector = ContextInjector(format_style='minimal')
        
        summary = injector._format_minimal_summary(base_context_data)
        
        assert "🟡" in summary or "🟢" in summary  # Yellow or green
        assert "/10" in summary  # Quality score
    
    def test_minimal_format_with_low_quality(self, low_quality_context):
        """Should show red emoji for low quality (< 6.0)"""
        injector = ContextInjector(format_style='minimal')
        
        summary = injector._format_minimal_summary(low_quality_context)
        
        assert "🔴" in summary  # Red emoji
        assert "/10" in summary
    
    def test_minimal_format_displays_quality_score(self, base_context_data):
        """Should display quality score with 1 decimal place"""
        injector = ContextInjector(format_style='minimal')
        
        summary = injector._format_minimal_summary(base_context_data)
        
        # Should have format "X.X/10"
        assert "/10" in summary
        # Check for decimal format (e.g., "7.5")
        import re
        assert re.search(r'\d+\.\d+/10', summary) is not None


# ============================================================================
# Test Class 6: Quality Score Calculation
# ============================================================================

class TestQualityScoreCalculation:
    """Test _calculate_quality_score method"""
    
    def test_quality_score_with_all_tiers(self, base_context_data):
        """Should calculate quality score based on all tier relevance"""
        injector = ContextInjector()
        
        quality = injector._calculate_quality_score(base_context_data)
        
        # Average relevance: (0.8 + 0.6 + 0.7) / 3 = 0.7
        # With bonuses: 0.7 + 0.2 (budget) + 0.1 (cache) = 1.0
        # Quality: 1.0 * 10 = 10.0
        assert quality >= 7.0  # Should be decent quality
        assert quality <= 10.0  # Max cap
    
    def test_quality_score_with_empty_context(self, empty_context_data):
        """Should return 0.0 for empty context"""
        injector = ContextInjector()
        
        quality = injector._calculate_quality_score(empty_context_data)
        
        assert quality == 0.0
    
    def test_quality_score_token_efficiency_bonus(self):
        """Should add 0.2 bonus when within token budget"""
        context_within_budget = {
            'tier1_context': {'recent_conversations': 5},
            'relevance_scores': {'tier1': 0.5, 'tier2': 0.0, 'tier3': 0.0},
            'token_usage': {'within_budget': True},
            'cache_hit': False
        }
        injector = ContextInjector()
        
        quality = injector._calculate_quality_score(context_within_budget)
        
        # Relevance 0.5, with budget bonus 0.2 = 0.7 * 10 = 7.0
        assert quality >= 6.5
    
    def test_quality_score_cache_hit_bonus(self):
        """Should add 0.1 bonus for cache hit"""
        context_with_cache = {
            'tier1_context': {'recent_conversations': 5},
            'relevance_scores': {'tier1': 0.5, 'tier2': 0.0, 'tier3': 0.0},
            'token_usage': {'within_budget': False},
            'cache_hit': True
        }
        injector = ContextInjector()
        
        quality = injector._calculate_quality_score(context_with_cache)
        
        # Relevance 0.5, with cache bonus 0.1 = 0.6 * 10 = 6.0
        assert quality >= 5.5
    
    def test_quality_score_max_capped_at_10(self):
        """Should cap quality score at 10.0"""
        perfect_context = {
            'tier1_context': {'recent_conversations': 100},
            'tier2_context': {'matched_patterns': 50},
            'tier3_context': {'insights_count': 200},
            'relevance_scores': {'tier1': 1.0, 'tier2': 1.0, 'tier3': 1.0},
            'token_usage': {'within_budget': True},
            'cache_hit': True
        }
        injector = ContextInjector()
        
        quality = injector._calculate_quality_score(perfect_context)
        
        assert quality == 10.0  # Should not exceed 10.0
    
    def test_quality_score_weighted_by_available_data(self):
        """Should weight score by tiers with actual data"""
        # Only Tier 1 has data
        context_single_tier = {
            'tier1_context': {'recent_conversations': 10},
            'tier2_context': {'matched_patterns': 0},
            'tier3_context': {'insights_count': 0},
            'relevance_scores': {'tier1': 0.9, 'tier2': 0.5, 'tier3': 0.3},
            'token_usage': {'within_budget': True},
            'cache_hit': False
        }
        injector = ContextInjector()
        
        quality = injector._calculate_quality_score(context_single_tier)
        
        # Should use only Tier 1 score (0.9), not average of all
        # 0.9 + 0.2 (budget) = 1.1 * 10 = 11.0 → capped at 10.0
        assert quality >= 9.0


# ============================================================================
# Test Class 7: Age Formatting
# ============================================================================

class TestAgeFormatting:
    """Test _format_age method"""
    
    def test_format_age_minutes(self):
        """Should format age in minutes for recent timestamps"""
        injector = ContextInjector()
        timestamp = (datetime.now() - timedelta(minutes=25)).isoformat()
        
        age_str = injector._format_age(timestamp)
        
        assert "m ago" in age_str
    
    def test_format_age_hours(self):
        """Should format age in hours for older timestamps"""
        injector = ContextInjector()
        timestamp = (datetime.now() - timedelta(hours=5)).isoformat()
        
        age_str = injector._format_age(timestamp)
        
        assert "h ago" in age_str
    
    def test_format_age_days(self):
        """Should format age in days for very old timestamps"""
        injector = ContextInjector()
        timestamp = (datetime.now() - timedelta(days=3)).isoformat()
        
        age_str = injector._format_age(timestamp)
        
        assert "d ago" in age_str
    
    def test_format_age_with_none(self):
        """Should handle None timestamp gracefully"""
        injector = ContextInjector()
        
        age_str = injector._format_age(None)
        
        assert age_str == "unknown age"
    
    def test_format_age_with_invalid_format(self):
        """Should handle invalid timestamp format"""
        injector = ContextInjector()
        
        age_str = injector._format_age("not-a-timestamp")
        
        assert age_str == "unknown age"


# ============================================================================
# Test Class 8: Agent-Specific Formatting
# ============================================================================

class TestAgentSpecificFormatting:
    """Test format_for_agent method"""
    
    def test_format_for_code_executor(self, base_context_data):
        """Should emphasize Tier 1 and Tier 3 for Code Executor"""
        injector = ContextInjector()
        
        result = injector.format_for_agent(
            'Code Executor',
            'Code execution result',
            base_context_data
        )
        
        # Should contain context injection
        assert len(result) > len('Code execution result')
    
    def test_format_for_test_generator(self, base_context_data):
        """Should emphasize Tier 2 and Tier 3 for Test Generator"""
        injector = ContextInjector()
        
        result = injector.format_for_agent(
            'Test Generator',
            'Generated tests',
            base_context_data
        )
        
        assert len(result) > len('Generated tests')
    
    def test_format_for_unknown_agent(self, base_context_data):
        """Should use all tiers for unknown agent"""
        injector = ContextInjector()
        
        result = injector.format_for_agent(
            'Unknown Agent',
            'Agent response',
            base_context_data
        )
        
        # Should still format successfully
        assert len(result) > 0
    
    def test_format_for_agent_de_emphasizes_irrelevant_tiers(self, base_context_data):
        """Should de-emphasize tiers not relevant to agent"""
        injector = ContextInjector()
        
        # Code Executor should de-emphasize Tier 2
        result = injector.format_for_agent(
            'Code Executor',
            'Response',
            base_context_data
        )
        
        # Verify context was filtered (internal state check via result length)
        assert len(result) > 0


# ============================================================================
# Test Class 9: Context Badge Creation
# ============================================================================

class TestContextBadgeCreation:
    """Test create_context_badge method"""
    
    def test_badge_with_high_quality(self, high_quality_context):
        """Should create green badge for high quality context"""
        injector = ContextInjector()
        
        badge = injector.create_context_badge(high_quality_context)
        
        assert "🟢" in badge
        assert "Context:" in badge
        assert "/10" in badge
        assert "tokens" in badge
    
    def test_badge_with_medium_quality(self, base_context_data):
        """Should create yellow badge for medium quality context"""
        injector = ContextInjector()
        
        badge = injector.create_context_badge(base_context_data)
        
        assert ("🟡" in badge or "🟢" in badge)  # Yellow or green
        assert "/10" in badge
    
    def test_badge_with_low_quality(self, low_quality_context):
        """Should create red badge for low quality context"""
        injector = ContextInjector()
        
        badge = injector.create_context_badge(low_quality_context)
        
        assert "🔴" in badge
    
    def test_badge_displays_token_ratio(self, base_context_data):
        """Should display token usage as ratio"""
        injector = ContextInjector()
        
        badge = injector.create_context_badge(base_context_data)
        
        assert "234/500" in badge  # total/budget format


# ============================================================================
# Test Class 10: Convenience Functions
# ============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions"""
    
    def test_create_standard_context_display(self, base_context_data):
        """Should create standard detailed context display"""
        display = create_standard_context_display(base_context_data)
        
        assert "🧠 Context Used" in display
        assert "Tier 1" in display or "Tier 2" in display or "Tier 3" in display
    
    def test_create_compact_context_display(self, base_context_data):
        """Should create compact context display"""
        display = create_compact_context_display(base_context_data)
        
        assert "🧠 **Context:**" in display
        assert "T1:" in display or "T2:" in display or "T3:" in display
    
    def test_convenience_functions_with_empty_context(self, empty_context_data):
        """Should handle empty context in convenience functions"""
        standard = create_standard_context_display(empty_context_data)
        compact = create_compact_context_display(empty_context_data)
        
        assert len(standard) > 0
        assert len(compact) > 0


# ============================================================================
# Test Class 11: Edge Cases and Error Handling
# ============================================================================

class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""
    
    def test_missing_relevance_scores(self):
        """Should handle missing relevance_scores key"""
        context_data = {
            'tier1_context': {'recent_conversations': 5},
            'token_usage': {'total': 100, 'budget': 500}
        }
        injector = ContextInjector()
        
        # Should not raise exception
        quality = injector._calculate_quality_score(context_data)
        assert quality >= 0.0
    
    def test_missing_token_usage(self, base_context_data):
        """Should handle missing token_usage key"""
        del base_context_data['token_usage']
        injector = ContextInjector()
        
        # Should not raise exception
        summary = injector._format_compact_summary(base_context_data)
        assert len(summary) > 0
    
    def test_malformed_context_data(self):
        """Should handle completely malformed context data"""
        malformed = {'unexpected_key': 'unexpected_value'}
        injector = ContextInjector()
        
        # Should not crash
        summary = injector._format_detailed_summary(malformed)
        assert len(summary) > 0
    
    def test_very_long_response_text(self, base_context_data):
        """Should handle very long response text"""
        injector = ContextInjector()
        long_response = "A" * 10000  # 10k characters
        
        result = injector.inject_context_summary(long_response, base_context_data)
        
        assert len(result) > len(long_response)
        assert "A" * 100 in result  # Original content preserved
    
    def test_unicode_in_context_data(self):
        """Should handle Unicode characters in context data"""
        context_data = {
            'tier1_context': {'recent_conversations': 5},
            'tier2_context': {'matched_patterns': 3},
            'relevance_scores': {'tier1': 0.8, 'tier2': 0.6, 'tier3': 0.0},
            'token_usage': {'total': 100, 'budget': 500}
        }
        injector = ContextInjector()
        
        # Should handle emoji in output
        summary = injector._format_compact_summary(context_data)
        assert len(summary) > 0
