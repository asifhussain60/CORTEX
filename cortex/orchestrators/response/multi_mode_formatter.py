"""Multi-Mode Formatter

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum


class ResponseComponent(Enum):
    """Response component types."""
    CONTEXT = "context"
    SUMMARY = "summary"
    EXPLANATION = "explanation"
    CODE = "code"
    ALTERNATIVES = "alternatives"
    WARNINGS = "warnings"
    STEPS = "steps"
    METADATA = "metadata"


@dataclass
class FormattingProfile:
    """Formatting profile."""
    profile_id: str
    format_type: str = "markdown"


@dataclass
class FormattingOptions:
    """Formatting options."""
    mode: str = "default"
    include_metadata: bool = False
    max_length: int = 0


class MultiModeFormatter:
    """Format responses in multiple modes."""
    
    def format(self, content: str, profile: FormattingProfile) -> str:
        """Format content."""
        return content


@dataclass
class FormattedResponseSection:
    """Formatted response section."""
    section_id: str
    component: ResponseComponent
    content: str
    metadata: dict = field(default_factory=dict)


class ChatResponseFormatter:
    """Format responses for chat interfaces."""
    
    def format(self, response: str) -> str:
        """Format response for chat."""
        return response


class CommandLineResponseFormatter:
    """Format responses for command line interfaces."""
    
    def format(self, response: str) -> str:
        """Format response for CLI."""
        return response


class VisualizationResponseFormatter:
    """Format responses with visualizations."""
    
    def format(self, response: str) -> str:
        """Format response with visualizations."""
        return response

__all__ = ["ResponseComponent", "FormattingProfile", "FormattingOptions", "FormattedResponseSection", "ChatResponseFormatter", "CommandLineResponseFormatter", "VisualizationResponseFormatter", "MultiModeFormatter"]
