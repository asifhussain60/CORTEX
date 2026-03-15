"""cortex_govern mega-tool.

Phase M5: unify governance operations behind a single MCP tool.
"""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolCategory, ToolParameter, ToolResult


class CortexGovern(ConsolidatedTool):
    @property
    def name(self) -> str:
        return "cortex_govern"

    @property
    def description(self) -> str:
        return "Unified governance operations: audit, health, enforce, vacuum."

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.GOVERNANCE

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="op", type="string", required=False, enum=self.supported_operations, description="Governance operation."),
            ToolParameter(name="operation", type="string", required=False, enum=self.supported_operations, description="Alias of op for compatibility."),
            ToolParameter(name="target", type="string", required=False, description="Target path."),
            ToolParameter(name="context", type="object", required=False, description="Execution context."),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["audit", "health", "enforce", "vacuum"]

    async def execute(self, **params: Any) -> ToolResult:
        operation = str(params.get("op") or params.get("operation") or "").lower().strip()
        if operation not in self.supported_operations:
            return ToolResult(
                success=False,
                error=(
                    f"Unsupported op '{operation or '<empty>'}' for cortex_govern. "
                    f"Allowed: {', '.join(self.supported_operations)}"
                ),
                metadata={"trust_boundary": "deny_by_default", "allowed_ops": self.supported_operations},
            )

        routes: Dict[str, str] = {
            "audit": "AuditCoordinator.audit",
            "health": "HealthOrchestrator.health_check",
            "enforce": "EnforcementOrchestrator.enforce",
            "vacuum": "VacuumOrchestrator.execute",
        }
        return ToolResult(
            success=True,
            data={
                "tool": self.name,
                "op": operation,
                "route": routes[operation],
                "target": params.get("target"),
            },
            metadata={"trust_boundary": "governance-only", "allowed_ops": self.supported_operations},
        )
