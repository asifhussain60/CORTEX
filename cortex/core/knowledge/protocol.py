# PHASE-21: Intelligent Knowledge Protocol (AC-IKP-001-01)
"""
Core knowledge provider protocol definition (Tier0 abstraction).

PHASE-21-AC-IKP-001-01: Define KnowledgeProvider Protocol

This module defines the KnowledgeProvider protocol that all knowledge
repositories must implement. Using typing.Protocol enables structural
subtyping, allowing existing KnowledgeRepository and BusinessKnowledgeRepository
to satisfy the protocol without modification.

Protocol Definition:
  - is_loaded: bool property - Repository loaded status
  - entry_count: int property - Total entries available
  - domains: List[str] property - Available knowledge domains
  - query: Query by keywords, tags, or fields
  - get_by_domain: Get all knowledge in a domain
  - get_relevant_knowledge: Multi-criteria query with domain and keywords

Design Benefits:
  1. Structural Typing: No inheritance required
  2. Backward Compatible: Existing repos implement protocol automatically
  3. Type Safe: Full mypy --strict compliance
  4. Interface Contract: Clear method signatures and semantics
  5. Extensible: New providers just implement the 6 methods

Example Usage:
    from cortex.core.knowledge import KnowledgeProvider
    from cortex.brain.core.knowledge import KnowledgeRepository
    from cortex.brain.domain_brain import BusinessKnowledgeRepository
    
    def process_with_provider(provider: KnowledgeProvider) -> None:
        \"\"\"Works with any knowledge provider.\"\"\"
        if not provider.is_loaded:
            return
        
        domains = provider.domains
        technical_knowledge = provider.query(keywords=["design", "patterns"])
        architecture_knowledge = provider.get_by_domain("ARCHITECTURE")
        
        relevant = provider.get_relevant_knowledge(
            domains=["ARCHITECTURE", "SECURITY"],
            keywords=["microservices", "authentication"]
        )

CORE Governance:
  - CORE-004: Tier organization (Tier0 = core protocols)
  - CORE-011: Type hints (100% coverage)
  - CORE-012: Docstrings (Google style)

References:
  - PEP 544: Protocols – Structural subtyping
  - PHASE-21-KICKOFF.md: Full specification
  - PHASE-21-ARCHITECTURE-REVIEW.md: Design validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class KnowledgeQuery:
    """
    Structured knowledge query parameters.
    
    Attributes:
        domains: List of domain names to filter by
        keywords: Keywords to search for
        tags: Tags to filter by (for technical knowledge)
        entity_types: Entity types to filter by (for business knowledge)
        limit: Maximum results to return (default: None = no limit)
        offset: Pagination offset (default: 0)
    """
    domains: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    entity_types: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: int = 0
    
    def has_filters(self) -> bool:
        """Check if query has any active filters."""
        return any([
            self.domains,
            self.keywords,
            self.tags,
            self.entity_types,
        ])


@dataclass
class KnowledgeQueryResult:
    """
    Unified result from a knowledge query.
    
    Attributes:
        entries: List of knowledge entries (dicts to support both repos)
        total_matches: Total number of matches found
        query: Original query that produced this result
        timestamp: ISO format timestamp of query execution
        provider_type: Type of provider (TECHNICAL or BUSINESS)
        response_time_ms: Query response time in milliseconds
    """
    entries: List[Dict[str, Any]]
    total_matches: int
    query: KnowledgeQuery = field(default_factory=KnowledgeQuery)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    provider_type: str = "UNKNOWN"
    response_time_ms: float = 0.0


# =============================================================================
# PROTOCOL DEFINITION (Tier0)
# =============================================================================

@runtime_checkable
class KnowledgeProvider(Protocol):
    """
    Protocol for knowledge repository providers.
    
    All knowledge repositories must implement this protocol to be usable
    by the MasterOrchestrator and other CORTEX components.
    
    This is a structural protocol: any class with these methods and properties
    automatically satisfies the protocol, no inheritance required.
    
    Methods:
        is_loaded: Check if repository is ready
        entry_count: Get total entries available
        domains: Get list of available domains
        query: Query by keywords, tags, or entity types
        get_by_domain: Get all knowledge in a specific domain
        get_relevant_knowledge: Multi-criteria query combining domains + keywords
    
    CORE Governance:
      - CORE-004: Tier0 protocol (all tiers depend on)
      - CORE-011: Type hints enforced (Protocol enforces signatures)
      - CORE-012: Docstrings required (this docstring validates)
    """
    
    @property
    def is_loaded(self) -> bool:
        """
        Check if the knowledge repository is loaded and ready.
        
        Returns:
            True if repository is loaded, False otherwise.
            
        Examples:
            >>> provider = KnowledgeRepository()
            >>> if provider.is_loaded:
            ...     entries = provider.entry_count
        """
        ...
    
    @property
    def entry_count(self) -> int:
        """
        Get total number of knowledge entries available.
        
        Returns:
            Total count of entries in repository.
            Must return 0 if repository is not loaded.
            
        Examples:
            >>> count = provider.entry_count
            >>> assert count >= 0
        """
        ...
    
    @property
    def domains(self) -> List[str]:
        """
        Get list of available knowledge domains.
        
        Returns:
            List of domain names (e.g., ["ARCHITECTURE", "SECURITY"]).
            Must return empty list if repository is not loaded.
            
        Examples:
            >>> domains = provider.domains
            >>> if "SECURITY" in domains:
            ...     security_knowledge = provider.get_by_domain("SECURITY")
        """
        ...
    
    def query(
        self,
        keywords: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> KnowledgeQueryResult:
        """
        Query knowledge by keywords, tags, or entity types.
        
        Args:
            keywords: List of keywords to search for. Supports AND semantics
                (all keywords must be present in entry). Optional.
            tags: List of tags to filter by (technical knowledge only).
                Supports OR semantics (any tag can match). Optional.
            entity_types: List of entity types to filter by (business knowledge
                only, e.g., "SERVICE", "API"). Optional.
            limit: Maximum number of results to return. If None, return all.
            offset: Pagination offset (default: 0).
        
        Returns:
            KnowledgeQueryResult with matching entries and metadata.
        
        Examples:
            >>> result = provider.query(keywords=["design", "patterns"])
            >>> print(f"Found {result.total_matches} entries")
            
            >>> api_knowledge = provider.query(tags=["api"])
            >>> business_result = provider.query(entity_types=["SERVICE"])
        
        Notes:
            - Query with no filters should return all entries (respecting limit/offset)
            - Query result must include response_time_ms for performance tracking
            - Empty result should return total_matches=0, entries=[]
        """
        ...
    
    def get_by_domain(self, domain: str) -> KnowledgeQueryResult:
        """
        Get all knowledge entries for a specific domain.
        
        Args:
            domain: Domain name (must match exactly, case-sensitive).
        
        Returns:
            KnowledgeQueryResult with entries for the domain.
            
        Raises:
            ValueError: If domain is not available in this provider.
        
        Examples:
            >>> security_knowledge = provider.get_by_domain("SECURITY")
            >>> print(f"Security entries: {security_knowledge.total_matches}")
            
            >>> if "ARCHITECTURE" in provider.domains:
            ...     arch_knowledge = provider.get_by_domain("ARCHITECTURE")
        
        Notes:
            - Raises ValueError if domain doesn't exist
            - Query result provider_type should indicate source (TECHNICAL/BUSINESS)
        """
        ...
    
    def get_relevant_knowledge(
        self,
        domains: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
    ) -> KnowledgeQueryResult:
        """
        Get knowledge matching both domain and keyword criteria.
        
        This is the primary method for knowledge retrieval in MasterOrchestrator.
        It combines domain filtering with keyword search.
        
        Args:
            domains: Specific domains to include (OR semantics: any domain match).
                If None, search all domains.
            keywords: Keywords to search for (AND semantics: all must be present).
                If None, return all in selected domains.
        
        Returns:
            KnowledgeQueryResult with entries matching criteria.
        
        Examples:
            >>> knowledge = provider.get_relevant_knowledge(
            ...     domains=["ARCHITECTURE", "SECURITY"],
            ...     keywords=["microservices", "authentication"]
            ... )
            >>> print(f"Relevant entries: {knowledge.total_matches}")
            
            >>> # Get all security knowledge without keywords
            >>> security_all = provider.get_relevant_knowledge(domains=["SECURITY"])
            
            >>> # Search all domains for specific keywords
            >>> keywords_search = provider.get_relevant_knowledge(
            ...     keywords=["design", "patterns"]
            ... )
        
        Notes:
            - If both domains and keywords are None, returns all entries
            - Empty domains list means no domain filter (search all)
            - Empty keywords list means no keyword filter (return all in domains)
            - Query result must include response_time_ms for performance analysis
            - This method is used by IntelligentKnowledgeRouter to evaluate affinity
        """
        ...


# =============================================================================
# PROTOCOL VALIDATION UTILITIES
# =============================================================================

def is_knowledge_provider(obj: Any) -> bool:
    """
    Check if an object implements the KnowledgeProvider protocol.
    
    This uses structural subtyping, so any object with the required
    methods and properties will return True.
    
    Args:
        obj: Object to check.
    
    Returns:
        True if object implements KnowledgeProvider protocol, False otherwise.
    
    Examples:
        >>> from cortex.brain.core.knowledge import KnowledgeRepository
        >>> repo = KnowledgeRepository()
        >>> assert is_knowledge_provider(repo)
        
        >>> from cortex.brain.domain_brain import BusinessKnowledgeRepository
        >>> business_repo = BusinessKnowledgeRepository()
        >>> assert is_knowledge_provider(business_repo)
        
        >>> assert not is_knowledge_provider("not a provider")
    """
    return isinstance(obj, KnowledgeProvider)
