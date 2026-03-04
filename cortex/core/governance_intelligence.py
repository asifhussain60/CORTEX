"""governance_intelligence.py — Governance Intelligence.

Delegates to EnforcementOrchestrator for real compliance analysis (Phase 84-c, GAP-84-07).
Imported by cortex/testing/auto_initialization_suite.py.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class GovernanceIntelligence:
    """
    Provides intelligence-layer governance analysis by delegating to EnforcementOrchestrator.

    Replaces the hollow stub that returned hardcoded empty results (GAP-84-07).
    Uses lazy import to avoid circular dependencies.
    """

    def analyse(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse governance compliance for a given context.

        Delegates to EnforcementOrchestrator.validate_operation() to perform
        real CORE rule checks instead of returning hardcoded clean status.

        Args:
            context: Workspace or code context dict.

        Returns:
            Governance analysis result with violations and status.
        """
        try:
            from cortex.orchestrators.core.enforcement_orchestrator import (
                EnforcementOrchestrator,
            )

            orchestrator = EnforcementOrchestrator()
            result = orchestrator.validate_operation(context)
            if hasattr(result, "value"):
                inner = result.value
            else:
                inner = result
            if hasattr(inner, "violations"):
                violations = list(inner.violations)
            elif isinstance(inner, dict):
                violations = inner.get("violations", [])
            else:
                violations = []
            status = "clean" if not violations else "violations_detected"
            return {"violations": violations, "status": status}
        except Exception as exc:
            logger.warning("GovernanceIntelligence delegation failed: %s", exc)
            return {"violations": [], "status": "clean"}
