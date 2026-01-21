"""Multi-Mode Response Formatting (AC-RESP-002-01).

Author: CORTEX Framework
Date: 2025
Version: 1.0.0
"""

import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FormattingProfile(str, Enum):
    """Formatting profile options.
    
    Attributes:
        COMPACT: Minimal spacing, terse output
        STANDARD: Default balanced formatting
        VERBOSE: Extended details and explanations
        MINIMAL: Bare minimum information
        RICH: Enhanced formatting with decorations
    """
    COMPACT = "compact"
    STANDARD = "standard"
    VERBOSE = "verbose"
    MINIMAL = "minimal"
    RICH = "rich"


class ResponseComponent(str, Enum):
    """Response component types.
    
    Attributes:
        OPERATION_CONTEXT: Context about the operation
        BRIEF_SUMMARY: Quick summary of response
        DETAILED_EXPLANATION: Full details and explanations
        CODE_EXAMPLE: Code snippets and examples
        ALTERNATIVES: Alternative approaches
        WARNINGS: Warnings and cautions
        NEXT_STEPS: Suggested next steps
        METADATA: Operation metadata
    """
    OPERATION_CONTEXT = "operation_context"
    BRIEF_SUMMARY = "brief_summary"
    DETAILED_EXPLANATION = "detailed_explanation"
    CODE_EXAMPLE = "code_example"
    ALTERNATIVES = "alternatives"
    WARNINGS = "warnings"
    NEXT_STEPS = "next_steps"
    METADATA = "metadata"


@dataclass
class FormattingOptions:
    """Formatting options configuration.
    
    Attributes:
        profile: Selected formatting profile
        include_metadata: Whether to include metadata in output
        max_line_length: Maximum line length for text wrapping
    """
    profile: FormattingProfile = FormattingProfile.STANDARD
    include_metadata: bool = True
    max_line_length: int = 80


@dataclass
class FormattedResponseSection:
    """Formatted response section.
    
    Attributes:
        section_type: Type of component in this section
        title: Section title
        content: Section content
        priority: Display priority (higher = earlier)
    """
    section_type: ResponseComponent
    title: str
    content: str
    priority: int = 0


class ChatResponseFormatter:
    """Format responses for chat interfaces.
    
    Provides clean, conversational formatting suitable for chat UIs.
    """
    
    @staticmethod
    def format(content: str, options: Optional[FormattingOptions] = None) -> str:
        """Format content for chat interface.
        
        Args:
            content: Content to format
            options: Formatting options
            
        Returns:
            Formatted string for chat display
        """
        if options is None:
            options = FormattingOptions()
        
        # Strip whitespace for compact profile
        if options.profile == FormattingProfile.COMPACT:
            lines = [line.strip() for line in content.split('\n')]
            content = '\n'.join(line for line in lines if line)
        
        # Apply line wrapping if max_line_length specified
        if options.max_line_length > 0:
            wrapped_lines = []
            for line in content.split('\n'):
                if len(line) <= options.max_line_length:
                    wrapped_lines.append(line)
                else:
                    wrapped = textwrap.fill(
                        line,
                        width=options.max_line_length,
                        break_long_words=False,
                        break_on_hyphens=False
                    )
                    wrapped_lines.append(wrapped)
            content = '\n'.join(wrapped_lines)
        
        return content


class CommandLineResponseFormatter:
    """Format responses for command line interfaces.
    
    Provides structured, terminal-friendly formatting with headers and metadata.
    """
    
    @staticmethod
    def format(content: str, options: Optional[FormattingOptions] = None) -> str:
        """Format content for command line interface.
        
        Args:
            content: Content to format
            options: Formatting options
            
        Returns:
            Formatted string for CLI display
        """
        if options is None:
            options = FormattingOptions()
        
        lines = []
        lines.append("=" * 40)
        lines.append("RESPONSE")
        lines.append("=" * 40)
        
        if options.include_metadata:
            lines.append("✓ Operation complete")
            lines.append("")
        
        lines.append(content)
        lines.append("=" * 40)
        
        return '\n'.join(lines)


