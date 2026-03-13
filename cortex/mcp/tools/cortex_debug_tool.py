"""
CortexDebug — Debug cycle management for CORTEX applications.

Extracted from cortex/mcp/tools/operations.py (Phase 103-d, GAP-103-07).
Single Responsibility: Inject debug markers, capture logs, analyze issues,
generate fix plans, and clean up markers across all supported stacks.

CORE-011: type hints | CORE-012: docstrings
"""
from __future__ import annotations

from typing import List

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context


class CortexDebug(ConsolidatedTool):
    """
    Debug cycle management.

    Operations:
    - inject: Inject debug markers
    - capture: Capture debug logs
    - analyze: Analyze debug output
    - fix_plan: Generate fix plan
    - cleanup: Remove debug markers
    """

    @property
    def name(self) -> str:
        """Return the name."""
        return "cortex_debug"

    @property
    def description(self) -> str:
        """Return the description."""
        return (
            "Comprehensive debugging for CORTEX applications. Inject markers, "
            "capture logs, analyze issues, and generate fix plans."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the category."""
        return ToolCategory.OPERATIONS

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the parameters."""
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Debug operation: inject, capture, analyze, fix_plan, cleanup",
                required=True,
                enum=["inject", "capture", "analyze", "fix_plan", "cleanup"],
            ),
            ToolParameter(
                name="target",
                type="string",
                description="Target file or directory",
                required=False,
            ),
            ToolParameter(
                name="markers",
                type="array",
                description="Debug markers to inject",
                required=False,
            ),
            ToolParameter(
                name="log_level",
                type="string",
                description="Log level: debug, info, warning, error",
                required=False,
                enum=["debug", "info", "warning", "error"],
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["inject", "capture", "analyze", "fix_plan", "cleanup"]

    async def execute(self, **params) -> ToolResult:
        """Execute debug operation."""
        # ENFORCEMENT: Validate orchestrator routing — raises ValueError on direct calls
        validate_orchestrator_context(params.get("orchestrator_context"))

        operation = params.get("operation", "analyze")
        target = params.get("target")
        markers = params.get("markers", [])
        log_level = params.get("log_level", "debug")

        # WAVE-R Integration: Use DebugMCPTools for operations
        if operation == "inject":
            try:
                from cortex.mcp.tools.debug_tools import DebugMCPTools
                from cortex.core.event_bus import EventBus
                from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator

                # Initialize infrastructure
                event_bus = EventBus()
                orchestrator = DebuggerOrchestrator(event_bus)
                tools = DebugMCPTools(event_bus, orchestrator)

                # Extract marker injection parameters
                trigger_type = params.get("trigger_type", "test_failure")
                file_path = target or "/tmp/unknown.py"
                line_number = params.get("line_number", 1)
                context = params.get("context", {})

                # Inject markers via DebugMCPTools
                result = tools.auto_inject(
                    trigger_type=trigger_type,
                    file_path=file_path,
                    line_number=line_number,
                    context=context
                )

                return ToolResult(
                    success=result["status"] == "success",
                    data=result,
                    metadata={"operation": "inject", "wave_r": True},
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Debug marker injection failed: {str(e)}",
                    metadata={"operation": "inject"}
                )

        elif operation == "list_sessions":
            try:
                from cortex.mcp.tools.debug_tools import DebugMCPTools
                from cortex.core.event_bus import EventBus
                from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator

                event_bus = EventBus()
                orchestrator = DebuggerOrchestrator(event_bus)
                tools = DebugMCPTools(event_bus, orchestrator)

                status_filter = params.get("status_filter", "all")
                result = tools.list_sessions(status_filter=status_filter)

                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"operation": "list_sessions", "wave_r": True}
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Session listing failed: {str(e)}",
                    metadata={"operation": "list_sessions"}
                )

        elif operation == "cleanup":
            try:
                from cortex.mcp.tools.debug_tools import DebugMCPTools
                from cortex.core.event_bus import EventBus
                from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator

                event_bus = EventBus()
                orchestrator = DebuggerOrchestrator(event_bus)
                tools = DebugMCPTools(event_bus, orchestrator)

                session_id = params.get("session_id")
                cleanup_all = params.get("cleanup_all", False)
                result = tools.cleanup(session_id=session_id, cleanup_all=cleanup_all)

                return ToolResult(
                    success=result["status"] == "success",
                    data=result,
                    metadata={"operation": "cleanup", "wave_r": True}
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Debug cleanup failed: {str(e)}",
                    metadata={"operation": "cleanup"}
                )

        elif operation == "capture":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "logs_captured": [],
                    "log_level": log_level,
                    "duration": "0s",
                },
                metadata={"operation": "capture"},
            )

        elif operation == "analyze":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "issues_found": [],
                    "root_causes": [],
                    "severity": "low",
                },
                metadata={"operation": "analyze"},
            )

        elif operation == "fix_plan":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "plan": [],
                    "estimated_effort": "low",
                    "auto_fixable": True,
                },
                metadata={"operation": "fix_plan"},
            )

        return ToolResult(success=False, error=f"Unknown operation: {operation}")
