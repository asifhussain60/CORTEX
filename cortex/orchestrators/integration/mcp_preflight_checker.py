"""
MCP Pre-Flight Checker - Validate MCP availability before routing.

AC_START: AC-INTEGRATION-002
Description: Implement MCP pre-flight check to block direct file operations
Authority: ROOT-CAUSE-ANALYSIS-2026-02-08 (P0: MCP-FIRST Enforcement Missing)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ManagedStatus(Enum):
    """MCP availability status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"


@dataclass
class MCPPreFlightResult:
    """Result of MCP pre-flight check."""
    status: ManagedStatus
    available_tools: List[str]
    missing_tools: List[str]
    mcp_server_running: bool
    configuration_valid: bool
    error_message: Optional[str] = None

    def is_available(self) -> bool:
        """Check if MCP is fully available."""
        return self.status == ManagedStatus.AVAILABLE

    def get_block_message(self) -> str:
        """Get user-facing block message."""
        if not self.mcp_server_running:
            return (
                "❌ MCP Server Not Running\n"
                "CORTEX requires the MCP server to be active.\n"
                "Start: python -m cortex.mcp.server\n"
                "Then restart Copilot session."
            )

        if not self.configuration_valid:
            return (
                "❌ MCP Configuration Invalid\n"
                ".vscode/settings.json missing MCP configuration.\n"
                "Run: python .cortex/setup-mcp.py\n"
                "Then restart Copilot."
            )

        if self.missing_tools:
            return (
                f"❌ Required MCP Tools Missing\n"
                f"Missing: {', '.join(self.missing_tools)}\n"
                f"Available: {len(self.available_tools)}/10\n"
                f"Run: python -m cortex.mcp.server --reload"
            )

        return "❌ MCP System Not Ready"


class MCPPreFlightChecker:
    """
    Pre-flight validation for MCP availability and configuration.

    Runs BEFORE processing user requests to ensure:
    1. MCP server is running
    2. Required tools are available
    3. Configuration is valid
    4. Direct file operations can be blocked
    """

    # Tools required for different intents
    REQUIRED_TOOLS = {
        "IMPLEMENT": ["cortex_process_request", "cortex_challenge"],
        "FIX": ["cortex_process_request", "cortex_challenge"],
        "REFACTOR": ["cortex_process_request", "cortex_challenge"],
        "ANALYZE": ["cortex_lens_analyze"],
        "AUDIT": ["cortex_lens_analyze", "cortex_challenge"],
        "PLAN": ["cortex_plan_setup", "cortex_plan_execute_autonomous"],
    }

    def __init__(self) -> None:
        """Initialize MCP pre-flight checker."""
        self.required_tools_list = [
            "cortex_process_request",
            "cortex_lens_analyze",
            "cortex_challenge",
            "cortex_total_recall",
            "cortex_git_history",
            "cortex_ast_analyze",
            "cortex_detect_duplicates",
            "cortex_plan_setup",
            "cortex_plan_teardown",
            "cortex_plan_execute_autonomous",
        ]

    def check_mcp_availability(
        self,
        available_tools: Optional[List[str]] = None,
        mcp_server_running: bool = False,
        config_valid: bool = False
    ) -> MCPPreFlightResult:
        """
        Check MCP availability with provided information.

        Args:
            available_tools: List of currently available MCP tools
            mcp_server_running: Whether MCP server is running
            config_valid: Whether MCP configuration is valid

        Returns:
            MCPPreFlightResult with detailed status
        """
        available_tools = available_tools or []

        # Find missing tools
        missing = [t for t in self.required_tools_list if t not in available_tools]

        # Determine status
        if mcp_server_running and config_valid and not missing:
            status = ManagedStatus.AVAILABLE
        elif mcp_server_running and config_valid:
            status = ManagedStatus.DEGRADED
        else:
            status = ManagedStatus.UNAVAILABLE

        return MCPPreFlightResult(
            status=status,
            available_tools=available_tools,
            missing_tools=missing,
            mcp_server_running=mcp_server_running,
            configuration_valid=config_valid,
        )

    def should_block_operation(
        self,
        intent: str,
        preflight_result: MCPPreFlightResult
    ) -> bool:
        """
        Determine if operation should be blocked due to MCP unavailability.

        Args:
            intent: User intent (IMPLEMENT, FIX, REFACTOR, etc.)
            preflight_result: Result of MCP pre-flight check

        Returns:
            True if operation should be blocked
        """
        # These intents REQUIRE MCP
        blocking_intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "AUDIT", "PLAN"]

        if intent not in blocking_intents:
            return False

        # Check if all required tools are available
        required = self.REQUIRED_TOOLS.get(intent, [])
        available_set = set(preflight_result.available_tools)

        missing = [t for t in required if t not in available_set]

        return len(missing) > 0 or not preflight_result.configuration_valid

    def get_status_report(self, result: MCPPreFlightResult) -> str:
        """
        Get human-readable status report.

        Args:
            result: MCP pre-flight result

        Returns:
            Formatted status report
        """
        lines = [
            "🔧 MCP System Status",
            "=" * 50,
            f"Server Running: {'✅ Yes' if result.mcp_server_running else '❌ No'}",
            f"Configuration: {'✅ Valid' if result.configuration_valid else '❌ Invalid'}",
            f"Tools Available: {len(result.available_tools)}/10",
        ]

        if result.missing_tools:
            lines.append(f"Missing Tools: {', '.join(result.missing_tools)}")

        lines.append(f"Overall: {'🟢 READY' if result.is_available() else '🔴 NOT READY'}")

        return "\n".join(lines)


# AC_COMPLETE: AC-INTEGRATION-002 ✅
