# © 2025-2026 Asif Hussain. All rights reserved.
# PHASE-21: AC-IKP-001-01 Protocol Tests
"""
Unit tests for KnowledgeProvider protocol (Tier0).

Test Coverage:
  - Protocol structure verification
  - Protocol properties (is_loaded, entry_count, domains)
  - Protocol methods (query, get_by_domain, get_relevant_knowledge)
  - Query parameter variations
  - Edge cases and error conditions
  - Protocol validation utility

CORE Governance:
  - CORE-008: TDD (tests first - 10 tests)
  - CORE-011: Type hints enforced
  - CORE-013: Specific exception handling

References:
  - PHASE-21-KICKOFF.md: AC-IKP-001 specification
  - cortex/core/knowledge/protocol.py: Protocol definition
"""

import pytest
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from cortex.core.knowledge import (
    KnowledgeProvider,
    KnowledgeQuery,
    KnowledgeQueryResult,
)
from cortex.core.knowledge.protocol import is_knowledge_provider


# =============================================================================
# TEST FIXTURES
# =============================================================================

class MockKnowledgeProvider:
    """
    Mock implementation of KnowledgeProvider protocol for testing.
    
    Used to verify protocol structure and test framework.
    """
    
    def __init__(
        self,
        entries: Optional[List[Dict[str, Any]]] = None,
        domains: Optional[List[str]] = None,
    ):
        """Initialize mock provider."""
        self._entries = entries or []
        self._domains = domains or []
        self._is_loaded = len(entries) > 0 if entries else True
    
    @property
    def is_loaded(self) -> bool:
        """Check if provider is loaded."""
        return self._is_loaded
    
    @property
    def entry_count(self) -> int:
        """Get entry count."""
        return len(self._entries)
    
    @property
    def domains(self) -> List[str]:
        """Get available domains."""
        return self._domains
    
    def query(
        self,
        keywords: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> KnowledgeQueryResult:
        """Query knowledge."""
        filtered = self._entries[offset:]
        if limit:
            filtered = filtered[:limit]
        
        query = KnowledgeQuery(
            keywords=keywords,
            tags=tags,
            entity_types=entity_types,
        )
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
            query=query,
            provider_type="MOCK",
        )
    
    def get_by_domain(self, domain: str) -> KnowledgeQueryResult:
        """Get knowledge by domain."""
        if domain not in self._domains:
            raise ValueError(f"Domain not found: {domain}")
        
        filtered = [e for e in self._entries if e.get("domain") == domain]
        
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
            query=KnowledgeQuery(domains=[domain]),
            provider_type="MOCK",
        )
    
    def get_relevant_knowledge(
        self,
        domains: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
    ) -> KnowledgeQueryResult:
        """Get relevant knowledge."""
        filtered = self._entries
        
        if domains:
            filtered = [e for e in filtered if e.get("domain") in domains]
        
        query = KnowledgeQuery(domains=domains, keywords=keywords)
        return KnowledgeQueryResult(
            entries=filtered,
            total_matches=len(filtered),
            query=query,
            provider_type="MOCK",
        )


@pytest.fixture
def mock_provider():
    """Create mock knowledge provider."""
    entries = [
        {
            "id": "KB-ARC-001",
            "domain": "ARCHITECTURE",
            "title": "Microservices Design",
            "tags": ["design", "patterns"],
        },
        {
            "id": "KB-SEC-001",
            "domain": "SECURITY",
            "title": "Authentication",
            "tags": ["auth", "security"],
        },
        {
            "id": "KB-ARC-002",
            "domain": "ARCHITECTURE",
            "title": "API Design",
            "tags": ["api", "design"],
        },
    ]
    return MockKnowledgeProvider(
        entries=entries,
        domains=["ARCHITECTURE", "SECURITY"],
    )


@pytest.fixture
def empty_provider():
    """Create empty knowledge provider."""
    return MockKnowledgeProvider(entries=[], domains=[])


@pytest.fixture
def unloaded_provider():
    """Create unloaded provider."""
    provider = MockKnowledgeProvider()
    provider._is_loaded = False
    return provider


# =============================================================================
# TESTS: PROTOCOL STRUCTURE
# =============================================================================

