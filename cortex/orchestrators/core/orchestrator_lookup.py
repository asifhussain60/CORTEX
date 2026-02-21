"""
Orchestrator Lookup — Registry for orchestrator discovery and routing.

Provides orchestrator registration, keyword-based lookup, and intent routing.

Authority: Phase 53 + Production Readiness Audit
CORE-035: Single canonical implementation
"""

from typing import Any, Dict, List, Optional


class OrchestratorLookup:
    """
    Orchestrator registry lookup service.

    Supports registration with keywords for intent-based routing,
    lookup by ID/name/keyword, and singleton access pattern.
    """

    _instance: Optional['OrchestratorLookup'] = None

    def __init__(self) -> None:
        """Initialize orchestrator lookup."""
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._keyword_map: Dict[str, List[str]] = {}  # keyword -> [orchestrator_ids]

    @classmethod
    def instance(cls: object) -> 'OrchestratorLookup':
        """Get singleton instance.

        Returns:
            OrchestratorLookup singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(
        self,
        orchestrator_id: str,
        metadata: Dict[str, Any],
        keywords: Optional[List[str]] = None,
    ) -> None:
        """
        Register orchestrator with metadata and optional keywords.

        Args:
            orchestrator_id: Unique orchestrator identifier
            metadata: Orchestrator metadata dict
            keywords: Optional list of intent keywords for routing
        """
        self._registry[orchestrator_id] = metadata
        if keywords:
            for keyword in keywords:
                kw_lower = keyword.lower()
                if kw_lower not in self._keyword_map:
                    self._keyword_map[kw_lower] = []
                if orchestrator_id not in self._keyword_map[kw_lower]:
                    self._keyword_map[kw_lower].append(orchestrator_id)

    def get(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """
        Get orchestrator by ID.

        Args:
            orchestrator_id: Orchestrator identifier

        Returns:
            Orchestrator metadata or None
        """
        return self._registry.get(orchestrator_id)

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get orchestrator by name (case-insensitive search).

        Args:
            name: Orchestrator name

        Returns:
            Orchestrator metadata or None
        """
        # Exact match first
        if name in self._registry:
            return self._registry[name]
        # Case-insensitive search
        name_lower = name.lower()
        for oid, metadata in self._registry.items():
            if oid.lower() == name_lower:
                return metadata
            if metadata.get("name", "").lower() == name_lower:
                return metadata
        return None

    def find_by_intent(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Find orchestrator by intent type.

        Args:
            intent: Intent type (e.g., 'IMPLEMENT', 'FIX', 'REFACTOR')

        Returns:
            Orchestrator metadata or None
        """
        intent_lower = intent.lower()
        orchestrator_ids = self._keyword_map.get(intent_lower, [])
        if orchestrator_ids:
            return self._registry.get(orchestrator_ids[0])
        return None

    def find_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Find all orchestrators matching a keyword.

        Args:
            keyword: Keyword to search for

        Returns:
            List of matching orchestrator metadata
        """
        kw_lower = keyword.lower()
        orchestrator_ids = self._keyword_map.get(kw_lower, [])
        return [
            self._registry[oid]
            for oid in orchestrator_ids
            if oid in self._registry
        ]

    def find_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Find orchestrators by domain.

        Args:
            domain: Domain name

        Returns:
            List of orchestrator metadata
        """
        domain_lower = domain.lower()
        return [
            meta for meta in self._registry.values()
            if meta.get("domain", "").lower() == domain_lower
        ]

    def add_keyword_mapping(self, keyword: str, orchestrator_id: str) -> None:
        """
        Add a keyword mapping to an existing orchestrator.

        Args:
            keyword: Intent keyword
            orchestrator_id: Orchestrator identifier to map to
        """
        kw_lower = keyword.lower()
        if kw_lower not in self._keyword_map:
            self._keyword_map[kw_lower] = []
        if orchestrator_id not in self._keyword_map[kw_lower]:
            self._keyword_map[kw_lower].append(orchestrator_id)

    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all registered orchestrators.

        Returns:
            List of all orchestrator metadata
        """
        return list(self._registry.values())

    def list_keywords(self) -> Dict[str, List[str]]:
        """
        List all keyword mappings.

        Returns:
            Dict mapping keywords to orchestrator IDs
        """
        return dict(self._keyword_map)
