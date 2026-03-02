"""
Phase 86 — FrontendConsoleStrategy
Injects console.log / console.debug CORTEX_DEBUG markers into JS/TS/JSX/TSX/Vue files.

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

_FRONTEND_EXTENSIONS = {".js", ".ts", ".jsx", ".tsx", ".vue", ".mjs", ".cjs"}


class FrontendConsoleStrategy(AbstractInjectionStrategy):
    """Inject console.log CORTEX_DEBUG markers into frontend JS/TS/Vue files.

    Supports: JavaScript, TypeScript, JSX, TSX, Vue SFC, ESM (.mjs/.cjs).
    Marker format: console.debug('[CORTEX_DEBUG:{session_id}:{line}]', ...)
    """

    def analyze(self, context: MarkerContext) -> List[int]:
        """Determine injection lines for a frontend file.

        Targets the reported line_number and the line immediately before it
        so the marker appears at the point of interest.

        Args:
            context: MarkerContext containing file_path and line_number.

        Returns:
            A list of line numbers where markers should be injected.
        """
        line = context.line_number
        # Inject at the target line; also one line prior if there's room
        lines = [line]
        if line > 1:
            lines = [line - 1] + lines
        return lines

    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """Format a console.debug CORTEX_DEBUG marker for the given line.

        Args:
            context: MarkerContext providing session_id and trigger_type.
            line_number: The line where the marker will be inserted.

        Returns:
            A JavaScript console.debug statement as a string.
        """
        return (
            f"console.debug('[CORTEX_DEBUG:{context.session_id}:{line_number}]', "
            f"{{ trigger: '{context.trigger_type}', file: '{context.file_path}', "
            f"line: {line_number} }});  // CORTEX_DEBUG — remove before commit"
        )
