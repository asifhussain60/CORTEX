"""
MCP Tool Registry: Production Tool Definitions.

This module defines the COMPLETE set of production tools (24 tools).
No more, no fewer. Every tool serves a specific business capability.

Tool Count Strategy:
    - 98 tools (legacy) → 24 tools (v3)
    - Removed deprecated tools: cortex_process_request, cortex_lens
    - Consolidation by business capability
    - Operation parameters instead of separate tools
    - Removal of dev-only tools
    - Elimination of duplicates
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
import logging

from cortex.mcp.mcp_tool_base import Tool, ToolDefinition, ToolCategory, ToolParameter


# ============================================================================
# PRODUCTION TOOL DEFINITIONS (24 Tools)
# Removed: cortex_process_request (deprecated), cortex_lens (deleted per architect spec)
# ============================================================================

PRODUCTION_TOOLS: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # TIER 1: CORE REQUEST PROCESSING (3 tools)
    # Note: cortex_process_request removed — deprecated per architect prompt
    # =========================================================================
    "cortex_challenge": {
        "description": "Generate challenges and alternatives for proposed approaches. Implements disagreement detection.",
        "category": ToolCategory.CORE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["generate", "review", "validate"], "description": "Challenge operation"},
            {"name": "request", "type": "string", "required": True, "description": "The user request to challenge"},
            {"name": "context", "type": "object", "required": False, "description": "Implementation context"},
            {"name": "depth", "type": "string", "required": False, "enum": ["shallow", "standard", "deep"], "description": "Challenge depth"},
        ],
        "operations": ["generate", "review", "validate"],
    },
    "cortex_classify": {
        "description": "Classify user intent and request type using LENS analysis.",
        "category": ToolCategory.CORE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["intent", "type", "priority"], "description": "Classification operation"},
            {"name": "request", "type": "string", "required": True, "description": "Request to classify"},
        ],
        "operations": ["intent", "type", "priority"],
    },
    "cortex_request_lifecycle": {
        "description": "Manage request approval workflow (approve, reject, modify).",
        "category": ToolCategory.CORE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["create", "approve", "reject", "modify", "query"], "description": "Lifecycle operation"},
            {"name": "request_id", "type": "string", "required": False, "description": "Request identifier"},
            {"name": "reason", "type": "string", "required": False, "description": "Reason for operation"},
        ],
        "operations": ["create", "approve", "reject", "modify", "query"],
    },
    
    # =========================================================================
    # TIER 2: CODE INTELLIGENCE (3 tools)
    # Note: cortex_lens removed — deleted tool per architect prompt; use cortex/lens/ module directly
    # =========================================================================
    "cortex_knowledge": {
        "description": "Knowledge base operations: search, domain analysis, best practices, gap detection.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["search", "domain", "best_practices", "gaps"], "description": "Knowledge operation"},
            {"name": "query", "type": "string", "required": True, "description": "Search query or topic"},
            {"name": "domain", "type": "string", "required": False, "description": "Domain filter"},
        ],
        "operations": ["search", "domain", "best_practices", "gaps"],
    },
    "cortex_git": {
        "description": "Git operations: history analysis, blame, diff, context extraction.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["history", "blame", "diff", "context", "changes"], "description": "Git operation"},
            {"name": "path", "type": "string", "required": False, "description": "File or directory path"},
            {"name": "hours", "type": "number", "required": False, "description": "Hours of history (default: 24)"},
        ],
        "operations": ["history", "blame", "diff", "context", "changes"],
    },
    "cortex_generate_tests": {
        "description": "Generate intelligent test suites using multi-strategy analysis. Detects blind spots, edge cases, and security vulnerabilities.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "target", "type": "string", "required": True, "description": "Target function name or API endpoint"},
            {"name": "target_type", "type": "string", "required": True, "enum": ["function", "endpoint"], "description": "Type of target: 'function' or 'endpoint'"},
            {"name": "file_path", "type": "string", "required": True, "description": "Path to file containing target"},
            {"name": "parameters", "type": "array", "required": False, "description": "Function parameters or endpoint schema"},
            {"name": "coverage_report", "type": "object", "required": False, "description": "Existing coverage data"},
        ],
        "operations": [],
    },
    
    # =========================================================================
    # TIER 3: GOVERNANCE & COMPLIANCE (4 tools)
    # =========================================================================
    "cortex_governance": {
        "description": "Governance operations: query rules, execute checks, analyze impact, generate reports, Stage 0 audit.",
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["query", "execute", "analyze_impact", "report", "remediation_plan", "stage0_audit"], "description": "Governance operation"},
            {"name": "target", "type": "string", "required": False, "description": "Target path or rule ID"},
            {"name": "context", "type": "object", "required": False, "description": "Operation context"},
            {"name": "request", "type": "string", "required": False, "description": "User request for stage0_audit operation"},
        ],
        "operations": ["query", "execute", "analyze_impact", "report", "remediation_plan", "stage0_audit"],
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
        "description": "Load governance configurations: rules, modes, checklist, format.",
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["rules", "modes", "checklist", "format"], "description": "Load operation / resource to load"},
            {"name": "tier", "type": "string", "required": False, "enum": ["tier0", "tier1", "tier2"], "description": "Tier filter"},
        ],
        "operations": ["rules", "modes", "checklist", "format"],
    },
    "cortex_validate_request": {
        "description": "Phase 48 holistic validation: Pre-implementation checklist + challenge generation + confidence scoring with 0.7 threshold gating.",
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {"name": "intent", "type": "string", "required": True, "enum": ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE"], "description": "User intent: IMPLEMENT, FIX, REFACTOR"},
            {"name": "request", "type": "string", "required": True, "description": "User's implementation request"},
            {"name": "target", "type": "string", "required": False, "description": "Target file or component"},
            {"name": "context", "type": "object", "required": False, "description": "Additional context (security_critical, effort, etc.)"},
            {"name": "operation", "type": "string", "required": False, "enum": ["validate", "quick", "challenges"], "description": "Validation operation: validate (full), quick (checklist only), challenges (alternatives only)"},
        ],
        "operations": ["validate", "quick", "challenges"],
    },
    
    # =========================================================================
    # TIER 4: OPERATIONS (5 tools)
    # =========================================================================
    "cortex_debug": {
        "description": "Debugging workflow: inject markers, capture state, analyze, generate fix plans.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["inject", "capture", "analyze", "fix_plan", "cleanup"], "description": "Debug operation"},
            {"name": "target", "type": "string", "required": True, "description": "Target path"},
            {"name": "context", "type": "object", "required": False, "description": "Debug context"},
        ],
        "operations": ["inject", "capture", "analyze", "fix_plan", "cleanup"],
    },
    "cortex_refactor": {
        "description": "Refactoring operations: execute refactoring, list available operations, check language support.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["extract", "rename", "move", "inline", "organize"], "description": "Refactor operation"},
            {"name": "target", "type": "string", "required": False, "description": "Target for refactoring"},
            {"name": "refactor_type", "type": "string", "required": False, "description": "Type of refactoring"},
            {"name": "scope", "type": "string", "required": False, "enum": ["local", "module", "package", "workspace"], "description": "Refactoring scope"},
        ],
        "operations": ["extract", "rename", "move", "inline", "organize"],
    },
    "cortex_plan": {
        "description": "Planning lifecycle: create, update, complete, query, sync.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["create", "update", "complete", "query", "sync"], "description": "Plan operation"},
            {"name": "phase_id", "type": "string", "required": False, "description": "Phase identifier"},
            {"name": "options", "type": "object", "required": False, "description": "Operation options"},
        ],
        "operations": ["create", "update", "complete", "query", "sync"],
    },
    "cortex_onboard": {
        "description": "Repository onboarding: analyze configs, full onboarding (v2/v3), security scan.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["full", "lens", "security", "status"], "description": "Onboard operation"},
            {"name": "path", "type": "string", "required": True, "description": "Repository path"},
            {"name": "version", "type": "string", "required": False, "enum": ["v2", "v3"], "description": "Onboarding version"},
        ],
        "operations": ["full", "lens", "security", "status"],
    },
    "cortex_dashboard": {
        "description": "Dashboard management: generate suite/landing/repo, query, full lifecycle.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["generate", "update", "query", "landing", "full_cycle"], "description": "Dashboard operation"},
            {"name": "repo_id", "type": "string", "required": False, "description": "Repository identifier"},
            {"name": "data", "type": "object", "required": False, "description": "Operation data"},
            {"name": "output_format", "type": "string", "required": False, "enum": ["html", "json", "yaml"], "description": "Output format"},
        ],
        "operations": ["generate", "update", "query", "landing", "full_cycle"],
    },
    
    # =========================================================================
    # TIER 5: TOOLKIT OPERATIONS (4 tools) — NEW
    # =========================================================================
    "cortex_scan": {
        "description": "Hierarchical file scanning with organization detection. Supports custom extensions and pluggable adapters.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "root_path", "type": "string", "required": True, "description": "Root directory to scan"},
            {"name": "extensions", "type": "array", "required": False, "description": "File extensions to scan (e.g., ['.py', '.yaml'])"},
            {"name": "organization_adapter", "type": "string", "required": False, "enum": ["media", "code", "docs"], "description": "Organization detection adapter"},
        ],
        "operations": [],
    },
    "cortex_batch_transform": {
        "description": "Batch processing with configurable triggers (size/timeout). Applies transformation operations to items.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "items", "type": "array", "required": True, "description": "Items to batch process"},
            {"name": "batch_size", "type": "number", "required": False, "description": "Trigger flush after N items (default: 100)"},
            {"name": "timeout_ms", "type": "number", "required": False, "description": "Trigger flush after N ms (default: 5000)"},
            {"name": "operation", "type": "string", "required": False, "enum": ["identity", "uppercase", "sanitize"], "description": "Transformation operation"},
        ],
        "operations": ["identity", "uppercase", "sanitize"],
    },
    "cortex_enrich": {
        "description": "Content enrichment via domain adapters. Applies morph rules, organization detection, and external source integration.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "content", "type": "string", "required": True, "description": "Content to enrich (filename, text, etc.)"},
            {"name": "domain", "type": "string", "required": False, "enum": ["media", "code", "docs"], "description": "Domain adapter type (default: 'media')"},
            {"name": "enrichment_sources", "type": "array", "required": False, "description": "External sources to query (e.g., ['iafd', 'tmdb'])"},
        ],
        "operations": [],
    },
    "cortex_workflow": {
        "description": "Generic workflow orchestration. Chains toolkit operations (scan → batch → enrich) into reusable pipelines.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "workflow_type", "type": "string", "required": False, "enum": ["scan_batch_enrich", "batch_transform"], "description": "Workflow template (default: 'scan_batch_enrich')"},
            {"name": "root_path", "type": "string", "required": False, "description": "Root path for scan operation"},
            {"name": "batch_size", "type": "number", "required": False, "description": "Batch size (default: 100)"},
            {"name": "domain", "type": "string", "required": False, "enum": ["media", "code", "docs"], "description": "Domain adapter (default: 'media')"},
        ],
        "operations": ["scan_batch_enrich", "batch_transform"],
    },
    
    # =========================================================================
    # TIER 5: UTILITIES (9 tools - kept separate for clarity)
    # =========================================================================
    "cortex_verify": {
        "description": "Verification operations: environment check, claim verification, MCP config.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["environment", "claim", "mcp"], "description": "Verification type"},
            {"name": "target", "type": "string", "required": False, "description": "Target for verification (claim text, config path)"},
            {"name": "auto_fix", "type": "boolean", "required": False, "description": "Attempt auto-fix for issues"},
        ],
        "operations": ["environment", "claim", "mcp"],
    },
    "cortex_ask": {
        "description": "Educational queries about CORTEX architecture with truth-based verification.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["architecture", "features", "governance"], "description": "Question type"},
            {"name": "question", "type": "string", "required": True, "description": "Question about CORTEX"},
        ],
        "operations": ["architecture", "features", "governance"],
    },
    "cortex_vacuum": {
        "description": "Cleanup markdown sprawl with automated archival and verification.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["scan", "clean", "archive", "verify"], "description": "Vacuum operation"},
            {"name": "path", "type": "string", "required": False, "description": "Path to clean"},
            {"name": "dry_run", "type": "boolean", "required": False, "description": "Preview without changes"},
        ],
        "operations": ["scan", "clean", "archive", "verify"],
    },
    "cortex_tools_catalog": {
        "description": "Discover all available MCP tools with descriptions and parameters.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["list", "search", "describe", "categories"], "description": "Catalog operation"},
            {"name": "query", "type": "string", "required": False, "description": "Search query or tool name"},
            {"name": "category", "type": "string", "required": False, "enum": ["core", "intelligence", "governance", "operations", "utilities"], "description": "Filter by category"},
        ],
        "operations": ["list", "search", "describe", "categories"],
    },
    "cortex_total_recall": {
        "description": "Discover and recall CORTEX features, components, and capabilities.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["discover", "recall", "search"], "description": "Recall operation"},
            {"name": "feature", "type": "string", "required": False, "description": "Feature name or search query"},
            {"name": "category", "type": "string", "required": False, "description": "Feature category filter"},
        ],
        "operations": ["discover", "recall", "search"],
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
        "description": "System checks: dependency drift, status check, health check, orchestrator health monitoring.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["dependencies", "status", "health", "orchestrator_health"], "description": "Check type"},
            {"name": "operation_id", "type": "string", "required": False, "description": "Operation ID for status check"},
            {"name": "orchestrator", "type": "string", "required": False, "description": "Specific orchestrator name for health check"},
            {"name": "parallel", "type": "boolean", "required": False, "description": "Check all orchestrators in parallel (default: true)"},
        ],
        "operations": ["dependencies", "status", "health", "orchestrator_health"],
    },
    "cortex_vision": {
        "description": "Vision API for UI analysis, URL extraction, and structural mapping.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["analyze", "ui", "extract"], "description": "Vision operation"},
            {"name": "image", "type": "string", "required": True, "description": "Image path or base64 data"},
            {"name": "options", "type": "object", "required": False, "description": "Analysis options"},
        ],
        "operations": ["analyze", "ui", "extract"],
    },
    "cortex_orchestrator": {
        "description": "Orchestrator management: list, status, invoke, health_check for all 22 wired orchestrators.",
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["list", "status", "invoke", "health_check"], "description": "Orchestrator operation"},
            {"name": "orchestrator", "type": "string", "required": False, "description": "Orchestrator name for status/invoke/health_check"},
            {"name": "params", "type": "object", "required": False, "description": "Parameters for orchestrator invocation"},
        ],
        "operations": ["list", "status", "invoke", "health_check"],
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
        """Initialize instance."""
        self.logger = logging.getLogger(__name__)
        self._tools: Dict[str, ToolMetadata] = {}
        self._implementations: Dict[str, Tool] = {}
        
        # Auto-register production tools
        self._register_production_tools()
    
    def _register_production_tools(self) -> None:
        """Register all production tools from PRODUCTION_TOOLS."""
        # Step 1: Register metadata for all tools
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
        
        self.logger.info(f"Registered {len(self._tools)} production tool metadata")
        
        # Step 2: Register tool implementations
        self._register_implementations()
    
    def _register_implementations(self) -> None:
        """Register all tool implementations."""
        try:
            from cortex.mcp.tools import register_all_tools
            count = register_all_tools(self)
            self.logger.info(f"Registered {count} internal tool implementations for {len(self._tools)} public tools")
        except ImportError as e:
            self.logger.warning(f"Could not import tool implementations: {e}")
        except Exception as e:
            self.logger.error(f"Failed to register implementations: {e}")
    
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
            List of tool definitions in MCP format with category and operations
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
                "category": metadata.category.value,  # Include category
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            
            # Include operations for consolidated tools
            if metadata.operations:
                schema["operations"] = metadata.operations
            
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
