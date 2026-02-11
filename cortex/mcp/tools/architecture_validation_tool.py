"""
Architecture Validation MCP Tool - Phase 24 Layer 1
MCP-exposed interface for ArchitectureGuard orchestrator
"""

import logging
from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool
from cortex.orchestrators.core.architecture_guard import (
    ArchitectureGuard,
    GateVerdict,
)

logger = logging.getLogger(__name__)

# Module-level orchestrator instance
_architecture_guard: Optional[ArchitectureGuard] = None


def _get_guard() -> ArchitectureGuard:
    """Get or initialize ArchitectureGuard singleton."""
    global _architecture_guard
    if _architecture_guard is None:
        _architecture_guard = ArchitectureGuard()
        init_result = _architecture_guard.initialize()
        if init_result.is_err():
            raise RuntimeError(f"ArchitectureGuard initialization failed: {init_result.error}")
    return _architecture_guard


@mcp_tool(
    name="cortex_validate_architecture",
    description="Validate user request against master plan to prevent regression",
    parameters={
        "request_description": {
            "type": "string",
            "description": "Description of requested change",
            "required": True
        },
        "intent_type": {
            "type": "string",
            "description": "Type of change intent",
            "required": True,
            "enum": ["IMPLEMENT", "REFACTOR", "FIX", "DESIGN"]
        },
        "scope": {
            "type": "array",
            "description": "Affected files/orchestrators",
            "required": False,
            "items": {"type": "string"}
        }
    }
)
def cortex_validate_architecture(
    request_description: str,
    intent_type: str,
    scope: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Validate user request against master plan.

    Prevents:
    - Architectural regression
    - Master plan drift
    - Untracked significant changes
    - Contradictions with completed phases

    Returns verdictUnion[PROCEED, CREATE_PHASE] | BLOCK

    Args:
        request_description: Description of requested change
        intent_type: IMPLEMENT, REFACTOR, FIX, or DESIGN
        scope: Optional list of affected files

    Returns:
        Dict with status, verdict, reasoning, and phase_alignment
    """
    try:
        guard = _get_guard()

        # Validate request
        validation_result = guard.validate_request(
            request_description=request_description,
            intent_type=intent_type,
            scope=scope or []
        )

        if validation_result.is_err():
            return {
                "status": "error",
                "error": f"Validation failed: {validation_result.error}"
            }

        validation = validation_result.unwrap()

        # Format result based on verdict
        if validation.verdict == GateVerdict.PROCEED:
            return {
                "status": "success",
                "verdict": "PROCEED",
                "reasoning": validation.reasoning,
                "phase_alignment": {
                    "active_phases": validation.phase_alignment.active_phases,
                    "conflicts": validation.phase_alignment.conflicts,
                    "regression_risk": validation.phase_alignment.regression_risk,
                    "brittleness_risk": validation.phase_alignment.brittleness_risk
                },
                "message": f"✅ Request approved: {validation.reasoning}"
            }

        elif validation.verdict == GateVerdict.CREATE_PHASE:
            suggested_phase = {}
            if validation.suggested_phase:
                suggested_phase = {
                    "id": validation.suggested_phase.id,
                    "title": validation.suggested_phase.title,
                    "priority": validation.suggested_phase.priority,
                    "estimated_effort": validation.suggested_phase.estimated_effort,
                    "scope": validation.suggested_phase.scope
                }

            return {
                "status": "success",
                "verdict": "CREATE_PHASE",
                "reasoning": validation.reasoning,
                "suggested_phase": suggested_phase,
                "phase_alignment": {
                    "active_phases": validation.phase_alignment.active_phases,
                    "regression_risk": validation.phase_alignment.regression_risk
                },
                "message": f"📋 Phase creation recommended: {validation.reasoning}"
            }

        else:  # BLOCK
            return {
                "status": "blocked",
                "verdict": "BLOCK",
                "reasoning": validation.reasoning,
                "phase_alignment": {
                    "active_phases": validation.phase_alignment.active_phases,
                    "conflicts": validation.phase_alignment.conflicts,
                    "regression_risk": validation.phase_alignment.regression_risk
                },
                "error": f"❌ Request blocked: {validation.reasoning}"
            }

    except Exception as e:
        logger.error(f"Architecture validation tool error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Tool execution failed: {str(e)}"
        }


# Module exports
__all__ = ["cortex_validate_architecture"]

