"""
CORTEX Entry Point Package

Provides unified interface for all CORTEX interactions.

Main Components:
- CortexEntry: Main entry point coordinator
- RequestParser: Natural language → AgentRequest
- ResponseFormatter: AgentResponse → user-friendly output

Usage:
    from CORTEX.src.entry_point import CortexEntry
    
    cortex = CortexEntry()
    response = cortex.process("Add tests for auth.py")
    print(response)
"""

from .cortex_entry import CortexEntry
from .request_parser import RequestParser
from .response_formatter import ResponseFormatter

__all__ = [
    "CortexEntry",
    "RequestParser",
    "ResponseFormatter",
]
