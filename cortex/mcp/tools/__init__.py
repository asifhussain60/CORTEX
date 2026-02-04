"""
CORTEX MCP Tools Registry
Model Context Protocol tools for enhanced capabilities.

Available Tools:
- intelligent_git_merge: Intelligent merging with cortex_brain preservation
- lens_tools: LENS analysis tools (git, AST, comments, duplicates) - UNIFIED in cortex.lens
- intelligent_lens_tools: Tiered LENS with LLM enhancement (NEW)
- onboarding_tools: Repository onboarding and config analysis (LENS v2.0)
- dashboard_aggregator_v3_tool: Dashboard v3 JSON generation + HTTP serving + E2E tests (PHASE-21)

LENS CONSOLIDATION (2026-02-02):
All LENS analyzers consolidated in cortex.lens package:
- cortex.lens.analyzers: ASTAnalyzer, GitHistoryAnalyzer, CommentExtractor, etc.
- cortex.lens.discovery: ConfigurationDiscovery, DatabaseDiscovery
- cortex.lens.orchestrator: LENSOrchestrator (unified analysis)
MCP tools import from cortex.lens (thin wrappers)

DASHBOARD V3 (PHASE-21):
JSON-first dashboard with dual-format support (JSON + SQLite):
- cortex_aggregate_dashboard_data_v3: Generate dashboard-data.json
- cortex_serve_dashboard: HTTP server for local viewing
- cortex_test_dashboard_e2e: Playwright browser E2E tests
"""

# Core MCP Tools
from .intelligent_git_merge import IntelligentGitMergeTool, create_intelligent_merge_mcp_tool

# LENS Analysis Tools (ARCH-007)
from .lens_tools import (
    cortex_lens_analyze,
    cortex_git_history,
    cortex_ast_analyze,
    cortex_extract_comments,
    cortex_detect_duplicates,
    cortex_tools_catalog,
)

# Intelligent LENS Tools with LLM (AC-LENS-LLM-004)
from .intelligent_lens_tools import (
    cortex_lens_deep_analyze,
)

# Onboarding Tools (LENS v2.0 - AC-LENS-V2-ONBOARD-001)
from .onboarding_tools import (
    cortex_onboard_repository,
    cortex_analyze_config,
    cortex_analyze_repository_configs,
)

# Dashboard Tools v3 (PHASE-21)
# TODO: Implement dashboard_aggregator_v3_tool.py
# from .dashboard_aggregator_v3_tool import (
#     cortex_aggregate_dashboard_data_v3,
#     cortex_serve_dashboard,
#     cortex_test_dashboard_e2e,
# )

# Vacuum Tools (Markdown Cleanup - CORE-002)
from .vacuum_tools import (
    cortex_vacuum,
)

# Educational Tools (Phase 22 - ASK Mode)
from .cortex_ask import (
    cortex_ask,
)
from .cortex_verify_claim import (
    cortex_verify_claim,
)

__all__ = [
    # Git Merge
    "IntelligentGitMergeTool",
    "create_intelligent_merge_mcp_tool",
    # LENS Tools
    "cortex_lens_analyze",
    "cortex_git_history",
    "cortex_ast_analyze",
    "cortex_extract_comments",
    "cortex_detect_duplicates",
    "cortex_tools_catalog",
    # Intelligent LENS Tools (LLM-enhanced)
    "cortex_lens_deep_analyze",
    # Onboarding Tools
    "cortex_onboard_repository",
    "cortex_analyze_config",
    "cortex_analyze_repository_configs",
    # Dashboard Tools v3
    # "cortex_aggregate_dashboard_data_v3",  # TODO: Implement
    # "cortex_serve_dashboard",  # TODO: Implement
    # "cortex_test_dashboard_e2e",  # TODO: Implement
    # Vacuum Tools
    "cortex_vacuum",
    # Educational Tools (Phase 22)
    "cortex_ask",
    "cortex_verify_claim",
]

