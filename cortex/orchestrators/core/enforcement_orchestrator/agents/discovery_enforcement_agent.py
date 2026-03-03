"""
DiscoveryEnforcementAgent — Pre-execution discovery enforcement.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rules: CORE-030, CORE-035 (ENH-047 Pre-Execution Discovery Protocol).

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-008
"""

from __future__ import annotations

from typing import Any, Dict

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class DiscoveryEnforcementAgent:
    """
    Enforces pre-execution discovery to prevent duplicate implementations.

    Rules:
    - CORE-030: Implementation Truth (verify existing implementations)
    - CORE-035: Single canonical implementation (no duplicates)

    Authority: ENH-047 Pre-Execution Discovery Protocol
    """

    def __init__(self) -> None:
        """Initialize discovery enforcement agent."""
        self.name = "DiscoveryEnforcementAgent"
        self.rules = ["CORE-030", "CORE-035"]

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation using pre-execution discovery.

        Args:
            operation: Operation context with intent, feature_name, scope, etc.

        Returns:
            EnforcementResult with violations if discovery blocks execution
        """
        violations = []
        warnings = []

        intent = operation.get("intent", "UNKNOWN")

        if intent not in ["IMPLEMENT", "DESIGN", "REFACTOR"]:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                metadata={
                    "agent": "DiscoveryEnforcementAgent",
                    "skipped": f"Intent {intent} does not require discovery",
                },
            )

        discovery_result = operation.get("discovery_result")

        if not discovery_result:
            violations.append(
                "CORE-030 VIOLATION: Pre-execution discovery not performed. "
                "Run cortex_discover before IMPLEMENT/DESIGN/REFACTOR operations."
            )

            return EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=violations,
                metadata={
                    "agent": "DiscoveryEnforcementAgent",
                    "rules_checked": ["CORE-030", "CORE-035"],
                    "authority": "ENH-047",
                },
            )

        recommendation = discovery_result.get("recommendation")
        duplicates = discovery_result.get("duplicates", [])
        existing_features = discovery_result.get("existing_features", [])

        if duplicates and len(duplicates) > 0:
            violations.append(
                f"CORE-035 VIOLATION: {len(duplicates)} duplicate implementation(s) detected. "
                f"Consolidate existing implementations first: {[d['file_path'] for d in duplicates[:3]]}"
            )

        if existing_features and len(existing_features) > 0:
            extend_mode = operation.get("extend_mode", False)

            if not extend_mode and recommendation == "EXTEND":
                warnings.append(
                    f"CORE-030 WARNING: {len(existing_features)} similar implementation(s) found. "
                    f"Consider extending: {[f['file_path'] for f in existing_features[:3]]}. "
                    "Add --extend flag if intentionally creating new implementation."
                )

        level = EnforcementLevel.BLOCKED if violations else (
            EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS
        )

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "DiscoveryEnforcementAgent",
                "rules_checked": ["CORE-030", "CORE-035"],
                "discovery_summary": {
                    "recommendation": recommendation,
                    "duplicates_found": len(duplicates),
                    "existing_features_found": len(existing_features),
                },
                "authority": "ENH-047",
            },
        )
