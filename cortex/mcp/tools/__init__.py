"""
CORTEX MCP Tools Registry
Model Context Protocol tools for enhanced capabilities.

Available Tools:
- intelligent_git_merge: Intelligent merging with cortex_brain preservation
"""

# Core MCP Tools
from .intelligent_git_merge import IntelligentGitMergeTool, create_intelligent_merge_mcp_tool

__all__ = [
    "IntelligentGitMergeTool",
    "create_intelligent_merge_mcp_tool"
]

# MCP Tool Registry for discovery
MCP_TOOLS = {
    "intelligent_git_merge": {
        "class": IntelligentGitMergeTool,
        "factory": create_intelligent_merge_mcp_tool,
        "description": "Intelligent git merging with cortex_brain preservation",
        "category": "integration",
        "features": ["local_favoring_merge", "cortex_brain_protection", "automatic_backup"]
    }
}
