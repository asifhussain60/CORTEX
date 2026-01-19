# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: KN-002-01 - Knowledge Repository Integration
"""
Knowledge Repository for Best Practices YAML Access (KN-002-01).

PHASE-REMEDIATION-06: Master Orchestrator Knowledge Integration
AC-ID: KN-002-01 - Knowledge Repository Access Layer

This module provides the Master Orchestrator with access to the curated
knowledge YAML files containing best practices, security guidelines,
architecture patterns, and domain-specific expertise.

Core Responsibilities:
1. Load knowledge index from .knowledge-index.json
2. Provide domain-based knowledge lookup
3. Query knowledge by tags, domain, or keywords
4. Support knowledge evaluation during request composition
5. Cache loaded knowledge for performance

Integration Points:
- MasterOrchestrator: Evaluates knowledge during coordinate_operation()
- GovernanceRegistry: Cross-references governance rules with knowledge
- BehavioralBoundaryRules: Validates actions against security knowledge

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

from __future__ import annotations

import json
import os
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class KnowledgeEntry:
    """
    Represents a single knowledge entry from the repository.
    
    Attributes:
        id: Unique identifier (e.g., KB-ARC-001)
        domain: Knowledge domain (e.g., ARCHITECTURE, SECURITY)
        title: Human-readable title
        description: Brief description or summary
        file_path: Relative path to YAML file
        source_file: Original source file path
        tags: List of tags for categorization
        version: Entry version
        content: Full YAML content (lazy loaded)
        migrated_at: When entry was migrated
    """
    id: str
    domain: str
    title: str
    description: Any  # Can be string or dict
    file_path: str
    source_file: str = ""
    tags: List[str] = field(default_factory=list)
    version: str = "1.0"
    content: Optional[Dict[str, Any]] = None
    migrated_at: str = ""


@dataclass
class KnowledgeQueryResult:
    """
    Result from a knowledge query.
    
    Attributes:
        entries: List of matching KnowledgeEntry objects
        query_domain: Domain filter used (if any)
        query_tags: Tags filter used (if any)
        query_keywords: Keywords searched (if any)
        total_matches: Total number of matches
        timestamp: When query was executed
    """
    entries: List[KnowledgeEntry]
    query_domain: Optional[str] = None
    query_tags: Optional[List[str]] = None
    query_keywords: Optional[List[str]] = None
    total_matches: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        self.total_matches = len(self.entries)


# =============================================================================
# KNOWLEDGE REPOSITORY
# =============================================================================

class KnowledgeRepository:
    """
    Repository for accessing curated knowledge YAML files.
    
    Provides the Master Orchestrator with access to best practices,
    security guidelines, architecture patterns, and domain expertise
    stored in the knowledge YAML files.
    
    Usage:
        repo = KnowledgeRepository()
        
        # Load knowledge by domain
        security_knowledge = repo.get_by_domain("SECURITY")
        
        # Query by tags
        api_knowledge = repo.query(tags=["api", "design"])
        
        # Get all knowledge for a request context
        relevant = repo.get_relevant_knowledge(
            domains=["ARCHITECTURE", "SECURITY"],
            keywords=["microservices", "authentication"]
        )
    
    CORE Governance:
      - CORE-011: Type hints - all methods typed
      - CORE-012: Docstrings - Google style
      - CORE-013: Specific exception handling
    """
    
    # Default paths (relative to project root)
    DEFAULT_INDEX_PATH = "cortex_brain/tier3/knowledge/.knowledge-index.json"
    DEFAULT_KNOWLEDGE_DIR = "cortex_brain/tier3/knowledge"
    
    def __init__(
        self,
        project_root: Optional[str] = None,
        index_path: Optional[str] = None,
        knowledge_dir: Optional[str] = None
    ) -> None:
        """
        Initialize the Knowledge Repository.
        
        Args:
            project_root: Path to project root (auto-detected if None)
            index_path: Path to .knowledge-index.json (relative to root)
            knowledge_dir: Path to knowledge directory (relative to root)
        
        Raises:
            FileNotFoundError: If index file is not found
        """
        self._project_root = self._resolve_project_root(project_root)
        self._index_path = index_path or self.DEFAULT_INDEX_PATH
        self._knowledge_dir = knowledge_dir or self.DEFAULT_KNOWLEDGE_DIR
        
        self._index: Dict[str, Any] = {}
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._domains: Dict[str, List[str]] = {}  # domain -> list of entry IDs
        self._loaded = False
        self._content_cache: Dict[str, Dict[str, Any]] = {}
        
        # Load index on initialization
        self._load_index()
    
    def _resolve_project_root(self, provided_root: Optional[str]) -> Path:
        """
        Resolve the project root directory.
        
        Args:
            provided_root: User-provided root path or None
            
        Returns:
            Path to project root
        """
        if provided_root:
            return Path(provided_root)
        
        # Auto-detect: walk up from this file's location
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / "cortex_brain").exists() or (parent / "src").exists():
                return parent
        
        # Fallback to current working directory
        return Path.cwd()
    
    def _load_index(self) -> None:
        """
        Load the knowledge index from .knowledge-index.json.
        
        Raises:
            FileNotFoundError: If index file is not found
            json.JSONDecodeError: If index file is invalid JSON
        """
        index_file = self._project_root / self._index_path
        
        if not index_file.exists():
            raise FileNotFoundError(
                f"Knowledge index not found: {index_file}. "
                f"Run knowledge migration first."
            )
        
        with open(index_file, 'r', encoding='utf-8') as f:
            self._index = json.load(f)
        
        # Parse entries
        for entry_data in self._index.get("entries", []):
            entry = KnowledgeEntry(
                id=entry_data.get("id", ""),
                domain=entry_data.get("domain", ""),
                title=entry_data.get("title", ""),
                description=entry_data.get("description", ""),
                file_path=entry_data.get("file_path", ""),
                source_file=entry_data.get("source_file", ""),
                tags=entry_data.get("tags", []),
                version=entry_data.get("version", "1.0"),
                migrated_at=entry_data.get("migrated_at", "")
            )
            self._entries[entry.id] = entry
            
            # Index by domain
            if entry.domain not in self._domains:
                self._domains[entry.domain] = []
            self._domains[entry.domain].append(entry.id)
        
        self._loaded = True
    
    @property
    def is_loaded(self) -> bool:
        """Check if repository is loaded."""
        return self._loaded
    
    @property
    def entry_count(self) -> int:
        """Get total number of knowledge entries."""
        return len(self._entries)
    
    @property
    def domains(self) -> List[str]:
        """Get list of available domains."""
        return list(self._domains.keys())
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get index metadata."""
        return self._index.get("metadata", {})
    
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """
        Get a specific knowledge entry by ID.
        
        Args:
            entry_id: The knowledge entry ID (e.g., KB-ARC-001)
            
        Returns:
            KnowledgeEntry if found, None otherwise
        """
        return self._entries.get(entry_id)
    
    def get_by_domain(self, domain: str) -> List[KnowledgeEntry]:
        """
        Get all knowledge entries for a domain.
        
        Args:
            domain: Domain name (e.g., ARCHITECTURE, SECURITY)
            
        Returns:
            List of KnowledgeEntry objects for the domain
        """
        entry_ids = self._domains.get(domain.upper(), [])
        return [self._entries[eid] for eid in entry_ids if eid in self._entries]
    
    def query(
        self,
        domains: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> KnowledgeQueryResult:
        """
        Query knowledge entries with optional filters.
        
        Args:
            domains: List of domains to filter by
            tags: List of tags to filter by (any match)
            keywords: List of keywords to search in title/description
            
        Returns:
            KnowledgeQueryResult with matching entries
        """
        results: List[KnowledgeEntry] = []
        
        for entry in self._entries.values():
            # Domain filter
            if domains and entry.domain not in [d.upper() for d in domains]:
                continue
            
            # Tag filter (any match)
            if tags:
                entry_tags_lower = [t.lower() for t in entry.tags]
                if not any(t.lower() in entry_tags_lower for t in tags):
                    continue
            
            # Keyword filter (search title and description)
            if keywords:
                searchable = f"{entry.title} {entry.description}".lower()
                if not any(kw.lower() in searchable for kw in keywords):
                    continue
            
            results.append(entry)
        
        return KnowledgeQueryResult(
            entries=results,
            query_domain=domains[0] if domains and len(domains) == 1 else None,
            query_tags=tags,
            query_keywords=keywords
        )
    
    def get_relevant_knowledge(
        self,
        domains: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        max_entries: int = 10
    ) -> List[KnowledgeEntry]:
        """
        Get the most relevant knowledge entries for a context.
        
        This is the primary method used by MasterOrchestrator when
        composing requests. It returns knowledge sorted by relevance.
        
        Args:
            domains: Preferred domains to prioritize
            keywords: Keywords to match
            max_entries: Maximum entries to return
            
        Returns:
            List of relevant KnowledgeEntry objects
        """
        # Query with filters
        result = self.query(domains=domains, keywords=keywords)
        
        # Sort by relevance (domain match weight + keyword match weight)
        def relevance_score(entry: KnowledgeEntry) -> float:
            score = 0.0
            
            # Domain match
            if domains and entry.domain in [d.upper() for d in domains]:
                score += 1.0
            
            # Keyword match count
            if keywords:
                searchable = f"{entry.title} {entry.description}".lower()
                for kw in keywords:
                    if kw.lower() in searchable:
                        score += 0.5
            
            return score
        
        sorted_entries = sorted(result.entries, key=relevance_score, reverse=True)
        return sorted_entries[:max_entries]
    
    def load_content(self, entry: KnowledgeEntry) -> Dict[str, Any]:
        """
        Load the full YAML content for a knowledge entry.
        
        Uses caching to avoid repeated file reads.
        
        Args:
            entry: The KnowledgeEntry to load content for
            
        Returns:
            Dict containing the YAML content
            
        Raises:
            FileNotFoundError: If YAML file is not found
        """
        if entry.id in self._content_cache:
            return self._content_cache[entry.id]
        
        yaml_path = self._project_root / entry.file_path
        if not yaml_path.exists():
            # Try source file path
            yaml_path = self._project_root / entry.source_file
        
        if not yaml_path.exists():
            raise FileNotFoundError(f"Knowledge YAML not found: {entry.file_path}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f) or {}
        
        self._content_cache[entry.id] = content
        entry.content = content
        return content
    
    def get_security_knowledge(self) -> List[KnowledgeEntry]:
        """Get all security-related knowledge entries."""
        return self.get_by_domain("SECURITY")
    
    def get_architecture_knowledge(self) -> List[KnowledgeEntry]:
        """Get all architecture-related knowledge entries."""
        return self.get_by_domain("ARCHITECTURE")
    
    def get_performance_knowledge(self) -> List[KnowledgeEntry]:
        """Get all performance-related knowledge entries."""
        return self.get_by_domain("PERFORMANCE")
    
    def get_testing_knowledge(self) -> List[KnowledgeEntry]:
        """Get all testing-related knowledge entries."""
        return self.get_by_domain("TESTING-VALIDATION")
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all available knowledge.
        
        Returns:
            Dict with domain counts, total entries, and metadata
        """
        domain_counts = {
            domain: len(ids) for domain, ids in self._domains.items()
        }
        
        return {
            "total_entries": self.entry_count,
            "domains": self.domains,
            "domain_counts": domain_counts,
            "metadata": self.metadata,
            "loaded": self._loaded
        }
    
    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._content_cache.clear()
    
    def reload(self) -> None:
        """Reload the knowledge index from disk."""
        self._entries.clear()
        self._domains.clear()
        self._content_cache.clear()
        self._loaded = False
        self._load_index()


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_repository_instance: Optional[KnowledgeRepository] = None


def get_knowledge_repository(
    project_root: Optional[str] = None,
    force_reload: bool = False
) -> KnowledgeRepository:
    """
    Get the singleton KnowledgeRepository instance.
    
    Args:
        project_root: Path to project root (only used on first call)
        force_reload: Force reload of the repository
        
    Returns:
        KnowledgeRepository singleton instance
    """
    global _repository_instance
    
    if _repository_instance is None or force_reload:
        _repository_instance = KnowledgeRepository(project_root=project_root)
    
    return _repository_instance
