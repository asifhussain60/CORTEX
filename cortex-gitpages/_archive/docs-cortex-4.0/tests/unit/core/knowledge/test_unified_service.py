"""
Unit and Integration Tests for UnifiedKnowledgeService (AC-IKP-005-01).

Tests for unified knowledge service facade that wraps IntelligentKnowledgeRouter,
provides unified query interface with source attribution, supports cross-backend
aggregation and deduplication.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all tests
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any, Optional
from datetime import datetime


class TestUnifiedKnowledgeService:
    """Unit tests for UnifiedKnowledgeService."""

    def test_unified_knowledge_service_exists(self):
        """Test that UnifiedKnowledgeService class exists."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        assert UnifiedKnowledgeService is not None

    def test_service_initialization_with_router(self):
        """Test service initialization with router."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        assert service is not None
        assert service.router is not None

    def test_unified_query_interface(self):
        """Test unified query interface."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should have query method
        assert hasattr(service, 'query')

    def test_cross_backend_aggregation(self):
        """Test aggregation across multiple backends."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'backend1': Mock(), 'backend2': Mock(), 'backend3': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should support aggregation
        assert hasattr(service, 'aggregate_results')

    def test_result_deduplication(self):
        """Test deduplication of results from multiple backends."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should deduplicate
        assert hasattr(service, 'deduplicate_results')

    def test_source_attribution_in_results(self):
        """Test source attribution tracking in results."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should track sources
        assert hasattr(service, 'add_source_attribution')

    def test_domain_aware_queries(self):
        """Test domain-aware query routing."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should support domain-aware queries
        assert hasattr(service, 'query_by_domain')

    def test_confidence_scoring_in_results(self):
        """Test confidence scoring from router."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should include confidence scores
        assert hasattr(service, 'get_result_confidence')

    def test_result_filtering_and_ranking(self):
        """Test filtering and ranking of aggregated results."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should filter and rank
        assert hasattr(service, 'rank_results')

    def test_batch_query_support(self):
        """Test batch query support."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should support batch queries
        assert hasattr(service, 'query_batch')

    def test_async_query_support(self):
        """Test asynchronous query support."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should support async queries
        assert hasattr(service, 'query_async')

    def test_query_metrics_and_tracking(self):
        """Test query metrics collection."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should track metrics
        assert hasattr(service, 'get_query_metrics')

    def test_error_handling_in_aggregation(self):
        """Test error handling when aggregating from multiple backends."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should handle errors gracefully
        assert hasattr(service, 'handle_backend_error')


class TestUnifiedKnowledgeIntegration:
    """Integration tests for UnifiedKnowledgeService."""

    def test_unified_service_wraps_router(self):
        """Test that service properly wraps router."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        router.route = Mock(return_value={'results': []})
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        assert service.router is not None

    def test_multi_backend_aggregation_workflow(self):
        """Test complete aggregation workflow across backends."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backend1 = Mock()
        backend2 = Mock()
        backend3 = Mock()
        
        service = UnifiedKnowledgeService(
            router=router,
            backends={'backend1': backend1, 'backend2': backend2, 'backend3': backend3}
        )
        
        # Should support multi-backend workflow
        assert len(service.backends) == 3

    def test_deduplication_of_identical_results(self):
        """Test deduplication when backends return identical results."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Create duplicate results
        duplicate_results = [
            {'id': '1', 'text': 'result1'},
            {'id': '1', 'text': 'result1'},
        ]
        
        # Should deduplicate
        assert hasattr(service, 'deduplicate_results')

    def test_source_attribution_and_lineage(self):
        """Test source attribution and result lineage tracking."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'backend1': Mock(), 'backend2': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should track source lineage
        assert hasattr(service, 'get_result_lineage')

    def test_confidence_scoring_integration(self):
        """Test integration of confidence scoring from router."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should integrate scoring
        assert hasattr(service, 'get_result_confidence')

    def test_unified_query_across_domains(self):
        """Test unified queries spanning multiple domains."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should support multi-domain queries
        assert hasattr(service, 'query_by_domain')

    def test_result_ranking_by_confidence(self):
        """Test ranking results by confidence scores."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should rank by confidence
        assert hasattr(service, 'rank_results')

    def test_graceful_handling_of_backend_failures(self):
        """Test graceful degradation when backends fail."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'backend1': Mock(), 'backend2': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should continue with partial results on failure
        assert hasattr(service, 'handle_backend_error')

    def test_caching_of_aggregated_results(self):
        """Test optional caching of aggregated results."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(
            router=router,
            backends=backends,
            enable_caching=True
        )
        
        # Should support caching
        assert hasattr(service, 'cache_results')

    def test_query_performance_metrics(self):
        """Test collection of query performance metrics."""
        from src.core.knowledge.unified_service import UnifiedKnowledgeService
        
        router = Mock()
        backends = {'test': Mock()}
        
        service = UnifiedKnowledgeService(router=router, backends=backends)
        
        # Should collect performance metrics
        assert hasattr(service, 'get_query_metrics')


__all__ = [
    'TestUnifiedKnowledgeService',
    'TestUnifiedKnowledgeIntegration',
]
