"""
types.py — MCP Type Definitions

Canonical type stubs for MCP tool inputs/outputs. Restored for
import compatibility after WAVE-100 consolidation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MCPRequest:
    """Represents an inbound MCP tool request."""

    tool: str
    operation: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPResponse:
    """Represents an outbound MCP tool response."""

    tool: str
    operation: str
    status: str = "ok"
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class MCPContext:
    """Orchestrator context passed through MCP tool invocations."""

    session_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
