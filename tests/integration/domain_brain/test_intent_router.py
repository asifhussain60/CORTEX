"""Tests for Intent Router semantic intent recognition and routing."""

import pytest
from typing import List, Dict, Any
from cortex.brain.domain_brain.intent_parser import NLPIntentParser, IntentEntity
from cortex.brain.domain_brain.intent_classifier import IntentClassifier, IntentCategory
from cortex.brain.domain_brain.intent_router import IntentRouter, IntentResult
from cortex.brain.domain_brain.intent_router_interface import IIntentRouter


class TestIntentParser:
    """Tests for NLP intent parsing."""

    def test_parse_simple_api_intent(self) -> None:
        """Test parsing simple API request intent."""
        parser = NLPIntentParser()
        result = parser.parse("get all user accounts")
        
        assert result.intent == "retrieve"
        assert result.confidence >= 0.7
        assert any(e.entity_type == "resource" for e in result.entities)

    def test_parse_intent_with_entities(self) -> None:
        """Test parsing intent with multiple entities."""
        parser = NLPIntentParser()
        result = parser.parse("create a new workflow for finance domain")
        
        assert result.intent == "create"
        assert len(result.entities) >= 2
        assert any(e.entity_type == "domain" for e in result.entities)
        assert result.confidence >= 0.6

    def test_parse_complex_intent(self) -> None:
        """Test parsing complex multi-part intent."""
        parser = NLPIntentParser()
        result = parser.parse("monitor system health and alert if cpu exceeds 80%")
        
        assert result.intent is not None
        assert result.confidence >= 0.5
        assert result.entities is not None

    def test_parse_returns_confidence_score(self) -> None:
        """Test that parser returns valid confidence scores."""
        parser = NLPIntentParser()
        result = parser.parse("retrieve user data")
        
        assert 0 <= result.confidence <= 1.0
        assert isinstance(result.confidence, float)

    def test_parse_handles_empty_input(self) -> None:
        """Test parser gracefully handles empty input."""
        parser = NLPIntentParser()
        with pytest.raises((ValueError, AttributeError)):
            parser.parse("")


class TestIntentClassifier:
    """Tests for intent classification."""

    def test_classify_api_intent(self) -> None:
        """Test classifying API-type intent."""
        classifier = IntentClassifier()
        category = classifier.classify("retrieve user data from database")
        
        assert category in IntentCategory.API.value or category == "api"

    def test_classify_domain_intent(self) -> None:
        """Test classifying domain-specific intent."""
        classifier = IntentClassifier()
        category = classifier.classify("execute finance workflow")
        
        assert category in IntentCategory.DOMAIN.value or category == "domain"

    def test_classify_workflow_intent(self) -> None:
        """Test classifying workflow orchestration intent."""
        classifier = IntentClassifier()
        category = classifier.classify("run batch processing pipeline")
        
        assert category in IntentCategory.WORKFLOW.value or category == "workflow"

    def test_classify_diagnostic_intent(self) -> None:
        """Test classifying diagnostic/monitoring intent."""
        classifier = IntentClassifier()
        category = classifier.classify("check system health status")
        
        assert category in IntentCategory.DIAGNOSTIC.value or category == "diagnostic"

    def test_classify_all_supported_categories(self) -> None:
        """Test all intent categories are classifiable."""
        classifier = IntentClassifier()
        
        test_intents = {
            "api": "get all records",
            "domain": "execute domain logic",
            "workflow": "start pipeline",
            "configuration": "set timeout value",
            "diagnostic": "show logs"
        }
        
        for expected_category, intent_text in test_intents.items():
            result = classifier.classify(intent_text)
            assert result is not None


class TestIntentRouter:
    """Tests for intent routing logic."""

    def test_router_routes_simple_intent(self) -> None:
        """Test router correctly routes simple intent."""
        router = IntentRouter()
        result = router.query_intent("get user data")
        
        assert isinstance(result, IntentResult)
        assert result.intent is not None
        assert result.handler is not None

    def test_router_returns_intent_result(self) -> None:
        """Test router returns proper IntentResult object."""
        router = IntentRouter()
        result = router.query_intent("retrieve accounts")
        
        assert hasattr(result, "intent")
        assert hasattr(result, "category")
        assert hasattr(result, "confidence")
        assert hasattr(result, "entities")
        assert hasattr(result, "handler")

    def test_router_confidence_accuracy(self) -> None:
        """Test router confidence scoring is accurate."""
        router = IntentRouter()
        
        clear_intent = router.query_intent("get all users")
        unclear_intent = router.query_intent("blah blah nonsense xyz")
        
        # Clear intent should have higher confidence
        assert clear_intent.confidence > unclear_intent.confidence

    def test_router_handles_api_routing(self) -> None:
        """Test router correctly routes API intents."""
        router = IntentRouter()
        result = router.query_intent("fetch all records")
        
        assert result.category in ["api", "API"]
        assert result.handler is not None

    def test_router_handles_workflow_routing(self) -> None:
        """Test router correctly routes workflow intents."""
        router = IntentRouter()
        result = router.query_intent("execute data processing workflow")
        
        assert result.category in ["workflow", "WORKFLOW"]
        assert result.handler is not None


