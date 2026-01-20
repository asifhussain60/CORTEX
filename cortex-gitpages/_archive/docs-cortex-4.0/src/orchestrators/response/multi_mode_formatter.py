"""Multi-Mode Response Formatting System (AC-RESP-002-01)."""
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re

class FormattingProfile(Enum):
    """Formatting profile presets for different use cases."""
    COMPACT = "compact"              # Minimal formatting, max content
    STANDARD = "standard"            # Balanced formatting
    VERBOSE = "verbose"              # Detailed with all context
    MINIMAL = "minimal"              # Absolute minimum
    RICH = "rich"                    # Rich formatting with colors

class ResponseComponent(Enum):
    """Response component types."""
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
    """Options for response formatting."""
    profile: FormattingProfile = FormattingProfile.STANDARD
    include_metadata: bool = True
    include_timestamps: bool = False
    include_context: bool = True
    max_line_length: int = 80
    include_code_blocks: bool = True
    include_warnings: bool = True
    language_hint: str = "python"
    color_enabled: bool = False
    indentation_level: int = 0

@dataclass
class FormattedResponseSection:
    """A formatted section of a response."""
    section_type: ResponseComponent
    title: str
    content: str
    formatting_applied: List[str] = field(default_factory=list)
    priority: int = 0  # Higher = more important

class ChatResponseFormatter:
    """Format responses for chat interfaces."""
    
    @staticmethod
    def format(
        content: str,
        options: FormattingOptions,
    ) -> str:
        """
        Format content for chat display.
        
        Args:
            content: Raw response content
            options: Formatting options
            
        Returns:
            Formatted chat response
        """
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Remove excessive whitespace
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Apply formatting based on profile
            if options.profile == FormattingProfile.COMPACT:
                # Keep it tight
                formatted_lines.append(stripped)
            elif options.profile == FormattingProfile.VERBOSE:
                # Add spacing
                formatted_lines.append(f"  {stripped}")
            else:
                # Standard
                formatted_lines.append(stripped)
        
        # Join and apply final formatting
        formatted = '\n'.join(formatted_lines)
        
        # Wrap to line length if specified
        if options.max_line_length > 0:
            formatted = ChatResponseFormatter._wrap_text(formatted, options.max_line_length)
        
        return formatted
    
    @staticmethod
    def _wrap_text(text: str, max_width: int) -> str:
        """Wrap text to specified width."""
        lines = []
        for paragraph in text.split('\n'):
            if len(paragraph) <= max_width:
                lines.append(paragraph)
            else:
                # Simple word wrap
                words = paragraph.split(' ')
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 <= max_width:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                
                if current_line:
                    lines.append(' '.join(current_line))
        
        return '\n'.join(lines)

class CommandLineResponseFormatter:
    """Format responses for CLI/command line output."""
    
    @staticmethod
    def format(
        content: str,
        options: FormattingOptions,
    ) -> str:
        """Format content for command line display."""
        lines = [
            "=" * 60,
            "RESPONSE",
            "=" * 60,
            content,
            "=" * 60,
        ]
        
        if options.include_metadata:
            lines.append("✓ Response complete")
        
        return '\n'.join(lines)

class VisualizationResponseFormatter:
    """Format responses for visualization (graphs, diagrams)."""
    
    @staticmethod
    def format(
        content: str,
        data: Optional[Dict[str, Any]] = None,
        options: Optional[FormattingOptions] = None,
    ) -> Dict[str, Any]:
        """
        Format response for visualization.
        
        Args:
            content: Response content
            data: Structured data for visualization
            options: Formatting options
            
        Returns:
            Visualization-formatted response
        """
        return {
            "type": "visualization",
            "content": content,
            "data": data or {},
            "metadata": {
                "generated_at": str(__import__('datetime').datetime.now()),
            }
        }

class JSONAPIResponseFormatter:
    """Format responses for JSON API."""
    
    @staticmethod
    def format(
        content: str,
        operation_id: str,
        turn_number: int,
        options: FormattingOptions,
    ) -> Dict[str, Any]:
        """Format content for JSON API response."""
        return {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "response",
                "id": f"{operation_id}-{turn_number}",
                "attributes": {
                    "content": content,
                    "formatted": True,
                    "profile": options.profile.value,
                },
            }
        }

class MarkdownResponseFormatter:
    """Format responses as Markdown."""
    
    @staticmethod
    def format(
        content: str,
        title: Optional[str] = None,
        sections: Optional[List[FormattedResponseSection]] = None,
        options: Optional[FormattingOptions] = None,
    ) -> str:
        """
        Format response as markdown.
        
        Args:
            content: Main content
            title: Optional title
            sections: Optional list of sections
            options: Formatting options
            
        Returns:
            Markdown formatted response
        """
        options = options or FormattingOptions()
        lines = []
        
        if title:
            lines.append(f"# {title}\n")
        
        lines.append(content)
        
        if sections:
            for section in sorted(sections, key=lambda s: -s.priority):
                lines.append(f"\n## {section.title}\n")
                lines.append(section.content)
        
        return '\n'.join(lines)

