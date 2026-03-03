"""
ExtendedGovernanceAgent — CORE-058 through CORE-063 enforcement.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rules: CORE-058, CORE-059, CORE-060, CORE-061, CORE-062, CORE-063.

Authority: governance_alignment_phase_2.py + cortex-refactor-master.yaml GAP-008

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-009
"""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class ExtendedGovernanceAgent:
    """
    Enforces the 6 extended CORE governance rules (CORE-058 through CORE-063).

    Rules:
    - CORE-058 (Tier 0): SQLite WAL mode mandatory for all audit databases
    - CORE-059 (Tier 1): MCP footprint auditing — every tool invocation must be logged
    - CORE-060 (Tier 1): SDLC brain governance — decisions must flow through SDLC Brain
    - CORE-061 (Tier 1): Business expressibility — business-critical ops must have clear intent
    - CORE-062 (Tier 0): Plan-first execution — IMPLEMENT/FIX/REFACTOR require approved plan
    - CORE-063 (Tier 0): Challenge-first gate — SYSTEM-scope ops require challenge issuance

    Authority: governance_alignment_phase_2.py + cortex-refactor-master.yaml GAP-008
    """

    # Operation types that require an approved plan document (CORE-062)
    PLAN_REQUIRED_OPS = {"IMPLEMENT", "FIX", "REFACTOR", "DEPLOY", "DELETE"}

    def __init__(self) -> None:
        """Initialize ExtendedGovernanceAgent with rule list."""
        self.rules = [
            "CORE-058",
            "CORE-059",
            "CORE-060",
            "CORE-061",
            "CORE-062",
            "CORE-063",
        ]

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate context against CORE-058 through CORE-063.

        Args:
            context: Operation context. Recognised keys:
                - sqlite_db_paths (List[str]): Paths to SQLite DBs being opened/created
                - wal_mode_enabled (bool): Whether WAL mode is active (CORE-058)
                - mcp_tool_invoked (str): Name of MCP tool being called (CORE-059)
                - mcp_logging_enabled (bool): Whether invocation logging is active (CORE-059)
                - sdlc_action (str): SDLC lifecycle action being taken (CORE-060)
                - sdlc_approved (bool): Whether SDLC Brain approved the action (CORE-060)
                - operation_type (str): e.g. "IMPLEMENT", "FIX", "READ" (CORE-062)
                - plan_document (str): Path to approved plan YAML (CORE-062)
                - operation_scope (str): e.g. "SYSTEM", "MODULE", "FILE" (CORE-063)
                - challenge_issued (bool): Whether holistic challenge was issued (CORE-063)

        Returns:
            EnforcementResult — BLOCKED for Tier-0 violations, WARNING for Tier-1, PASS otherwise
        """
        violations: List[str] = []
        warnings: List[str] = []

        # ── CORE-058: SQLite WAL Mode Mandatory ────────────────────────────
        sqlite_db_paths = context.get("sqlite_db_paths", [])
        if sqlite_db_paths:
            wal_enabled = context.get("wal_mode_enabled", True)
            if not wal_enabled:
                violations.append(
                    "CORE-058 VIOLATION: SQLite WAL mode is DISABLED. "
                    "All audit databases MUST use WAL (Write-Ahead Logging) mode "
                    "for concurrent-safe writes. Set PRAGMA journal_mode=WAL on open."
                )

        # ── CORE-059: MCP Footprint Auditing ───────────────────────────────
        mcp_tool = context.get("mcp_tool_invoked")
        if mcp_tool:
            mcp_logging = context.get("mcp_logging_enabled", True)
            if not mcp_logging:
                warnings.append(
                    f"CORE-059 WARNING: MCP tool '{mcp_tool}' invoked without logging enabled. "
                    "Every MCP tool invocation MUST be logged with: timestamp, tool_id, "
                    "input_params, execution_duration, output_status."
                )

        # ── CORE-060: SDLC Brain Governance ────────────────────────────────
        sdlc_action = context.get("sdlc_action")
        if sdlc_action:
            sdlc_approved = context.get("sdlc_approved", False)
            if not sdlc_approved:
                warnings.append(
                    f"CORE-060 WARNING: SDLC action '{sdlc_action}' taken without SDLC Brain "
                    "approval. All SDLC decisions MUST flow through SDLC Brain for compliance "
                    "verification. No direct execution without approval."
                )

        # ── CORE-061: Business Expressibility (advisory) ──────────────────
        # Tier-1 recommended; no hard block enforced at this layer

        # ── CORE-062: Plan-First Execution ─────────────────────────────────
        operation_type = context.get("operation_type", "").upper()
        if operation_type in self.PLAN_REQUIRED_OPS:
            plan_doc = context.get("plan_document")
            if not plan_doc:
                violations.append(
                    f"CORE-062 VIOLATION: Operation type '{operation_type}' requires an approved "
                    "plan document. Specify 'plan_document' key with path to the approved plan "
                    "YAML (e.g. cortex-registry/planning/cortex-refactor-master.yaml). "
                    "Ad-hoc execution is BLOCKED."
                )

        # ── CORE-063: Challenge-First Governance Gate ───────────────────────
        operation_scope = context.get("operation_scope", "").upper()
        if operation_scope == "SYSTEM":
            challenge = context.get("challenge_issued", False)
            if not challenge:
                violations.append(
                    "CORE-063 VIOLATION: SYSTEM-scope operation requires a holistic challenge "
                    "before execution. Set 'challenge_issued': True after issuing challenge. "
                    "Challenge forces reconsideration: optimal approach? risks? alternatives?"
                )

        if violations:
            level = EnforcementLevel.BLOCKED
        elif warnings:
            level = EnforcementLevel.WARNING
        else:
            level = EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "ExtendedGovernanceAgent",
                "rules_checked": self.rules,
                "sqlite_db_paths": sqlite_db_paths,
                "mcp_tool_invoked": mcp_tool,
                "operation_type": operation_type or None,
                "operation_scope": operation_scope or None,
            },
        )
