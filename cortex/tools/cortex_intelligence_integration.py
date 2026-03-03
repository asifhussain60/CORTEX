"""cortex_intelligence_integration.py — Intelligence Integration.

Delegates to IntelligenceFacade for all intelligence queries (Phase 109-D, GAP-109-14).
Imported by cortex/orchestrators/core/business_wisdom_formatter.py.

Phase 84-c (GAP-84-10): Original implementation.
Phase 109-D (GAP-109-14): Migrated from UnifiedIntelligenceProvider to IntelligenceFacade
  — single canonical entry point per CORE-035.

Authority: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CortexIntelligenceIntegration:
    """
    Bridges the tool layer with the intelligence layer via IntelligenceFacade (GAP-109-14).

    Routes all queries through the single canonical IntelligenceFacade entry point
    instead of calling UnifiedIntelligenceProvider directly. This ensures CORE-035
    compliance and gives IntelligenceFacade visibility into all tool-layer intelligence
    calls.

    Uses lazy import to avoid circular dependencies.
    """

    def query(self, domain: str, prompt: str) -> Dict[str, Any]:
        """
        Query the intelligence layer by delegating to IntelligenceFacade.

        Args:
            domain: Intelligence domain to query (e.g. 'security', 'architecture').
            prompt: Query prompt string.

        Returns:
            Intelligence response dictionary with domain, response, and status.
        """
        try:
            from cortex.intelligence.facade import IntelligenceFacade

            facade = IntelligenceFacade()
            result = facade.query(query=prompt, domain=domain)
            if isinstance(result, dict):
                return {"domain": domain, **result, "status": "ok"}
            return {"domain": domain, "response": str(result), "status": "ok"}
        except Exception as exc:
            logger.warning("CortexIntelligenceIntegration delegation failed: %s", exc)
            return {"domain": domain, "response": "", "status": "degraded", "error": str(exc)}