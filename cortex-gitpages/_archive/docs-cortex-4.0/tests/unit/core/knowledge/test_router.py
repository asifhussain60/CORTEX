"""
Test suite for IntelligentKnowledgeRouter Implementation (AC-IKP-002-01).

Tests smart query routing that analyzes query intent and routes to appropriate
backend with confidence scoring and audit trails.

Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

import pytest
from typing import Dict, List, Any, Tuple
from unittest.mock import Mock, MagicMock, patch


class TestIntelligentKnowledgeRouter:
    """Unit tests for IntelligentKnowledgeRouter."""

    def test_router_class_exists(self):
        """Test that IntelligentKnowledgeRouter class is defined."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        assert IntelligentKnowledgeRouter is not None

    def test_router_initialization(self):
        """Test router initialization with backends."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend2 = Mock()
        
        router = IntelligentKnowledgeRouter(
            backends={'technical': backend1, 'business': backend2}
        )
        
        assert router is not None
        assert len(router.backends) == 2

    def test_router_analyze_query_intent(self):
        """Test query intent analysis."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        # Test technical query
        intent = router.analyze_query_intent("How do I debug Python memory leaks?")
        assert intent is not None
        assert 'intent_type' in intent or hasattr(intent, 'intent_type')

    def test_router_detect_domain_keywords(self):
        """Test domain keyword detection."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        # Technical keywords
        query = "What are the best practices for async/await in Python?"
        domains = router.detect_domain_keywords(query)
        assert isinstance(domains, list)

    def test_router_score_backend_confidence(self):
        """Test backend confidence scoring."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend2 = Mock()
        
        router = IntelligentKnowledgeRouter(
            backends={'technical': backend1, 'business': backend2}
        )
        
        query = "How to configure CI/CD pipeline?"
        scores = router.score_backend_confidence(query)
        
        assert isinstance(scores, dict)
        assert len(scores) > 0

    def test_router_select_best_backend(self):
        """Test selection of best backend based on confidence."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend2 = Mock()
        
        router = IntelligentKnowledgeRouter(
            backends={'technical': backend1, 'business': backend2}
        )
        
        query = "What is the company policy on remote work?"
        selected = router.select_best_backend(query)
        
        assert selected is not None

    def test_router_route_query_returns_tuple(self):
        """Test that route_query returns (backend, confidence, audit_entry)."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        result = router.route_query("test query")
        
        # Should return tuple of (backend, confidence, audit_info)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_router_confidence_score_range(self):
        """Test that confidence scores are between 0 and 1."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend2 = Mock()
        
        router = IntelligentKnowledgeRouter(
            backends={'tech': backend1, 'biz': backend2}
        )
        
        query = "Sample query"
        backend, confidence, audit = router.route_query(query)
        
        assert 0.0 <= confidence <= 1.0

    def test_router_handles_multiple_backends(self):
        """Test router handles multiple backend candidates."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backends = {
            'technical': Mock(),
            'business': Mock(),
            'policy': Mock(),
            'architectural': Mock(),
        }
        
        router = IntelligentKnowledgeRouter(backends=backends)
        
        assert len(router.backends) == 4
        
        backend, confidence, audit = router.route_query("query")
        assert backend is not None

    def test_router_audit_entry_contains_metadata(self):
        """Test audit entry contains routing decision metadata."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        query = "test query"
        backend_selected, confidence, audit = router.route_query(query)
        
        assert audit is not None
        assert 'confidence' in audit or hasattr(audit, 'confidence')
        assert 'selected_backend' in audit or hasattr(audit, 'selected_backend')

    def test_router_fallback_to_parallel_query(self):
        """Test fallback mechanism when confidence is low."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend2 = Mock()
        
        router = IntelligentKnowledgeRouter(
            backends={'tech': backend1, 'biz': backend2},
            confidence_threshold=0.8  # High threshold
        )
        
        # Query that might not match any backend well
        backend, confidence, audit = router.route_query("ambiguous query")
        
        # Should either return high confidence or indicate fallback
        assert backend is not None
        assert confidence is not None

    def test_router_handles_empty_query(self):
        """Test router handles empty queries gracefully."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        with pytest.raises((ValueError, RuntimeError)):
            router.route_query("")

    def test_router_returns_same_backend_for_similar_queries(self):
        """Test consistency: similar queries route to same backend."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        query1 = "How to optimize database queries?"
        query2 = "Tips for improving database performance?"
        
        backend1, conf1, _ = router.route_query(query1)
        backend2, conf2, _ = router.route_query(query2)
        
        # Should route to same backend with similar confidence
        assert backend1 == backend2

    def test_router_explicit_domain_override(self):
        """Test explicit domain specification in query."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        tech_backend = Mock()
        biz_backend = Mock()
        
        router = IntelligentKnowledgeRouter(
            backends={'technical': tech_backend, 'business': biz_backend}
        )
        
        # Query with explicit domain hint
        query = "[business] What are company benefits?"
        backend, confidence, audit = router.route_query(query)
        
        # Should route to business backend despite generic query
        assert backend == biz_backend

    def test_router_confidence_factors(self):
        """Test that confidence scoring considers multiple factors."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        # Should have method to get scoring breakdown
        factors = router.get_confidence_factors("sample query")
        
        assert factors is not None
        assert isinstance(factors, dict) or hasattr(factors, '__iter__')


