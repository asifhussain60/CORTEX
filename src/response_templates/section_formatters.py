"""
Section Formatters for CORTEX Response Templates

Provides mode-specific formatting for individual response sections
(understanding, challenge, response, request_echo, next_steps).

Each interaction mode has its own formatter that customizes:
- Section headers and prefixes
- Content length and verbosity
- Visual styling and formatting
- Additional context and enrichment

Author: Asif Hussain
Phase: 5.4 - Dynamic Section Rendering
Version: 1.0
Created: December 2, 2025
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class SectionFormatter(ABC):
    """Base class for mode-specific section formatters."""
    
    def __init__(self, mode_name: str):
        """Initialize section formatter.
        
        Args:
            mode_name: Name of the interaction mode
        """
        self.mode_name = mode_name
        self.max_response_lines = 30  # Default, can be overridden
    
    def _format_with_header(self, emoji: str, title: str, content: str) -> str:
        """Helper to format section with consistent header style.
        
        Args:
            emoji: Section emoji
            title: Section title
            content: Section content
            
        Returns:
            Formatted section with header
        """
        if not content:
            return ""
        return f"### {emoji} {title}\n{content}"
    
    def _is_empty_challenge(self, content: str) -> bool:
        """Check if challenge content is empty or "no challenge".
        
        Args:
            content: Challenge content to check
            
        Returns:
            True if challenge is empty or "no challenge"
        """
        return not content or content.lower() == "no challenge"
    
    @abstractmethod
    def format_understanding(self, content: str, context: Dict[str, Any]) -> str:
        """Format understanding section.
        
        Args:
            content: Understanding content
            context: Additional context data
            
        Returns:
            Formatted understanding section
        """
        pass
    
    @abstractmethod
    def format_challenge(self, content: str, context: Dict[str, Any]) -> str:
        """Format challenge section.
        
        Args:
            content: Challenge content
            context: Additional context data
            
        Returns:
            Formatted challenge section
        """
        pass
    
    @abstractmethod
    def format_response(self, content: str, context: Dict[str, Any]) -> str:
        """Format response section.
        
        Args:
            content: Response content
            context: Additional context data
            
        Returns:
            Formatted response section
        """
        pass
    
    def format_request_echo(self, content: str, context: Dict[str, Any]) -> str:
        """Format request echo section.
        
        Args:
            content: Request echo content
            context: Additional context data
            
        Returns:
            Formatted request echo section
        """
        return f"### 📝 Your Request\n{content}"
    
    @abstractmethod
    def format_next_steps(self, steps: List[str], context: Dict[str, Any]) -> str:
        """Format next steps section.
        
        Args:
            steps: List of next step items
            context: Additional context data
            
        Returns:
            Formatted next steps section
        """
        pass
    
    def _truncate_to_lines(self, content: str, max_lines: int) -> str:
        """Truncate content to maximum number of lines.
        
        Args:
            content: Content to truncate
            max_lines: Maximum number of lines
            
        Returns:
            Truncated content
        """
        lines = content.split('\n')
        if len(lines) <= max_lines:
            return content
        
        return '\n'.join(lines[:max_lines]) + "\n..."


class AutonomousSectionFormatter(SectionFormatter):
    """Formatter for autonomous mode (minimal, compact, efficient)."""
    
    def __init__(self):
        super().__init__('autonomous')
        self.max_response_lines = 10
    
    def format_understanding(self, content: str, context: Dict[str, Any]) -> str:
        """Format understanding section - compact, no header."""
        if not content:
            return ""
        # Autonomous: just the content, no header
        return content
    
    def format_challenge(self, content: str, context: Dict[str, Any]) -> str:
        """Format challenge section - inline or omitted."""
        if not content or content.lower() == "no challenge":
            return ""
        # Very brief, inline format
        return f"**Challenge:** {content}"
    
    def format_response(self, content: str, context: Dict[str, Any]) -> str:
        """Format response section - compact with max 10 lines."""
        if not content:
            return ""
        # Truncate to max lines
        truncated = self._truncate_to_lines(content, self.max_response_lines)
        return truncated
    
    def format_request_echo(self, content: str, context: Dict[str, Any]) -> str:
        """Format request echo - omitted in autonomous mode."""
        # Autonomous mode: skip request echo for brevity
        return ""
    
    def format_next_steps(self, steps: List[str], context: Dict[str, Any]) -> str:
        """Format next steps - compact format without header."""
        if not steps:
            return ""
        
        # Compact format: "**Next:** step1, step2"
        if len(steps) == 1:
            return f"**Next:** {steps[0]}"
        
        # Multiple steps as comma-separated
        steps_text = ", ".join(steps[:3])  # Max 3 steps
        return f"**Next:** {steps_text}"


class GuidedSectionFormatter(SectionFormatter):
    """Formatter for guided mode (standard, balanced, clear)."""
    
    def __init__(self):
        super().__init__('guided')
        self.max_response_lines = 30
    
    def format_understanding(self, content: str, context: Dict[str, Any]) -> str:
        """Format understanding section - standard with full header."""
        return self._format_with_header("🎯", "My Understanding Of Your Request", content)
    
    def format_challenge(self, content: str, context: Dict[str, Any]) -> str:
        """Format challenge section - always visible."""
        if not content:
            content = "No Challenge"
        return self._format_with_header("⚠️", "Challenge", content)
    
    def format_response(self, content: str, context: Dict[str, Any]) -> str:
        """Format response section - standard format with max 30 lines."""
        if not content:
            return ""
        truncated = self._truncate_to_lines(content, self.max_response_lines)
        return self._format_with_header("💬", "Response", truncated)
    
    def format_next_steps(self, steps: List[str], context: Dict[str, Any]) -> str:
        """Format next steps - numbered list."""
        if not steps:
            return ""
        steps_text = "\n".join([f"{i}. {step}" for i, step in enumerate(steps, 1)])
        return self._format_with_header("🔍", "Next Steps", steps_text)


class EducationalSectionFormatter(SectionFormatter):
    """Formatter for educational mode (detailed, learning-focused, enriched)."""
    
    def __init__(self):
        super().__init__('educational')
        self.max_response_lines = 50
    
    def format_understanding(self, content: str, context: Dict[str, Any]) -> str:
        """Format understanding section - includes context enrichment."""
        if not content:
            return ""
        
        # Always add context explanation for educational mode
        enriched = (f"{content}\n\n"
                   "**Context:** This helps us establish shared understanding before proceeding. "
                   "I want to ensure we're aligned on the requirements and approach.")
        
        return self._format_with_header("🎯", "My Understanding Of Your Request", enriched)
    
    def format_challenge(self, content: str, context: Dict[str, Any]) -> str:
        """Format challenge section - includes explanation."""
        if not content:
            content = "No Challenge"
        
        # Add "why" explanation if challenge exists
        if not self._is_empty_challenge(content) and context.get('include_explanation'):
            content += "\n\n**Why this matters:** Understanding challenges helps anticipate solutions."
        
        return self._format_with_header("⚠️", "Challenge", content)
    
    def format_response(self, content: str, context: Dict[str, Any]) -> str:
        """Format response section - detailed with analysis."""
        if not content:
            return ""
        
        truncated = self._truncate_to_lines(content, self.max_response_lines)
        
        # Always add analysis for educational mode
        enriched = (f"{truncated}\n\n"
                   "**Analysis:** Breaking down the approach helps build understanding and reveals key decision points.\n\n"
                   "**Recommendations:** Consider best practices, common pitfalls, and long-term maintainability.")
        
        return self._format_with_header("💬", "Response", enriched)
    
    def format_next_steps(self, steps: List[str], context: Dict[str, Any]) -> str:
        """Format next steps - checkboxes with learning resources."""
        if not steps:
            return ""
        
        # Checkbox format for tracking
        steps_text = "\n".join([f"☐ {step}" for step in steps])
        
        # Add learning resources if requested
        if context.get('include_learning_resources'):
            steps_text += "\n\n**Learning Resources:** Consult documentation and examples as you progress."
        
        return self._format_with_header("🔍", "Next Steps", steps_text)


class PairSectionFormatter(SectionFormatter):
    """Formatter for pair mode (collaborative, options-focused, interactive)."""
    
    def __init__(self):
        super().__init__('pair')
        self.max_response_lines = 40
    
    def format_understanding(self, content: str, context: Dict[str, Any]) -> str:
        """Format understanding section - collaborative tone."""
        if not content:
            return ""
        
        # Collaborative phrasing
        enriched = content
        if context.get('collaborative_tone'):
            enriched += "\n\n**Does this match your thinking?**"
        
        return f"### 🎯 My Understanding Of Your Request\n{enriched}"
    
    def format_challenge(self, content: str, context: Dict[str, Any]) -> str:
        """Format challenge section - presents options."""
        if not content:
            content = "No Challenge"
        
        formatted = f"### ⚠️ Challenge\n{content}"
        
        # Present options if available
        if context.get('present_options') and content.lower() != "no challenge":
            formatted += "\n\n**I see a few approaches we could consider...**"
        
        return formatted
    
    def format_response(self, content: str, context: Dict[str, Any]) -> str:
        """Format response section - includes trade-offs."""
        if not content:
            return ""
        
        truncated = self._truncate_to_lines(content, self.max_response_lines)
        formatted = f"### 💬 Response\n{truncated}"
        
        # Add trade-offs discussion
        if context.get('include_tradeoffs'):
            formatted += "\n\n**Trade-offs:** Let's discuss the pros and cons of each approach."
        
        if context.get('ask_preferences'):
            formatted += "\n\n**What's your preference?**"
        
        return formatted
    
    def format_next_steps(self, steps: List[str], context: Dict[str, Any]) -> str:
        """Format next steps - presents options/tracks."""
        if not steps:
            return ""
        
        # Present as options or tracks
        if len(steps) <= 3 and any('option' in step.lower() or 'track' in step.lower() for step in steps):
            # Already formatted as options
            steps_text = "\n\n".join([f"**{step}**" for step in steps])
            formatted = f"### 🔍 Next Steps\n\n{steps_text}"
        else:
            # Format as parallel tracks
            steps_text = "\n\n".join([f"**Track {chr(65+i)}:** {step}" for i, step in enumerate(steps[:3])])
            formatted = f"### 🔍 Next Steps\n\n{steps_text}"
        
        # Add decision prompt
        if context.get('include_decision_points'):
            formatted += "\n\n**Which track would you like to pursue first?**"
        
        return formatted


class SectionFormatterRegistry:
    """Registry for section formatters by interaction mode."""
    
    def __init__(self):
        """Initialize registry with default formatters."""
        self._formatters: Dict[str, SectionFormatter] = {
            'autonomous': AutonomousSectionFormatter(),
            'guided': GuidedSectionFormatter(),
            'educational': EducationalSectionFormatter(),
            'pair': PairSectionFormatter()
        }
    
    def register(self, mode: str, formatter: SectionFormatter):
        """Register a custom formatter for a mode.
        
        Args:
            mode: Mode name
            formatter: Formatter instance
        """
        self._formatters[mode] = formatter
    
    def get_formatter(self, mode: str) -> SectionFormatter:
        """Get formatter for a mode.
        
        Args:
            mode: Mode name
            
        Returns:
            Formatter instance (falls back to guided if mode not found)
        """
        return self._formatters.get(mode, self._formatters['guided'])
    
    def has_formatter(self, mode: str) -> bool:
        """Check if formatter exists for a mode.
        
        Args:
            mode: Mode name
            
        Returns:
            True if formatter exists
        """
        return mode in self._formatters
