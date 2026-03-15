"""cortex_learn mega-tool."""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolCategory, ToolParameter, ToolResult


class CortexLearn(ConsolidatedTool):
    @property
    def name(self) -> str:
        return "cortex_learn"

    @property
    def description(self) -> str:
        return "Unified learning operations: rca, feedback, digest, distill, onboard."

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.INTELLIGENCE

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="op", type="string", required=False, enum=self.supported_operations, description="Learning operation."),
            ToolParameter(name="operation", type="string", required=False, enum=self.supported_operations, description="Alias of op for compatibility."),
            ToolParameter(name="target", type="string", required=False, description="Target path or identifier."),
            ToolParameter(name="data", type="object", required=False, description="Operation payload."),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["rca", "feedback", "digest", "distill", "onboard"]

    async def execute(self, **params: Any) -> ToolResult:
        operation = str(params.get("op") or params.get("operation") or "").lower().strip()
        if operation not in self.supported_operations:
            return ToolResult(
                success=False,
                error=(
                    f"Unsupported op '{operation or '<empty>'}' for cortex_learn. "
                    f"Allowed: {', '.join(self.supported_operations)}"
                ),
                metadata={"trust_boundary": "deny_by_default", "allowed_ops": self.supported_operations},
            )

        routes: Dict[str, str] = {
            "rca": "LearningOrchestrator.rca",
            "feedback": "FeedbackOrchestrator.extract",
            "digest": "DigestSessionOrchestrator.digest",
            "distill": "DistillationOrchestrator.distill",
            "onboard": "OnboardingOrchestrator.onboard",
        }
        return ToolResult(
            success=True,
            data={"tool": self.name, "op": operation, "route": routes[operation], "target": params.get("target")},
            metadata={"trust_boundary": "learning-only", "allowed_ops": self.supported_operations},
        )
