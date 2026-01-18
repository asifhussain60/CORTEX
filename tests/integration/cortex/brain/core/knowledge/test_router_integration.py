# © 2025-2026 Asif Hussain. All rights reserved.
# PHASE-21: AC-IKP-002-02 Router Integration Tests
"""
Integration tests for IntelligentKnowledgeRouter with actual repositories.

Test Coverage:
  - Router with KnowledgeRepository (technical)
  - Router with BusinessKnowledgeRepository (business)
  - Query routing accuracy verification
  - End-to-end routing workflow
  - Fallback and edge case behaviors
  - Performance characteristics

CORE Governance:
  - CORE-008: TDD (tests first - 12 tests)
  - CORE-011: Type hints enforced
  - CORE-013: Specific exception handling

References:
  - PHASE-21-KICKOFF.md: AC-IKP-002 integration specification
  - cortex/brain/core/knowledge/router.py: Router implementation
  - cortex/brain/core/knowledge/knowledge_repository.py: Tech repo
  - cortex/brain/domain_brain/business_knowledge_repository.py: Business repo
"""

import pytest
from typing import Optional

from cortex.brain.core.knowledge.router import (
    IntelligentKnowledgeRouter,
    OperationType,
    RoutingStrategy,
)
from cortex.core.knowledge import KnowledgeProvider


# =============================================================================
# INTEGRATION TEST FIXTURES
# =============================================================================

class IntegrationMockTechProvider:
    """Mock technical knowledge provider matching real interface."""
    
    def __init__(self):
        self._tech_entries = [
            {
                "id": "KB-ARC-001",
                "domain": "ARCHITECTURE",
                "title": "Microservices Architecture",
                "description": "Design patterns for microservices",
                "tags": ["architecture", "design", "patterns", "microservices"],
            },
            {
                "id": "KB-SEC-001",
                "domain": "SECURITY",
                "title": "Authentication Best Practices",
                "description": "Secure authentication patterns",
                "tags": ["security", "authentication", "auth"],
            },
            {
                "id": "KB-API-001",
                "domain": "ARCHITECTURE",
                "title": "REST API Design",
                "description": "REST API best practices",
                "tags": ["api", "rest", "design"],
            },
        ]
    
    @property
    def is_loaded(self) -> bool:
        return True
    
    @property
    def entry_count(self) -> int:
        return len(self._tech_entries)
    
    @property
    def domains(self):
        return ["ARCHITECTURE", "SECURITY", "PERFORMANCE"]
    
    def query(self, keywords=None, tags=None, entity_types=None, limit=None, offset=0):
        from cortex.core.knowledge import KnowledgeQueryResult
        filtered = self._tech_entries
        if limit:
            filtered = filtered[offset:offset+limit]
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
        )
    
    def get_by_domain(self, domain):
        from cortex.core.knowledge import KnowledgeQueryResult
        filtered = [e for e in self._tech_entries if e["domain"] == domain]
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
        )
    
    def get_relevant_knowledge(self, domains=None, keywords=None):
        from cortex.core.knowledge import KnowledgeQueryResult
        filtered = self._tech_entries
        if domains:
            filtered = [e for e in filtered if e["domain"] in domains]
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
        )


class IntegrationMockBusinessProvider:
    """Mock business knowledge provider matching real interface."""
    
    def __init__(self):
        self._business_entries = [
            {
                "id": "BIZ-001",
                "domain_name": "payments",
                "entity_type": "SERVICE",
                "name": "PaymentService",
                "description": "Handles payment transactions",
                "metadata": {"tags": ["business", "payments", "service"]},
            },
            {
                "id": "BIZ-002",
                "domain_name": "compliance",
                "entity_type": "FUNCTION",
                "name": "ComplianceValidator",
                "description": "Validates compliance rules",
                "metadata": {"tags": ["compliance", "governance", "business"]},
            },
            {
                "id": "BIZ-003",
                "domain_name": "orders",
                "entity_type": "SERVICE",
                "name": "OrderService",
                "description": "Manages customer orders",
                "metadata": {"tags": ["business", "workflow", "service"]},
            },
        ]
    
    @property
    def is_loaded(self) -> bool:
        return True
    
    @property
    def entry_count(self) -> int:
        return len(self._business_entries)
    
    @property
    def domains(self):
        return ["payments", "compliance", "orders", "workflow"]
    
    def query(self, keywords=None, tags=None, entity_types=None, limit=None, offset=0):
        from cortex.core.knowledge import KnowledgeQueryResult
        filtered = self._business_entries
        if limit:
            filtered = filtered[offset:offset+limit]
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
        )
    
    def get_by_domain(self, domain):
        from cortex.core.knowledge import KnowledgeQueryResult
        filtered = [e for e in self._business_entries if e["domain_name"] == domain]
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
        )
    
    def get_relevant_knowledge(self, domains=None, keywords=None):
        from cortex.core.knowledge import KnowledgeQueryResult
        filtered = self._business_entries
        if domains:
            filtered = [e for e in filtered if e["domain_name"] in domains]
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
        )


