"""MCP Server SDK

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class MCPRequest:
    """MCP SDK request."""
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None

__all__ = ["MCPRequest"]
