"""
CortexDistill — MCP tool for Phase 129 Distillation Mode.

Reduces a multi-turn conversation to an executable, context-dense prompt.
Single Responsibility: delegate to DistillationOrchestrator and format result.

CORE-011: type hints | CORE-012: docstrings
"""
from __future__ import annotations

from typing import Any, List, Optional

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context


class CortexDistill(ConsolidatedTool):
    """
    Distil a multi-turn conversation into an executable, context-dense prompt.

    Operations:
    - distill: Run the full 5-stage distillation pipeline on a conversation
    """

    # ------------------------------------------------------------------
    # ConsolidatedTool metadata
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the tool name."""
        return "cortex_distill"

    @property
    def description(self) -> str:
        """Return the tool description."""
        return (
            "Distil a multi-turn conversation into an executable, context-dense prompt. "
            "Runs a 5-stage pipeline: segment → reconstruct → reconcile → synthesise → compress. "
            "Eliminates noise, preserves goals, decisions, and constraints."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the tool category."""
        return ToolCategory.UTILITIES

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the tool parameters."""
        return [
            ToolParameter(
                name="conversation",
                type="string",
                description=(
                    "Raw multi-turn conversation text to distil. "
                    "Supports 'User: / Agent:' prefix format or plain prose."
                ),
                required=True,
            ),
            ToolParameter(
                name="file_path",
                type="string",
                description=(
                    "Optional path to the source file. When provided, the file is "
                    "overwritten in place with the compressed distilled content."
                ),
                required=False,
                default=None,
            ),
            ToolParameter(
                name="orchestrator_context",
                type="string",
                description="Optional orchestrator context for governance routing.",
                required=False,
                default=None,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["distill"]

    # ------------------------------------------------------------------
    # Execution (async variant — kept for future async MCP framework use)
    # ------------------------------------------------------------------

    async def execute_async(self, **kwargs: Any) -> ToolResult:
        """
        Execute the distillation pipeline asynchronously.

        Args:
            conversation: Raw multi-turn conversation text.
            orchestrator_context: Optional routing context.

        Returns:
            :class:`ToolResult` with ``distilled_prompt`` in data on success.
        """
        orchestrator_context = kwargs.get("orchestrator_context")
        if orchestrator_context is not None:
            validate_orchestrator_context(orchestrator_context)

        conversation: str = kwargs.get("conversation", "")
        file_path: Optional[str] = kwargs.get("file_path") or None

        if not isinstance(conversation, str) or not conversation.strip():
            return ToolResult(
                success=False,
                error="Parameter 'conversation' is required and must be a non-empty string.",
            )

        try:
            from cortex.orchestrators.support.distillation_orchestrator import (
                DistillationOrchestrator,
            )
            orch = DistillationOrchestrator()
            result = orch.distill(conversation=conversation, file_path=file_path)

            if not result.success:
                return ToolResult(
                    success=False,
                    error=result.error_message or "Distillation failed.",
                    data={"segment_count": result.segment_count},
                )

            return self.format_response(ToolResult(
                success=True,
                data={
                    "distilled_prompt": result.distilled_prompt,
                    "segment_count": result.segment_count,
                    "noise_ratio": result.noise_ratio,
                    "metadata": result.metadata,
                },
            ))

        except Exception as exc:  # pylint: disable=broad-except
            return ToolResult(
                success=False,
                error=f"cortex_distill execution error: {exc}",
            )

    # ------------------------------------------------------------------
    # Synchronous execute — canonical entry point for MCP and tests
    # ------------------------------------------------------------------

    def execute(self, params: dict, **kwargs: Any) -> ToolResult:
        """
        Synchronous shim for test compatibility.

        The MCP framework calls the async variant; tests call this directly.

        Args:
            params: Dict of tool parameters.

        Returns:
            :class:`ToolResult`.
        """
        if isinstance(params, dict):
            kwargs.update(params)

        orchestrator_context = kwargs.get("orchestrator_context")
        if orchestrator_context is not None:
            validate_orchestrator_context(orchestrator_context)

        conversation: str = kwargs.get("conversation", "")
        file_path: Optional[str] = kwargs.get("file_path") or None

        if not isinstance(conversation, str) or not conversation.strip():
            return ToolResult(
                success=False,
                error="Parameter 'conversation' is required and must be a non-empty string.",
            )

        try:
            from cortex.orchestrators.support.distillation_orchestrator import (
                DistillationOrchestrator,
            )
            orch = DistillationOrchestrator()
            result = orch.distill(conversation=conversation, file_path=file_path)

            if not result.success:
                return ToolResult(
                    success=False,
                    error=result.error_message or "Distillation failed.",
                    data={"segment_count": result.segment_count},
                )

            return self.format_response(ToolResult(
                success=True,
                data={
                    "distilled_prompt": result.distilled_prompt,
                    "segment_count": result.segment_count,
                    "noise_ratio": result.noise_ratio,
                    "metadata": result.metadata,
                },
            ))

        except Exception as exc:  # pylint: disable=broad-except
            return ToolResult(
                success=False,
                error=f"cortex_distill execution error: {exc}",
            )
