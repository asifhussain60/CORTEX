"""
Tests for AC-PHX-007-04 through AC-PHX-007-10

Consolidated tests for confidence scoring, context preservation,
routing logic, fallback strategies, learning loops, performance
metrics, and orchestration integration.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.intent_router.confidence_scorer import ConfidenceScorer
from cortex.intent_router.context_manager import ContextManager, ConversationContext
from cortex.intent_router.routing_engine import RoutingEngine
from cortex.intent_router.fallback_strategy import FallbackStrategy
from cortex.intent_router.intent_learner import IntentLearner
from cortex.intent_router.performance_metrics import PerformanceMetrics
from cortex.intent_router.orchestration_integrator import OrchestrationIntegrator
from cortex.intent_router.classifier import IntentCategory


class TestConfidenceScorer:
    """Test AC-PHX-007-04: Confidence Scoring."""
    
    def test_scorer_initialization(self) -> None:
        """Should initialize confidence scorer."""
        scorer = ConfidenceScorer()
        assert scorer is not None
    
    def test_score_computation(self) -> None:
        """Should compute confidence scores."""
        scorer = ConfidenceScorer()
        score = scorer.score(keywords=3, signals=2)
        assert 0.0 <= score <= 1.0
    
    def test_metrics_tracking(self) -> None:
        """Should track scoring metrics."""
        scorer = ConfidenceScorer()
        scorer.score(1, 1)
        scorer.score(2, 2)
        metrics = scorer.get_metrics()
        assert metrics["total_scores"] == 2


class TestContextManager:
    """Test AC-PHX-007-05: Intent Context Preservation."""
    
    def test_context_initialization(self) -> None:
        """Should create context for session."""
        manager = ContextManager()
        context = manager.get_context("session-1")
        assert isinstance(context, ConversationContext)
    
    def test_context_persistence(self) -> None:
        """Should preserve context across calls."""
        manager = ContextManager()
        context1 = manager.get_context("session-1")
        context2 = manager.get_context("session-1")
        assert context1 is context2
    
    def test_update_context(self) -> None:
        """Should update context with intents."""
        manager = ContextManager()
        manager.update_context("session-1", "create")
        manager.update_context("session-1", "modify")
        context = manager.get_context("session-1")
        assert len(context.previous_intents) == 2
        assert context.turn_count == 2


class TestRoutingEngine:
    """Test AC-PHX-007-06: Routing Decision Logic."""
    
    def test_routing_initialization(self) -> None:
        """Should initialize routing engine."""
        engine = RoutingEngine()
        assert engine is not None
    
    def test_route_to_create_handler(self) -> None:
        """Should route CREATE intent."""
        engine = RoutingEngine()
        handler = engine.route(IntentCategory.CREATE)
        assert handler == "CreateHandler"
    
    def test_route_to_fix_handler(self) -> None:
        """Should route FIX intent."""
        engine = RoutingEngine()
        handler = engine.route(IntentCategory.FIX)
        assert handler == "FixHandler"
    
    def test_all_intents_routable(self) -> None:
        """All intent categories should be routable."""
        engine = RoutingEngine()
        for intent in IntentCategory:
            if intent == IntentCategory.UNKNOWN:
                continue
            handler = engine.route(intent)
            assert handler is not None


class TestFallbackStrategy:
    """Test AC-PHX-007-07: Fallback Strategies."""
    
    def test_fallback_chain_for_create(self) -> None:
        """Should provide fallback chain for CREATE."""
        chain = FallbackStrategy.get_fallback_chain(IntentCategory.CREATE)
        assert len(chain) > 0
        assert chain[-1] == "GeneralHandler"
    
    def test_high_confidence_no_fallback(self) -> None:
        """High confidence should use primary handler."""
        handler = FallbackStrategy.apply_fallback(0.95, "CreateHandler")
        assert handler == "CreateHandler"
    
    def test_low_confidence_uses_fallback(self) -> None:
        """Low confidence should use fallback."""
        handler = FallbackStrategy.apply_fallback(0.5, "CreateHandler")
        assert handler == FallbackStrategy.DEFAULT_FALLBACK


class TestIntentLearner:
    """Test AC-PHX-007-08: Intent Learning Loop."""
    
    def test_learner_initialization(self) -> None:
        """Should initialize learner."""
        learner = IntentLearner()
        assert learner is not None
    
    def test_record_feedback(self) -> None:
        """Should record user feedback."""
        learner = IntentLearner()
        learner.record_feedback("create", IntentCategory.CREATE, True)
        assert len(learner.feedback_log) == 1
    
    def test_accuracy_calculation(self) -> None:
        """Should calculate accuracy from feedback."""
        learner = IntentLearner()
        learner.record_feedback("create", IntentCategory.CREATE, True)
        learner.record_feedback("fix", IntentCategory.CREATE, False)
        accuracy = learner.get_accuracy()
        assert accuracy == 0.5


class TestPerformanceMetrics:
    """Test AC-PHX-007-09: Performance Metrics."""
    
    def test_metrics_initialization(self) -> None:
        """Should initialize metrics."""
        metrics = PerformanceMetrics()
        assert metrics.get_metrics()["classifications"] == 0
    
    def test_record_classification(self) -> None:
        """Should record classification latency."""
        metrics = PerformanceMetrics()
        metrics.record_classification(5.0)
        metrics.record_classification(10.0)
        data = metrics.get_metrics()
        assert data["classifications"] == 2
        assert 7.0 <= data["avg_latency_ms"] <= 8.0  # Average of 5 and 10
    
    def test_metrics_contain_timestamp(self) -> None:
        """Metrics should include timestamp."""
        metrics = PerformanceMetrics()
        data = metrics.get_metrics()
        assert "start_time" in data


class TestOrchestrationIntegrator:
    """Test AC-PHX-007-10: Orchestration Integration."""
    
    def test_integrator_initialization(self) -> None:
        """Should initialize integrator."""
        integrator = OrchestrationIntegrator()
        assert integrator is not None
    
    def test_register_orchestrator(self) -> None:
        """Should register orchestrator."""
        integrator = OrchestrationIntegrator()
        integrator.register_orchestrator("create", "/handlers/create")
        assert integrator.get_orchestrator("create") == "/handlers/create"
    
    def test_get_unregistered_orchestrator(self) -> None:
        """Should return None for unregistered."""
        integrator = OrchestrationIntegrator()
        result = integrator.get_orchestrator("unknown")
        assert result is None
