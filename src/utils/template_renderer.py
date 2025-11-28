"""
Template Renderer with Progress Bar Integration.

This module provides template rendering with embedded progress indicators
for multi-step workflows in CORTEX response templates.

Example:
    >>> renderer = TemplateRenderer()
    >>> template = "Processing: {progress}"
    >>> result = renderer.render_with_progress(template, current=5, total=10)
    >>> print(result)
    Processing: █████░░░░░ 50%
"""

from typing import Any
from src.utils.progress_bar import ProgressBar


class TemplateRenderer:
    """
    Renders templates with progress bar integration.
    
    This renderer supports standard Python format strings with a special
    {progress} placeholder that embeds a visual progress bar.
    """
    
    def render_with_progress(
        self, 
        template: str, 
        current: int, 
        total: int,
        progress_width: int = 20,
        **kwargs: Any
    ) -> str:
        """
        Render template with progress bar and additional placeholders.
        
        Args:
            template: Template string with {progress} and other placeholders
            current: Current progress value (e.g., completed items)
            total: Total progress value (e.g., total items)
            progress_width: Width of progress bar in characters (default: 20)
            **kwargs: Additional placeholder values for template
        
        Returns:
            Rendered template string with progress bar and substituted values
        
        Example:
            >>> renderer = TemplateRenderer()
            >>> template = "Task: {task_name} | Progress: {progress}"
            >>> result = renderer.render_with_progress(
            ...     template,
            ...     current=3,
            ...     total=10,
            ...     task_name="Processing"
            ... )
            >>> print(result)
            Task: Processing | Progress: ███░░░░░░░ 30%
        """
        # Generate progress bar
        bar = ProgressBar(current, total, width=progress_width)
        progress_str = bar.render()
        
        # Add progress to kwargs for formatting
        format_values = {'progress': progress_str, **kwargs}
        
        # Replace placeholders
        try:
            result = template.format(**format_values)
        except KeyError:
            # If template has {progress} but it's not in format_values,
            # or missing other keys, return with only known values
            result = template
            for key, value in format_values.items():
                placeholder = f"{{{key}}}"
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
        
        return result
