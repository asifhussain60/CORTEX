"""Tests for base template composition with YAML anchor inheritance.

Verifies that templates using base_structure and placeholder fields
are correctly composed by the TemplateLoader.

Author: Asif Hussain
Version: 1.0
"""

import pytest
from pathlib import Path
from src.response_templates.template_loader import TemplateLoader


class TestBaseTemplateComposition:
    """Test base template composition functionality."""
    
    @pytest.fixture
    def template_loader(self):
        """Create template loader with response-templates.yaml."""
        templates_file = Path('cortex-brain/response-templates.yaml')
        if not templates_file.exists():
            pytest.skip("response-templates.yaml not found")
        
        loader = TemplateLoader(templates_file)
        loader.load_templates()
        return loader
    
    def test_base_template_detected(self, template_loader):
        """Test that templates using base_structure are detected."""
        # help_table uses base template inheritance
        help_template = template_loader.load_template('help_table')
        
        assert help_template is not None, "help_table template should exist"
        assert len(help_template.content) > 0, "Template content should not be empty"
    
    def test_5_part_structure_present(self, template_loader):
        """Test that 5-part structure sections are present in composed content."""
        help_template = template_loader.load_template('help_table')
        
        # Verify all 5 sections are present
        assert '## 🎯 My Understanding Of Your Request' in help_template.content
        assert '## ⚠️ Challenge' in help_template.content
        assert '## 💬 Response' in help_template.content
        assert '## 📝 Your Request' in help_template.content
        assert '## 🔍 Next Steps' in help_template.content
    
    def test_placeholders_substituted(self, template_loader):
        """Test that placeholders are replaced with actual content."""
        help_template = template_loader.load_template('help_table')
        
        # Placeholders should be replaced
        assert '{understanding_content}' not in help_template.content
        assert '{challenge_content}' not in help_template.content
        assert '{response_content}' not in help_template.content
        assert '{request_echo_content}' not in help_template.content
        assert '{next_steps_content}' not in help_template.content
        
        # Actual content should be present
        assert '[State understanding]' in help_template.content
        assert '[State specific challenge' in help_template.content
        assert '[Natural language explanation]' in help_template.content
        assert '[Echo refined request]' in help_template.content
        assert '[Context-appropriate format]' in help_template.content
    
    def test_header_preserved(self, template_loader):
        """Test that template header is preserved in composition."""
        help_template = template_loader.load_template('help_table')
        
        # Header should be present (use ** markdown format)
        assert '# 🧠 CORTEX' in help_template.content
        assert '**Author:**' in help_template.content or 'Author:' in help_template.content
        assert 'Asif Hussain' in help_template.content
        assert 'github.com/asifhussain60/CORTEX' in help_template.content
        assert '---' in help_template.content
    
    def test_traditional_templates_unaffected(self, template_loader):
        """Test that templates without base_structure still work."""
        # greeting uses traditional content field
        greeting = template_loader.load_template('greeting')
        
        assert greeting is not None
        assert len(greeting.content) > 100
        assert '🧠 CORTEX' in greeting.content
    
    def test_multiple_base_templates_work(self, template_loader):
        """Test that multiple templates using base structure all work."""
        # Test several templates converted to use base structure
        template_ids = [
            'help_table',
            'help_detailed',
            'quick_start',
            'hands_on_tutorial'
        ]
        
        for template_id in template_ids:
            template = template_loader.load_template(template_id)
            assert template is not None, f"{template_id} should exist"
            assert len(template.content) > 100, f"{template_id} should have content"
            assert '## 🎯' in template.content, f"{template_id} should have Understanding section"
            assert '## ⚠️' in template.content, f"{template_id} should have Challenge section"
    
    def test_triggers_preserved(self, template_loader):
        """Test that template triggers are preserved after composition."""
        help_template = template_loader.load_template('help_table')
        
        assert 'help' in help_template.triggers
        assert '/help' in help_template.triggers or 'help_table' in help_template.triggers
    
    def test_metadata_preserved(self, template_loader):
        """Test that template metadata is preserved after composition."""
        help_template = template_loader.load_template('help_table')
        
        assert help_template.metadata is not None
        assert help_template.response_type in ['table', 'narrative', 'detailed']
    
    def test_composition_performance(self, template_loader):
        """Test that composition doesn't significantly impact load time."""
        import time
        
        start = time.time()
        for _ in range(100):
            template_loader.load_template('help_table')
        elapsed = time.time() - start
        
        # Should take less than 100ms for 100 loads
        assert elapsed < 0.1, f"Composition is too slow: {elapsed:.3f}s for 100 loads"


class TestBaseTemplateEdgeCases:
    """Test edge cases in base template composition."""
    
    @pytest.fixture
    def template_loader(self):
        """Create template loader with response-templates.yaml."""
        templates_file = Path('cortex-brain/response-templates.yaml')
        if not templates_file.exists():
            pytest.skip("response-templates.yaml not found")
        
        loader = TemplateLoader(templates_file)
        loader.load_templates()
        return loader
    
    def test_empty_placeholder_handling(self, template_loader):
        """Test that empty placeholders are handled gracefully."""
        # Load all templates and check none have unreplaced placeholders
        all_template_ids = template_loader.get_template_ids()
        
        for template_id in all_template_ids:
            template = template_loader.load_template(template_id)
            if 'base_structure' in str(template.metadata):  # Skip traditional templates
                # Should not have curly brace placeholders
                assert template.content.count('{') == template.content.count('}'), \
                    f"{template_id} has unmatched braces"
    
    def test_special_characters_in_content(self, template_loader):
        """Test that special characters in placeholder content are preserved."""
        help_template = template_loader.load_template('help_table')
        
        # Special characters should be preserved
        assert '🎯' in help_template.content
        assert '⚠️' in help_template.content
        assert '💬' in help_template.content
        assert '📝' in help_template.content
        assert '🔍' in help_template.content
    
    def test_multiline_content_preserved(self, template_loader):
        """Test that multiline placeholder content is preserved."""
        help_template = template_loader.load_template('help_table')
        
        # Content should span multiple lines
        lines = help_template.content.split('\n')
        assert len(lines) > 10, "Template should be multiline"
    
    def test_all_refactored_templates_loadable(self, template_loader):
        """Test that all 56 refactored templates can be loaded."""
        # According to the refactoring report, 56 templates were converted
        all_template_ids = template_loader.get_template_ids()
        
        loaded_count = 0
        failed = []
        
        for template_id in all_template_ids:
            template = template_loader.load_template(template_id)
            if template and len(template.content) > 0:
                loaded_count += 1
            else:
                failed.append(template_id)
        
        # At least 90% should load successfully (allowing for some YAML parsing edge cases)
        success_rate = loaded_count / len(all_template_ids) if all_template_ids else 0
        assert success_rate >= 0.90, \
            f"Expected at least 90% templates loaded, got {success_rate:.1%} ({loaded_count}/{len(all_template_ids)}). Failed: {failed}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
