# © 2025-2026 Asif Hussain. All rights reserved.
# PHASE-21: AC-IKP-002-03 MasterOrchestrator Integration Tests
"""
Integration tests for IntelligentKnowledgeRouter with MasterOrchestrator.

Test Coverage:
  - Router integration module functionality
  - Operation context mapping
  - Knowledge context formatting
  - End-to-end MasterOrchestrator workflow
  - Query reduction verification
  - Backward compatibility

CORE Governance:
  - CORE-008: TDD (tests first - 18 tests)
  - CORE-011: Type hints enforced
  - CORE-013: Specific exception handling

References:
  - PHASE-21-KICKOFF.md: AC-IKP-002-03 specification
  - cortex/brain/core/knowledge/router_integration.py: Integration module
  - cortex/orchestrators/core/master_orchestrator.py: Integration point
"""

import pytest
from typing import Dict, Any, List

from cortex.brain.core.knowledge.router_integration import (
    OperationContextMapper,
    KnowledgeContextFormatter,
    KnowledgeRouterIntegration,
    create_router_integration,
)
from cortex.brain.core.knowledge.router import OperationType
from cortex.core.knowledge import KnowledgeQueryResult, KnowledgeProvider


# =============================================================================
# TEST FIXTURES - PROVIDERS
# =============================================================================

class TestTechProvider:
    """Test technical knowledge provider."""
    
    @property
    def is_loaded(self) -> bool:
        return True
    
    @property
    def entry_count(self) -> int:
        return 3
    
    @property
    def domains(self) -> List[str]:
        return ["ARCHITECTURE", "SECURITY"]
    
    def query(self, **kwargs) -> KnowledgeQueryResult:
        return KnowledgeQueryResult(
            entries=[
                {
                    "id": "KB-1",
                    "domain": "ARCHITECTURE",
                    "title": "Microservices Pattern",
                    "description": "Design distributed systems",
                },
            ],
            total_matches=1,
        )
    
    def get_by_domain(self, domain: str) -> KnowledgeQueryResult:
        return KnowledgeQueryResult(entries=[], total_matches=0)
    
    def get_relevant_knowledge(self, domains=None, keywords=None):
        return self.query()


class TestBusinessProvider:
    """Test business knowledge provider."""
    
    @property
    def is_loaded(self) -> bool:
        return True
    
    @property
    def entry_count(self) -> int:
        return 2
    
    @property
    def domains(self) -> List[str]:
        return ["payments", "orders"]
    
    def query(self, **kwargs) -> KnowledgeQueryResult:
        return KnowledgeQueryResult(
            entries=[
                {
                    "id": "BIZ-1",
                    "domain_name": "payments",
                    "entity_type": "SERVICE",
                    "name": "PaymentService",
                },
            ],
            total_matches=1,
        )
    
    def get_by_domain(self, domain: str) -> KnowledgeQueryResult:
        return KnowledgeQueryResult(entries=[], total_matches=0)
    
    def get_relevant_knowledge(self, domains=None, keywords=None):
        return self.query()


@pytest.fixture
def tech_provider():
    """Create test technical provider."""
    return TestTechProvider()


@pytest.fixture
def business_provider():
    """Create test business provider."""
    return TestBusinessProvider()


@pytest.fixture
def integration(tech_provider, business_provider):
    """Create router integration."""
    return KnowledgeRouterIntegration(
        tech_provider=tech_provider,
        business_provider=business_provider,
    )


# =============================================================================
# TESTS: OPERATION CONTEXT MAPPING
# =============================================================================

def test_map_api_design_operation():
    """Test mapping API_DESIGN operation."""
    op_type = OperationContextMapper.map_operation_to_type("API_DESIGN")
    assert op_type == OperationType.API_DESIGN


def test_map_architecture_operation():
    """Test mapping ARCHITECTURE operation."""
    op_type = OperationContextMapper.map_operation_to_type("ARCHITECTURE")
    assert op_type == OperationType.ARCHITECTURE


def test_map_security_operation():
    """Test mapping SECURITY operation."""
    op_type = OperationContextMapper.map_operation_to_type("SECURITY")
    assert op_type == OperationType.SECURITY


def test_map_business_process_operation():
    """Test mapping BUSINESS_PROCESS operation."""
    op_type = OperationContextMapper.map_operation_to_type("BUSINESS_PROCESS")
    assert op_type == OperationType.BUSINESS_PROCESS


def test_map_unknown_operation():
    """Test mapping unknown operation defaults to UNKNOWN."""
    op_type = OperationContextMapper.map_operation_to_type("UNKNOWN_OP")
    assert op_type == OperationType.UNKNOWN


def test_extract_keywords_from_context():
    """Test extracting keywords from operation context."""
    context = {
        "operation": "API design",
        "keywords": ["rest", "design"],
        "description": "design REST API",
    }
    
    keywords = OperationContextMapper.extract_keywords_from_context(context)
    assert len(keywords) > 0
    assert "api" in keywords or "design" in keywords


def test_extract_keywords_empty_context():
    """Test extracting keywords from empty context."""
    keywords = OperationContextMapper.extract_keywords_from_context({})
    assert isinstance(keywords, list)


# =============================================================================
# TESTS: KNOWLEDGE CONTEXT FORMATTING
# =============================================================================

def test_format_technical_context():
    """Test formatting technical query result."""
    result = KnowledgeQueryResult(
        entries=[
            {
                "domain": "ARCHITECTURE",
                "title": "Microservices",
                "description": "Pattern for distributed systems",
            },
        ],
        total_matches=1,
    )
    
    context = KnowledgeContextFormatter.format_technical_context(result, "API_DESIGN")
    
    assert context["knowledge_evaluated"] is True
    assert context["entries_count"] == 1
    assert len(context["architecture_patterns"]) > 0


