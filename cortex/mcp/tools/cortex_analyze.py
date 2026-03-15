"""cortex_analyze mega-tool."""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolCategory, ToolParameter, ToolResult


class CortexAnalyze(ConsolidatedTool):
    @property
    def name(self) -> str:
        return "cortex_analyze"

    @property
    def description(self) -> str:
        return "Unified analysis operations: lens, investigate, architecture, complexity."

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.INTELLIGENCE

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="op", type="string", required=False, enum=self.supported_operations, description="Analysis operation."),
            ToolParameter(name="operation", type="string", required=False, enum=self.supported_operations, description="Alias of op for compatibility."),
            ToolParameter(name="target", type="string", required=False, description="Target path."),
            ToolParameter(name="query", type="string", required=False, description="Query payload."),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["lens", "investigate", "architecture", "complexity"]

    async def execute(self, **params: Any) -> ToolResult:
        operation = str(params.get("op") or params.get("operation") or "").lower().strip()
        if operation not in self.supported_operations:
            return ToolResult(
                success=False,
                error=(
                    f"Unsupported op '{operation or '<empty>'}' for cortex_analyze. "
                    f"Allowed: {', '.join(self.supported_operations)}"
                ),
                metadata={"trust_boundary": "deny_by_default", "allowed_ops": self.supported_operations},
            )

        routes: Dict[str, str] = {
            "lens": "LensOrchestrator.analyze",
            "investigate": "InvestigationOrchestrator.investigate",
            "architecture": "ArchitectureAnalyzer.analyze",
            "complexity": "ComplexityAnalyzer.analyze",
        }
        return ToolResult(
            success=True,
            data={"tool": self.name, "op": operation, "route": routes[operation], "target": params.get("target"), "query": params.get("query")},
            metadata={"trust_boundary": "analysis-only", "allowed_ops": self.supported_operations},
        )
