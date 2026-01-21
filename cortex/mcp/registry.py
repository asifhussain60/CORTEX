"""MCP Registry (compatibility)

This redirects to the main registry module.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ToolEntry:
    """Tool registry entry."""
    tool_id: str
    name: str
    description: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ToolRegistry:
    """Tool registry."""
    
    def __init__(self):
        """Initialize tool registry."""
        self._tools: Dict[str, ToolEntry] = {}
    
    def register(self, entry: ToolEntry) -> bool:
        """Register tool entry."""
        self._tools[entry.tool_id] = entry
        return True
    
    def register_tool(
        self,
        tool_id: str,
        tool_name: str,
        description: str = "",
        parameters: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Register tool with detailed parameters.
        
        Args:
            tool_id: Unique tool identifier
            tool_name: Display name for the tool
            description: Tool description
            parameters: Tool parameters schema
            metadata: Additional tool metadata
            
        Returns:
            bool: True if registration successful
        """
        if metadata is None:
            metadata = {}
        
        if parameters:
            metadata["parameters"] = parameters
        
        entry = ToolEntry(
            tool_id=tool_id,
            name=tool_name,
            description=description,
            metadata=metadata
        )
        return self.register(entry)
    
    def get(self, tool_id: str) -> ToolEntry:
        """Get tool entry."""
        if tool_id in self._tools:
            return self._tools[tool_id]
        return ToolEntry(tool_id=tool_id, name=tool_id)


# Global registry instance
_GLOBAL_REGISTRY: ToolRegistry = None


def get_mcp_tool_registry() -> ToolRegistry:
    """
    Get the global MCP tool registry instance.
    
    Returns:
        ToolRegistry: Global tool registry singleton
    """
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = ToolRegistry()
    return _GLOBAL_REGISTRY


__all__ = ["ToolEntry", "ToolRegistry", "get_mcp_tool_registry"]