# MCP Tool Registry for discovery
MCP_TOOLS = {
    "intelligent_git_merge": {
        "class": IntelligentGitMergeTool,
        "factory": create_intelligent_merge_mcp_tool,
        "description": "Intelligent git merging with cortex_brain preservation",
        "category": "integration",
        "features": ["local_favoring_merge", "cortex_brain_protection", "automatic_backup"]
    },
    # LENS Analysis Tools (ARCH-007: MCP-first)
    "cortex_lens_analyze": {
        "function": cortex_lens_analyze,
        "description": "Unified LENS code intelligence analysis",
        "category": "analysis",
        "features": ["git_analysis", "ast_analysis", "comment_extraction"]
    },
    # Intelligent LENS Tools (AC-LENS-LLM-004: LLM-enhanced tiered analysis)
    "cortex_lens_deep_analyze": {
        "function": cortex_lens_deep_analyze,
        "description": "Intelligent tiered LENS analysis with optional LLM enhancement and company domain context",
        "category": "analysis",
        "features": [
            "tiered_analysis",
            "llm_enhancement",
            "company_domain_context",
            "pii_sanitization",
            "token_budget_management",
            "natural_language_triggers"
        ]
    },
    # Onboarding Tools (LENS v2.0)
    "cortex_onboard_repository": {
        "function": cortex_onboard_repository,
        "description": "Onboard repository with holistic LENS analysis + security assessment",
        "category": "onboarding",
        "features": ["multi_layer_analysis", "security_threat_modeling", "dashboard_generation"]
    },
    "cortex_analyze_config": {
        "function": cortex_analyze_config,
        "description": "Analyze configuration file for security issues",
        "category": "security",
        "features": ["secret_detection", "insecure_defaults", "compliance_check"]
    },
    "cortex_analyze_repository_configs": {
        "function": cortex_analyze_repository_configs,
        "description": "Analyze all config files in repository",
        "category": "security",
        "features": ["repository_scan", "aggregated_findings", "p0_p1_p2_classification"]
    },
    "cortex_git_history": {
        "function": cortex_git_history,
        "description": "Git history analysis (24h context, blame, patterns)",
        "category": "analysis",
        "features": ["commit_history", "blame", "pattern_detection"]
    },
    "cortex_ast_analyze": {
        "function": cortex_ast_analyze,
        "description": "AST structure, complexity, dead code analysis",
        "category": "analysis",
        "features": ["structure", "complexity", "dead_code"]
    },
    "cortex_extract_comments": {
        "function": cortex_extract_comments,
        "description": "Extract TODOs, FIXMEs, docstrings",
        "category": "analysis",
        "features": ["todos", "fixmes", "docstrings"]
    },
    "cortex_detect_duplicates": {
        "function": cortex_detect_duplicates,
        "description": "CORE-035 duplicate detection",
        "category": "governance",
        "features": ["duplicate_detection", "canonical_location"]
    },
    "cortex_tools_catalog": {
        "function": cortex_tools_catalog,
        "description": "Discover all MCP tools",
        "category": "discovery",
        "features": ["tool_listing", "category_filter"]
    },
    # Dashboard Tools v3 (PHASE-21: JSON-first SPA) - NOT YET IMPLEMENTED
    # "cortex_aggregate_dashboard_data_v3": {
    #     "function": cortex_aggregate_dashboard_data_v3,
    #     "description": "Generate dashboard-data.json (v3 schema) for repository intelligence SPA",
    #     "category": "dashboard",
    #     "features": ["json_generation", "pydantic_validation", "13_tab_schema", "dual_format_ready"]
    # },
    # "cortex_serve_dashboard": {
    #     "function": cortex_serve_dashboard,
    #     "description": "Serve dashboard SPA via HTTP (Python http.server)",
    #     "category": "dashboard",
    #     "features": ["http_server", "local_viewing", "background_process"]
    # },
    # "cortex_test_dashboard_e2e": {
    #     "function": cortex_test_dashboard_e2e,
    #     "description": "Run Playwright E2E tests for dashboard browser validation",
    #     "category": "testing",
    #     "features": ["playwright", "browser_e2e", "ui_validation", "console_error_detection"]
    # },
    # Vacuum Tool (CORE-002: Markdown cleanup)
    "cortex_vacuum": {
        "category": "governance",
        "features": ["duplicate_detection", "canonical_location"]
    },
    "cortex_tools_catalog": {
        "function": cortex_tools_catalog,
        "description": "Discover all MCP tools",
        "category": "discovery",
        "features": ["tool_listing", "category_filter"]
    },
    # Vacuum Tool (CORE-002: Markdown cleanup)
    "cortex_vacuum": {
        "function": cortex_vacuum,
        "description": "Markdown cleanup with post-cleanup validation workflow",
        "category": "maintenance",
        "features": ["markdown_cleanup", "file_archival", "verification", "audit_offering"]
    },
}
