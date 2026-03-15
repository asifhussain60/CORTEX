"""cortex_ops mega-tool."""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolCategory, ToolParameter, ToolResult


class CortexOps(ConsolidatedTool):
    @property
    def name(self) -> str:
        return "cortex_ops"

    @property
    def description(self) -> str:
        return "Unified operations: sync, upgrade, setup, status."

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="op", type="string", required=False, enum=self.supported_operations, description="Ops operation."),
            ToolParameter(name="operation", type="string", required=False, enum=self.supported_operations, description="Alias of op for compatibility."),
            ToolParameter(name="target", type="string", required=False, description="Target path or service."),
            ToolParameter(name="options", type="object", required=False, description="Operation options."),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["sync", "upgrade", "setup", "status"]

    async def execute(self, **params: Any) -> ToolResult:
        operation = str(params.get("op") or params.get("operation") or "").lower().strip()
        if operation not in self.supported_operations:
            return ToolResult(
                success=False,
                error=(
                    f"Unsupported op '{operation or '<empty>'}' for cortex_ops. "
                    f"Allowed: {', '.join(self.supported_operations)}"
                ),
                metadata={"trust_boundary": "deny_by_default", "allowed_ops": self.supported_operations},
            )

        routes: Dict[str, str] = {
            "sync": "GitOrchestrator.sync",
            "upgrade": "UpgradeOrchestrator.upgrade",
            "setup": "SetupOrchestrator.setup",
            "status": "OperationsOrchestrator.status",
        }
        return ToolResult(
            success=True,
            data={"tool": self.name, "op": operation, "route": routes[operation], "target": params.get("target")},
            metadata={"trust_boundary": "ops-only", "allowed_ops": self.supported_operations},
        )