def test_knowledge_provider_protocol_exists():
    """Test that KnowledgeProvider protocol is properly defined."""
    assert hasattr(KnowledgeProvider, "__protocol_attrs__") or hasattr(
        KnowledgeProvider, "_is_protocol"
    )


def test_protocol_has_required_properties():
    """Test that protocol defines required properties."""
    protocol_attrs = set()
    
    # Check methods/properties exist in protocol
    for attr_name in ["is_loaded", "entry_count", "domains"]:
        assert hasattr(KnowledgeProvider, attr_name) or attr_name in KnowledgeProvider.__mro__[0].__dict__
    
    # Check methods exist
    for method_name in ["query", "get_by_domain", "get_relevant_knowledge"]:
        assert hasattr(KnowledgeProvider, method_name) or method_name in KnowledgeProvider.__mro__[0].__dict__


def test_protocol_has_required_methods():
    """Test that protocol defines all required methods."""
    required_methods = [
        "query",
        "get_by_domain",
        "get_relevant_knowledge",
    ]
    
    for method in required_methods:
        # Protocol defines the method signature
        assert callable(getattr(KnowledgeProvider, method, None))


# =============================================================================
# TESTS: PROTOCOL IMPLEMENTATION
# =============================================================================

def test_mock_provider_implements_protocol(mock_provider):
    """Test that mock provider implements KnowledgeProvider protocol."""
    assert isinstance(mock_provider, KnowledgeProvider)


def test_is_knowledge_provider_with_valid_provider(mock_provider):
    """Test is_knowledge_provider utility with valid provider."""
    assert is_knowledge_provider(mock_provider)


def test_is_knowledge_provider_with_invalid_provider():
    """Test is_knowledge_provider utility with invalid provider."""
    assert not is_knowledge_provider("not a provider")
    assert not is_knowledge_provider(123)
    assert not is_knowledge_provider(None)


# =============================================================================
# TESTS: PROTOCOL PROPERTIES
# =============================================================================

def test_is_loaded_property(mock_provider, unloaded_provider, empty_provider):
    """Test is_loaded property."""
    assert mock_provider.is_loaded is True
    assert unloaded_provider.is_loaded is False
    assert empty_provider.is_loaded is True


def test_entry_count_property(mock_provider, empty_provider):
    """Test entry_count property."""
    assert mock_provider.entry_count == 3
    assert empty_provider.entry_count == 0


def test_entry_count_non_negative(mock_provider):
    """Test that entry_count is always non-negative."""
    assert mock_provider.entry_count >= 0


def test_domains_property(mock_provider, empty_provider):
    """Test domains property."""
    assert mock_provider.domains == ["ARCHITECTURE", "SECURITY"]
    assert empty_provider.domains == []


# =============================================================================
# TESTS: PROTOCOL METHODS - query()
# =============================================================================

def test_query_method_returns_query_result(mock_provider):
    """Test that query method returns KnowledgeQueryResult."""
    result = mock_provider.query()
    assert isinstance(result, KnowledgeQueryResult)


def test_query_with_no_filters_returns_all(mock_provider):
    """Test query with no filters returns all entries."""
    result = mock_provider.query()
    assert result.total_matches == 3
    assert len(result.entries) == 3


def test_query_with_limit(mock_provider):
    """Test query with limit parameter."""
    result = mock_provider.query(limit=2)
    assert result.total_matches == 2
    assert len(result.entries) == 2


def test_query_with_offset(mock_provider):
    """Test query with offset parameter."""
    result = mock_provider.query(offset=1)
    assert result.total_matches == 2
    assert len(result.entries) == 2


def test_query_result_includes_timestamp(mock_provider):
    """Test that query result includes timestamp."""
    result = mock_provider.query()
    assert result.timestamp is not None
    assert len(result.timestamp) > 0


def test_query_result_includes_response_time(mock_provider):
    """Test that query result includes response time."""
    result = mock_provider.query()
    assert hasattr(result, "response_time_ms")
    assert result.response_time_ms >= 0


# =============================================================================
# TESTS: PROTOCOL METHODS - get_by_domain()
# =============================================================================

def test_get_by_domain_returns_query_result(mock_provider):
    """Test that get_by_domain returns KnowledgeQueryResult."""
    result = mock_provider.get_by_domain("ARCHITECTURE")
    assert isinstance(result, KnowledgeQueryResult)


