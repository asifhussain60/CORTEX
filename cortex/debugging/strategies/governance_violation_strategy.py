"""
Governance Violation Marker Injection Strategy

Locates governance violation locations and injects markers.

Strategy:
    1. Parse governance violation details from event
    2. Identify violation location (file + line)
    3. Inject marker at violation site

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Stage 2

AC-ID: AC-WAVE-R-S2-006
"""

from typing import List

from cortex.debugging.strategies.base import AbstractInjectionStrategy, MarkerContext


class GovernanceViolationStrategy(AbstractInjectionStrategy):
    """
    Strategy for injecting markers on governance violations.
    
    Uses violation metadata to locate injection points.
    """
    
    def analyze(self, context: MarkerContext) -> List[int]:
        """
        Analyze governance violation context to find marker injection point.
        
        Args:
            context: MarkerContext with rule_id and violation_details
        
        Returns:
            List containing single line number (violation location)
        """
        # For governance violations, line_number should be provided in context
        if context.line_number > 0:
            return [context.line_number]
        
        # Fallback: Try to extract from additional_context
        violation_line = context.additional_context.get("violation_line", 0)
        if violation_line > 0:
            return [violation_line]
        
        return []
    
    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """
        Format governance violation marker.
        
        Args:
            context: MarkerContext
            line_number: Target line number
        
        Returns:
            Formatted marker string
        """
        rule_id = context.additional_context.get("rule_id", "unknown")
        rule_name = context.additional_context.get("rule_name", "")
        timestamp = context.additional_context.get("timestamp", "")
        
        marker = (
            f"CORTEX_DEBUG[{context.session_id}]: GOVERNANCE_VIOLATION at line {line_number} | "
            f"rule={rule_id} ({rule_name}) | time={timestamp}"
        )
        
        return marker
