"""
MCP Tool: cortex_master_plan — CortexMasterPlanOrchestrator exposure

Exposes CortexMasterPlanOrchestrator via the CORTEX MCP server.

Operations:
  - create: Create a new sequential CORTEX phase entry
  - sync: Sync _cortex-master/phases/ folders to match registry status
  - next_sequence: Return the next sequential phase number
  - load_template: Load a workflow template by name

Authority: Phase 50 — CortexMasterPlanOrchestrator
CORE Rules: CORE-008, CORE-011, CORE-012, CORE-028, CORE-035
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.orchestrators.core.master_plan_orchestrator import (
    CortexMasterPlanOrchestrator,
    PhaseCreationRequest,
    PhaseLifecycleError,
)

logger = logging.getLogger(__name__)

# Singleton orchestrator instance (initialised on first call)
_orchestrator: CortexMasterPlanOrchestrator | None = None


def _get_orchestrator() -> CortexMasterPlanOrchestrator:
    """Return the singleton CortexMasterPlanOrchestrator, initialising on first call.

    Returns:
        Configured orchestrator pointed at the CORTEX workspace root.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CortexMasterPlanOrchestrator()
    return _orchestrator


def cortex_master_plan(operation: str, **kwargs: Any) -> Dict[str, Any]:
    """Entry point for the cortex_master_plan MCP tool.

    Args:
        operation: One of 'create', 'sync', 'next_sequence', 'load_template'.
        **kwargs: Operation-specific parameters (see below).

    Operations:
        create:
            title (str): Phase title (required).
            description (str): Phase scope description (required).
            priority (str): P0/P1/P2/P3 (required).
            supersedes (list[str]): Prior phase IDs replaced (optional).

        sync:
            No additional parameters.

        next_sequence:
            No additional parameters.

        load_template:
            template_name (str): Template name without .yaml extension (required).

    Returns:
        Dict with 'success' bool, 'operation', and operation-specific data.

    Raises:
        PhaseLifecycleError: On any orchestrator lifecycle failure.
        ValueError: On invalid operation or missing required parameters.
    """
    orch = _get_orchestrator()
    logger.info("cortex_master_plan: operation=%s kwargs=%s", operation, list(kwargs.keys()))

    if operation == "create":
        _require(kwargs, "title", "description", "priority")
        request = PhaseCreationRequest(
            title=kwargs["title"],
            description=kwargs["description"],
            priority=kwargs["priority"],
            supersedes=kwargs.get("supersedes", []),
            governance_rules=kwargs.get("governance_rules", []),
        )
        record = orch.create_phase(request)
        return {
            "success": True,
            "operation": "create",
            "phase_id": record.phase_id,
            "sequence": record.sequence,
            "file_path": str(record.file_path),
            "title": record.title,
        }

    if operation == "sync":
        result = orch.sync_phase_folders()
        return {
            "success": True,
            "operation": "sync",
            "moved_to_completed": result.moved_to_completed,
            "moved_to_deferred": result.moved_to_deferred,
            "anomalies": result.anomalies,
        }

    if operation == "next_sequence":
        seq = orch.next_sequence_number()
        return {
            "success": True,
            "operation": "next_sequence",
            "next_sequence": seq,
            "next_phase_id": CortexMasterPlanOrchestrator._phase_id_from_sequence(seq),
        }

    if operation == "load_template":
        _require(kwargs, "template_name")
        template = orch.load_workflow_template(kwargs["template_name"])
        return {
            "success": True,
            "operation": "load_template",
            "template_name": kwargs["template_name"],
            "workflow_name": template["workflow"].get("name"),
            "stage_count": len(template["workflow"].get("stages", [])),
        }

    raise ValueError(
        f"Unknown operation '{operation}'. "
        "Valid operations: create, sync, next_sequence, load_template"
    )


def _require(kwargs: Dict[str, Any], *keys: str) -> None:
    """Assert that all required keys are present in kwargs.

    Args:
        kwargs: Keyword arguments dict to check.
        *keys: Required key names.

    Raises:
        ValueError: If any required key is missing.
    """
    missing = [k for k in keys if k not in kwargs or kwargs[k] is None]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")


# ---------------------------------------------------------------------------
# ConsolidatedTool wrapper — enables MCP ALL_TOOLS registration (Phase 50)
# ---------------------------------------------------------------------------


class CortexMasterPlanTool(ConsolidatedTool):
    """MCP ConsolidatedTool wrapper for cortex_master_plan function.

    Exposes CortexMasterPlanOrchestrator phase-lifecycle operations via the
    standard ConsolidatedTool interface so it can be registered in ALL_TOOLS.

    Operations: create | sync | next_sequence | load_template

    Authority: Phase 50 | CORE-035 | CORE-011 | CORE-012
    """

    @property
    def name(self) -> str:
        """Return canonical MCP tool name."""
        return "cortex_master_plan"

    @property
    def description(self) -> str:
        """Return tool description for MCP discovery."""
        return (
            "Manage CORTEX phase lifecycle via CortexMasterPlanOrchestrator. "
            "Operations: create (new sequential phase), sync (folder status), "
            "next_sequence (compute next phase number), load_template (workflow YAML). "
            "Authority: cortex-master.yaml is SSOT for all phase status."
        )

    @property
    def category(self) -> ToolCategory:
        """Return tool category."""
        return ToolCategory.OPERATIONS

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return parameter schema for MCP introspection."""
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Operation: create | sync | next_sequence | load_template",
                required=True,
                enum=["create", "sync", "next_sequence", "load_template"],
            ),
            ToolParameter(
                name="title",
                type="string",
                description="[create] Phase title (non-empty string)",
                required=False,
            ),
            ToolParameter(
                name="description",
                type="string",
                description="[create] Phase scope description",
                required=False,
            ),
            ToolParameter(
                name="priority",
                type="string",
                description="[create] CORTEX priority: P0 | P1 | P2 | P3",
                required=False,
                enum=["P0", "P1", "P2", "P3"],
            ),
            ToolParameter(
                name="supersedes",
                type="array",
                description="[create] Prior phase IDs this phase replaces",
                required=False,
            ),
            ToolParameter(
                name="template_name",
                type="string",
                description="[load_template] Template filename without .yaml extension",
                required=False,
            ),
        ]

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the cortex_master_plan operation.

        Args:
            params: Dict containing 'operation' plus operation-specific keys.

        Returns:
            ToolResult with success/failure and operation data.
        """
        try:
            operation = params.get("operation")
            if not operation:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: operation",
                )
            kwargs = {k: v for k, v in params.items() if k != "operation"}
            result = cortex_master_plan(operation, **kwargs)
            return ToolResult(success=True, data=result)
        except (ValueError, PhaseLifecycleError) as exc:
            logger.warning("CortexMasterPlanTool error: %s", exc)
            return ToolResult(success=False, error=str(exc))
