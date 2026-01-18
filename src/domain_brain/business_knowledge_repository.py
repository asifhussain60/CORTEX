# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: KN-003-01 - Business Knowledge Repository Integration
"""
Business Knowledge Repository for Domain Brain Access (KN-003-01).

PHASE-REMEDIATION-06: Business Knowledge Repository Integration
AC-ID: KN-003-01 - Business Knowledge Repository Access Layer

This module provides the Master Orchestrator with access to business
domain knowledge stored in the Domain Brain (BKIO). Mirrors the structure
of KnowledgeRepository for technical best practices, enabling unified
knowledge evaluation during request composition.

Core Responsibilities:
1. Query business domains and entities from DomainBrainAPI
2. Provide domain-based knowledge lookup
3. Query knowledge by domain, entity type, or keywords
4. Support business knowledge evaluation during request composition
5. Cache loaded knowledge for performance

Integration Points:
- MasterOrchestrator: Evaluates business knowledge during coordinate_operation()
- BKIO: Sources business knowledge from ingested documents
- DomainBrainAPI: Underlying storage/query interface

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.domain_brain.api import DomainBrainAPI
from src.domain_brain.models import Domain, Entity, EntityType


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BusinessKnowledgeEntry:
    """
    Represents a single business knowledge entry from Domain Brain.
    
    Attributes:
        id: Unique identifier (entity_id)
        domain_id: Domain this entity belongs to
        domain_name: Human-readable domain name
        entity_type: Type of entity (SERVICE, FUNCTION, API, etc.)
        name: Entity name
        description: Entity description
        source: Knowledge source (BKIO, AST, etc.)
        metadata: Additional metadata
        version: Entry version
    """
    id: str
    domain_id: str
    domain_name: str
    entity_type: str
    name: str
    description: str
    source: str = "BKIO"
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1


@dataclass
class BusinessKnowledgeQueryResult:
    """
    Result from a business knowledge query.
    
    Attributes:
        entries: List of matching BusinessKnowledgeEntry objects
        query_domain: Domain filter used (if any)
        query_entity_type: Entity type filter used (if any)
        query_keywords: Keywords searched (if any)
        total_matches: Total number of matches
        timestamp: When query was executed
    """
    entries: List[BusinessKnowledgeEntry]
    query_domain: Optional[str] = None
    query_entity_type: Optional[str] = None
    query_keywords: Optional[List[str]] = None
    total_matches: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        self.total_matches = len(self.entries)


# =============================================================================
# BUSINESS KNOWLEDGE REPOSITORY
# =============================================================================

class BusinessKnowledgeRepository:
    """
    Repository for accessing business domain knowledge from Domain Brain.
    
    Provides the Master Orchestrator with access to business domain
    entities, services, APIs, and workflows stored via BKIO ingestion.
    Mirrors the KnowledgeRepository interface for consistency.
    
    Usage:
        repo = BusinessKnowledgeRepository()
        
        # Get domains
        domains = repo.get_domains()
        
        # Query by domain
        payments_knowledge = repo.get_by_domain("payments")
        
        # Query by entity type
        services = repo.query(entity_types=["service"])
        
        # Get all knowledge for a request context
        relevant = repo.get_relevant_knowledge(
            domains=["payments", "compliance"],
            keywords=["transaction", "validation"]
        )
    
    CORE Governance:
      - CORE-011: Type hints - all methods typed
      - CORE-012: Docstrings - Google style
      - CORE-013: Specific exception handling
    """
    
    def __init__(
        self,
        domain_brain_api: Optional[DomainBrainAPI] = None
    ) -> None:
        """
        Initialize the Business Knowledge Repository.
        
        Args:
            domain_brain_api: DomainBrainAPI instance (creates new if None)
        """
        self._api = domain_brain_api or DomainBrainAPI()
        self._cache: Dict[str, List[BusinessKnowledgeEntry]] = {}
        self._cache_timestamp: Optional[str] = None
        self._loaded = True  # Domain Brain API is always available
    
    @property
    def is_loaded(self) -> bool:
        """Check if repository is loaded."""
        return self._loaded
    
    @property
    def entry_count(self) -> int:
        """Get total number of knowledge entries across all domains."""
        count = 0
        for domain in self._api.list_domains():
            count += len(domain.entities)
        return count
    
    @property
    def domains(self) -> List[str]:
        """Get list of available domain IDs."""
        return [d.domain_id for d in self._api.list_domains()]
    
    @property
    def domain_names(self) -> Dict[str, str]:
        """Get mapping of domain IDs to names."""
        return {d.domain_id: d.name for d in self._api.list_domains()}
    
    def get_domain(self, domain_id: str) -> Optional[Domain]:
        """
        Get a specific domain by ID.
        
        Args:
            domain_id: The domain ID
            
        Returns:
            Domain if found, None otherwise
        """
        return self._api.query_domain(domain_id)
    
    def get_by_domain(self, domain_id: str) -> List[BusinessKnowledgeEntry]:
        """
        Get all knowledge entries for a domain.
        
        Args:
            domain_id: Domain ID to query
            
        Returns:
            List of BusinessKnowledgeEntry objects for the domain
        """
        domain = self._api.query_domain(domain_id)
        if not domain:
            return []
        
        entries = []
        for entity in domain.entities.values():
            entry = self._entity_to_entry(entity, domain)
            entries.append(entry)
        
        return entries
    
    def _entity_to_entry(
        self, entity: Entity, domain: Domain
    ) -> BusinessKnowledgeEntry:
        """Convert Domain Brain Entity to BusinessKnowledgeEntry."""
        return BusinessKnowledgeEntry(
            id=entity.entity_id,
            domain_id=domain.domain_id,
            domain_name=domain.name,
            entity_type=entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
            name=entity.name,
            description=entity.description,
            source=entity.source,
            metadata=entity.metadata,
            version=getattr(entity, 'version', 1)
        )
    
    def query(
        self,
        domains: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> BusinessKnowledgeQueryResult:
        """
        Query business knowledge entries with optional filters.
        
        Args:
            domains: List of domain IDs to filter by
            entity_types: List of entity types to filter by
            keywords: List of keywords to search in name/description
            
        Returns:
            BusinessKnowledgeQueryResult with matching entries
        """
        results: List[BusinessKnowledgeEntry] = []
        
        # Get domains to search
        search_domains = self._api.list_domains()
        if domains:
            search_domains = [d for d in search_domains if d.domain_id in domains]
        
        for domain in search_domains:
            for entity in domain.entities.values():
                # Entity type filter
                if entity_types:
                    entity_type_str = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
                    if entity_type_str.lower() not in [t.lower() for t in entity_types]:
                        continue
                
                # Keyword filter
                if keywords:
                    searchable = f"{entity.name} {entity.description}".lower()
                    if not any(kw.lower() in searchable for kw in keywords):
                        continue
                
                entry = self._entity_to_entry(entity, domain)
                results.append(entry)
        
        return BusinessKnowledgeQueryResult(
            entries=results,
            query_domain=domains[0] if domains and len(domains) == 1 else None,
            query_entity_type=entity_types[0] if entity_types and len(entity_types) == 1 else None,
            query_keywords=keywords
        )
    
    def get_relevant_knowledge(
        self,
        domains: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        max_entries: int = 10
    ) -> List[BusinessKnowledgeEntry]:
        """
        Get the most relevant business knowledge entries for a context.
        
        This is the primary method used by MasterOrchestrator when
        composing requests. It returns knowledge sorted by relevance.
        
        Args:
            domains: Preferred domains to prioritize
            keywords: Keywords to match
            max_entries: Maximum entries to return
            
        Returns:
            List of relevant BusinessKnowledgeEntry objects
        """
        # Query with filters
        result = self.query(domains=domains, keywords=keywords)
        
        # Sort by relevance
        def relevance_score(entry: BusinessKnowledgeEntry) -> float:
            score = 0.0
            
            # Domain match
            if domains and entry.domain_id in domains:
                score += 1.0
            
            # Keyword match count
            if keywords:
                searchable = f"{entry.name} {entry.description}".lower()
                for kw in keywords:
                    if kw.lower() in searchable:
                        score += 0.5
            
            # Prefer BKIO source (highest in hierarchy)
            if entry.source == "BKIO":
                score += 0.3
            
            return score
        
        sorted_entries = sorted(result.entries, key=relevance_score, reverse=True)
        return sorted_entries[:max_entries]
    
    def search_entities(self, query: str) -> List[BusinessKnowledgeEntry]:
        """
        Search for entities across all domains.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching BusinessKnowledgeEntry objects
        """
        entities = self._api.search_entities(query)
        
        # Need to find domain for each entity
        entries = []
        for entity in entities:
            # Find domain containing this entity
            for domain in self._api.list_domains():
                if entity.entity_id in domain.entities:
                    entry = self._entity_to_entry(entity, domain)
                    entries.append(entry)
                    break
        
        return entries
    
    def get_services(self) -> List[BusinessKnowledgeEntry]:
        """Get all service entities."""
        return self.query(entity_types=["service"]).entries
    
    def get_apis(self) -> List[BusinessKnowledgeEntry]:
        """Get all API entities."""
        return self.query(entity_types=["api"]).entries
    
    def get_workflows(self) -> List[BusinessKnowledgeEntry]:
        """Get all workflow entities."""
        return self.query(entity_types=["workflow"]).entries
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all available business knowledge.
        
        Returns:
            Dict with domain counts, total entries, and metadata
        """
        all_domains = self._api.list_domains()
        
        domain_counts = {}
        entity_type_counts: Dict[str, int] = {}
        
        for domain in all_domains:
            domain_counts[domain.domain_id] = len(domain.entities)
            
            for entity in domain.entities.values():
                entity_type = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
                entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        return {
            "total_domains": len(all_domains),
            "total_entries": self.entry_count,
            "domains": self.domains,
            "domain_counts": domain_counts,
            "entity_type_counts": entity_type_counts,
            "loaded": self._loaded
        }
    
    def clear_cache(self) -> None:
        """Clear the entry cache."""
        self._cache.clear()
        self._cache_timestamp = None
    
    def refresh(self) -> None:
        """Refresh knowledge from Domain Brain (re-query all domains)."""
        self._cache.clear()
        self._cache_timestamp = datetime.now().isoformat()


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_repository_instance: Optional[BusinessKnowledgeRepository] = None


def get_business_knowledge_repository(
    domain_brain_api: Optional[DomainBrainAPI] = None,
    force_reload: bool = False
) -> BusinessKnowledgeRepository:
    """
    Get the singleton BusinessKnowledgeRepository instance.
    
    Args:
        domain_brain_api: DomainBrainAPI instance (only used on first call)
        force_reload: Force recreation of the repository
        
    Returns:
        BusinessKnowledgeRepository singleton instance
    """
    global _repository_instance
    
    if _repository_instance is None or force_reload:
        _repository_instance = BusinessKnowledgeRepository(
            domain_brain_api=domain_brain_api
        )
    
    return _repository_instance
