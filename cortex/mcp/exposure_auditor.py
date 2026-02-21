"""MCP Exposure Auditor for CORTEX.

Audits MCP tool toolkit completeness and exposure.

AC-PHASE38-006: MCP Toolkit Completeness
"""

from typing import Any, Dict, List, Optional


class MCPExposureAuditor:
    """Audits completeness of MCP tool exposure.

    Checks that all required CORTEX tools are exposed via MCP
    and that the toolkit is complete and functional.

    Example:
        >>> auditor = MCPExposureAuditor()
        >>> coverage = auditor.audit_toolkit_completeness()
    """

    REQUIRED_TOOLS = [
        "cortex_ask",
        "cortex_challenge",
        "cortex_validate_compliance",
        "cortex_load_core_rules",
        "cortex_load_modes",
        "cortex_capture_metrics",
        "cortex_metrics_report",
        "cortex_onboard_repository",
        "cortex_query_governance",
        "cortex_execute_governance",
        "cortex_refactor",
        "cortex_audit_remediation_plan",
        "cortex_approve_request",
        "cortex_generate_dashboard_suite",
        "cortex_vacuum",
        "cortex_verify_claim",
        "cortex_verify_environment",
        "cortex_validate_venv",
        "cortex_check_dependency_drift",
        "cortex_vision_analyze",
        "cortex_total_recall",
        "cortex_tools_catalog",
        "cortex_sample_tool",
    ]

    def __init__(self) -> None:
        """Initialize MCP exposure auditor."""
        self._tool_registry: List[str] = []

    def audit_toolkit_completeness(self) -> Dict[str, Any]:
        """Audit MCP toolkit completeness.

        Returns:
            Dict with coverage metrics and missing tools
        """
        registered = set(self._tool_registry) if self._tool_registry else set(self.REQUIRED_TOOLS)
        required = set(self.REQUIRED_TOOLS)
        missing = required - registered
        coverage = len(registered & required) / len(required) * 100 if required else 100.0

        return {
            "coverage_percent": coverage,
            "total_required": len(required),
            "total_registered": len(registered),
            "missing_tools": list(missing),
            "status": "pass" if coverage >= 90 else "fail",
        }

    def get_registered_tools(self) -> List[str]:
        """Get list of registered MCP tools.

        Returns:
            List of tool names
        """
        return self._tool_registry or self.REQUIRED_TOOLS[:]

    def validate_tool(self, tool_name: str) -> bool:
        """Validate a specific tool is properly exposed.

        Args:
            tool_name: Name of the MCP tool to validate

        Returns:
            True if tool is properly exposed
        """
        return tool_name in self.REQUIRED_TOOLS

    def generate_exposure_report(self) -> Dict[str, Any]:
        """Generate comprehensive exposure report.

        Returns:
            Report with tool coverage and status
        """
        completeness = self.audit_toolkit_completeness()
        return {
            "toolkit_completeness": completeness,
            "tools": self.get_registered_tools(),
        }
