"""
Code snippet extraction with context
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import CodeElement

logger = logging.getLogger(__name__)


@dataclass
class CodeSnippet:
    """Code snippet with context"""
    code: str
    start_line: int
    end_line: int
    context_before: str
    context_after: str
    highlighted: str


class SnippetExtractor:
    """Extract code snippets with surrounding context"""
    
    def __init__(self):
        """Initialize snippet extractor"""
        pass
    
    def extract_snippet(self, element: CodeElement, context_lines: int = 3) -> Optional[CodeSnippet]:
        """
        Extract code snippet with context
        
        Args:
            element: Code element to extract
            context_lines: Number of context lines before/after
            
        Returns:
            CodeSnippet with context or None
        """
        try:
            with open(element.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Calculate bounds
            start_idx = max(0, element.line_start - 1)
            end_idx = min(len(lines), element.line_end)
            
            # Get code
            code = ''.join(lines[start_idx:end_idx])
            
            # Get context
            context_start = max(0, start_idx - context_lines)
            context_end = min(len(lines), end_idx + context_lines)
            
            context_before = ''.join(lines[context_start:start_idx])
            context_after = ''.join(lines[end_idx:context_end])
            
            return CodeSnippet(
                code=code,
                start_line=element.line_start,
                end_line=element.line_end,
                context_before=context_before,
                context_after=context_after,
                highlighted=code  # Will be highlighted later
            )
        except Exception as e:
            logger.error(f"Error extracting snippet from {element.file_path}: {e}")
            return None
    
    def highlight_matches(self, snippet: str, query: str) -> str:
        """
        Highlight search matches in snippet
        
        Args:
            snippet: Code snippet
            query: Search query to highlight
            
        Returns:
            Highlighted snippet
        """
        # Simple highlighting with markers
        import re
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        highlighted = pattern.sub(f">>>{query}<<<", snippet)
        return highlighted
    
    def get_surrounding_context(self, file_path: Path, line_number: int, context_lines: int = 3) -> str:
        """
        Get surrounding context for a line
        
        Args:
            file_path: Path to file
            line_number: Target line number
            context_lines: Lines of context
            
        Returns:
            Context string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)
            
            context = ''.join(lines[start:end])
            return context
        except Exception as e:
            logger.error(f"Error getting context from {file_path}: {e}")
            return ""
