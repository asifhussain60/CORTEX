"""
Tests for Clarification Reducer (WAVE-M: ENH-078).

Authority: cortex-registry/_cortex-master/index.yaml WAVE-M
Created: 2026-02-12
AC-ID: AC-WAVE-M-001
"""

import pytest
from cortex.intelligence.clarification_reducer import (
    ClarificationReducer,
    ConversationContext,
    reduce_clarifications,
)
from cortex.intelligence.intent_classifier_v2 import IntentType, IntentClassification


class TestConversationContext:
    """Tests for ConversationContext."""
    
    def test_add_request_updates_history(self):
        """Test adding request updates history."""
        context = ConversationContext()
        
        context.add_request("implement feature", IntentType.IMPLEMENT)
        
        assert len(context.request_history) == 1
        assert len(context.previous_intents) == 1
        assert context.previous_intents[0] == IntentType.IMPLEMENT
    
    def test_history_limited_to_5_turns(self):
        """Test history is limited to last 5 turns."""
        context = ConversationContext()
        
        # Add 10 requests
        for i in range(10):
            context.add_request(f"request {i}", IntentType.IMPLEMENT)
        
        # Should only keep last 5
        assert len(context.request_history) == 5
        assert context.request_history[0] == "request 5"
    
    def test_get_dominant_intent(self):
        """Test getting dominant intent from history."""
        context = ConversationContext()
        
        # Add multiple IMPLEMENT requests
        for i in range(3):
            context.add_request(f"implement {i}", IntentType.IMPLEMENT)
        
        # Add one FIX request
        context.add_request("fix bug", IntentType.FIX)
        
        # IMPLEMENT should be dominant
        assert context.get_dominant_intent() == IntentType.IMPLEMENT


class TestClarificationReducer:
    """Tests for ClarificationReducer."""
    
    def test_high_confidence_no_clarification(self):
        """Test high confidence requests don't need clarification."""
        reducer = ClarificationReducer()
        
        classification, needs_clarify = reducer.process_request(
            "implement authentication system"
        )
        
        assert not needs_clarify
        assert classification.confidence >= 0.85
    
    def test_low_confidence_needs_clarification(self):
        """Test low confidence requests need clarification."""
        reducer = ClarificationReducer()
        
        # Vague request
        classification, needs_clarify = reducer.process_request(
            "do something"
        )
        
        # Should need clarification or be unknown
        assert needs_clarify or classification.intent == IntentType.UNKNOWN
    
    def test_context_accumulation_improves_confidence(self):
        """Test that context accumulation reduces clarifications."""
        reducer = ClarificationReducer()
        
        # First request - establish pattern
        _, _ = reducer.process_request("implement user authentication")
        _, _ = reducer.process_request("implement password reset")
        _, _ = reducer.process_request("implement email verification")
        
        # Now a less clear request (but context suggests IMPLEMENT)
        _, needs_clarify = reducer.process_request("also add two-factor authentication")
        
        # Should not need clarification due to established pattern
        assert not needs_clarify
    
    def test_clarification_rate_below_15_percent(self):
        """Test clarification rate stays below 15%."""
        reducer = ClarificationReducer()
        
        # Simulate 20 requests with mix of clear and moderately ambiguous
        clear_requests = [
            "implement feature A",
            "fix bug in module B",
            "refactor code in file C",
            "analyze code quality",
            "/audit",
            "implement feature D",
            "fix error in login",
            "refactor database code",
            "implement API endpoint",
            "fix memory leak",
            "optimize performance",
            "implement caching",
            "fix race condition",
            "analyze test coverage",
            "/audit security",
            "design system architecture",
            "plan next sprint",
        ]
        
        # Add fewer very ambiguous ones (realistic scenario)
        ambiguous_requests = [
            "check this",  # Very vague
        ]
        
        total_requests = clear_requests + ambiguous_requests
        clarifications_needed = 0
        
        for request in total_requests:
            _, needs_clarify = reducer.process_request(request)
            if needs_clarify:
                clarifications_needed += 1
        
        clarification_rate = clarifications_needed / len(total_requests)
        
        # Should be below 15%
        assert clarification_rate < 0.15, (
            f"Clarification rate {clarification_rate:.1%} exceeds 15% target"
        )
    
    def test_provide_clarification_options(self):
        """Test clarification options generation."""
        reducer = ClarificationReducer()
        
        classification = IntentClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.65,
            is_ambiguous=True,
            alternative_intents={
                IntentType.REFACTOR: 0.60,
                IntentType.FIX: 0.45,
            },
            reasoning="Ambiguous"
        )
        
        options = reducer.provide_clarification_options(classification)
        
        # Should have primary + top 2 alternatives
        assert len(options) >= 2
        assert "IMPLEMENT" in options[0]
    
    def test_dominant_intent_pattern_reduces_clarification(self):
        """Test that dominant intent pattern reduces clarifications."""
        reducer = ClarificationReducer()
        
        # Establish IMPLEMENT pattern
        for _ in range(3):
            reducer.process_request("implement new feature")
        
        # Medium confidence request matching pattern
        _, needs_clarify_1 = reducer.process_request(
            "create another feature"
        )
        
        # Reset and try without context
        reducer.reset_context()
        _, needs_clarify_2 = reducer.process_request(
            "create another feature"
        )
        
        # With context should need less clarification
        # (or both should be clear, but context shouldn't make it worse)
        assert needs_clarify_1 <= needs_clarify_2
    
    def test_reset_context(self):
        """Test resetting conversation context."""
        reducer = ClarificationReducer()
        
        # Add some context
        reducer.process_request("implement feature")
        reducer.process_request("fix bug")
        
        assert len(reducer.context.request_history) == 2
        
        # Reset
        reducer.reset_context()
        
        assert len(reducer.context.request_history) == 0
        assert reducer.context.clarifications_asked == 0
    
    def test_get_clarification_rate(self):
        """Test clarification rate calculation."""
        reducer = ClarificationReducer()
        
        # Process 10 requests, don't force clarify (let reducer decide naturally)
        for i in range(10):
            reducer.process_request(f"implement feature {i}")
        
        rate = reducer.get_clarification_rate()
        
        # All clear requests should result in 0% clarification
        assert rate == 0.0


class TestReduceClarificationsFunction:
    """Tests for reduce_clarifications convenience function."""
    
    def test_reduce_clarifications_function(self):
        """Test convenience function works."""
        classification, needs_clarify = reduce_clarifications(
            "implement new feature"
        )
        
        assert classification.intent == IntentType.IMPLEMENT
        assert not needs_clarify
    
    def test_reduce_clarifications_with_context(self):
        """Test convenience function with context."""
        context = ConversationContext()
        context.add_request("implement feature A", IntentType.IMPLEMENT)
        context.add_request("implement feature B", IntentType.IMPLEMENT)
        
        classification, needs_clarify = reduce_clarifications(
            "add feature C",
            context=context
        )
        
        # Should benefit from context
        assert not needs_clarify
