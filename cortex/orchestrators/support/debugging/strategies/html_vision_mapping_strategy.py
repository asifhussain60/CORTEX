"""
Phase 86 — HtmlVisionMappingStrategy
Injects data-cortex-debug attributes into HTML elements for Vision API
bounding-box → DOM element mapping during visual debugging sessions.

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


class HtmlVisionMappingStrategy(AbstractInjectionStrategy):
    """Inject data-cortex-debug attributes into HTML for Vision API mapping.

    Adds ``data-cortex-debug="SESSION:{session_id}:LINE:{line}"`` to HTML
    elements so the Vision API can correlate screenshot bounding boxes with
    specific DOM nodes during visual regression debugging.
    """

    def analyze(self, context: MarkerContext) -> List[int]:
        """Identify injection lines in the HTML file.

        Targets the reported line_number where an opening HTML tag is expected.

        Args:
            context: MarkerContext with file_path and line_number.

        Returns:
            A list of line numbers for marker injection.
        """
        return [context.line_number]

    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """Format a data-cortex-debug HTML attribute injection marker.

        The injected comment placed immediately before the target element
        provides a Vision API anchor point tied to the debug session.

        Args:
            context: MarkerContext providing session_id and trigger_type.
            line_number: The line where the attribute will be injected.

        Returns:
            An HTML comment + data-attribute marker string.
        """
        return (
            f"<!-- CORTEX_DEBUG:{context.session_id}:{line_number} "
            f"trigger={context.trigger_type} vision-anchor=true -->"
            f"\n<!-- data-cortex-debug=\"session:{context.session_id}:line:{line_number}\" -->"
        )
