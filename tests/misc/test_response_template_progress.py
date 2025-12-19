"""
Tests for Response Template Progress Integration.

This module validates progress bar integration in YAML response templates.
"""

import pytest
from pathlib import Path
import yaml
from src.utils.template_renderer import TemplateRenderer


class TestResponseTemplateProgressIntegration:
    """Test progress bar integration in response templates."""
    
    def test_response_templates_yaml_exists(self):
        """Verify response-templates.yaml exists."""
        templates_file = Path("cortex-brain/response-templates.yaml")
        assert templates_file.exists()
    
    def test_response_templates_can_be_loaded(self):
        """Verify templates YAML can be parsed."""
        templates_file = Path("cortex-brain/response-templates.yaml")
        
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        assert templates is not None
        assert "templates" in templates
    
    def test_status_check_template_has_progress_bars(self):
        """Verify status_check template includes progress bar examples."""
        templates_file = Path("cortex-brain/response-templates.yaml")
        
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        status_template = templates["templates"]["status_check"]
        response_content = status_template["response_content"]
        
        # Should contain Unicode block characters
        assert "█" in response_content or "░" in response_content
    
    def test_template_renderer_with_yaml_template(self):
        """Verify TemplateRenderer works with YAML template content."""
        templates_file = Path("cortex-brain/response-templates.yaml")
        
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        # Extract a template with {progress} placeholder (or create one)
        test_template = "## Increments Progress\n\nCurrent: {progress}"
        
        renderer = TemplateRenderer()
        result = renderer.render_with_progress(
            test_template,
            current=7,
            total=25
        )
        
        # 7/25 = 28%, with default width=20: 5.6 blocks filled ≈ 5-6 blocks
        assert "█████" in result  # At least 5 filled blocks
        assert "28%" in result
    
    def test_planning_workflow_progress_simulation(self):
        """Verify progress bar for planning workflow (25 increments)."""
        renderer = TemplateRenderer()
        
        # Simulate INCREMENT 7 of 25
        template = "**Combined Enhancements Progress:** {progress}"
        
        result = renderer.render_with_progress(
            template,
            current=7,
            total=25,
            progress_width=25
        )
        
        # 7/25 = 28% with width 25 = "███████░░░░░░░░░░░░░░░"
        assert "███████" in result
        assert "28%" in result
    
    def test_multi_phase_progress_rendering(self):
        """Verify progress bars for multi-phase workflows."""
        renderer = TemplateRenderer()
        
        template = """
        **Phase 1 (Foundation):** {phase1_progress}
        **Phase 2 (Git Enhancements):** {phase2_progress}
        **Phase 3 (Governance):** {phase3_progress}
        """
        
        # Can't use render_with_progress for multiple progress bars
        # This test validates the need for multi-progress support (future enhancement)
        # For now, we'd need to manually replace each
        from src.utils.progress_bar import ProgressBar
        
        phase1_bar = ProgressBar(6, 6, width=10).render()  # Complete
        phase2_bar = ProgressBar(1, 9, width=10).render()  # Just started
        phase3_bar = ProgressBar(0, 10, width=10).render()  # Not started
        
        result = template.format(
            phase1_progress=phase1_bar,
            phase2_progress=phase2_bar,
            phase3_progress=phase3_bar
        )
        
        assert "██████████ 100%" in result  # Phase 1
        assert "█░░░░░░░░░ 11%" in result   # Phase 2
        assert "░░░░░░░░░░ 0%" in result    # Phase 3