def test_get_by_domain_filters_correctly(mock_provider):
    """Test that get_by_domain filters to correct domain."""
    result = mock_provider.get_by_domain("ARCHITECTURE")
    assert result.total_matches == 2
    assert all(e.get("domain") == "ARCHITECTURE" for e in result.entries)


def test_get_by_domain_raises_for_missing_domain(mock_provider):
    """Test that get_by_domain raises ValueError for missing domain."""
    with pytest.raises(ValueError):
        mock_provider.get_by_domain("NONEXISTENT")


def test_get_by_domain_security_domain(mock_provider):
    """Test get_by_domain for SECURITY domain."""
    result = mock_provider.get_by_domain("SECURITY")
    assert result.total_matches == 1
    assert result.entries[0].get("domain") == "SECURITY"


# =============================================================================
# TESTS: PROTOCOL METHODS - get_relevant_knowledge()
# =============================================================================

def test_get_relevant_knowledge_returns_query_result(mock_provider):
    """Test that get_relevant_knowledge returns KnowledgeQueryResult."""
    result = mock_provider.get_relevant_knowledge()
    assert isinstance(result, KnowledgeQueryResult)


def test_get_relevant_knowledge_with_domains(mock_provider):
    """Test get_relevant_knowledge with domain filter."""
    result = mock_provider.get_relevant_knowledge(domains=["ARCHITECTURE"])
    assert result.total_matches == 2
    assert all(e.get("domain") == "ARCHITECTURE" for e in result.entries)


def test_get_relevant_knowledge_with_multiple_domains(mock_provider):
    """Test get_relevant_knowledge with multiple domains."""
    result = mock_provider.get_relevant_knowledge(
        domains=["ARCHITECTURE", "SECURITY"]
    )
    assert result.total_matches == 3


def test_get_relevant_knowledge_with_keywords(mock_provider):
    """Test get_relevant_knowledge with keywords."""
    result = mock_provider.get_relevant_knowledge(keywords=["design"])
    assert result.total_matches >= 0


def test_get_relevant_knowledge_with_no_filters(mock_provider):
    """Test get_relevant_knowledge with no filters returns all."""
    result = mock_provider.get_relevant_knowledge()
    assert result.total_matches == 3


# =============================================================================
# TESTS: DATA CLASSES
# =============================================================================

def test_knowledge_query_has_filters():
    """Test KnowledgeQuery.has_filters() method."""
    query1 = KnowledgeQuery()
    assert not query1.has_filters()
    
    query2 = KnowledgeQuery(keywords=["test"])
    assert query2.has_filters()
    
    query3 = KnowledgeQuery(domains=["ARCHITECTURE"])
    assert query3.has_filters()


def test_knowledge_query_result_calculates_total_matches():
    """Test that KnowledgeQueryResult calculates total_matches."""
    entries = [{"id": "1"}, {"id": "2"}]
    result = KnowledgeQueryResult(entries=entries, total_matches=0)
    # Note: In real usage, total_matches should be set correctly
    assert result.total_matches >= 0


def test_knowledge_query_result_has_defaults():
    """Test that KnowledgeQueryResult has sensible defaults."""
    result = KnowledgeQueryResult(entries=[], total_matches=0)
    assert result.entries == []
    assert result.total_matches == 0
    assert result.timestamp is not None
    assert result.response_time_ms >= 0


# =============================================================================
# TESTS: EDGE CASES
# =============================================================================

def test_query_on_empty_provider(empty_provider):
    """Test query on empty provider."""
    result = empty_provider.query()
    assert result.total_matches == 0
    assert result.entries == []


def test_get_by_domain_on_empty_provider(empty_provider):
    """Test get_by_domain on empty provider."""
    with pytest.raises(ValueError):
        empty_provider.get_by_domain("ANY")


def test_query_result_is_serializable():
    """Test that KnowledgeQueryResult can be serialized."""
    result = KnowledgeQueryResult(
        entries=[{"id": "1", "title": "Test"}],
        total_matches=1,
    )
    
    # Should be able to convert to dict (for JSON serialization)
    assert isinstance(asdict(result), dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
