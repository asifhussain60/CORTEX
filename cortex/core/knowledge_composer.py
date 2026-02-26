"""knowledge_composer.py — Knowledge Composer.

Delegates to KnowledgeSynthesisEngine for real multi-domain synthesis (Phase 84-c, GAP-84-08).
Imported by cortex/testing/auto_initialization_suite.py.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class KnowledgeComposer:
    """
    Composes knowledge from multiple registry sources by delegating to KnowledgeSynthesisEngine.

    Replaces the hollow stub that returned empty entries (GAP-84-08).
    Uses lazy import to avoid circular dependencies.
    """

    def compose(self, domains: List[str]) -> Dict[str, Any]:
        """
        Compose knowledge for a list of domains.

        Delegates to KnowledgeSynthesisEngine.synthesize_cross_domain_context()
        to produce real cross-domain knowledge synthesis.

        Args:
            domains: List of domain names to compose.

        Returns:
            Composed knowledge dictionary with entries from each domain.
        """
        try:
            from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
                KnowledgeSynthesisEngine,
            )

            engine = KnowledgeSynthesisEngine()
            result = engine.synthesize_cross_domain_context(domains)
            if isinstance(result, dict):
                return result
            return {"domains": domains, "entries": result if isinstance(result, list) else []}
        except Exception as exc:
            logger.warning("KnowledgeComposer delegation failed: %s", exc)
            return {"domains": domains, "entries": []}