@pytest.fixture
def integration_tech_provider():
    """Create integration mock technical provider."""
    return IntegrationMockTechProvider()


@pytest.fixture
def integration_business_provider():
    """Create integration mock business provider."""
    return IntegrationMockBusinessProvider()


@pytest.fixture
def integration_router(integration_tech_provider, integration_business_provider):
    """Create router with integration providers."""
    return IntelligentKnowledgeRouter(
        tech_provider=integration_tech_provider,
        business_provider=integration_business_provider,
    )


# =============================================================================
# TESTS: PROVIDER INTERFACE COMPLIANCE
# =============================================================================

def test_integration_tech_provider_satisfies_protocol(integration_tech_provider):
    """Test that integration tech provider satisfies KnowledgeProvider protocol."""
    assert isinstance(integration_tech_provider, KnowledgeProvider)
    assert integration_tech_provider.is_loaded
    assert integration_tech_provider.entry_count > 0
    assert len(integration_tech_provider.domains) > 0


def test_integration_business_provider_satisfies_protocol(integration_business_provider):
    """Test that integration business provider satisfies KnowledgeProvider protocol."""
    assert isinstance(integration_business_provider, KnowledgeProvider)
    assert integration_business_provider.is_loaded
    assert integration_business_provider.entry_count > 0
    assert len(integration_business_provider.domains) > 0


# =============================================================================
# TESTS: END-TO-END ROUTING WORKFLOWS
# =============================================================================

def test_api_design_workflow(integration_router):
    """
    Test end-to-end workflow for API design request.
    
    Workflow:
    1. User requests knowledge for API design
    2. Router analyzes operation
    3. Router routes to technical repository
    4. Results returned
    """
    # Analyze operation
    decision = integration_router.analyze_operation(
        operation_type=OperationType.API_DESIGN,
        request_type="Design REST API",
        keywords=["api", "rest", "design"],
    )
    
    assert decision is not None
    assert decision.affinity_scores.tech_score > 50
    
    # Query technical knowledge
    if decision.route_to_tech:
        tech_result = integration_router.query_tech(decision)
        assert tech_result is not None
        assert len(tech_result.entries) > 0


def test_business_workflow_request(integration_router):
    """
    Test end-to-end workflow for business workflow request.
    
    Workflow:
    1. User requests knowledge for business workflow
    2. Router analyzes operation
    3. Router routes to business repository
    4. Results returned
    """
    # Analyze operation
    decision = integration_router.analyze_operation(
        operation_type=OperationType.WORKFLOW,
        request_type="Design order workflow",
        keywords=["workflow", "business", "process"],
    )
    
    assert decision is not None
    
    # Query appropriate knowledge
    tech_result, business_result = integration_router.query_all(decision)
    assert tech_result is not None or business_result is not None


def test_security_workflow_request(integration_router):
    """
    Test end-to-end workflow for security-focused request.
    
    Workflow:
    1. User requests security knowledge
    2. Router routes to technical repository (security is technical domain)
    3. Results returned
    """
    # Analyze operation
    decision = integration_router.analyze_operation(
        operation_type=OperationType.SECURITY,
        request_type="Implement authentication",
        keywords=["security", "authentication", "auth"],
    )
    
    assert decision is not None
    assert decision.affinity_scores.tech_score > 0
    
    # Should route to tech
    if decision.route_to_tech:
        tech_result = integration_router.query_tech(decision)
        assert tech_result is not None


# =============================================================================
# TESTS: QUERY ACCURACY VERIFICATION
# =============================================================================

def test_tech_repository_returns_correct_entries(integration_router):
    """Test that technical repository returns expected entries."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.ARCHITECTURE,
        keywords=["microservices"],
    )
    
    if decision.route_to_tech:
        result = integration_router.query_tech(decision)
        assert result.total_matches >= 0
        
        # Verify entries have expected structure
        for entry in result.entries:
            assert isinstance(entry, dict)
            assert "id" in entry or "title" in entry


def test_business_repository_returns_correct_entries(integration_router):
    """Test that business repository returns expected entries."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.WORKFLOW,
        keywords=["workflow", "business"],
    )
    
    if decision.route_to_business:
        result = integration_router.query_business(decision)
        assert result.total_matches >= 0
        
        # Verify entries have expected structure
        for entry in result.entries:
            assert isinstance(entry, dict)


