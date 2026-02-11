"""
Domain Brain Connector - Knowledge repository integration

AC-PHASE-41: Master Orchestrator Decomposition
- Queries domain knowledge base
- Retrieves synthesis rules
- Caches frequently accessed patterns
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DomainBrainResult:
    """Result from domain brain query."""
    domain: str
    patterns: List[str]
    rules: Dict[str, Any]
    confidence: float
    cache_hit: bool


class DomainBrainConnector:
    """
    Queries Domain Brain for context and synthesis rules.

    Responsibilities:
    - Query domain knowledge base
    - Retrieve synthesis rules for intent
    - Cache frequently accessed patterns
    - Handle Knowledge Brain integration

    Example:
        connector = DomainBrainConnector(domain_brain=knowledge_brain)
        result = connector.query_synthesis_rules(
            domain="architecture",
            intent="IMPLEMENT"
        )
    """

    def __init__(self, domain_brain: Optional[Any] = None) -> None:
        """
        Initialize Domain Brain connector.

        Args:
            domain_brain: Reference to domain knowledge base
        """
        self.domain_brain = domain_brain
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, DomainBrainResult] = {}

    def query_synthesis_rules(
        self,
        domain: str,
        intent: str,
        context: Dict[str, Any]
    ) -> DomainBrainResult:
        """
        Query synthesis rules for given domain + intent.

        Args:
            domain: Domain name (architecture, security, performance)
            intent: Intent type (IMPLEMENT, FIX, REFACTOR)
            context: Operation context

        Returns:
            Domain brain result with patterns and rules
        """
        cache_key = f"{domain}:{intent}"

        # Check cache first
        if cache_key in self._cache:
            self.logger.debug(f"Cache hit: {cache_key}")
            return self._cache[cache_key]

        # Query domain brain
        if not self.domain_brain:
            return DomainBrainResult(
                domain=domain,
                patterns=[],
                rules={},
                confidence=0.0,
                cache_hit=False
            )

        try:
            # Query patterns for domain + intent
            patterns = self.domain_brain.get_patterns(domain, intent)
            rules = self.domain_brain.get_synthesis_rules(domain)

            result = DomainBrainResult(
                domain=domain,
                patterns=patterns or [],
                rules=rules or {},
                confidence=0.85,  # Reasonable default confidence
                cache_hit=False
            )

            # Cache result
            self._cache[cache_key] = result
            return result

        except Exception as e:
            self.logger.error(f"Error querying domain brain: {str(e)}")
            return DomainBrainResult(
                domain=domain,
                patterns=[],
                rules={},
                confidence=0.0,
                cache_hit=False
            )

    def clear_cache(self) -> None:
        """Clear cached patterns."""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_queries": len(self._cache),
            "total_size_bytes": sum(
                len(str(v)) for v in self._cache.values()
            )
        }
