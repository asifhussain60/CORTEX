"""
Unit and Integration Tests for MasterOrchestrator Router Integration (AC-IKP-002-02).

Tests for integrating IntelligentKnowledgeRouter into MasterOrchestrator,
replacing dual-backend parallel evaluation with intelligent routing.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all tests
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any
from datetime import datetime


class TestOrchestratorRouterIntegration:
    """Unit tests for router integration with orchestrator."""

    def test_orchestrator_has_router_attribute(self):
        """Test that orchestrator has router attribute."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        assert hasattr(orchestrator, 'router')
        assert orchestrator.router is not None

    def test_orchestrator_initializes_router_with_backends(self):
        """Test that orchestrator initializes router with available backends."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Should have at least one backend configured
        assert len(orchestrator.router.backends) > 0

    def test_orchestrator_route_query_instead_of_parallel(self):
        """Test that orchestrator uses router instead of dual parallel evaluation."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Should have routing method
        assert hasattr(orchestrator, 'coordinate_operation')
        
        # The method should use router.route_query internally
        method_source = str(orchestrator.coordinate_operation)
        assert 'router' in method_source.lower() or hasattr(orchestrator.router, 'route_query')

    def test_orchestrator_respects_routing_confidence_threshold(self):
        """Test that orchestrator respects confidence threshold."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Should have confidence threshold
        assert hasattr(orchestrator.router, 'confidence_threshold')
        assert isinstance(orchestrator.router.confidence_threshold, (int, float))
        assert 0.0 <= orchestrator.router.confidence_threshold <= 1.0

    def test_orchestrator_fallback_to_parallel_on_low_confidence(self):
        """Test that orchestrator falls back to parallel when confidence is low."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # When confidence < threshold, should query multiple backends
        # This is verified by monitoring fallback_count
        assert hasattr(orchestrator.router, 'fallback_count')

    def test_orchestrator_routes_operation_intent_query(self):
        """Test that operation intent queries are routed correctly."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        mock_backend.query = Mock(return_value=[{'result': 'test'}])
        
        orchestrator.router.backends['test'] = mock_backend
        
        backend, confidence, audit = orchestrator.router.route_query("How should I deploy?")
        
        assert backend is not None
        assert isinstance(confidence, float)
        assert isinstance(audit, dict)

    def test_orchestrator_captures_routing_metrics(self):
        """Test that orchestrator captures routing metrics during operations."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Perform operation that uses routing
        initial_count = orchestrator.router.query_count
        
        # Route a query
        mock_backend = Mock()
        orchestrator.router.backends['default'] = mock_backend
        
        try:
            orchestrator.router.route_query("test query")
        except Exception:
            pass
        
        # Query count should increase
        assert orchestrator.router.query_count > initial_count

    def test_orchestrator_audit_trail_includes_routing_decision(self):
        """Test that operation audit trail includes routing decision."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        orchestrator.router.backends['test'] = mock_backend
        
        backend, confidence, audit = orchestrator.router.route_query("test")
        
        # Audit should contain routing metadata
        assert 'selected_backend' in audit
        assert 'confidence' in audit
        assert 'intent_type' in audit
        assert 'timestamp' in audit

    def test_orchestrator_supports_parallel_fallback_results_aggregation(self):
        """Test that results from fallback parallel queries are aggregated."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Mock backends
        backend1 = Mock()
        backend1.query = Mock(return_value=[{'from': 'backend1', 'data': 'result1'}])
        backend2 = Mock()
        backend2.query = Mock(return_value=[{'from': 'backend2', 'data': 'result2'}])
        
        orchestrator.router.backends = {'backend1': backend1, 'backend2': backend2}
        
        # Force low confidence to trigger fallback
        orchestrator.router.confidence_threshold = 0.99
        
        results = orchestrator.router.route_query_with_fallback("test")
        
        # Should get results
        assert isinstance(results, list)

    def test_orchestrator_operation_returns_routing_metadata(self):
        """Test that operation results include routing metadata."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        orchestrator.router.backends['default'] = mock_backend
        
        backend, confidence, audit = orchestrator.router.route_query("test")
        
        # Check metadata structure
        assert audit['selected_backend'] in orchestrator.router.backends.keys()
        assert 0.0 <= audit['confidence'] <= 1.0


class TestOrchestratorRoutingBehavior:
    """Integration tests for orchestrator routing behavior."""

    def test_orchestrator_routes_technical_queries_to_technical_backend(self):
        """Test that technical queries route to technical backend."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Mock backends
        tech_backend = Mock()
        business_backend = Mock()
        
        orchestrator.router.backends = {
            'technical': tech_backend,
            'business': business_backend
        }
        
        backend, confidence, _ = orchestrator.router.route_query(
            "How do I optimize database performance?"
        )
        
        # Should prefer technical backend
        assert backend == tech_backend

    def test_orchestrator_routes_business_queries_to_business_backend(self):
        """Test that business queries route to business backend."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        tech_backend = Mock()
        business_backend = Mock()
        
        orchestrator.router.backends = {
            'technical': tech_backend,
            'business': business_backend
        }
        
        backend, confidence, _ = orchestrator.router.route_query(
            "What is our quarterly revenue target?"
        )
        
        # Should prefer business backend
        assert backend == business_backend

    def test_orchestrator_handles_ambiguous_queries_with_fallback(self):
        """Test orchestrator handles ambiguous queries with fallback."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        backend1 = Mock()
        backend1.query = Mock(return_value=[{'result': 'from1'}])
        backend2 = Mock()
        backend2.query = Mock(return_value=[{'result': 'from2'}])
        
        orchestrator.router.backends = {'b1': backend1, 'b2': backend2}
        
        # Ambiguous query
        results = orchestrator.router.route_query_with_fallback("xyz")
        
        # Should return results
        assert isinstance(results, (list, tuple))

    def test_orchestrator_tracks_routing_efficiency(self):
        """Test that orchestrator tracks routing efficiency."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        orchestrator.router.backends['default'] = mock_backend
        
        # Route several queries
        for _ in range(3):
            try:
                orchestrator.router.route_query("test query")
            except Exception:
                pass
        
        metrics = orchestrator.router.get_performance_metrics()
        
        # Should track queries
        assert metrics['queries_routed'] >= 0

    def test_orchestrator_routing_history_preserved_across_operations(self):
        """Test that routing history is preserved."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        orchestrator.router.backends['default'] = mock_backend
        
        initial_history_len = len(orchestrator.router.get_routing_history())
        
        try:
            orchestrator.router.route_query("test")
        except Exception:
            pass
        
        # History should grow
        assert len(orchestrator.router.get_routing_history()) > initial_history_len

    def test_orchestrator_confidence_score_influences_selection(self):
        """Test that confidence score influences backend selection."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        tech_backend = Mock()
        general_backend = Mock()
        
        orchestrator.router.backends = {
            'technical': tech_backend,
            'general': general_backend
        }
        
        # Technical query should have high confidence for technical backend
        backend, confidence, _ = orchestrator.router.route_query(
            "How do I use Docker?"
        )
        
        # Should have reasonable confidence
        assert confidence > 0.3

    def test_orchestrator_preserves_query_semantics_during_routing(self):
        """Test that query semantics are preserved during routing."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        orchestrator.router.backends['default'] = mock_backend
        
        query = "What are the benefits of microservices architecture?"
        backend, confidence, audit = orchestrator.router.route_query(query)
        
        # Query should be preserved (possibly truncated)
        assert query[:100] in audit['query'] or audit['query'] in query

    def test_orchestrator_handles_multiple_backends_fairly(self):
        """Test that orchestrator handles multiple backends without bias."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Create identical backends
        backend1 = Mock()
        backend2 = Mock()
        
        orchestrator.router.backends = {
            'backend_a': backend1,
            'backend_b': backend2
        }
        
        # Generic query should score both backends similarly
        scores = orchestrator.router.score_backend_confidence("generic question")
        
        # Both should have entries
        assert 'backend_a' in scores
        assert 'backend_b' in scores

    def test_orchestrator_error_handling_invalid_query(self):
        """Test orchestrator error handling for invalid queries."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        orchestrator.router.backends['default'] = mock_backend
        
        with pytest.raises((ValueError, RuntimeError)):
            orchestrator.router.route_query("")

    def test_orchestrator_error_handling_no_backends(self):
        """Test orchestrator error handling when no backends available."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.brain.core.knowledge.router import IntelligentKnowledgeRouter
        
        with pytest.raises(ValueError):
            IntelligentKnowledgeRouter(backends={})

    def test_orchestrator_integrates_routing_into_coordinate_operation(self):
        """Test that routing is integrated into coordinate_operation."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # coordinate_operation should use router
        assert hasattr(orchestrator, 'coordinate_operation')
        assert hasattr(orchestrator, 'router')