class StreamResponseFormatter:
    """Format responses for streaming/real-time display."""
    
    @staticmethod
    def format_chunk(
        chunk: str,
        chunk_number: int,
        total_chunks: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Format a chunk for streaming response.
        
        Args:
            chunk: Content chunk
            chunk_number: Sequential chunk number
            total_chunks: Optional total number of chunks
            
        Returns:
            Formatted chunk
        """
        return {
            "type": "chunk",
            "number": chunk_number,
            "total": total_chunks,
            "content": chunk,
            "is_final": (total_chunks and chunk_number == total_chunks) or False,
        }
    
    @staticmethod
    def format_stream(
        chunks: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Format multiple chunks for streaming.
        
        Args:
            chunks: List of content chunks
            
        Returns:
            List of formatted chunks
        """
        total = len(chunks)
        return [
            StreamResponseFormatter.format_chunk(chunk, i + 1, total)
            for i, chunk in enumerate(chunks)
        ]

class ResponseFormattingEngine:
    """Main engine for multi-mode response formatting."""
    
    def __init__(self):
        """Initialize formatting engine."""
        self.formatters = {
            'chat': ChatResponseFormatter,
            'command': CommandLineResponseFormatter,
            'visualization': VisualizationResponseFormatter,
            'json': JSONAPIResponseFormatter,
            'markdown': MarkdownResponseFormatter,
            'stream': StreamResponseFormatter,
        }
        self.formatting_stats = {
            'total_formatted': 0,
            'by_mode': {},
            'by_profile': {},
        }
    
    def format_response(
        self,
        content: str,
        mode: str = 'chat',
        options: Optional[FormattingOptions] = None,
        **kwargs,
    ) -> Union[str, Dict[str, Any]]:
        """
        Format response in specified mode.
        
        Args:
            content: Content to format
            mode: Output mode ('chat', 'command', 'visualization', 'json', 'markdown', 'stream')
            options: Formatting options
            **kwargs: Mode-specific arguments
            
        Returns:
            Formatted response (type depends on mode)
        """
        options = options or FormattingOptions()
        
        # Track statistics
        self.formatting_stats['total_formatted'] += 1
        self.formatting_stats['by_mode'][mode] = self.formatting_stats['by_mode'].get(mode, 0) + 1
        self.formatting_stats['by_profile'][options.profile.value] = (
            self.formatting_stats['by_profile'].get(options.profile.value, 0) + 1
        )
        
        if mode == 'chat':
            return ChatResponseFormatter.format(content, options)
        elif mode == 'command':
            return CommandLineResponseFormatter.format(content, options)
        elif mode == 'visualization':
            return VisualizationResponseFormatter.format(
                content,
                kwargs.get('data'),
                options
            )
        elif mode == 'json':
            return JSONAPIResponseFormatter.format(
                content,
                kwargs.get('operation_id', 'unknown'),
                kwargs.get('turn_number', 0),
                options
            )
        elif mode == 'markdown':
            return MarkdownResponseFormatter.format(
                content,
                kwargs.get('title'),
                kwargs.get('sections'),
                options
            )
        elif mode == 'stream':
            return StreamResponseFormatter.format_stream(
                kwargs.get('chunks', [content])
            )
        else:
            # Default to chat
            return ChatResponseFormatter.format(content, options)
    
    def batch_format(
        self,
        contents: List[str],
        mode: str = 'chat',
        options: Optional[FormattingOptions] = None,
    ) -> List[Union[str, Dict[str, Any]]]:
        """
        Format multiple responses.
        
        Args:
            contents: List of contents to format
            mode: Output mode
            options: Formatting options
            
        Returns:
            List of formatted responses
        """
        return [
            self.format_response(content, mode, options)
            for content in contents
        ]
    
    def get_formatting_statistics(self) -> Dict[str, Any]:
        """Get formatting statistics."""
        return {
            "total_formatted": self.formatting_stats['total_formatted'],
            "by_mode": self.formatting_stats['by_mode'],
            "by_profile": self.formatting_stats['by_profile'],
        }
    
    def reset_statistics(self) -> None:
        """Reset formatting statistics."""
        self.formatting_stats = {
            'total_formatted': 0,
            'by_mode': {},
            'by_profile': {},
        }
    
    def convert_format(
        self,
        content: Union[str, Dict[str, Any]],
        from_mode: str,
        to_mode: str,
        options: Optional[FormattingOptions] = None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Convert response from one format to another.
        
        Args:
            content: Content in source format
            from_mode: Source mode
            to_mode: Target mode
            options: Formatting options
            
        Returns:
            Content in target format
        """
        # First extract plain text if needed
        if isinstance(content, dict):
            content = content.get('content', str(content))
        else:
            content = str(content)
        
        # Then format to target mode
        return self.format_response(content, to_mode, options)
