"""
Tests for TemplateRenderer with progress bar integration.

This module validates template rendering with embedded progress indicators.
"""

import pytest
from src.utils.template_renderer import TemplateRenderer
from src.utils.progress_bar import ProgressBar


class TestTemplateRendererProgressIntegration:
    """Test progress bar integration in template rendering."""
    
    def test_render_with_progress_inserts_bar(self):
        """Verify progress bar is inserted into template."""
        template = "Processing: {progress}"
        renderer = TemplateRenderer()
        
        result = renderer.render_with_progress(
            template, 
            current=5, 
            total=10
        )
        
        assert "█████░░░░░" in result
        assert "50%" in result
    
    def test_render_without_progress_placeholder_unchanged(self):
        """Verify templates without {progress} remain unchanged."""
        template = "This has no progress indicator"
        renderer = TemplateRenderer()
        
        result = renderer.render_with_progress(
            template,
            current=5,
            total=10
        )
        
        assert result == template
    
    def test_render_multiple_progress_placeholders(self):
        """Verify multiple {progress} placeholders are replaced."""
        template = "Start: {progress} | End: {progress}"
        renderer = TemplateRenderer()
        
        result = renderer.render_with_progress(
            template,
            current=7,
            total=10
        )
        
        # Both should be replaced with same progress bar
        progress_count = result.count("███████░░░")
        assert progress_count == 2
    
    def test_render_with_custom_width(self):
        """Verify custom progress bar width parameter."""
        template = "Progress: {progress}"
        renderer = TemplateRenderer()
        
        result = renderer.render_with_progress(
            template,
            current=5,
            total=10,
            progress_width=5
        )
        
        # 5/10 = 50% with width 5 = "██░░░"
        assert "██░░░" in result
    
    def test_render_with_additional_placeholders(self):
        """Verify progress works alongside other template placeholders."""
        template = "Task: {task_name} | Progress: {progress}"
        renderer = TemplateRenderer()
        
        result = renderer.render_with_progress(
            template,
            current=3,
            total=10,
            task_name="Data Processing"
        )
        
        assert "Data Processing" in result
        assert "███░░░░░░░" in result
        assert "30%" in result
