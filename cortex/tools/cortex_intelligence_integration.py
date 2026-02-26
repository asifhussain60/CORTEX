"""cortex_intelligence_integration.py — Intelligence Integration.

Delegates to UnifiedIntelligenceProvider for real intelligence queries (Phase 84-c, GAP-84-10).
Imported by cortex/orchestrators/core/business_wisdom_formatter.py.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CortexIntelligenceIntegration:
    """
    Bridges the tool layer with the intelligence provider by delegating to
    UnifiedIntelligenceProvider (GAP-84-10).

    Replaces the hollow stub that returned empty responses.
    Uses lazy import to avoid circular dependencies.
    """

    def query(self, domain: str, prompt: str) -> Dict[str, Any]:
        """
        Query the intelligence layer by delegating to UnifiedIntelligenceProvider.

        Args:
            domain: Intelligence domain to query (e.g. 'security', 'architecture').
            prompt: Query prompt string.

        Returns:
            Intelligence response dictionary with domain, response, and status.
        """
        try:
            from cortex.intelligence.provider import UnifiedIntelligenceProvider

            provider = UnifiedIntelligenceProvider()
            result = provider.query(domain=domain, prompt=prompt)
            if isinstance(result, dict):
                return {"domain": domain, **result, "status": "ok"}
            return {"domain": domain, "response": str(result), "status": "ok"}
        except Exception as exc:
            logger.warning("CortexIntelligenceIntegration delegation failed: %s", exc)
            return {"domain": domain, "response": "", "status": "degraded", "error": str(exc)}