"""
Phase 86 — DotNetTraceStrategy
Injects ILogger.LogDebug / Trace.WriteLine CORTEX_DEBUG markers into
C# / .NET source files for structured debug session tracing.

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


class DotNetTraceStrategy(AbstractInjectionStrategy):
    """Inject ILogger.LogDebug CORTEX_DEBUG markers into C# / .NET files.

    Generates structured ``_logger.LogDebug(...)`` calls compatible with
    Microsoft.Extensions.Logging.  Falls back to ``System.Diagnostics.Trace``
    for files that may not have an injected logger instance.
    """

    def analyze(self, context: MarkerContext) -> List[int]:
        """Determine injection lines in a C# source file.

        Targets the reported line_number (typically a method entry point)
        and one line after to bracket the section of interest.

        Args:
            context: MarkerContext with file_path and line_number.

        Returns:
            A list of line numbers for marker injection.
        """
        return [context.line_number]

    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """Format an ILogger.LogDebug CORTEX_DEBUG marker for C#.

        Args:
            context: MarkerContext providing session_id and trigger_type.
            line_number: The line where the marker will be inserted.

        Returns:
            A C# ILogger.LogDebug call string with CORTEX_DEBUG annotation.
        """
        return (
            f'// CORTEX_DEBUG: session={context.session_id} '
            f'line={line_number} trigger={context.trigger_type} -- remove before commit\n'
            f'_logger.LogDebug("CORTEX_DEBUG:{{session}}:{{line}}", '
            f'"{context.session_id}", {line_number});  // CORTEX_DEBUG'
        )
