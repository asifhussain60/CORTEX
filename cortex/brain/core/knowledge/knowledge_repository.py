# AC-ID: KN-002-01 - Knowledge Repository Integration
# AC-ID: KN-005-01 - Company Knowledge Override Integration
"""
Knowledge Repository for Best Practices YAML Access (KN-002-01).

PHASE-REMEDIATION-06: Master Orchestrator Knowledge Integration
AC-ID: KN-002-01 - Knowledge Repository Access Layer
AC-ID: KN-005-01 - Company Knowledge Override Integration

This module provides the Master Orchestrator with access to the curated
knowledge YAML files containing best practices, security guidelines,
architecture patterns, and domain-specific expertise.

ENHANCED (KN-005-01): Now integrates with CompanyKnowledgeLoader to support
company-specific knowledge overrides with proper precedence:
  1. company/domains/{company}/  - Company-specific overrides (highest)
  2. company/domains/compliance-standards/  - Industry standards (medium)
  3. cortex_brain/tier3/knowledge/  - CORTEX base knowledge (lowest)

Core Responsibilities:
1. Load knowledge index from .knowledge-index.json
2. Provide domain-based knowledge lookup
3. Query knowledge by tags, domain, or keywords
4. Support knowledge evaluation during request composition
5. Cache loaded knowledge for performance
6. (NEW) Integrate company knowledge with precedence override
7. (NEW) Auto-detect applicable compliance standards

Integration Points:
- MasterOrchestrator: Evaluates knowledge during coordinate_operation()
- GovernanceRegistry: Cross-references governance rules with knowledge
- BehavioralBoundaryRules: Validates actions against security knowledge
- CompanyKnowledgeLoader: Provides company/compliance knowledge with precedence

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

import yaml

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

        # NEW (KN-005-01): Get merged knowledge with company overrides
        merged = repo.get_merged_knowledge_with_overrides(
            domain="SECURITY",
            code_content="def process_payment(card_number): ..."
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
        knowledge_dir: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> None:
        """
        Initialize the Knowledge Repository.

        Args:
            project_root: Path to project root (auto-detected if None)
            index_path: Path to .knowledge-index.json (relative to root)
            knowledge_dir: Path to knowledge directory (relative to root)
            company_name: Optional company name for company-specific overrides

        Raises:
            FileNotFoundError: If index file is not found
        """
        self._project_root = self._resolve_project_root(project_root)
        self._index_path = index_path or self.DEFAULT_INDEX_PATH
        self._knowledge_dir = knowledge_dir or self.DEFAULT_KNOWLEDGE_DIR
        self._company_name = company_name

        self._index: Dict[str, Any] = {}
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._domains: Dict[str, List[str]] = {}  # domain -> list of entry IDs
        self._loaded = False
        self._content_cache: Dict[str, Dict[str, Any]] = {}

        # KN-005-01: Initialize company knowledge loader (lazy)
        self._company_loader: Optional['CompanyKnowledgeLoader'] = None

        # Load index on initialization
        self._load_index()

    def _get_company_loader(self) -> 'CompanyKnowledgeLoader':
        """
        Get or initialize the company knowledge loader.

        Returns:
            CompanyKnowledgeLoader instance
        """
        if self._company_loader is None:
            from cortex.brain.core.knowledge.company_knowledge_loader import (
                CompanyKnowledgeLoader,
            )
            self._company_loader = CompanyKnowledgeLoader(
                project_root=str(self._project_root),
                company_name=self._company_name,
            )
        return self._company_loader

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

    # =========================================================================
    # KN-005-01: COMPANY KNOWLEDGE OVERRIDE METHODS
    # =========================================================================

    def set_company(self, company_name: str) -> None:
        """
        Set the active company for knowledge overrides.

        Args:
            company_name: Company name to activate
        """
        self._company_name = company_name
        loader = self._get_company_loader()
        loader.set_company(company_name)

    def get_merged_knowledge_with_overrides(
        self,
        domain: str,
        code_content: Optional[str] = None,
        include_compliance: bool = True,
    ) -> Dict[str, Any]:
        """
        Get merged knowledge with company overrides applied.

        This is the primary method for getting knowledge with proper
        precedence. Company-specific knowledge overrides CORTEX base
        knowledge, and compliance standards are auto-detected from
        code content.

        Precedence Order:
          1. company/domains/{company}/  - Company-specific (highest)
          2. company/domains/compliance-standards/  - Industry standards
          3. cortex_brain/tier3/knowledge/  - CORTEX base (lowest)

        Args:
            domain: Knowledge domain to query (e.g., 'SECURITY', 'API-DESIGN')
            code_content: Optional code to analyze for compliance detection
            include_compliance: Whether to auto-detect and include compliance

        Returns:
            Dict with merged knowledge and metadata:
              - merged_content: The merged knowledge
              - source_layers: Layers that contributed
              - override_count: Number of overrides applied
              - detected_standards: Auto-detected compliance standards (if any)
        """
        loader = self._get_company_loader()

        # Get base knowledge from CORTEX tier3
        base_entries = self.get_by_domain(domain)
        base_knowledge: Dict[str, Any] = {}

        for entry in base_entries:
            try:
                content = self.load_content(entry)
                base_knowledge[entry.id] = content
            except FileNotFoundError:
                pass  # Skip entries with missing files

        # Detect applicable compliance standards from code
        detected_standards: List[str] = []
        if include_compliance and code_content:
            compliance_result = loader.get_applicable_compliance_standards(
                code_content,
                load_full=False,
            )
            detected_standards = [
                s["standard_id"]
                for s in compliance_result.get("detected_standards", [])
            ]

        # Get merged knowledge with company overrides
        merged_result = loader.get_merged_knowledge(
            domain=domain,
            include_compliance=detected_standards if detected_standards else None,
        )

        # Combine base knowledge with merged overrides
        final_merged = base_knowledge.copy()
        for key, value in merged_result.merged_content.items():
            if key in final_merged and isinstance(final_merged[key], dict):
                # Deep merge
                final_merged[key] = {**final_merged[key], **value}
            else:
                final_merged[key] = value

        return {
            "merged_content": final_merged,
            "source_layers": merged_result.source_layers + ["cortex-base"],
            "override_count": merged_result.override_count,
            "detected_standards": detected_standards,
            "base_entry_count": len(base_entries),
            "domain": domain,
            "company": self._company_name,
        }

    def get_compliance_standards_for_code(
        self,
        code_content: str,
    ) -> Dict[str, Any]:
        """
        Get applicable compliance standards for code content.

        Analyzes code to detect which compliance standards apply,
        then loads the full standard details.

        Args:
            code_content: Code content to analyze

        Returns:
            Dict with detected standards and their content
        """
        loader = self._get_company_loader()
        return loader.get_applicable_compliance_standards(
            code_content,
            load_full=True,
        )

    def load_compliance_standard(
        self,
        standard_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Load a specific compliance standard by ID.

        Args:
            standard_id: The compliance standard ID (e.g., 'pci-dss', 'hipaa')

        Returns:
            Dict containing the compliance standard, or None if not found
        """
        loader = self._get_company_loader()
        return loader.load_compliance_standard(standard_id)

    def get_company_knowledge(
        self,
        domain: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get company-specific knowledge for a domain.

        Args:
            domain: Knowledge domain (e.g., 'compliance', 'policies')

        Returns:
            Dict with company knowledge, or None if no company set
        """
        if not self._company_name:
            return None

        loader = self._get_company_loader()
        return loader.load_company_knowledge(domain)


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_repository_instance: Optional[KnowledgeRepository] = None


def get_knowledge_repository(
    project_root: Optional[str] = None,
    company_name: Optional[str] = None,
    force_reload: bool = False,
) -> KnowledgeRepository:
    """
    Get the singleton KnowledgeRepository instance.

    Args:
        project_root: Path to project root (only used on first call)
        company_name: Optional company name for overrides
        force_reload: Force reload of the repository

    Returns:
        KnowledgeRepository singleton instance
    """
    global _repository_instance

    if _repository_instance is None or force_reload:
        _repository_instance = KnowledgeRepository(
            project_root=project_root,
            company_name=company_name,
        )
    elif company_name and company_name != _repository_instance._company_name:
        _repository_instance.set_company(company_name)

    return _repository_instance
