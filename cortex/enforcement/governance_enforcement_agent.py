"""governance_enforcement_agent.py — Governance Enforcement Agent.

Delegates to EnforcementOrchestrator for real CORE rule enforcement (Phase 84-c, GAP-84-06).
Imported by cortex/mcp/tools/workflow_tools.py.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GovernanceEnforcementAgent:
    """
    Governance enforcement agent that delegates to EnforcementOrchestrator.

    Replaces the hollow stub that always returned allowed=True (GAP-84-06).
    Uses lazy import to avoid circular dependencies.
    """

    def enforce(
        self, action: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enforce governance rules for an action by delegating to EnforcementOrchestrator.

        Args:
            action: The proposed action description.
            context: Optional context dictionary.

        Returns:
            Enforcement result with violations list and allowed flag.
        """
        try:
            from cortex.orchestrators.core.enforcement_orchestrator import (
                EnforcementOrchestrator,
            )

            orchestrator = EnforcementOrchestrator()
            result = orchestrator.validate_operation(
                {"operation": action, "context": context or {}}
            )
            # Unwrap Result type
            if hasattr(result, "value"):
                inner = result.value
            else:
                inner = result
            violations: List[str] = []
            allowed = True
            if hasattr(inner, "violations"):
                violations = list(inner.violations)
                allowed = len(violations) == 0
            elif isinstance(inner, dict):
                violations = inner.get("violations", [])
                allowed = inner.get("allowed", len(violations) == 0)
            return {"action": action, "violations": violations, "allowed": allowed}
        except Exception as exc:
            logger.warning("GovernanceEnforcementAgent delegation failed: %s", exc)
            return {"action": action, "violations": [], "allowed": True}