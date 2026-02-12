"""
CORTEX MCP v2: Consolidated Model Context Protocol Server.

This is the SINGLE entry point for ALL CORTEX functionality.
Every operation - implementation, analysis, governance, debugging -
flows through MCP tools.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    External Clients                         │
    │  (VS Code Copilot, CLI, REST API, CI/CD Pipelines)          │
    └───────────────────────┬─────────────────────────────────────┘
                            │ JSON-RPC 2.0 / stdio
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    MCP Server v2                             │
    │  ┌────────────────────────────────────────────────────────┐ │
    │  │ Tool Registry (24 Production Tools)                    │ │
    │  │  ├── Core: process_request, challenge                  │ │
    │  │  ├── Intelligence: lens, knowledge                     │ │
    │  │  ├── Governance: governance, validate                  │ │
    │  │  ├── Operations: debug, refactor, plan                 │ │
    │  │  └── Utilities: verify, vacuum, catalog                │ │
    │  └────────────────────────────────────────────────────────┘ │
    └───────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                 Orchestrator Layer                          │
    │  MasterOrchestrator → IntentRouter → Domain Orchestrators   │
    └─────────────────────────────────────────────────────────────┘

Design Principles:
    1. SINGLE ENTRY POINT: All functionality via MCP tools
    2. 24 TOOLS MAXIMUM: Consolidated by business capability
    3. CROSS-PLATFORM: Works on macOS, Windows, Linux
    4. EXTENSIBLE: New capabilities = new operations, not new tools
    5. TESTABLE: Every tool has comprehensive tests

Version: 2.0.0
"""

__version__ = "2.0.0"
__all__ = [
    "MCPServerV2",
    "Tool",
    "ToolDefinition",
    "ToolRegistry",
    "PRODUCTION_TOOLS",
]

from cortex.mcp.v2.server import MCPServerV2
from cortex.mcp.v2.registry import ToolRegistry, PRODUCTION_TOOLS
from cortex.mcp.v2.base import Tool, ToolDefinition