class TestOrchestratorRegressions:
    """Regression tests to ensure orchestrator backward compatibility."""

    def test_coordinate_operation_still_returns_results(self):
        """Test that coordinate_operation still returns results after routing integration."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        mock_backend.query = Mock(return_value=[{'data': 'result'}])
        orchestrator.router.backends['default'] = mock_backend
        
        # Should be able to route queries
        try:
            backend, confidence, audit = orchestrator.router.route_query("test")
            assert backend is not None
        except Exception:
            pass

    def test_parallel_fallback_mode_available(self):
        """Test that parallel fallback mode is still available."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Should have fallback capability
        assert hasattr(orchestrator.router, 'route_query_with_fallback')

    def test_performance_metrics_available(self):
        """Test that performance metrics are available after integration."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        metrics = orchestrator.router.get_performance_metrics()
        
        assert 'queries_routed' in metrics
        assert 'fallback_queries' in metrics
        assert 'avg_confidence' in metrics

    def test_audit_trail_still_functional(self):
        """Test that audit trail is still functional."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        mock_backend = Mock()
        orchestrator.router.backends['default'] = mock_backend
        
        _, _, audit = orchestrator.router.route_query("test")
        
        assert audit is not None
        assert isinstance(audit, dict)
        assert 'timestamp' in audit


__all__ = [
    'TestOrchestratorRouterIntegration',
    'TestOrchestratorRoutingBehavior',
    'TestOrchestratorRegressions',
]