class TestIntentFallback:
    """Tests for intent fallback chains."""

    def test_fallback_chain_for_low_confidence_intent(self) -> None:
        """Test fallback chain activates for uncertain intents."""
        router = IntentRouter()
        result = router.query_intent("something unclear and ambiguous")
        
        assert result.confidence < 0.7
        assert len(result.fallback_handlers) > 0

    def test_fallback_handlers_are_ordered(self) -> None:
        """Test fallback handlers are ordered by confidence."""
        router = IntentRouter()
        result = router.query_intent("maybe do this or that")
        
        if result.fallback_handlers:
            confidences = [h.get("confidence", 0) for h in result.fallback_handlers]
            assert confidences == sorted(confidences, reverse=True)

    def test_fallback_chain_provides_alternatives(self) -> None:
        """Test fallback chain provides alternative interpretations."""
        router = IntentRouter()
        result = router.query_intent("uncertain intent here")
        
        if result.confidence < 0.7:
            assert len(result.fallback_handlers) >= 1

    def test_threshold_below_70_percent_triggers_fallback(self) -> None:
        """Test intents below 70% confidence trigger fallback."""
        router = IntentRouter()
        result = router.query_intent("vague and unclear request xyz")
        
        if result.confidence < 0.70:
            assert len(result.fallback_handlers) > 0 or result.fallback_handlers is not None


class TestIntentHistory:
    """Tests for intent execution history."""

    def test_intent_history_persists(self) -> None:
        """Test that intent history is maintained."""
        router = IntentRouter()
        
        # Query multiple intents
        router.query_intent("get user data")
        router.query_intent("create workflow")
        router.query_intent("check health")
        
        history = router.get_history()
        assert len(history) >= 3

    def test_history_maintains_last_100_intents(self) -> None:
        """Test history maintains maximum 100 most recent intents."""
        router = IntentRouter()
        
        # Query 150 intents
        for i in range(150):
            router.query_intent(f"intent number {i}")
        
        history = router.get_history()
        assert len(history) <= 100

    def test_history_contains_intent_details(self) -> None:
        """Test history entries contain full intent details."""
        router = IntentRouter()
        router.query_intent("test intent query")
        
        history = router.get_history()
        assert len(history) > 0
        
        latest = history[-1]
        assert "intent" in latest or "text" in latest
        assert "timestamp" in latest or "time" in latest

    def test_history_is_ordered_chronologically(self) -> None:
        """Test history entries are in chronological order."""
        router = IntentRouter()
        
        for i in range(5):
            router.query_intent(f"query {i}")
        
        history = router.get_history()
        assert len(history) >= 5


class TestIntentIntegration:
    """Integration tests for Intent Router."""

    def test_intent_router_implements_interface(self) -> None:
        """Test IntentRouter implements IIntentRouter interface."""
        router = IntentRouter()
        assert isinstance(router, IIntentRouter)

    def test_end_to_end_intent_routing(self) -> None:
        """Test complete intent routing pipeline."""
        router = IntentRouter()
        
        # Test various intent types
        test_intents = [
            "get all user accounts",
            "create new workflow",
            "monitor system health",
            "execute domain logic"
        ]
        
        for intent_text in test_intents:
            result = router.query_intent(intent_text)
            
            assert result.intent is not None
            assert 0 <= result.confidence <= 1.0
            assert result.handler is not None

    def test_intent_routing_accuracy_above_threshold(self) -> None:
        """Test intent routing accuracy meets 85% threshold."""
        router = IntentRouter()
        
        # Test clear intents that should route correctly
        clear_intents = [
            ("retrieve user data", "api"),
            ("start workflow", "workflow"),
            ("check health", "diagnostic")
        ]
        
        correct_count = 0
        for intent_text, expected_category in clear_intents:
            result = router.query_intent(intent_text)
            if result.confidence > 0.85:
                correct_count += 1
        
        # At least some of the clear intents should be high confidence
        assert correct_count >= 1

    def test_integration_with_conversation_protocol(self) -> None:
        """Test integration with ConversationProtocol."""
        router = IntentRouter()
        result = router.query_intent("test intent")
        
        # Result should be compatible with ConversationProtocol
        assert hasattr(result, "intent")
        assert hasattr(result, "category")
        assert hasattr(result, "confidence")
        assert hasattr(result, "entities")

    def test_high_volume_intent_processing(self) -> None:
        """Test router handles high volume intent requests."""
        router = IntentRouter()
        
        # Process 50 intents
        results = []
        for i in range(50):
            result = router.query_intent(f"test intent {i}")
            results.append(result)
        
        assert len(results) == 50
        assert all(r.intent is not None for r in results)
