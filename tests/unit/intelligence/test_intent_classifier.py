"""
Tests for Enhanced Intent Classifier v2 (WAVE-M: ENH-078).

Authority: cortex-registry/_cortex-master/index.yaml WAVE-M
Created: 2026-02-12
AC-ID: AC-WAVE-M-001
"""

import pytest
from cortex.intelligence.intent_classifier import (
    IntentClassifierV2,
    IntentType,
    IntentClassification,
    classify_intent,
)


class TestIntentClassifierV2:
    """Tests for IntentClassifierV2 class."""
    
    def test_classify_implement_intent_high_confidence(self):
        """Test classifying IMPLEMENT intent with high confidence."""
        classifier = IntentClassifierV2()
        
        result = classifier.classify("implement authentication system")
        
        assert result.intent == IntentType.IMPLEMENT
        assert result.confidence >= 0.85
        assert not result.needs_clarification()
    
    def test_classify_fix_intent_high_confidence(self):
        """Test classifying FIX intent with high confidence."""
        classifier = IntentClassifierV2()
        
        result = classifier.classify("fix the login bug that's preventing users from signing in")
        
        assert result.intent == IntentType.FIX
        assert result.confidence >= 0.85
        assert not result.needs_clarification()
    
    def test_classify_refactor_intent(self):
        """Test classifying REFACTOR intent."""
        classifier = IntentClassifierV2()
        
        result = classifier.classify("refactor the database connection code to improve performance")
        
        assert result.intent == IntentType.REFACTOR
        assert result.confidence >= 0.75
    
    def test_classify_analyze_intent(self):
        """Test classifying ANALYZE intent."""
        classifier = IntentClassifierV2()
        
        result = classifier.classify("analyze the code quality of the authentication module")
        
        assert result.intent == IntentType.ANALYZE
        assert result.confidence >= 0.75
    
    def test_classify_audit_intent(self):
        """Test classifying AUDIT intent."""
        classifier = IntentClassifierV2()
        
        result = classifier.classify("/audit")
        
        assert result.intent == IntentType.AUDIT
        assert result.confidence >= 0.85
    
    def test_classify_ambiguous_triggers_clarification(self):
        """Test that ambiguous requests trigger clarification."""
        classifier = IntentClassifierV2()
        
        # Vague request that could be multiple intents
        result = classifier.classify("change the login code")
        
        # Should need clarification (could be FIX, REFACTOR, or IMPLEMENT)
        assert result.needs_clarification() or result.confidence < 0.75
    
    def test_classify_with_context_improves_confidence(self):
        """Test that context from previous turn improves confidence."""
        classifier = IntentClassifierV2()
        
        # Without context
        result_no_context = classifier.classify("also add validation")
        
        # With context (previous intent was IMPLEMENT)
        result_with_context = classifier.classify(
            "also add validation",
            context={"previous_intent": "implement"}
        )
        
        # Context should improve confidence
        assert result_with_context.confidence >= result_no_context.confidence
    
    def test_classify_query_intent(self):
        """Test classifying QUERY intent."""
        classifier = IntentClassifierV2()
        
        result = classifier.classify("what is the purpose of the MasterOrchestrator?")
        
        assert result.intent == IntentType.QUERY
        assert result.confidence >= 0.75
    
    def test_classify_empty_request(self):
        """Test classifying empty request."""
        classifier = IntentClassifierV2()
        
        result = classifier.classify("")
        
        assert result.intent == IntentType.UNKNOWN
        assert result.confidence == 0.0
        assert result.is_ambiguous
    
    def test_classify_command_prefix(self):
        """Test that command prefixes are strongly recognized."""
        classifier = IntentClassifierV2()
        
        # Test various command prefixes
        commands = [
            ("/implement feature", IntentType.IMPLEMENT),
            ("/fix bug", IntentType.FIX),
            ("/refactor code", IntentType.REFACTOR),
            ("/analyze module", IntentType.ANALYZE),
            ("/audit", IntentType.AUDIT),
            ("/plan phase", IntentType.PLAN),
        ]
        
        for command, expected_intent in commands:
            result = classifier.classify(command)
            assert result.intent == expected_intent
            assert result.confidence >= 0.85
    
    def test_alternative_intents_populated(self):
        """Test that alternative intents are populated."""
        classifier = IntentClassifierV2()
        
        # Request with multiple possible intents
        result = classifier.classify("improve the code quality")
        
        # Should have alternatives
        assert len(result.alternative_intents) > 0
        
        # Alternatives should have scores
        for intent, score in result.alternative_intents.items():
            assert 0.0 <= score <= 1.0
    
    def test_accuracy_benchmark_90_percent(self):
        """Test that classifier achieves 90% accuracy on benchmark set."""
        classifier = IntentClassifierV2()
        
        # Benchmark dataset (labeled requests)
        benchmark_data = [
            ("implement user authentication", IntentType.IMPLEMENT),
            ("fix the database connection error", IntentType.FIX),
            ("refactor the API endpoints", IntentType.REFACTOR),
            ("analyze code coverage", IntentType.ANALYZE),
            ("/audit", IntentType.AUDIT),
            ("design a caching layer", IntentType.DESIGN),
            ("plan the next sprint", IntentType.PLAN),
            ("what is CORTEX?", IntentType.QUERY),
            ("create a new feature", IntentType.IMPLEMENT),
            ("debug the login flow", IntentType.FIX),
            ("optimize database queries", IntentType.REFACTOR),
            ("examine the test results", IntentType.ANALYZE),
            ("security audit of API", IntentType.AUDIT),
            ("how does MCP work?", IntentType.QUERY),
            ("/implement lazy loading", IntentType.IMPLEMENT),
            ("resolve merge conflicts", IntentType.FIX),
            ("improve error handling", IntentType.REFACTOR),
            ("review pull request", IntentType.ANALYZE),
            ("plan phase 81", IntentType.PLAN),
            ("explain agent architecture", IntentType.QUERY),
        ]
        
        correct = 0
        total = len(benchmark_data)
        
        for request, expected_intent in benchmark_data:
            result = classifier.classify(request)
            if result.intent == expected_intent:
                correct += 1
        
        accuracy = correct / total
        
        # Should achieve at least 90% accuracy
        assert accuracy >= 0.90, f"Accuracy {accuracy:.1%} below 90% target"


