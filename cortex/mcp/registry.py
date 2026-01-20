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
    
    def register(self, entry: ToolEntry) -> bool:
        """Register tool."""
        return True
    
    def get(self, tool_id: str) -> ToolEntry:
        """Get tool entry."""
        return ToolEntry(tool_id=tool_id, name=tool_id)

__all__ = ["ToolEntry", "ToolRegistry"]
