"""
AC-ENH-059-006: Planning MCP Tools

MCP tools for remediation planning and audit coordination.

Authority: ENH-059 (P1, 8.5 confidence)
"""

import logging
from typing import Any, Dict

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


# ============================================================================
# MCP TOOL: cortex_audit_remediation_plan
# ============================================================================

@mcp_tool(
    name="cortex_audit_remediation_plan",
    description=(
        "Generate structured remediation plan from audit results. "
        "Presents 4 execution options: [1] Autonomous [2] Interactive [3] Review [4] Cancel. "
        "Part of ENH-059: Audit-Driven Auto-Planning."
    ),
    category="planning"
)
async def cortex_audit_remediation_plan(
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate remediation plan from audit results.

    Args:
        arguments: Dict with:
            - audit_results: Dict with 'findings' key
            - format: "markdown" or "json" (default: markdown)

    Returns:
        Dict with:
            - plan: RemediationPlan (if format=json)
            - formatted: Markdown plan (if format=markdown)
            - success: bool
    """
    try:
        from cortex.orchestrators.planning import AuditRemediationCoordinator

        audit_results = arguments.get("audit_results", {})
        output_format = arguments.get("format", "markdown")

        if not audit_results:
            return {
                "success": False,
                "error": "No audit_results provided"
            }

        # Initialize coordinator
        coordinator = AuditRemediationCoordinator()

        # Generate plan
        plan = coordinator.generate_remediation_plan(audit_results)

        # Format based on requested output
        if output_format == "json":
            return {
                "success": True,
                "plan": {
                    "phases": [
                        {
                            "phase_id": p.phase_id,
                            "name": p.name,
                            "description": p.description,
                            "estimated_minutes": p.estimated_minutes,
                            "risk_level": p.risk_level,
                            "dependencies": p.dependencies,
                            "test_requirements": p.test_requirements,
                            "files_to_modify": p.files_to_modify
                        }
                        for p in plan.phases
                    ],
                    "total_effort_minutes": plan.total_effort_minutes,
                    "overall_risk": plan.overall_risk,
                    "execution_options": plan.execution_options
                }
            }

        else:  # markdown (default)
            formatted = coordinator.format_plan_with_prompt(plan, audit_results)

            return {
                "success": True,
                "formatted": formatted,
                "phase_count": len(plan.phases),
                "total_effort_minutes": plan.total_effort_minutes
            }

    except Exception as e:
        logger.error(f"Error generating remediation plan: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@mcp_tool(
    name="cortex_process_remediation_selection",
    description=(
        "Process user's remediation execution mode selection (1-4). "
        "Returns execution mode and parameters for routing."
    ),
    category="planning"
)
async def cortex_process_remediation_selection(
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process user selection of execution mode.

    Args:
        arguments: Dict with:
            - option: int (1-4)

    Returns:
        Dict with mode and execution parameters
    """
    try:
        from cortex.orchestrators.planning import AuditRemediationCoordinator

        option = arguments.get("option")

        if option is None:
            return {
                "success": False,
                "error": "No option provided"
            }

        coordinator = AuditRemediationCoordinator()
        result = coordinator.process_user_selection(option)

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error(f"Error processing selection: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# TOOL DEFINITIONS (For discovery only - not used in MCP decorator pattern)
# ============================================================================

# Note: These tool definitions are for documentation/discovery purposes.
# The actual MCP tool registration happens via @mcp_tool decorators above.

