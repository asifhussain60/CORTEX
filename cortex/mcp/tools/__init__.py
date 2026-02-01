"""
CORTEX MCP Tools Registry
Model Context Protocol tools for enhanced capabilities.

Available Tools:
- intelligent_git_merge: Intelligent merging with cortex_brain preservation
- lens_tools: LENS analysis tools (git, AST, comments, duplicates)
- intelligent_lens_tools: Tiered LENS with LLM enhancement (NEW)
- onboarding_tools: Repository onboarding and config analysis (LENS v2.0)
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
}
