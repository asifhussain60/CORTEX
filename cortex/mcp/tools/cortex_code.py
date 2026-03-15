"""cortex_code mega-tool.

Phase M5: unify code execution operations behind a single MCP tool.
"""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolCategory, ToolParameter, ToolResult


class CortexCode(ConsolidatedTool):
    @property
    def name(self) -> str:
        return "cortex_code"

    @property
    def description(self) -> str:
        return "Unified code operations: implement, fix, refactor, review, test, debug."

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="op",
                type="string",
                required=False,
                enum=self.supported_operations,
                description="Code operation.",
            ),
            ToolParameter(
                name="operation",
                type="string",
                required=False,
                enum=self.supported_operations,
                description="Alias of op for compatibility.",
            ),
            ToolParameter(name="target", type="string", required=False, description="Target path or symbol."),
            ToolParameter(name="request", type="string", required=False, description="Request payload."),
            ToolParameter(name="context", type="object", required=False, description="Execution context."),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["implement", "fix", "refactor", "review", "test", "debug"]

    async def execute(self, **params: Any) -> ToolResult:
        operation = str(params.get("op") or params.get("operation") or "").lower().strip()
        if operation not in self.supported_operations:
            return ToolResult(
                success=False,
                error=(
                    f"Unsupported op '{operation or '<empty>'}' for cortex_code. "
                    f"Allowed: {', '.join(self.supported_operations)}"
                ),
                metadata={"trust_boundary": "deny_by_default", "allowed_ops": self.supported_operations},
            )

        routes: Dict[str, str] = {
            "implement": "TDDOrchestrator.implement",
            "fix": "TDDOrchestrator.fix",
            "refactor": "RefactoringOrchestrator.refactor",
            "review": "CodeReviewOrchestrator.review",
            "test": "TestingOrchestrator.execute",
            "debug": "DebuggerOrchestrator.debug",
        }
        return ToolResult(
            success=True,
            data={
                "tool": self.name,
                "op": operation,
                "route": routes[operation],
                "target": params.get("target"),
                "request": params.get("request"),
            },
            metadata={"trust_boundary": "code-only", "allowed_ops": self.supported_operations},
        )