class TestClassifyIntentFunction:
    """Tests for classify_intent convenience function."""
    
    def test_classify_intent_function(self):
        """Test convenience function works."""
        result = classify_intent("implement new feature")
        
        assert isinstance(result, IntentClassification)
        assert result.intent == IntentType.IMPLEMENT
    
    def test_classify_intent_with_context(self):
        """Test convenience function with context."""
        result = classify_intent(
            "also add tests",
            context={"previous_intent": "implement"}
        )
        
        assert isinstance(result, IntentClassification)
        # Should be IMPLEMENT due to context
        assert result.intent == IntentType.IMPLEMENT


class TestIntentClassification:
    """Tests for IntentClassification dataclass."""
    
    def test_needs_clarification_low_confidence(self):
        """Test needs_clarification for low confidence."""
        classification = IntentClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.6,
            is_ambiguous=False,
            alternative_intents={},
            reasoning="Low confidence"
        )
        
        # Should need clarification (below 0.75 threshold)
        assert classification.needs_clarification()
    
    def test_needs_clarification_ambiguous(self):
        """Test needs_clarification for ambiguous."""
        classification = IntentClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.8,
            is_ambiguous=True,
            alternative_intents={IntentType.REFACTOR: 0.75},
            reasoning="Ambiguous"
        )
        
        # Should need clarification (ambiguous)
        assert classification.needs_clarification()
    
    def test_no_clarification_needed(self):
        """Test no clarification needed for high confidence."""
        classification = IntentClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.9,
            is_ambiguous=False,
            alternative_intents={},
            reasoning="High confidence"
        )
        
        # Should NOT need clarification
        assert not classification.needs_clarification()