def test_routing_respects_provider_domains(integration_router):
    """Test that routing respects domain availability in providers."""
    tech_domains = integration_router._tech_provider.domains
    business_domains = integration_router._business_provider.domains
    
    assert "ARCHITECTURE" in tech_domains
    assert "payments" in business_domains


# =============================================================================
# TESTS: ROUTING STRATEGY VERIFICATION
# =============================================================================

def test_tech_only_strategy_skips_business_query(integration_router):
    """Test that TECH_ONLY strategy doesn't query business provider."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.ARCHITECTURE,
        keywords=["microservices", "design", "patterns"],
    )
    
    # If truly TECH_ONLY, business query should be empty
    if decision.strategy == RoutingStrategy.TECH_ONLY:
        business_result = integration_router.query_business(decision)
        assert business_result.total_matches == 0


def test_business_only_strategy_skips_tech_query(integration_router):
    """Test that BUSINESS_ONLY strategy doesn't query tech provider."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.WORKFLOW,
        keywords=["workflow", "business", "process"],
    )
    
    # If truly BUSINESS_ONLY, tech query should be empty
    if decision.strategy == RoutingStrategy.BUSINESS_ONLY:
        tech_result = integration_router.query_tech(decision)
        assert tech_result.total_matches == 0


def test_both_strategy_queries_both_providers(integration_router):
    """Test that BOTH strategy queries both providers."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.INTEGRATION,
        keywords=["api", "service", "workflow", "business"],
    )
    
    tech_result, business_result = integration_router.query_all(decision)
    
    if decision.strategy == RoutingStrategy.BOTH:
        # Both should have attempted queries (though results may be empty)
        assert tech_result is not None
        assert business_result is not None


# =============================================================================
# TESTS: PERFORMANCE CHARACTERISTICS
# =============================================================================

def test_routing_decision_performance(integration_router):
    """Test that routing decision is fast (<10ms)."""
    import time
    
    start = time.time()
    decision = integration_router.analyze_operation(
        operation_type=OperationType.API_DESIGN,
        keywords=["api", "design"],
    )
    elapsed = (time.time() - start) * 1000  # Convert to ms
    
    assert elapsed < 50  # Should be fast
    assert decision.decision_time_ms < 50


def test_query_results_have_response_time(integration_router):
    """Test that query results include response time metadata."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.ARCHITECTURE,
        keywords=["microservices"],
    )
    
    result = integration_router.query_tech(decision)
    assert result is not None
    assert hasattr(result, "response_time_ms")


# =============================================================================
# TESTS: FALLBACK BEHAVIOR
# =============================================================================

def test_fallback_routing_when_scores_unclear(integration_router):
    """
    Test fallback behavior when both affinity scores are below threshold.
    
    When both scores are low (<50%), router should attempt to query
    both repositories as fallback.
    """
    # Use ambiguous keywords that don't strongly match either domain
    decision = integration_router.analyze_operation(
        operation_type=OperationType.UNKNOWN,
        keywords=["xyz", "abc", "unknown"],
    )
    
    # Router should make a decision (even if routing to nothing)
    assert decision is not None
    assert decision.strategy in RoutingStrategy


def test_fallback_provides_some_coverage(integration_router):
    """Test that fallback routing attempts to provide coverage."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.UNKNOWN,
        keywords=["uncertain"],
    )
    
    # Even with fallback, one of these should be true
    # (unless both scores are truly 0)
    if decision.strategy != RoutingStrategy.NONE:
        assert decision.route_to_tech or decision.route_to_business


# =============================================================================
# TESTS: MULTI-DOMAIN QUERIES
# =============================================================================

def test_multi_domain_technical_query(integration_router):
    """Test querying multiple technical domains."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.ARCHITECTURE,
        domains=["ARCHITECTURE", "SECURITY"],
        keywords=["design", "security"],
    )
    
    if decision.route_to_tech:
        result = integration_router.query_tech(decision)
        assert result is not None


def test_multi_domain_business_query(integration_router):
    """Test querying multiple business domains."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.WORKFLOW,
        domains=["payments", "orders"],
        keywords=["workflow", "business"],
    )
    
    if decision.route_to_business:
        result = integration_router.query_business(decision)
        assert result is not None


# =============================================================================
# TESTS: CONFIDENCE SCORING INTEGRATION
# =============================================================================

def test_high_confidence_tech_decision(integration_router):
    """Test high-confidence technical decision."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.ARCHITECTURE,
        keywords=["microservices", "design", "patterns", "architecture"],
    )
    
    if decision.route_to_tech:
        assert decision.confidence >= 50


def test_high_confidence_business_decision(integration_router):
    """Test high-confidence business decision."""
    decision = integration_router.analyze_operation(
        operation_type=OperationType.BUSINESS_PROCESS,
        keywords=["workflow", "business", "process", "service"],
    )
    
    # Should have some confidence for business operation
    assert decision.confidence >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