class VisualizationResponseFormatter:
    """Format responses with visualizations.
    
    Provides structured data format for visualization rendering.
    """
    
    @staticmethod
    def format(
        content: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format content for visualization.
        
        Args:
            content: Content description
            data: Optional visualization data
            
        Returns:
            Dictionary with visualization structure
        """
        result = {
            "type": "visualization",
            "content": content,
            "metadata": {}
        }
        
        if data is not None:
            result["data"] = data
        
        return result


class JSONAPIResponseFormatter:
    """Format responses as JSON API.
    
    Provides JSON API v1.0 compliant response format.
    """
    
    @staticmethod
    def format(
        content: str,
        operation_id: str,
        turn_number: int,
        options: Optional[FormattingOptions] = None
    ) -> Dict[str, Any]:
        """Format content as JSON API response.
        
        Args:
            content: Response content
            operation_id: Operation identifier
            turn_number: Turn number
            options: Formatting options
            
        Returns:
            JSON API formatted dictionary
        """
        return {
            "jsonapi": {
                "version": "1.0"
            },
            "data": {
                "type": "response",
                "id": operation_id,
                "attributes": {
                    "content": content,
                    "turn_number": turn_number
                }
            }
        }


class MarkdownResponseFormatter:
    """Format responses as Markdown.
    
    Provides Markdown formatted output with optional sections.
    """
    
    @staticmethod
    def format(
        content: str,
        title: Optional[str] = None,
        sections: Optional[List[FormattedResponseSection]] = None
    ) -> str:
        """Format content as Markdown.
        
        Args:
            content: Main content
            title: Optional document title
            sections: Optional list of sections to include
            
        Returns:
            Markdown formatted string
        """
        lines = []
        
        if title:
            lines.append(f"# {title}")
            lines.append("")
        
        lines.append(content)
        
        if sections:
            # Sort by priority (higher first)
            sorted_sections = sorted(
                sections,
                key=lambda s: s.priority,
                reverse=True
            )
            
            lines.append("")
            for section in sorted_sections:
                lines.append(f"## {section.title}")
                lines.append("")
                lines.append(section.content)
                lines.append("")
        
        return '\n'.join(lines)


class StreamResponseFormatter:
    """Format responses for streaming.
    
    Provides chunk-based formatting for streaming responses.
    """
    
    @staticmethod
    def format_chunk(
        content: str,
        chunk_number: int,
        total_chunks: int
    ) -> Dict[str, Any]:
        """Format a single stream chunk.
        
        Args:
            content: Chunk content
            chunk_number: Current chunk number (1-based)
            total_chunks: Total number of chunks
            
        Returns:
            Dictionary with chunk information
        """
        return {
            "type": "chunk",
            "number": chunk_number,
            "total": total_chunks,
            "content": content,
            "is_final": chunk_number == total_chunks
        }
    
    @staticmethod
    def format_stream(chunks: List[str]) -> List[Dict[str, Any]]:
        """Format multiple chunks as a stream.
        
        Args:
            chunks: List of chunk contents
            
        Returns:
            List of formatted chunk dictionaries
        """
        total = len(chunks)
        return [
            StreamResponseFormatter.format_chunk(chunk, i + 1, total)
            for i, chunk in enumerate(chunks)
        ]


class ResponseFormattingEngine:
    """Main response formatting engine.
    
    Routes formatting requests to appropriate formatters based on mode.
    
    Attributes:
        formatters: Dictionary of mode to formatter mappings
        formatting_stats: Statistics about formatting operations
    """
    
    def __init__(self) -> None:
        """Initialize the formatting engine."""
        self.formatters = {
            'chat': ChatResponseFormatter,
            'command': CommandLineResponseFormatter,
            'visualization': VisualizationResponseFormatter,
            'json': JSONAPIResponseFormatter,
            'markdown': MarkdownResponseFormatter,
            'stream': StreamResponseFormatter
        }
        
        self.formatting_stats: Dict[str, Any] = {
            'total_formatted': 0,
            'by_mode': {mode: 0 for mode in self.formatters.keys()},
            'by_profile': {}
        }
    
    def format_response(
        self,
        content: str,
        mode: str = 'chat',
        **kwargs: Any
    ) -> Any:
        """Format response based on mode.
        
        Args:
            content: Content to format
            mode: Formatting mode (chat, command, json, markdown, stream)
            **kwargs: Additional formatter-specific arguments
            
        Returns:
            Formatted response (type depends on mode)
        """
        # Default to chat mode for unknown modes
        if mode not in self.formatters:
            mode = 'chat'
        
        formatter = self.formatters[mode]
        
        # Route to appropriate formatter
        if mode == 'chat':
            options = kwargs.get('options', FormattingOptions())
            result = formatter.format(content, options)
            # Track profile usage
            profile_name = options.profile.value
            self.formatting_stats['by_profile'][profile_name] = \
                self.formatting_stats['by_profile'].get(profile_name, 0) + 1
        elif mode == 'command':
            options = kwargs.get('options', FormattingOptions())
            result = formatter.format(content, options)
        elif mode == 'visualization':
            data = kwargs.get('data')
            result = formatter.format(content, data)
        elif mode == 'json':
            result = formatter.format(
                content,
                kwargs['operation_id'],
                kwargs['turn_number'],
                kwargs.get('options')
            )
        elif mode == 'markdown':
            result = formatter.format(
                content,
                kwargs.get('title'),
                kwargs.get('sections')
            )
        elif mode == 'stream':
            chunks = kwargs.get('chunks', [])
            result = formatter.format_stream(chunks)
        else:
            result = content
        
        # Update statistics
        self.formatting_stats['total_formatted'] += 1
        self.formatting_stats['by_mode'][mode] += 1
        
        return result
    
    def batch_format(
        self,
        contents: List[str],
        mode: str = 'chat',
        **kwargs: Any
    ) -> List[Any]:
        """Format multiple responses in batch.
        
        Args:
            contents: List of content strings to format
            mode: Formatting mode
            **kwargs: Additional formatter-specific arguments
            
        Returns:
            List of formatted responses
        """
        return [
            self.format_response(content, mode, **kwargs)
            for content in contents
        ]
    
    def convert_format(
        self,
        content: str,
        from_mode: str,
        to_mode: str
    ) -> Any:
        """Convert content from one format to another.
        
        Args:
            content: Content to convert
            from_mode: Source format mode
            to_mode: Target format mode
            
        Returns:
            Content formatted in target mode
        """
        # For now, simple conversion (assumes content is already formatted)
        return self.format_response(content, mode=to_mode)
    
    def reset_statistics(self) -> None:
        """Reset formatting statistics."""
        self.formatting_stats = {
            'total_formatted': 0,
            'by_mode': {},
            'by_profile': {}
        }
    
    def get_formatting_statistics(self) -> Dict[str, Any]:
        """Get formatting statistics.
        
        Returns:
            Dictionary with formatting statistics
        """
        return self.formatting_stats.copy()


__all__ = [
    "FormattingProfile",
    "ResponseComponent",
    "FormattingOptions",
    "FormattedResponseSection",
    "ChatResponseFormatter",
    "CommandLineResponseFormatter",
    "VisualizationResponseFormatter",
    "JSONAPIResponseFormatter",
    "MarkdownResponseFormatter",
    "StreamResponseFormatter",
    "ResponseFormattingEngine"
]
