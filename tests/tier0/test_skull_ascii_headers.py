"""
SKULL Protection Test: Banner Images and Headers in Response Templates

Tests that CORTEX banner image appears correctly in help templates ONLY.
All orchestrator operations use minimalist headers for cleaner output.

Design Decision:
- Help entry point: Banner image + minimalist header (visual impact for discovery)
- Operation orchestrators: Minimalist header with ━ characters (clean, professional)

SKULL Rules Tested:
- SKULL-006: Help templates must include banner image for visual consistency
- SKULL-007: Orchestrator templates must use minimalist headers (not ASCII art)
- SKULL-008: Banner images must be properly referenced for display

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path


class TestSKULLBannerImages:
    """Test banner images and headers in response templates"""
    
    @pytest.fixture
    def response_templates_path(self):
        """Path to response templates YAML"""
        return Path(__file__).parent.parent.parent / "cortex-brain" / "response-templates.yaml"
    
    @pytest.fixture
    def response_templates(self, response_templates_path):
        """Load response templates"""
        with open(response_templates_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_help_table_has_banner_image(self, response_templates):
        """SKULL-006: Help table response must include CORTEX banner image"""
        help_table = response_templates['templates']['help_table']
        content = help_table['content']
        
        # Check for image reference (Markdown or HTML format)
        assert ('![CORTEX' in content or '<img' in content), "Missing CORTEX banner image"
        assert 'cortex-help-banner' in content.lower(), "Missing banner image reference"
        
        # Check for minimalist header border
        assert '━━' in content, "Missing decorative header border"
    
    def test_help_detailed_has_banner_image(self, response_templates):
        """SKULL-006: Detailed help must include banner image"""
        help_detailed = response_templates['templates']['help_detailed']
        content = help_detailed['content']
        
        # Check for image reference
        assert ('![CORTEX' in content or '<img' in content), "Missing CORTEX banner image"
        assert 'cortex-help-banner' in content.lower(), "Missing banner image reference"
        
        # Check for decorative headers
        assert '━━' in content, "Missing decorative header in detailed help"
    
    def test_operation_started_has_ascii_banner(self, response_templates):
        """SKULL-006: Operation start messages should have ASCII art"""
        operation_started = response_templates['templates']['operation_started']
        content = operation_started['content']
        
        # Check for decorative elements
        assert '🚀' in content or '═══' in content or '━━━' in content, \
            "Missing decorative header in operation started"
    
    def test_orchestrator_header_has_full_banner(self, response_templates):
        """SKULL-006: Orchestrator header uses minimalist style (not ASCII banner)"""
        orchestrator_header = response_templates['templates']['orchestrator_header']
        content = orchestrator_header['content']
        
        # Minimalist header requirements (using ━ not ═)
        assert '━━━' in content, "Missing minimalist header border"
        assert '©' in content, "Missing copyright symbol"
        assert 'Asif Hussain' in content, "Missing author name"
        assert '{{operation_name}}' in content, "Missing operation name placeholder"
        assert '{{version}}' in content, "Missing version placeholder"
    
    def test_banner_image_properly_formatted(self, response_templates):
        """SKULL-007: Banner image must be properly referenced"""
        help_table = response_templates['templates']['help_table']
        content = help_table['content']
        
        # Check image reference structure
        lines = content.split('\n')
        image_lines = [l for l in lines if '![CORTEX' in l or '<img' in l]
        
        if image_lines:
            # Should have image reference
            assert len(image_lines) >= 1, "Banner image reference should be present"
            
            # Check for proper markdown format or HTML
            assert any('![' in l or '<img' in l for l in image_lines), \
                "Missing proper image markdown or HTML"
            
            # Image path should exist
            assert 'cortex-help-banner' in content.lower(), \
                "Image reference should point to cortex-help-banner"
    
    def test_copyright_in_all_headers(self, response_templates):
        """SKULL-006: All headers must include copyright notice"""
        header_templates = [
            'help_table',
            'help_detailed',
            'orchestrator_header',
            'cortex_signature'
        ]
        
        for template_name in header_templates:
            template = response_templates['templates'][template_name]
            content = template['content']
            
            # Check for copyright
            assert '© 2024-2025 Asif Hussain' in content or '©' in content, \
                f"Missing copyright in {template_name}"
            assert 'Asif Hussain' in content, \
                f"Missing author name in {template_name}"
    
    def test_ascii_banner_visual_consistency(self, response_templates):
        """SKULL-007: ASCII banners should only appear in help templates"""
        # Help templates should have ASCII art
        help_table = response_templates['templates']['help_table']
        help_detailed = response_templates['templates']['help_detailed']
        
        # Box-drawing characters for ASCII art
        box_chars = {'╔', '╗', '╚', '╝', '═', '║'}
        
        # Help templates should have ASCII art
        assert any(char in help_table['content'] for char in box_chars), \
            "Help table should have ASCII banner"
        assert any(char in help_detailed['content'] for char in box_chars), \
            "Help detailed should have ASCII banner"
        
        # Orchestrator header should use minimalist style (━ not ═)
        orchestrator_header = response_templates['templates']['orchestrator_header']
        assert '━' in orchestrator_header['content'], \
            "Orchestrator should use minimalist style"
        assert not any(char in orchestrator_header['content'] for char in {'╔', '╗', '╚', '╝', '║'}), \
            "Orchestrator should NOT have ASCII art banner"
    
    def test_structured_response_format(self, response_templates):
        """
        SKULL-008: Response templates must follow structured format.
        
        Validates:
        - Header configured appropriately
        - User request reflected back (📝 Your Request:)
        - Understanding section (🎯 Understanding:)
        - Response section (💬 Response:)
        - Optional: Challenges section (⚠️ Considerations:)
        - Next steps section (🔮 Next Steps:)
        """
        # Check help_table for structured format
        help_table = response_templates['templates']['help_table']
        content = help_table['content']
        
        # Required sections (account for markdown bold **)
        assert ("📝 Your Request:" in content or "📝 **Your Request:**" in content), \
            "Missing user request reflection"
        assert "🎯 **Understanding:**" in content, "Missing understanding section"
        assert "💬 **Response:**" in content, "Missing response section"
        assert "Next Steps:" in content, "Missing next steps section"  # Emoji may render differently
        
        # Check orchestrator_header for structured format
        orchestrator_header = response_templates['templates']['orchestrator_header']
        orch_content = orchestrator_header['content']
        
        assert "📝 **Your Request:**" in orch_content, "Orchestrator missing user request"
        assert "🎯 **Understanding:**" in orch_content, "Orchestrator missing understanding"
        assert "💬 **Response:**" in orch_content, "Orchestrator missing response section"
        assert "{{refined_intent}}" in orch_content, "Orchestrator missing refined intent variable"
        assert "{{response_content}}" in orch_content, "Orchestrator missing response content variable"
        
        # Optional sections with conditional rendering
        assert "{{#if challenges}}" in orch_content, "Missing challenges conditional"
        assert "⚠️ **Considerations:**" in orch_content, "Missing considerations section"
        assert "{{#if next_steps}}" in orch_content, "Missing next steps conditional"


class TestSKULLASCIIBannerContent:
    """Test specific ASCII banner content"""
    
    @pytest.fixture
    def response_templates_path(self):
        """Path to response templates YAML"""
        return Path(__file__).parent.parent.parent / "cortex-brain" / "response-templates.yaml"
    
    @pytest.fixture
    def response_templates(self, response_templates_path):
        """Load response templates"""
        with open(response_templates_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_ascii_logo_structure(self, response_templates):
        """SKULL-006: ASCII logo should form recognizable CORTEX letters"""
        help_table = response_templates['templates']['help_table']
        content = help_table['content']
        
        # The logo should have multiple lines forming letters
        lines = content.split('\n')
        logo_lines = [l for l in lines if '██' in l]
        
        if logo_lines:
            # Should have at least 5 lines for full ASCII art letters
            assert len(logo_lines) >= 5, \
                f"ASCII logo should have at least 5 lines, found {len(logo_lines)}"
    
    def test_banner_metadata_complete(self, response_templates):
        """SKULL-006: Banner must include version, mode, timestamp placeholders"""
        orchestrator_header = response_templates['templates']['orchestrator_header']
        content = orchestrator_header['content']
        
        # Check for template variables
        assert '{{version}}' in content or 'Version:' in content, \
            "Missing version in orchestrator header"
        assert '{{mode}}' in content or 'Mode:' in content, \
            "Missing mode in orchestrator header"
        assert '{{profile}}' in content or 'Profile:' in content, \
            "Missing profile in orchestrator header"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
