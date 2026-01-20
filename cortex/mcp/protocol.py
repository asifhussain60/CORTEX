"""MCP Protocol

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class MCPRequest:
    """MCP request."""
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None

@dataclass
class MCPResponse:
    """MCP response."""
    result: Any = None
    error: Optional[str] = None
    id: Optional[str] = None

__all__ = ["MCPRequest", "MCPResponse"]