class TestRouterIntegration:
    """Integration tests for IntelligentKnowledgeRouter."""

    def test_router_with_mock_backends(self):
        """Test router with mock backend implementations."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        # Create mock backends with KnowledgeProvider interface
        backend1 = Mock()
        backend1.domains = ['technical', 'architecture']
        backend1.entry_count = 1000
        
        backend2 = Mock()
        backend2.domains = ['business', 'policy']
        backend2.entry_count = 500
        
        router = IntelligentKnowledgeRouter(backends={
            'tech': backend1,
            'biz': backend2
        })
        
        # Route query about architecture
        backend, confidence, audit = router.route_query("microservices architecture")
        
        assert backend is not None
        assert confidence is not None

    def test_router_preserves_query_history(self):
        """Test that router maintains query routing history."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        queries = [
            "First query about Python",
            "Second query about Django",
            "Third query about Flask",
        ]
        
        for query in queries:
            router.route_query(query)
        
        # Should have history
        history = router.get_routing_history()
        assert history is not None
        assert len(history) >= 3

    def test_router_performance_metadata(self):
        """Test that router collects performance metrics."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend = Mock()
        router = IntelligentKnowledgeRouter(backends={'default': backend})
        
        # Run multiple queries
        for i in range(5):
            router.route_query(f"Query number {i}")
        
        # Should track metrics
        metrics = router.get_performance_metrics()
        
        assert metrics is not None
        assert 'queries_routed' in metrics or hasattr(metrics, 'queries_routed')

    def test_router_fallback_mode_multi_backend(self):
        """Test fallback to parallel queries with multiple backends."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend1.query = Mock(return_value=[{'result': 'from backend1'}])
        
        backend2 = Mock()
        backend2.query = Mock(return_value=[{'result': 'from backend2'}])
        
        router = IntelligentKnowledgeRouter(
            backends={'back1': backend1, 'back2': backend2},
            confidence_threshold=0.95  # Very high threshold
        )
        
        # Should trigger fallback
        results = router.route_query_with_fallback("ambiguous query")
        
        assert results is not None
        # Fallback should query multiple backends
        if isinstance(results, list):
            assert len(results) > 0

    def test_router_error_handling_invalid_backend(self):
        """Test error handling for invalid backend configuration."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        invalid_backend = "not_a_backend_object"
        
        with pytest.raises((TypeError, ValueError)):
            router = IntelligentKnowledgeRouter(
                backends={'invalid': invalid_backend}
            )

    def test_router_concurrent_queries(self):
        """Test router can handle multiple queries in sequence."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend2 = Mock()
        backend3 = Mock()
        
        router = IntelligentKnowledgeRouter(backends={
            'tech': backend1,
            'biz': backend2,
            'policy': backend3,
        })
        
        queries = [
            "Python best practices",
            "Company benefits policy",
            "Sales department budget",
            "API design patterns",
            "HR policies",
        ]
        
        results = []
        for query in queries:
            backend, conf, audit = router.route_query(query)
            results.append((backend, conf))
        
        assert len(results) == 5
        for backend, confidence in results:
            assert backend is not None
            assert 0.0 <= confidence <= 1.0

    def test_router_aggregates_results_fallback(self):
        """Test result aggregation when using fallback."""
        from src.core.knowledge.router import IntelligentKnowledgeRouter
        
        backend1 = Mock()
        backend1.query = Mock(return_value=[{'data': 'from_tech'}])
        
        backend2 = Mock()
        backend2.query = Mock(return_value=[{'data': 'from_biz'}])
        
        router = IntelligentKnowledgeRouter(
            backends={'tech': backend1, 'biz': backend2}
        )
        
        aggregated = router.aggregate_parallel_results(
            {'tech': [{'data': 'from_tech'}], 'biz': [{'data': 'from_biz'}]}
        )
        
        assert aggregated is not None
        assert isinstance(aggregated, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
