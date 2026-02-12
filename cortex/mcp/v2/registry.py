"""
MCP Tool Registry: Production Tool Definitions.

This module defines the COMPLETE set of production tools (24 tools).
No more, no fewer. Every tool serves a specific business capability.

Tool Count Strategy:
    - 98 tools (legacy) → 24 tools (v2)
    - 75% reduction achieved through:
      1. Consolidation by business capability
      2. Operation parameters instead of separate tools
      3. Removal of dev-only tools
      4. Elimination of duplicates
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
import logging

from cortex.mcp.v2.base import Tool, ToolDefinition, ToolCategory, ToolParameter


# ============================================================================
# PRODUCTION TOOL DEFINITIONS (24 Tools)
# ============================================================================

PRODUCTION_TOOLS: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # TIER 1: CORE REQUEST PROCESSING (4 tools)
    # =========================================================================
    "cortex_process_request": {
        "description": "Main entry point for all CORTEX requests. Routes to appropriate orchestrators based on intent classification.",
        "category": ToolCategory.CORE,
        "parameters": [
            {"name": "request", "type": "string", "required": True, "description": "User request text"},
            {"name": "context", "type": "object", "required": False, "description": "Additional context"},
            {"name": "mode", "type": "string", "required": False, "enum": ["tdd", "normal", "silent"], "description": "Execution mode"},
        ],
        "operations": [],  # Not consolidated - single purpose
    },
    "cortex_challenge": {
        "description": "Generate challenges and alternatives for proposed approaches. Implements disagreement detection.",
        "category": ToolCategory.CORE,
        "parameters": [
            {"name": "proposal", "type": "string", "required": True, "description": "Proposed approach to challenge"},
            {"name": "context", "type": "object", "required": False, "description": "Implementation context"},
        ],
        "operations": [],
    },
    "cortex_classify": {
        "description": "Classify user intent and request type using LENS analysis.",
        "category": ToolCategory.CORE,
        "parameters": [
            {"name": "request", "type": "string", "required": True, "description": "Request to classify"},
        ],
        "operations": [],
    },
    "cortex_request_lifecycle": {
        "description": "Manage request approval workflow (approve, reject, modify).",
        "category": ToolCategory.CORE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["approve", "reject", "modify"], "description": "Lifecycle operation"},
            {"name": "request_id", "type": "string", "required": True, "description": "Request identifier"},
            {"name": "reason", "type": "string", "required": False, "description": "Reason for operation"},
        ],
        "operations": ["approve", "reject", "modify"],
    },
    
    # =========================================================================
    # TIER 2: CODE INTELLIGENCE (3 tools)
    # =========================================================================
    "cortex_lens": {
        "description": "Unified code intelligence: analysis, AST parsing, pattern discovery, deep analysis.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["analyze", "deep_analyze", "ast", "discover", "extract_comments"], "description": "Analysis operation"},
            {"name": "target", "type": "string", "required": True, "description": "File or directory path"},
            {"name": "options", "type": "object", "required": False, "description": "Operation-specific options"},
        ],
        "operations": ["analyze", "deep_analyze", "ast", "discover", "extract_comments"],
    },
    "cortex_knowledge": {
        "description": "Knowledge base operations: search, gap analysis, TDD guidance, summary generation.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["search", "analyze_gap", "tdd_guidance", "generate_summary"], "description": "Knowledge operation"},
            {"name": "query", "type": "string", "required": True, "description": "Search query or topic"},
            {"name": "domain", "type": "string", "required": False, "description": "Domain filter"},
        ],
        "operations": ["search", "analyze_gap", "tdd_guidance", "generate_summary"],
    },
    "cortex_git": {
        "description": "Git operations: history analysis, duplicate detection, blame.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["history", "detect_duplicates", "blame"], "description": "Git operation"},
            {"name": "path", "type": "string", "required": False, "description": "File or directory path"},
            {"name": "hours", "type": "number", "required": False, "description": "Hours of history (default: 24)"},
        ],
        "operations": ["history", "detect_duplicates", "blame"],
    },
    
    # =========================================================================
    # TIER 3: GOVERNANCE & COMPLIANCE (3 tools)
    # =========================================================================
    "cortex_governance": {
        "description": "Governance operations: query rules, execute checks, analyze impact, generate reports.",
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["query", "execute", "analyze_impact", "report", "remediation_plan"], "description": "Governance operation"},
            {"name": "target", "type": "string", "required": False, "description": "Target path or rule ID"},
            {"name": "context", "type": "object", "required": False, "description": "Operation context"},
        ],
        "operations": ["query", "execute", "analyze_impact", "report", "remediation_plan"],
    },
    "cortex_validate": {
        "description": "Validation operations: compliance, architecture, holistic, environment, rules.",
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["compliance", "architecture", "holistic", "environment", "against_rules"], "description": "Validation type"},
            {"name": "target", "type": "string", "required": False, "description": "Target to validate"},
            {"name": "rules", "type": "array", "required": False, "description": "Specific rules to check"},
        ],
        "operations": ["compliance", "architecture", "holistic", "environment", "against_rules"],
    },
    "cortex_load": {
        "description": "Load governance configurations: core rules, audit checklist, modes, response format.",
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {"name": "resource", "type": "string", "required": True, "enum": ["core_rules", "audit_checklist", "modes", "response_format"], "description": "Resource to load"},
        ],
        "operations": ["core_rules", "audit_checklist", "modes", "response_format"],
    },
    
    # =========================================================================
    # TIER 4: OPERATIONS (5 tools)
    # =========================================================================
    "cortex_debug": {
        "description": "Debugging workflow: inject markers, capture state, analyze, generate fix plans.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["inject", "capture", "analyze", "fix_plan", "cleanup", "full_cycle", "status"], "description": "Debug operation"},
            {"name": "target", "type": "string", "required": True, "description": "Target path"},
            {"name": "context", "type": "object", "required": False, "description": "Debug context"},
        ],
        "operations": ["inject", "capture", "analyze", "fix_plan", "cleanup", "full_cycle", "status"],
    },
    "cortex_refactor": {
        "description": "Refactoring operations: execute refactoring, list available operations, check language support.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["execute", "available_operations", "supported_languages"], "description": "Refactor operation"},
            {"name": "target", "type": "string", "required": False, "description": "Target for refactoring"},
            {"name": "refactor_type", "type": "string", "required": False, "description": "Type of refactoring"},
        ],
        "operations": ["execute", "available_operations", "supported_languages"],
    },
    "cortex_plan": {
        "description": "Planning lifecycle: setup, execute, teardown, resolve, sync.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["setup", "execute", "teardown", "resolve", "sync"], "description": "Plan operation"},
            {"name": "phase_id", "type": "string", "required": False, "description": "Phase identifier"},
            {"name": "options", "type": "object", "required": False, "description": "Operation options"},
        ],
        "operations": ["setup", "execute", "teardown", "resolve", "sync"],
    },
    "cortex_onboard": {
        "description": "Repository onboarding: analyze configs, full onboarding (v2/v3), security scan.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["analyze_configs", "onboard", "security_scan"], "description": "Onboard operation"},
            {"name": "path", "type": "string", "required": True, "description": "Repository path"},
            {"name": "version", "type": "string", "required": False, "enum": ["v2", "v3"], "description": "Onboarding version"},
        ],
        "operations": ["analyze_configs", "onboard", "security_scan"],
    },
    "cortex_dashboard": {
        "description": "Dashboard management: CRUD repos, generate suite/landing/repo, server lifecycle.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["list_repos", "create_repo", "update_repo", "delete_repo", "generate_suite", "generate_repo", "generate_landing", "start_server", "health_check", "full_cycle"], "description": "Dashboard operation"},
            {"name": "repo_id", "type": "string", "required": False, "description": "Repository identifier"},
            {"name": "data", "type": "object", "required": False, "description": "Operation data"},
        ],
        "operations": ["list_repos", "create_repo", "update_repo", "delete_repo", "generate_suite", "generate_repo", "generate_landing", "start_server", "health_check", "full_cycle"],
    },
    
    # =========================================================================
    # TIER 5: UTILITIES (9 tools - kept separate for clarity)
    # =========================================================================
    "cortex_verify": {
        "description": "Verification operations: environment check, claim verification.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["environment", "claim"], "description": "Verification type"},
            {"name": "claim", "type": "string", "required": False, "description": "Claim to verify (for claim operation)"},
        ],
        "operations": ["environment", "claim"],
    },
    "cortex_ask": {
        "description": "Educational queries about CORTEX architecture with truth-based verification.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "question", "type": "string", "required": True, "description": "Question about CORTEX"},
        ],
        "operations": [],
    },
    "cortex_vacuum": {
        "description": "Cleanup markdown sprawl with automated archival and verification.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "path", "type": "string", "required": False, "description": "Path to clean"},
            {"name": "dry_run", "type": "boolean", "required": False, "description": "Preview without changes"},
        ],
        "operations": [],
    },
    "cortex_tools_catalog": {
        "description": "Discover all available MCP tools with descriptions and parameters.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "category", "type": "string", "required": False, "enum": ["core", "intelligence", "governance", "operations", "utilities"], "description": "Filter by category"},
        ],
        "operations": [],
    },
    "cortex_total_recall": {
        "description": "Discover and recall CORTEX features, components, and capabilities.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "query", "type": "string", "required": True, "description": "What to recall"},
        ],
        "operations": [],
    },
    "cortex_metrics": {
        "description": "Capture and report development metrics.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["capture", "report"], "description": "Metrics operation"},
            {"name": "metric_type", "type": "string", "required": False, "description": "Type of metric"},
            {"name": "data", "type": "object", "required": False, "description": "Metric data"},
        ],
        "operations": ["capture", "report"],
    },
    "cortex_check": {
        "description": "System checks: dependency drift, config analysis, test performance.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["dependency_drift", "config", "test_performance"], "description": "Check type"},
            {"name": "target", "type": "string", "required": False, "description": "Target path"},
        ],
        "operations": ["dependency_drift", "config", "test_performance"],
    },
    "cortex_vision": {
        "description": "Vision API for UI analysis, URL extraction, and structural mapping.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "image_path", "type": "string", "required": True, "description": "Path to image"},
            {"name": "analysis_type", "type": "string", "required": False, "enum": ["ui_elements", "urls", "structure"], "description": "Analysis type"},
        ],
        "operations": [],
    },
    "cortex_orchestrator": {
        "description": "Orchestrator diagnostics: health, issues, config optimization.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["health", "diagnose", "optimize_config"], "description": "Orchestrator operation"},
            {"name": "orchestrator_name", "type": "string", "required": False, "description": "Specific orchestrator"},
        ],
        "operations": ["health", "diagnose", "optimize_config"],
    },
}


@dataclass
class ToolMetadata:
    """
    Runtime metadata for a registered tool.
    """
    id: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    operations: List[str]
    version: str = "2.0.0"
    implementation: Optional[Type[Tool]] = None


class ToolRegistry:
    """
    Central registry for all MCP tools.
    
    Provides:
    - Tool registration and lookup
    - Category-based filtering
    - Schema generation for MCP protocol
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._tools: Dict[str, ToolMetadata] = {}
        self._implementations: Dict[str, Tool] = {}
        
        # Auto-register production tools
        self._register_production_tools()
    
    def _register_production_tools(self) -> None:
        """Register all production tools from PRODUCTION_TOOLS."""
        for tool_id, spec in PRODUCTION_TOOLS.items():
            params = [
                ToolParameter(
                    name=p["name"],
                    type=p["type"],
                    required=p.get("required", True),
                    description=p.get("description", ""),
                    enum=p.get("enum"),
                )
                for p in spec.get("parameters", [])
            ]
            
            metadata = ToolMetadata(
                id=tool_id,
                description=spec["description"],
                category=spec["category"],
                parameters=params,
                operations=spec.get("operations", []),
            )
            self._tools[tool_id] = metadata
        
        self.logger.info(f"Registered {len(self._tools)} production tools")
    
    def register(self, tool: Tool) -> None:
        """
        Register a tool implementation.
        
        Args:
            tool: Tool instance to register
        """
        definition = tool.definition
        self._implementations[definition.name] = tool
        
        # Update metadata with implementation
        if definition.name in self._tools:
            self._tools[definition.name].implementation = type(tool)
        
        self.logger.debug(f"Registered implementation: {definition.name}")
    
    def get(self, tool_id: str) -> Optional[Tool]:
        """
        Get tool implementation by ID.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool instance or None if not found
        """
        return self._implementations.get(tool_id)
    
    def get_metadata(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID."""
        return self._tools.get(tool_id)
    
    def list_all(self) -> List[ToolMetadata]:
        """List all registered tool metadata."""
        return list(self._tools.values())
    
    def list_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """List tools in a specific category."""
        return [t for t in self._tools.values() if t.category == category]
    
    def to_mcp_schema(self) -> List[Dict[str, Any]]:
        """
        Generate MCP protocol schema for all tools.
        
        Returns:
            List of tool definitions in MCP format
        """
        schemas = []
        for metadata in self._tools.values():
            properties = {}
            required = []
            
            for param in metadata.parameters:
                properties[param.name] = param.to_schema()
                if param.required:
                    required.append(param.name)
            
            schema = {
                "name": metadata.id,
                "description": metadata.description,
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            schemas.append(schema)
        
        return schemas
    
    @property
    def tool_count(self) -> int:
        """Get total number of registered tools."""
        return len(self._tools)


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get or create global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
