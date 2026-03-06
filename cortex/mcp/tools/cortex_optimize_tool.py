"""
CortexOptimize — MCP tool for Phase 130 Content Optimization Mode.

Optimizes arrays of files (HTML, Markdown, YAML, JSON, TXT, chat transcripts)
by removing noise and compressing content, then overwrites files in-place.

Single Responsibility: delegate to ContentOptimizationOrchestrator and format result.

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


class CortexOptimize(ConsolidatedTool):
    """
    Optimize arrays of files by removing noise and compressing content in-place.

    Operations:
    - optimize: Run the full 5-stage optimization pipeline on file arrays
    """

    # ------------------------------------------------------------------
    # ConsolidatedTool metadata
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the tool name."""
        return "cortex_optimize"

    @property
    def description(self) -> str:
        """Return the tool description."""
        return (
            "Optimize arrays of files (HTML, Markdown, YAML, JSON, TXT, chat transcripts) "
            "by removing noise and compressing content. Runs a 5-stage pipeline: "
            "classify → read → optimize → validate → write. Overwrites files in-place."
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
                name="file_paths",
                type="array",
                description=(
                    "Array of absolute file paths to optimize. Supports HTML, Markdown, "
                    "YAML, JSON, TXT, and chat transcript files. Files are overwritten "
                    "in-place with optimized content."
                ),
                required=True,
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
        return ["optimize"]

    # ------------------------------------------------------------------
    # Execution (async variant — kept for future async MCP framework use)
    # ------------------------------------------------------------------

    async def execute_async(self, **kwargs: Any) -> ToolResult:
        """
        Execute the optimization pipeline asynchronously.

        Args:
            file_paths: Array of file paths to optimize.
            orchestrator_context: Optional routing context.

        Returns:
            :class:`ToolResult` with optimization stats in data on success.
        """
        orchestrator_context = kwargs.get("orchestrator_context")
        if orchestrator_context is not None:
            validate_orchestrator_context(orchestrator_context)

        file_paths: Optional[List[str]] = kwargs.get("file_paths")

        if not isinstance(file_paths, list) or not file_paths:
            return ToolResult(
                success=False,
                error="'file_paths' must be a non-empty array of file paths.",
            )

        try:
            from cortex.orchestrators.support.content_optimization_orchestrator import (
                ContentOptimizationOrchestrator,
            )
            orch = ContentOptimizationOrchestrator()
            result = orch.optimize(file_paths=file_paths)

            if not result.success:
                return ToolResult(
                    success=False,
                    error=result.error_message or "Optimization failed.",
                    data={
                        "files_processed": result.files_processed,
                        "files_written": result.files_written,
                    },
                )

            return self.format_response(ToolResult(
                success=True,
                data={
                    "files_processed": result.files_processed,
                    "files_written": result.files_written,
                    "total_bytes_saved": result.total_bytes_saved,
                    "file_results": [
                        {
                            "file_path": fr["file_path"],
                            "content_type": fr["content_type"],
                            "compression_ratio": fr["compression_ratio"],
                            "success": fr["success"],
                            "error": fr.get("error"),
                        }
                        for fr in result.to_dict()["file_results"]
                    ],
                },
            ))

        except Exception as exc:  # pylint: disable=broad-except
            return ToolResult(
                success=False,
                error=f"cortex_optimize execution error: {exc}",
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

        file_paths: Optional[List[str]] = kwargs.get("file_paths")

        if not isinstance(file_paths, list) or not file_paths:
            return ToolResult(
                success=False,
                error="'file_paths' must be a non-empty array of file paths.",
            )

        try:
            from cortex.orchestrators.support.content_optimization_orchestrator import (
                ContentOptimizationOrchestrator,
            )
            orch = ContentOptimizationOrchestrator()
            result = orch.optimize(file_paths=file_paths)

            if not result.success:
                return ToolResult(
                    success=False,
                    error=result.error_message or "Optimization failed.",
                    data={
                        "files_processed": result.files_processed,
                        "files_written": result.files_written,
                    },
                )

            return self.format_response(ToolResult(
                success=True,
                data={
                    "files_processed": result.files_processed,
                    "files_written": result.files_written,
                    "total_bytes_saved": result.total_bytes_saved,
                    "file_results": [
                        {
                            "file_path": fr["file_path"],
                            "content_type": fr["content_type"],
                            "compression_ratio": fr["compression_ratio"],
                            "success": fr["success"],
                            "error": fr.get("error"),
                        }
                        for fr in result.to_dict()["file_results"]
                    ],
                },
            ))

        except Exception as exc:  # pylint: disable=broad-except
            return ToolResult(
                success=False,
                error=f"cortex_optimize execution error: {exc}",
            )
