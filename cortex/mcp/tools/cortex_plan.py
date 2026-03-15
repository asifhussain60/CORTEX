"""cortex_plan mega-tool."""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolCategory, ToolParameter, ToolResult


class CortexPlanMega(ConsolidatedTool):
    @property
    def name(self) -> str:
        return "cortex_plan"

    @property
    def description(self) -> str:
        return "Unified planning operations: plan, phase, track, decompose, totalrecall."

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="op", type="string", required=False, enum=self.supported_operations, description="Planning operation."),
            ToolParameter(name="operation", type="string", required=False, enum=self.supported_operations, description="Alias of op for compatibility."),
            ToolParameter(name="phase_id", type="string", required=False, description="Phase identifier."),
            ToolParameter(name="target", type="string", required=False, description="Target file or path."),
            ToolParameter(name="options", type="object", required=False, description="Operation options."),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["plan", "phase", "track", "decompose", "totalrecall"]

    async def execute(self, **params: Any) -> ToolResult:
        operation = str(params.get("op") or params.get("operation") or "").lower().strip()
        if operation not in self.supported_operations:
            return ToolResult(
                success=False,
                error=(
                    f"Unsupported op '{operation or '<empty>'}' for cortex_plan. "
                    f"Allowed: {', '.join(self.supported_operations)}"
                ),
                metadata={"trust_boundary": "deny_by_default", "allowed_ops": self.supported_operations},
            )

        routes: Dict[str, str] = {
            "plan": "PlanningOrchestrator.plan",
            "phase": "PlanningOrchestrator.phase",
            "track": "PlanningOrchestrator.track",
            "decompose": "PlanningOrchestrator.decompose",
            "totalrecall": "MasterOrchestrator.totalrecall",
        }
        return ToolResult(
            success=True,
            data={
                "tool": self.name,
                "op": operation,
                "route": routes[operation],
                "phase_id": params.get("phase_id"),
                "target": params.get("target"),
            },
            metadata={"trust_boundary": "planning-only", "allowed_ops": self.supported_operations},
        )
