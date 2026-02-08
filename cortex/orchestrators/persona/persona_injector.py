"""
PersonaInjector: Apply persona-specific formatting to responses
Authority: Phase 37 S2, CORE-008 (TDD-first)

Formats responses based on:
- Persona type (engineer, business_leader, etc.)
- Depth level (executive, standard, detailed, full)
- Content filtering (code visibility, metric selection)
- Word limits and presentation style
"""

from typing import Optional
import re

from cortex.orchestrators.persona.models import PersonaId, DepthLevel
from cortex.orchestrators.persona.persona_loader import PersonaLoader


class PersonaInjector:
    """
    Apply persona-specific formatting to responses.
    
    Attributes:
        loader: PersonaLoader instance for accessing persona configurations
    """

    # Word limits per depth level
    WORD_LIMITS = {
        DepthLevel.EXECUTIVE: 100,
        DepthLevel.STANDARD: 300,
        DepthLevel.DETAILED: 800,
        DepthLevel.FULL: 999999,  # Effectively unlimited
    }

    # Code visibility: which personas see code blocks
    CODE_VISIBILITY = {
        PersonaId.ENGINEER: True,
        PersonaId.PRODUCT_OWNER: False,
        PersonaId.SCRUM_MASTER: False,
        PersonaId.TECH_LEAD: True,
        PersonaId.BUSINESS_LEADER: False,
        PersonaId.UNKNOWN: True,
    }

    # Metric types each persona cares about
    PREFERRED_METRICS = {
        PersonaId.ENGINEER: [
            "latency",
            "throughput",
            "memory",
            "cpu",
            "response time",
            "performance",
            "optimization",
        ],
        PersonaId.PRODUCT_OWNER: [
            "churn",
            "adoption",
            "nps",
            "feature",
            "user",
            "engagement",
            "impact",
        ],
        PersonaId.SCRUM_MASTER: [
            "velocity",
            "sprint",
            "blockers",
            "process",
            "timeline",
            "capacity",
        ],
        PersonaId.TECH_LEAD: [
            "uptime",
            "replication",
            "cache",
            "health",
            "architecture",
            "scalability",
            "debt",
        ],
        PersonaId.BUSINESS_LEADER: [
            "cost",
            "revenue",
            "roi",
            "satisfaction",
            "business",
            "impact",
            "quarterly",
        ],
        PersonaId.UNKNOWN: [],  # No filtering
    }

    def __init__(self, loader: PersonaLoader) -> None:
        """
        Initialize PersonaInjector with PersonaLoader.
        
        Args:
            loader: PersonaLoader instance
        """
        self.loader = loader

    def format_response(
        self,
        response: str,
        persona: PersonaId,
        depth: Optional[DepthLevel] = None,
    ) -> str:
        """
        Format response according to persona preferences and depth level.
        
        Args:
            response: Original response text
            persona: Target PersonaId for formatting
            depth: Depth level (defaults to STANDARD)
            
        Returns:
            Formatted response text
        """
        if not response or not response.strip():
            return response

        # Default to STANDARD depth if not specified
        if depth is None:
            depth = DepthLevel.STANDARD

        formatted = response

        # Apply filtering based on content type
        formatted = self._filter_code_blocks(formatted, persona)
        formatted = self._filter_metrics(formatted, persona)

        # Apply word limits
        formatted = self._apply_word_limit(formatted, depth)

        # Apply formatting style
        formatted = self._apply_format_style(formatted, persona, depth)

        return formatted

    def _filter_code_blocks(self, response: str, persona: PersonaId) -> str:
        """
        Filter code blocks based on persona preferences.
        
        Args:
            response: Response text
            persona: Target PersonaId
            
        Returns:
            Response with code blocks filtered appropriately
        """
        if self.CODE_VISIBILITY.get(persona, True):
            # Keep code blocks for personas that want to see them
            return response

        # Remove code blocks for personas that don't need them
        # Match markdown code blocks (```...```)
        pattern = r'```[\s\S]*?```'
        
        # Replace code blocks with summaries
        def replace_code(match):
            code_block = match.group(0)
            # Extract first line as function/class name
            lines = code_block.split('\n')
            if len(lines) > 1:
                first_line = lines[1].strip()
                if 'def ' in first_line or 'class ' in first_line:
                    # Extract function/class name
                    name = first_line.split('(')[0].split(':')[0].replace('def ', '').replace('class ', '')
                    return f"[Code: {name.strip()}]"
            return "[Code snippet]"
        
        filtered = re.sub(pattern, replace_code, response)
        return filtered

    def _filter_metrics(self, response: str, persona: PersonaId) -> str:
        """
        Emphasize metrics relevant to persona.
        
        Args:
            response: Response text
            persona: Target PersonaId
            
        Returns:
            Response with metrics emphasized or de-emphasized
        """
        # For MVP, just return as-is
        # Future: prioritize metric ordering, hide irrelevant metrics
        return response

    def _apply_word_limit(self, response: str, depth: DepthLevel) -> str:
        """
        Apply word limits based on depth level.
        
        Args:
            response: Response text
            depth: Depth level
            
        Returns:
            Truncated response if exceeds limit
        """
        limit = self.WORD_LIMITS.get(depth, 300)
        
        words = response.split()
        if len(words) <= limit:
            return response

        # Truncate at word limit
        truncated = ' '.join(words[:limit])
        
        # Add ellipsis
        if limit > 0:
            truncated += '...'
        
        return truncated

    def _apply_format_style(
        self,
        response: str,
        persona: PersonaId,
        depth: DepthLevel,
    ) -> str:
        """
        Apply formatting style based on persona and depth.
        
        Args:
            response: Response text
            persona: Target PersonaId
            depth: Depth level
            
        Returns:
            Styled response
        """
        # BLUF (Bottom-Line-Up-Front) for executive depth
        if depth == DepthLevel.EXECUTIVE:
            # For executives, try to move key finding to top
            # Look for conclusion/recommendation patterns
            lines = response.split('\n')
            
            # Find first sentence with recommendation words
            recommendation_keywords = ['recommend', 'suggest', 'conclude', 'find', 'result', 'key']
            for i, line in enumerate(lines):
                if any(kw in line.lower() for kw in recommendation_keywords):
                    # Move this line to top
                    key_line = line
                    remaining = '\n'.join(lines[:i] + lines[i+1:])
                    return f"{key_line}\n\n{remaining}"
        
        # For detailed depth, preserve structure
        if depth == DepthLevel.DETAILED:
            # Keep step-by-step, numbered lists
            return response

        # Standard formatting: keep as-is
        return response
