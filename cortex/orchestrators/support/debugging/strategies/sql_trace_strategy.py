"""
Phase 86 — SqlTraceStrategy
Injects SQL comment trace markers for SQL Server, Oracle, and PostgreSQL
debugging sessions.  Markers are legal SQL comments that survive query parsing.

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case filename
CORE-035: Single canonical implementation
"""

from __future__ import annotations

from typing import List

from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import (
    AbstractInjectionStrategy,
    InjectionResult,
    MarkerContext,
)


class SqlTraceStrategy(AbstractInjectionStrategy):
    """Inject SQL comment CORTEX_DEBUG markers for SQL debugging sessions.

    Generates ANSI-compatible ``-- CORTEX_DEBUG`` comments that are safe
    for SQL Server, Oracle, PostgreSQL, and SQLite.  Also supports block
    comment style ``/* ... */`` for stored procedure headers.
    """

    def analyze(self, context: MarkerContext) -> List[int]:
        """Determine injection lines in a SQL file.

        Targets the line immediately before the reported line_number so
        the marker appears before the statement being investigated.

        Args:
            context: MarkerContext with file_path and line_number.

        Returns:
            A list of line numbers for marker injection.
        """
        line = max(1, context.line_number - 1)
        return [line, context.line_number]

    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """Format an ANSI SQL comment CORTEX_DEBUG marker.

        Args:
            context: MarkerContext providing session_id and trigger_type.
            line_number: The line where the marker will be inserted.

        Returns:
            A SQL line comment string suitable for any ANSI-compatible engine.
        """
        return (
            f"-- CORTEX_DEBUG: session={context.session_id} "
            f"line={line_number} trigger={context.trigger_type} "
            f"file={context.file_path} -- remove before release"
        )
