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

__all__ = ["ToolEntry"]
