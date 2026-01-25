"""
CORTEX MCP Tools Registry
Model Context Protocol tools for enhanced capabilities.

Available Tools:
- git_history_analyzer: Analyze git changes for governance tracking
- intelligent_git_merge: Intelligent merging with cortex_brain preservation
"""

# Core MCP Tools
from .git_history_analyzer import GitHistoryAnalyzer
from .intelligent_git_merge import IntelligentGitMergeTool, create_intelligent_merge_mcp_tool

__all__ = [
    "GitHistoryAnalyzer",
    "IntelligentGitMergeTool",
    "create_intelligent_merge_mcp_tool"
]

# MCP Tool Registry for discovery
MCP_TOOLS = {
    "git_history_analyzer": {
        "class": GitHistoryAnalyzer,
        "description": "Analyze git changes affecting CORTEX system state",
        "category": "governance"
    },
    "intelligent_git_merge": {
        "class": IntelligentGitMergeTool,
        "factory": create_intelligent_merge_mcp_tool,
        "description": "Intelligent git merging with cortex_brain preservation",
        "category": "integration",
        "features": ["local_favoring_merge", "cortex_brain_protection", "automatic_backup"]
    }
}
