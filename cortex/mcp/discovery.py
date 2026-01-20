"""MCP Discovery

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import List

@dataclass
class ToolDiscovery:
    """Tool discovery service."""
    
    def discover(self) -> List[str]:
        """Discover available tools."""
        return []

__all__ = ["ToolDiscovery"]
