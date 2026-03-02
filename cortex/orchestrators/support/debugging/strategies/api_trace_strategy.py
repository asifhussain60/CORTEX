"""
Phase 86 — ApiTraceStrategy
Injects HTTP request/response trace markers for REST, GraphQL, and gRPC APIs.
Supports Python (Flask/FastAPI/Django), Node.js (Express), and generic middleware.

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case filename
CORE-035: Single canonical implementation
"""

from __future__ import annotations

from typing import List

from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import (
    AbstractInjectionStrategy,
    MarkerContext,
)


class ApiTraceStrategy(AbstractInjectionStrategy):
    """Inject HTTP trace markers at API handler entry/exit points.

    Targets route handlers, middleware functions, and service boundaries.
    Marker includes request method, path, session_id, and timing anchor
    for correlating API failures with trace data.
    """

    def analyze(self, context: MarkerContext) -> List[int]:
        """Determine injection lines for an API handler file.

        Targets the reported line_number (typically the first line of the
        handler function body) and adds a second anchor at line+1 for
        capturing the response exit point.

        Args:
            context: MarkerContext with file_path and line_number.

        Returns:
            A list of line numbers for marker injection.
        """
        line = context.line_number
        return [line, line + 1]

    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """Format an API trace CORTEX_DEBUG marker.

        Args:
            context: MarkerContext providing session_id and trigger_type.
            line_number: The line where the marker will be inserted.

        Returns:
            A Python-style comment or logger call for the API trace marker.
        """
        return (
            f"# CORTEX_DEBUG_API_TRACE: session={context.session_id} "
            f"line={line_number} trigger={context.trigger_type} "
            f"file={context.file_path}  # remove before commit\n"
            f"# cortex_trace_request(session='{context.session_id}', "
            f"line={line_number})  # CORTEX_DEBUG"
        )
