"""
Story Formatting Utilities
Provides visual formatting enhancements for story generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

from typing import List


class StoryFormatter:
    """
    Visual formatting utility for story generation.
    Applies bold, italic, code, and markdown effects to enhance readability.
    
    Features:
    - Bold emphasis for key concepts
    - Italic for dramatic effect and inner voice
    - Code formatting for technical terms
    - Badges for features, warnings, and success indicators
    - Dialogue formatting
    - Lists and sections
    """
    
    @staticmethod
    def emphasize(text: str) -> str:
        """Apply bold emphasis to text"""
        return f"**{text}**"
    
    @staticmethod
    def italicize(text: str) -> str:
        """Apply italic emphasis to text"""
        return f"*{text}*"
    
    @staticmethod
    def code(text: str) -> str:
        """Format as inline code"""
        return f"`{text}`"
    
    @staticmethod
    def code_block(code: str, language: str = "") -> str:
        """Format as code block with optional language"""
        return f"```{language}\n{code}\n```"
    
    @staticmethod
    def blockquote(text: str) -> str:
        """Format as blockquote"""
        lines = text.strip().split('\n')
        return '\n'.join(f"> {line}" for line in lines)
    
    @staticmethod
    def quote(text: str) -> str:
        """Format as quoted dialogue or text"""
        return f'"{text}"'
    
    @staticmethod
    def feature_badge(text: str) -> str:
        """Format as feature badge with emphasis"""
        return f"**✨ {text}**"
    
    @staticmethod
    def warning_badge(text: str) -> str:
        """Format as warning badge"""
        return f"**⚠️ {text}**"
    
    @staticmethod
    def success_badge(text: str) -> str:
        """Format as success badge"""
        return f"**✅ {text}**"
    
    @staticmethod
    def technical_term(term: str) -> str:
        """Format technical terms with code + emphasis"""
        return f"`{term}`"
    
    @staticmethod
    def dialogue(speaker: str, text: str) -> str:
        """Format dialogue with speaker emphasis"""
        return f"**{speaker}:** {text}"
    
    @staticmethod
    def dramatic_pause() -> str:
        """Add dramatic pause with ellipsis"""
        return "\n*...*\n"
    
    @staticmethod
    def section_divider() -> str:
        """Add visual section divider"""
        return "\n---\n\n"
    
    @staticmethod
    def numbered_list(items: List[str]) -> str:
        """Create numbered list"""
        return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
    
    @staticmethod
    def bullet_list(items: List[str]) -> str:
        """Create bullet list"""
        return '\n'.join(f"- {item}" for item in items)
    
    @staticmethod
    def before_after(before: str, after: str) -> str:
        """Format before/after comparison"""
        return (
            f"**Before:** {before}\n\n"
            f"**After:** {after}"
        )
    
    @staticmethod
    def stat_highlight(label: str, value: str) -> str:
        """Highlight statistics"""
        return f"**{label}:** *{value}*"
    
    @staticmethod
    def chapter_header(chapter_num: int, title: str, subtitle: str = "") -> str:
        """Format chapter header with consistent styling"""
        header = f"# Chapter {chapter_num}: {title}\n\n"
        if subtitle:
            header += f"## {subtitle}\n\n"
        return header
    
    @staticmethod
    def feature_count_badge(count: int, category: str = "features") -> str:
        """Display feature count in consistent format"""
        return f"**Feature Count: {count} {category}**"


def apply_narrative_formatting(text: str) -> str:
    """
    Apply smart formatting to narrative text.
    Detects patterns and applies appropriate formatting.
    
    Patterns detected:
    - "THE WORD" in all caps → emphasize
    - Technical terms (specific keywords) → code format
    - Quoted dialogue → proper quote formatting
    """
    fmt = StoryFormatter()
    
    # Apply formatting patterns
    formatted = text
    
    # Emphasize all-caps words (for dramatic effect)
    import re
    formatted = re.sub(r'\b([A-Z]{2,})\b', lambda m: fmt.emphasize(m.group(1)), formatted)
    
    # Code format common technical terms
    tech_terms = [
        'JWT', 'bcrypt', 'SQLite', 'FTS5', 'FIFO', 'API', 'REST', 'GraphQL',
        'TDD', 'CI/CD', 'OAuth', 'CORS', 'JSON', 'YAML', 'async/await'
    ]
    for term in tech_terms:
        formatted = formatted.replace(term, fmt.code(term))
    
    return formatted
