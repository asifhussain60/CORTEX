"""MCP Tool Spec Generator for CORTEX.

Auto-generates MCP-compliant tool specifications for the tool registry.

AC-PHASE38-020: MCP tool registry auto-generation

CORE Governance:
    CORE-011: Type hints on all functions
    CORE-012: Docstrings on all public APIs
    CORE-028: snake_case naming
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


# Canonical MCP tools — matches cortex-architect.prompt.md spec (23 production tools)
_CANONICAL_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "cortex_ask",
        "description": "Ask educational questions about CORTEX architecture with truth-based verification",
        "inputSchema": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]},
    },
    {
        "name": "cortex_challenge",
        "description": "Generate AI-driven challenge to user request using LENS analysis",
        "inputSchema": {"type": "object", "properties": {"request": {"type": "string"}}, "required": ["request"]},
    },
    {
        "name": "cortex_validate_compliance",
        "description": "Validate code against CORE governance rules",
        "inputSchema": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
    },
    {
        "name": "cortex_load_core_rules",
        "description": "Load CORE governance rules from YAML registry",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_load_modes",
        "description": "Load HEXA-MODE definitions from YAML registry",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_capture_metrics",
        "description": "Record development metrics for analysis",
        "inputSchema": {"type": "object", "properties": {"metrics": {"type": "object"}}, "required": ["metrics"]},
    },
    {
        "name": "cortex_metrics_report",
        "description": "Export metrics report in YAML or JSON format",
        "inputSchema": {"type": "object", "properties": {"format": {"type": "string"}}},
    },
    {
        "name": "cortex_onboard_repository",
        "description": "Onboard repository with holistic LENS analysis + security assessment",
        "inputSchema": {"type": "object", "properties": {"repo_path": {"type": "string"}}, "required": ["repo_path"]},
    },
    {
        "name": "cortex_onboard_repository_v3",
        "description": "Onboard repository with LENS analysis + LLM business language + SQLite dashboard",
        "inputSchema": {"type": "object", "properties": {"repo_path": {"type": "string"}}, "required": ["repo_path"]},
    },
    {
        "name": "cortex_query_governance",
        "description": "Query governance state, rules, violations, and compliance data",
        "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
    {
        "name": "cortex_execute_governance",
        "description": "Execute governance actions — enforcement, blocking, remediation",
        "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}}, "required": ["action"]},
    },
    {
        "name": "cortex_refactor",
        "description": "Execute semantic refactoring operations across Python, C#, TypeScript/JavaScript",
        "inputSchema": {"type": "object", "properties": {"operation": {"type": "string"}, "target": {"type": "string"}}, "required": ["operation", "target"]},
    },
    {
        "name": "cortex_audit_remediation_plan",
        "description": "Generate structured remediation plan from audit results",
        "inputSchema": {"type": "object", "properties": {"audit_results": {"type": "object"}}, "required": ["audit_results"]},
    },
    {
        "name": "cortex_approve_request",
        "description": "Approve classified request and execute from stored approval session",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    {
        "name": "cortex_generate_dashboard_suite",
        "description": "Generate complete static dashboard suite with landing + per-repo dashboards",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_vacuum",
        "description": "Clean up markdown sprawl with automated archival and verification",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_verify_claim",
        "description": "Verify claims about CORTEX implementation against live code",
        "inputSchema": {"type": "object", "properties": {"claim": {"type": "string"}}, "required": ["claim"]},
    },
    {
        "name": "cortex_verify_environment",
        "description": "Verify CORTEX development environment setup",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_validate_venv",
        "description": "Validate virtual environment activation",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_check_dependency_drift",
        "description": "Check for dependency drift between requirements.txt and installed packages",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_vision_analyze",
        "description": "Analyze images via Vision API for UI elements, URLs, issues, and structural mappings",
        "inputSchema": {"type": "object", "properties": {"image_path": {"type": "string"}}, "required": ["image_path"]},
    },
    {
        "name": "cortex_total_recall",
        "description": "Discover and recall CORTEX features and components",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cortex_tools_catalog",
        "description": "Discover all MCP tools registered in CORTEX",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


class MCPToolSpecGenerator:
    """Generates and manages MCP-compliant tool specifications for the CORTEX registry.

    Builds a deduplicated, MCP-schema-compliant registry of all canonical
    CORTEX tools, supporting dry-run generation and merge with existing registries.

    Example:
        >>> gen = MCPToolSpecGenerator()
        >>> data = gen.build_registry_data()
        >>> assert len(data["tools"]) == 23
    """

    def __init__(self) -> None:
        """Initialise the generator with the canonical tool list."""
        self._canonical_tools: List[Dict[str, Any]] = list(_CANONICAL_TOOLS)

    def build_registry_data(self) -> Dict[str, Any]:
        """Build the full MCP tool registry data structure.

        Returns:
            Dict with 'tools' key containing all deduplicated tool specs
        """
        seen: set = set()
        deduped: List[Dict[str, Any]] = []
        for tool in self._canonical_tools:
            name = tool["name"]
            if name not in seen:
                seen.add(name)
                deduped.append(dict(tool))
        return {"tools": deduped, "count": len(deduped)}

    def generate_registry(
        self, output_path: Optional[Path]
    ) -> Optional[str]:
        """Generate the MCP tool registry, optionally writing to disk.

        Args:
            output_path: Target file path. Pass None for a dry-run (no I/O).

        Returns:
            str path written to, or "dry-run" if output_path is None
        """
        if output_path is None:
            return "dry-run"

        import json

        registry_data = self.build_registry_data()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(registry_data, indent=2))
        return str(output_path)

    def merge_with_existing(
        self, existing_tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge canonical tool list with an existing registry, deduplicating by name.

        Args:
            existing_tools: Existing tool spec list (from stored registry)

        Returns:
            Merged, deduplicated list of tool specs
        """
        merged: Dict[str, Dict[str, Any]] = {}
        for tool in existing_tools:
            merged[tool["name"]] = tool
        for tool in self._canonical_tools:
            if tool["name"] not in merged:
                merged[tool["name"]] = tool
        return list(merged.values())
