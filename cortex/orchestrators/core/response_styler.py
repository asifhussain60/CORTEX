"""
ResponseStyler agent for persona-based response formatting.

Applies word limits, code filtering, metric selection, and format styles.

AC_START: AC-PHASE37.2-008
"""

from typing import Optional, Dict, Any, List
import re

from cortex.orchestrators.core.persona_loader import PersonaLoader


class ResponseStyler:
    """Apply persona formatting to responses."""
    
    def __init__(self):
        """Initialize response styler."""
        self.persona_loader = PersonaLoader()
    
    def apply_style(
        self,
        response: str,
        persona_id: str,
        available_metrics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Apply persona-based styling to response.
        
        Args:
            response: Raw response text
            persona_id: Persona ID
            available_metrics: Optional metrics dictionary
        
        Returns:
            Styled response
        """
        persona = self.persona_loader.get_persona(persona_id)
        if not persona:
            return response  # No styling if persona not found
        
        styled = response
        
        # Apply word limit
        if persona.word_limit:
            styled = self._apply_word_limit(styled, persona.word_limit)
        
        # Filter code blocks
        if persona.show_code is False:
            styled = self._filter_code_blocks(styled)
        
        # Filter metrics
        if available_metrics and persona.show_metrics:
            styled = self._filter_metrics(styled, persona.metric_types, available_metrics)
        
        # Apply format style
        if persona.format == "BLUF":
            styled = self._apply_bluf_format(styled)
        
        return styled
    
    def _apply_word_limit(self, text: str, limit: int) -> str:
        """Truncate text to word limit.
        
        Args:
            text: Input text
            limit: Maximum words
        
        Returns:
            Truncated text
        """
        words = text.split()
        if len(words) <= limit:
            return text
        
        truncated = ' '.join(words[:limit])
        return truncated + "..."
    
    def _filter_code_blocks(self, text: str) -> str:
        """Remove code blocks from text.
        
        Args:
            text: Input text
        
        Returns:
            Text without code blocks
        """
        # Remove fenced code blocks
        pattern = r'```[\s\S]*?```'
        filtered = re.sub(pattern, '[Code block omitted]', text)
        
        # Remove inline code
        filtered = re.sub(r'`[^`]+`', '[code]', filtered)
        
        return filtered
    
    def _filter_metrics(
        self,
        text: str,
        allowed_metric_types: List[str],
        available_metrics: Dict[str, Any]
    ) -> str:
        """Include only allowed metrics in response.
        
        Args:
            text: Input text
            allowed_metric_types: Metrics persona wants to see
            available_metrics: All available metrics
        
        Returns:
            Text with filtered metrics
        """
        # Extract allowed metrics
        allowed_values = {
            k: v for k, v in available_metrics.items()
            if k in allowed_metric_types
        }
        
        if not allowed_values:
            return text
        
        # Append metrics section
        metrics_section = "\n\n**Metrics:**\n"
        for metric, value in allowed_values.items():
            metrics_section += f"- {metric}: {value}\n"
        
        return text + metrics_section
    
    def _apply_bluf_format(self, text: str) -> str:
        """Apply Bottom Line Up Front format.
        
        Extracts key takeaway and places at top.
        
        Args:
            text: Input text
        
        Returns:
            BLUF-formatted text
        """
        # Extract first sentence or conclusion
        sentences = text.split('.')
        if len(sentences) > 0:
            bluf = sentences[0].strip() + '.'
            return f"**BLUF:** {bluf}\n\n{text}"
        
        return text


# AC_COMPLETE: AC-PHASE37.2-008 ✅ ResponseStyler with formatting logic
