# AC_START: AC-PHASE57-S3-001
# Description: Architecture Classification Engine Tests
# Authority: CORE-008 TDD-first
# Stage: S3 - Architecture Classification (10 tests)

import pytest
from typing import Dict, List, Any
from cortex.intelligence.patterns.base import PatternMatch


class TestArchitectureClassifier:
    """Test ArchitectureClassifier for 7+ architecture types (T1-T10)."""

    def test_classifier_instantiation(self):
        """
        Verify ArchitectureClassifier can be instantiated.
        
        Requirement: ArchitectureClassifier() creates instance
        Expected: Classifier instance created
        """
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        assert classifier is not None

    def test_mvc_architecture_detection(self):
        """Verify MVC architecture detection (Models + Views + Controllers)."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        patterns = [
            PatternMatch("Model", 0.9, "app/models.py:1", {}),
            PatternMatch("View", 0.9, "app/views.py:1", {}),
            PatternMatch("Controller", 0.9, "app/controllers.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert result is not None
        assert "MVC" in result.get("type", "")

    def test_ddd_architecture_detection(self):
        """Verify Domain-Driven Design (DDD) architecture detection."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        patterns = [
            PatternMatch("AggregateRoot", 0.85, "domain/aggregate.py:1", {}),
            PatternMatch("DomainEvent", 0.85, "domain/events.py:1", {}),
            PatternMatch("Repository", 0.85, "domain/repository.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert result is not None
        assert "DDD" in result.get("type", "") or "Domain" in result.get("type", "")

    def test_layered_architecture_detection(self):
        """Verify Layered (N-tier) architecture detection."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        patterns = [
            PatternMatch("Facade", 0.8, "presentation/facade.py:1", {}),
            PatternMatch("ServiceLayer", 0.8, "business/services.py:1", {}),
            PatternMatch("DataAccessLayer", 0.8, "data/dao.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert result is not None
        assert "Layered" in result.get("type", "") or "Layer" in result.get("type", "")

    def test_microservices_architecture_detection(self):
        """Verify Microservices architecture detection."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        patterns = [
            PatternMatch("ServiceRegistry", 0.85, "infra/registry.py:1", {}),
            PatternMatch("APIGateway", 0.85, "infra/gateway.py:1", {}),
            PatternMatch("CircuitBreaker", 0.85, "infra/circuit_breaker.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert result is not None
        assert "Microservice" in result.get("type", "") or "Micro" in result.get("type", "")

    def test_event_driven_architecture_detection(self):
        """Verify Event-Driven architecture detection."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        patterns = [
            PatternMatch("EventProducer", 0.9, "events/producer.py:1", {}),
            PatternMatch("EventConsumer", 0.9, "events/consumer.py:1", {}),
            PatternMatch("EventBroker", 0.9, "events/broker.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert result is not None
        assert "Event" in result.get("type", "")

    def test_cqrs_architecture_detection(self):
        """Verify CQRS (Command Query Responsibility Segregation) detection."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        patterns = [
            PatternMatch("CommandModel", 0.85, "cqrs/commands.py:1", {}),
            PatternMatch("QueryModel", 0.85, "cqrs/queries.py:1", {}),
            PatternMatch("EventStore", 0.85, "cqrs/event_store.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert result is not None
        assert "CQRS" in result.get("type", "")

    def test_confidence_scoring(self):
        """Verify architecture classification includes confidence score."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        patterns = [
            PatternMatch("Model", 0.9, "models.py:1", {}),
            PatternMatch("View", 0.9, "views.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_mixed_architecture_patterns(self):
        """Verify mixed architecture patterns are handled."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        # Mixed: Some MVC + Some DDD patterns
        patterns = [
            PatternMatch("Model", 0.8, "models.py:1", {}),
            PatternMatch("Repository", 0.8, "repository.py:1", {}),
            PatternMatch("AggregateRoot", 0.8, "aggregate.py:1", {}),
        ]
        
        result = classifier.classify_architecture(patterns)
        assert result is not None
        assert "type" in result

    def test_no_patterns_detection(self):
        """Verify graceful handling when no patterns detected."""
        from cortex.intelligence.patterns.classification import ArchitectureClassifier
        
        classifier = ArchitectureClassifier()
        
        result = classifier.classify_architecture([])
        assert result is not None
        assert result.get("type", "") == "Unknown" or result.get("confidence", 0.0) < 0.5

# AC_COMPLETE: AC-PHASE57-S3-001 ✅
# Test Results: 10/10 tests designed
# Status: PENDING IMPLEMENTATION
