"""Response orchestrators package.

Phase 53: Simplified response formatting.
Use simple_response_formatter for orchestrator responses.
"""

# Phase 53: Simple response formatter (replaces complex template system)
from .simple_response_formatter import format_response

__all__ = [
    "format_response",
]