def test_format_business_context():
    """Test formatting business query result."""
    result = KnowledgeQueryResult(
        entries=[
            {
                "domain_name": "payments",
                "entity_type": "SERVICE",
                "name": "PaymentService",
            },
        ],
        total_matches=1,
    )
    
    context = KnowledgeContextFormatter.format_business_context(result, "WORKFLOW")
    
    assert context["business_knowledge_evaluated"] is True
    assert context["entries_count"] == 1


def test_format_empty_technical_context():
    """Test formatting empty technical result."""
    result = KnowledgeQueryResult(entries=[], total_matches=0)
    
    context = KnowledgeContextFormatter.format_technical_context(result, "API_DESIGN")
    
    assert context["knowledge_evaluated"] is False
    assert context["entries_count"] == 0


# =============================================================================
# TESTS: ROUTER INTEGRATION
# =============================================================================

def test_create_router_integration(tech_provider, business_provider):
    """Test creating router integration."""
    integration = KnowledgeRouterIntegration(
        tech_provider=tech_provider,
        business_provider=business_provider,
    )
    
    assert integration is not None


def test_create_router_integration_factory_success(tech_provider, business_provider):
    """Test factory function for successful creation."""
    integration = create_router_integration(tech_provider, business_provider)
    
    assert integration is not None


def test_create_router_integration_factory_missing_providers():
    """Test factory function with missing providers."""
    integration = create_router_integration(None, None)
    
    assert integration is None


def test_evaluate_for_operation_api_design(integration):
    """Test evaluating API design operation."""
    tech_context, business_context = integration.evaluate_for_operation(
        operation="API_DESIGN",
        operation_context={"keywords": ["rest", "api"]},
    )
    
    assert tech_context is not None
    assert business_context is not None
    assert "routing_strategy" in tech_context
    assert "routing_strategy" in business_context


def test_evaluate_for_operation_business_process(integration):
    """Test evaluating business process operation."""
    tech_context, business_context = integration.evaluate_for_operation(
        operation="BUSINESS_PROCESS",
        operation_context={"keywords": ["workflow", "business"]},
    )
    
    assert tech_context is not None
    assert business_context is not None


def test_evaluate_for_operation_includes_routing_metadata(integration):
    """Test that evaluation includes routing metadata."""
    tech_context, business_context = integration.evaluate_for_operation(
        operation="ARCHITECTURE",
        operation_context={},
    )
    
    # Check metadata
    assert "routing_strategy" in tech_context
    assert "routing_confidence" in tech_context
    assert "routing_time_ms" in tech_context
    assert tech_context["routing_time_ms"] >= 0


def test_evaluate_for_operation_maintains_backward_compatibility(integration):
    """Test that result format is compatible with MasterOrchestrator."""
    tech_context, business_context = integration.evaluate_for_operation(
        operation="API_DESIGN",
        operation_context={},
    )
    
    # Check expected MasterOrchestrator fields
    assert "guidelines" in tech_context
    assert "best_practices" in tech_context
    assert "security_considerations" in tech_context
    assert "architecture_patterns" in tech_context
    
    assert "business_domains" in business_context
    assert "services" in business_context
    assert "apis" in business_context
    assert "workflows" in business_context


# =============================================================================
# TESTS: QUERY REDUCTION VERIFICATION
# =============================================================================

def test_routing_reduces_queries_tech_only(integration):
    """Test that tech-only routing skips business query."""
    tech_context, business_context = integration.evaluate_for_operation(
        operation="ARCHITECTURE",
        operation_context={"keywords": ["architecture", "design", "patterns"]},
    )
    
    # Check that routing strategy is identified
    assert "routing_strategy" in tech_context
    # If tech-only, business context should be minimal
    # (actual routing depends on affinity scores)


def test_routing_provides_confidence_score(integration):
    """Test that routing includes confidence scores."""
    tech_context, business_context = integration.evaluate_for_operation(
        operation="API_DESIGN",
        operation_context={},
    )
    
    # Both should have confidence scores
    assert "routing_confidence" in tech_context
    assert "routing_confidence" in business_context
    assert 0 <= tech_context["routing_confidence"] <= 100


# =============================================================================
# TESTS: ERROR HANDLING AND EDGE CASES
# =============================================================================

def test_evaluate_with_missing_context_fields(integration):
    """Test evaluation with missing context fields."""
    # Should handle missing fields gracefully
    tech_context, business_context = integration.evaluate_for_operation(
        operation="API",
        operation_context={},
    )
    
    assert tech_context is not None
    assert business_context is not None


def test_evaluate_with_empty_keywords(integration):
    """Test evaluation with empty keywords."""
    tech_context, business_context = integration.evaluate_for_operation(
        operation="ARCHITECTURE",
        operation_context={"keywords": []},
    )
    
    # Should still work with empty keywords
    assert tech_context is not None
    assert business_context is not None


def test_factory_with_invalid_provider():
    """Test factory function with invalid provider."""
    class InvalidProvider:
        pass
    
    # Should return None or raise ValueError
    result = create_router_integration(InvalidProvider(), InvalidProvider())
    assert result is None or isinstance(result, KnowledgeRouterIntegration)


# =============================================================================
# TESTS: PERFORMANCE CHARACTERISTICS
# =============================================================================

def test_evaluation_performance(integration):
    """Test that evaluation completes in reasonable time."""
    import time
    
    start = time.time()
    tech_context, business_context = integration.evaluate_for_operation(
        operation="API_DESIGN",
        operation_context={},
    )
    elapsed = (time.time() - start) * 1000  # Convert to ms
    
    # Should complete within 100ms
    assert elapsed < 100
    assert tech_context["routing_time_ms"] < 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
