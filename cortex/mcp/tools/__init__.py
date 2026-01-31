"""
CORTEX MCP Tools Registry
Model Context Protocol tools for enhanced capabilities.

Available Tools:
- intelligent_git_merge: Intelligent merging with cortex_brain preservation
- lens_tools: LENS analysis tools (git, AST, comments, duplicates)
- database_audit: SQLite integrity checks (ARCH-012)
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

# Database Audit Tool (ARCH-012)
from .database_audit import cortex_db_audit

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
    # Database Audit
    "cortex_db_audit",
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
    "cortex_db_audit": {
        "function": cortex_db_audit,
        "description": "SQLite database integrity audit (ARCH-012)",
        "category": "governance",
        "features": ["orphan_tables", "duplicate_detection", "stale_data"]
    },
}
