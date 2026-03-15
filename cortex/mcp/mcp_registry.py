"""
MCP Tool Registry: Production Tool Definitions.

This module defines the COMPLETE set of production tools (36 tools).
No more, no fewer. Every tool serves a specific business capability.

Tool Count Strategy:
    - 98 tools (legacy) → 30 tools (v3, WAVE-101 consolidation)
    - Removed deprecated tools: cortex_process_request, cortex_lens
    - Removed cortex_check (ops absorbed into cortex_verify)
    - Removed cortex_total_recall (ops absorbed into cortex_tools_catalog)
    - Added cortex_scaffold_files, cortex_master_plan, cortex_brain_query (wired from orphan status)
    - Added cortex_content, cortex_ado (Phase 130-131 backport)
    - Added cortex_review (Phase 132 backport — CodeReviewOrchestrator)
    - Consolidation by business capability
    - Operation parameters instead of separate tools
    - Removal of dev-only tools
    - Elimination of duplicates
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type
import logging

from cortex.mcp.mcp_tool_base import Tool, ToolCategory, ToolParameter


LEGACY_MEGATOOL_ALIASES: Dict[str, Dict[str, str]] = {
    "cortex_implement": {"tool": "cortex_code", "op": "implement"},
    "cortex_fix": {"tool": "cortex_code", "op": "fix"},
    "cortex_test": {"tool": "cortex_code", "op": "test"},
    "cortex_audit": {"tool": "cortex_govern", "op": "audit"},
    "cortex_health": {"tool": "cortex_govern", "op": "health"},
    "cortex_enforce": {"tool": "cortex_govern", "op": "enforce"},
    "cortex_investigate": {"tool": "cortex_analyze", "op": "investigate"},
    "cortex_architecture": {"tool": "cortex_analyze", "op": "architecture"},
    "cortex_complexity": {"tool": "cortex_analyze", "op": "complexity"},
    "cortex_phase": {"tool": "cortex_plan", "op": "phase"},
    "cortex_track": {"tool": "cortex_plan", "op": "track"},
    "cortex_decompose": {"tool": "cortex_plan", "op": "decompose"},
    "cortex_totalrecall": {"tool": "cortex_plan", "op": "totalrecall"},
    "cortex_feedback": {"tool": "cortex_learn", "op": "feedback"},
    "cortex_digest": {"tool": "cortex_learn", "op": "digest"},
    "cortex_distill": {"tool": "cortex_learn", "op": "distill"},
    "cortex_sync": {"tool": "cortex_ops", "op": "sync"},
    "cortex_upgrade": {"tool": "cortex_ops", "op": "upgrade"},
    "cortex_setup": {"tool": "cortex_ops", "op": "setup"},
    "cortex_status": {"tool": "cortex_ops", "op": "status"},
}


# ============================================================================
# PRODUCTION TOOL DEFINITIONS (36 Tools — WAVE-101 + Phase 130-132 backport)
# Removed: cortex_process_request (deprecated), cortex_lens (deleted per architect spec)
#          cortex_check (ops merged into cortex_verify)
#          cortex_total_recall (ops merged into cortex_tools_catalog)
# Added:   cortex_scaffold_files, cortex_master_plan, cortex_brain_query
#          cortex_content, cortex_ado (Phase 130-131)
#          cortex_review (Phase 132 — CodeReviewOrchestrator 6-stage pipeline)
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
    "cortex_registry": {
        "description": (
            "Registry intelligence: query governance rules, workflow templates, "
            "patterns, plans, and the full cortex-registry/ index. "
            "op: query_governance | query_workflows | query_patterns | "
            "query_plans | registry_index."
        ),
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {
                "name": "op",
                "type": "string",
                "required": True,
                "enum": [
                    "query_governance",
                    "query_workflows",
                    "query_patterns",
                    "query_plans",
                    "registry_index",
                ],
                "description": "Registry operation",
            },
            {
                "name": "filter",
                "type": "string",
                "required": False,
                "description": (
                    "Optional filter: severity for governance, category for workflows, "
                    "tag for patterns, status for plans, domain for registry_index."
                ),
            },
        ],
        "operations": [
            "query_governance",
            "query_workflows",
            "query_patterns",
            "query_plans",
            "registry_index",
        ],
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
        "description": "Unified planning operations: plan, phase, track, decompose, totalrecall.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "op", "type": "string", "required": False, "enum": ["plan", "phase", "track", "decompose", "totalrecall"], "description": "Plan operation"},
            {"name": "operation", "type": "string", "required": False, "enum": ["plan", "phase", "track", "decompose", "totalrecall"], "description": "Alias of op"},
            {"name": "phase_id", "type": "string", "required": False, "description": "Phase identifier"},
            {"name": "target", "type": "string", "required": False, "description": "Target path"},
            {"name": "options", "type": "object", "required": False, "description": "Operation options"},
        ],
        "operations": ["plan", "phase", "track", "decompose", "totalrecall"],
    },
    "cortex_code": {
        "description": "Unified code operations: implement, fix, refactor, review, test, debug.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "op", "type": "string", "required": False, "enum": ["implement", "fix", "refactor", "review", "test", "debug"], "description": "Code operation"},
            {"name": "operation", "type": "string", "required": False, "enum": ["implement", "fix", "refactor", "review", "test", "debug"], "description": "Alias of op"},
            {"name": "target", "type": "string", "required": False, "description": "Target path or symbol"},
            {"name": "request", "type": "string", "required": False, "description": "Request payload"},
        ],
        "operations": ["implement", "fix", "refactor", "review", "test", "debug"],
    },
    "cortex_govern": {
        "description": "Unified governance operations: audit, health, enforce, vacuum.",
        "category": ToolCategory.GOVERNANCE,
        "parameters": [
            {"name": "op", "type": "string", "required": False, "enum": ["audit", "health", "enforce", "vacuum"], "description": "Governance operation"},
            {"name": "operation", "type": "string", "required": False, "enum": ["audit", "health", "enforce", "vacuum"], "description": "Alias of op"},
            {"name": "target", "type": "string", "required": False, "description": "Target path"},
        ],
        "operations": ["audit", "health", "enforce", "vacuum"],
    },
    "cortex_analyze": {
        "description": "Unified analysis operations: lens, investigate, architecture, complexity.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "op", "type": "string", "required": False, "enum": ["lens", "investigate", "architecture", "complexity"], "description": "Analysis operation"},
            {"name": "operation", "type": "string", "required": False, "enum": ["lens", "investigate", "architecture", "complexity"], "description": "Alias of op"},
            {"name": "target", "type": "string", "required": False, "description": "Target path"},
            {"name": "query", "type": "string", "required": False, "description": "Query payload"},
        ],
        "operations": ["lens", "investigate", "architecture", "complexity"],
    },
    "cortex_learn": {
        "description": "Unified learning operations: rca, feedback, digest, distill, onboard.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "op", "type": "string", "required": False, "enum": ["rca", "feedback", "digest", "distill", "onboard"], "description": "Learning operation"},
            {"name": "operation", "type": "string", "required": False, "enum": ["rca", "feedback", "digest", "distill", "onboard"], "description": "Alias of op"},
            {"name": "target", "type": "string", "required": False, "description": "Target path or ID"},
            {"name": "data", "type": "object", "required": False, "description": "Operation payload"},
        ],
        "operations": ["rca", "feedback", "digest", "distill", "onboard"],
    },
    "cortex_ops": {
        "description": "Unified operations: sync, upgrade, setup, status.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "op", "type": "string", "required": False, "enum": ["sync", "upgrade", "setup", "status"], "description": "Ops operation"},
            {"name": "operation", "type": "string", "required": False, "enum": ["sync", "upgrade", "setup", "status"], "description": "Alias of op"},
            {"name": "target", "type": "string", "required": False, "description": "Target path or service"},
            {"name": "options", "type": "object", "required": False, "description": "Operation options"},
        ],
        "operations": ["sync", "upgrade", "setup", "status"],
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
    # TIER 5: UTILITIES (8 tools — WAVE-101 consolidation)
    # Removed: cortex_check (ops absorbed into cortex_verify)
    #          cortex_total_recall (ops absorbed into cortex_tools_catalog)
    # Added:   cortex_scaffold_files, cortex_master_plan, cortex_brain_query
    # =========================================================================
    "cortex_verify": {
        "description": (
            "Verification and system checks (consolidated). "
            "Ops: environment, claim, mcp — plus — dependencies, status, health, orchestrator_health "
            "(formerly cortex_check)."
        ),
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True,
             "enum": ["environment", "claim", "mcp", "dependencies", "status", "health", "orchestrator_health"],
             "description": "Verification / check operation"},
            {"name": "target", "type": "string", "required": False,
             "description": "Target for verification (claim text, config path)"},
            {"name": "auto_fix", "type": "boolean", "required": False,
             "description": "Attempt auto-fix for environment issues"},
            {"name": "operation_id", "type": "string", "required": False,
             "description": "Operation ID for status check"},
            {"name": "orchestrator", "type": "string", "required": False,
             "description": "Specific orchestrator name for health check"},
            {"name": "parallel", "type": "boolean", "required": False,
             "description": "Check all orchestrators in parallel (default: true)"},
        ],
        "operations": ["environment", "claim", "mcp", "dependencies", "status", "health", "orchestrator_health"],
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
        "description": (
            "Discover MCP tools and recall CORTEX features (consolidated). "
            "Catalog ops: list, search, describe, categories. "
            "Feature recall ops: discover, recall (formerly cortex_total_recall)."
        ),
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "operation", "type": "string", "required": True,
             "enum": ["list", "search", "describe", "categories", "discover", "recall"],
             "description": "Catalog or recall operation"},
            {"name": "query", "type": "string", "required": False,
             "description": "Search query, tool name, or feature name"},
            {"name": "category", "type": "string", "required": False,
             "description": "Filter by category"},
        ],
        "operations": ["list", "search", "describe", "categories", "discover", "recall"],
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
    "cortex_scaffold_files": {
        "description": "File scaffolding operations: write new files from templates, check existence, list scaffolded artefacts.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True,
             "enum": ["write", "check", "list"],
             "description": "Scaffold operation"},
            {"name": "path", "type": "string", "required": False, "description": "Target file path"},
            {"name": "content", "type": "string", "required": False, "description": "File content to write"},
            {"name": "template", "type": "string", "required": False, "description": "Template name to use"},
        ],
        "operations": ["write", "check", "list"],
    },
    "cortex_master_plan": {
        "description": "Master plan operations: create, query, update, and sync phase planning documents.",
        "category": ToolCategory.OPERATIONS,
        "parameters": [
            {"name": "operation", "type": "string", "required": True,
             "enum": ["create", "query", "update", "sync"],
             "description": "Plan operation"},
            {"name": "phase_id", "type": "string", "required": False, "description": "Phase ID to query or update"},
            {"name": "data", "type": "object", "required": False, "description": "Phase data for create/update"},
        ],
        "operations": ["create", "query", "update", "sync"],
    },
    "cortex_brain_query": {
        "description": "CORTEX brain / reinforcement signal operations: query, history, decay, promote.",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True,
             "enum": ["query", "history", "decay", "promote"],
             "description": "Brain operation"},
            {"name": "signal_id", "type": "string", "required": False, "description": "Signal or pattern ID"},
            {"name": "data", "type": "object", "required": False, "description": "Signal payload"},
        ],
        "operations": ["query", "history", "decay", "promote"],
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
    "cortex_learning": {
        "description": "Unified Reinforcement Signal (URS) — closed-loop learning + Phase 87 RCA Memory Engine. Emit signals, query history, manage decay/promotion/quarantine, run root cause analysis across 4 methodologies (Five-Whys, Fishbone, Fault-Tree, Causal-Chain).",
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "operation", "type": "string", "required": True, "enum": ["emit", "history", "decay", "promote", "quarantine", "metrics", "rca"], "description": "Learning operation — 'rca' runs Phase 87 Root Cause Analysis"},
            {"name": "signal_type", "type": "string", "required": False, "description": "URS signal type (emit/promote/quarantine)"},
            {"name": "data", "type": "object", "required": False, "description": "Signal payload or RCA parameters (failure_description, category, methodology)"},
            {"name": "rca_action", "type": "string", "required": False, "enum": ["analyze", "query", "list"], "description": "RCA sub-action when operation='rca'"},
            {"name": "rca_id", "type": "string", "required": False, "description": "RCA analysis ID for query operations"},
        ],
        "operations": ["emit", "history", "decay", "promote", "quarantine", "metrics", "rca"],
    },
    "cortex_distill": {
        "description": (
            "Distil a multi-turn conversation into an executable, context-dense prompt. "
            "Runs a 5-stage pipeline: segment → reconstruct → reconcile → synthesise → compress. "
            "Eliminates noise, preserves goals, decisions, and constraints. Phase 129."
        ),
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "conversation", "type": "string", "required": True,
             "description": "Raw multi-turn conversation text to distil."},
            {"name": "orchestrator_context", "type": "string", "required": False,
             "description": "Optional orchestrator context for governance routing."},
        ],
        "operations": ["distill"],
    },
    "cortex_optimize": {
        "description": (
            "Optimize arrays of files (HTML, Markdown, YAML, JSON, TXT, chat transcripts) "
            "by removing noise and compressing content. Runs a 5-stage pipeline: "
            "classify → read → optimize → validate → write. Overwrites files in-place. Phase 130."
        ),
        "category": ToolCategory.UTILITIES,
        "parameters": [
            {"name": "file_paths", "type": "array", "required": True,
             "description": "Array of absolute file paths to optimize. Files are overwritten in-place."},
            {"name": "orchestrator_context", "type": "string", "required": False,
             "description": "Optional orchestrator context for governance routing."},
        ],
        "operations": ["optimize"],
    },
    # Phase 130-c: Content Library Engine — epoch-shuffled anti-repetition pool management
    "cortex_content": {
        "description": (
            "Manage CORTEX response content pools (quotes, principles, ai_sparks) "
            "with epoch-based anti-repetition guarantee (Fisher-Yates shuffle per epoch). "
            "Provides MCP control surface for ContentLibraryEngine. Phase 130."
        ),
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "op", "type": "string", "required": True,
             "enum": ["select", "history", "reset", "stats"],
             "description": "Operation: select (draw next item), history (recent draws), reset (epoch 0), stats (pool info)"},
            {"name": "pool", "type": "string", "required": False,
             "description": "Pool name: quotes | principles | ai_sparks (default: quotes). Comma-separated for select_across()."},
        ],
        "operations": ["select", "history", "reset", "stats"],
    },
    "cortex_ado": {
        "description": (
            "Azure DevOps context operations — fetch and synthesize work items "
            "within an 8000-char budget. "
            "Operations: get_story | get_full | get_tests | search | health. Phase 131."
        ),
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "op", "type": "string", "required": True,
             "enum": ["get_story", "get_full", "get_tests", "search", "health"],
             "description": "ADO operation"},
            {"name": "work_item_id", "type": "integer", "required": False,
             "description": "ADO work item ID (required for get_story, get_full, get_tests)"},
            {"name": "query", "type": "string", "required": False,
             "description": "Search query string (required for search)"},
            {"name": "project", "type": "string", "required": False,
             "description": "ADO project name (uses ADO_PROJECT env var if omitted)"},
        ],
        "operations": ["get_story", "get_full", "get_tests", "search", "health"],
    },
    # Phase 132-b: Code Review Orchestrator — 6-stage OWASP-aligned review pipeline
    "cortex_review": {
        "description": (
            "PR code review pipeline — 6-stage OWASP-aligned analysis producing "
            "APPROVE / REQUEST_CHANGES / BLOCK verdict with structured P0–P3 findings. "
            "Operations: review | findings | history | patterns | health. Phase 132."
        ),
        "category": ToolCategory.INTELLIGENCE,
        "parameters": [
            {"name": "op", "type": "string", "required": True,
             "enum": ["review", "findings", "history", "patterns", "health"],
             "description": "Operation: review | findings | history | patterns | health"},
            {"name": "diff", "type": "string", "required": False,
             "description": "Unified diff text of the PR (required for review)"},
            {"name": "pr_title", "type": "string", "required": False,
             "description": "Pull request title (optional context)"},
            {"name": "author", "type": "string", "required": False,
             "description": "PR author name (optional context)"},
        ],
        "operations": ["review", "findings", "history", "patterns", "health"],
    },
}


@dataclass
class ToolMetadata:  # CORE-035-scoped — domain-specific tool descriptor — different registry formats
    """
    Runtime metadata for a registered tool.
    """
    id: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    operations: List[str]
    version: str = "1.0"
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


def resolve_legacy_tool_alias(tool_name: str, params: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Resolve legacy tool names to mega-tool equivalents.

    Returns the original tool/params when no alias applies.
    """
    alias = LEGACY_MEGATOOL_ALIASES.get(tool_name)
    if not alias:
        return tool_name, params

    resolved_params = dict(params)
    resolved_params.setdefault("op", alias["op"])
    return alias["tool"], resolved_params
