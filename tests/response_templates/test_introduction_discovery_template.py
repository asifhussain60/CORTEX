"""
Test Introduction Discovery Template

Validates that the introduction_discovery template is properly configured
and can be loaded from response-templates.yaml.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path


class TestIntroductionDiscoveryTemplate:
    """Test introduction_discovery template configuration"""
    
    @pytest.fixture
    def response_templates(self):
        """Load response templates"""
        template_file = Path("cortex-brain/response-templates.yaml")
        if not template_file.exists():
            pytest.skip("response-templates.yaml not found")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_template_exists(self, response_templates):
        """Test introduction_discovery template exists"""
        assert 'templates' in response_templates
        assert 'introduction_discovery' in response_templates['templates']
    
    def test_template_has_required_fields(self, response_templates):
        """Test template has all required fields"""
        template = response_templates['templates']['introduction_discovery']
        
        assert 'name' in template
        assert 'triggers' in template
        assert 'response_type' in template
        assert 'content' in template
    
    def test_template_triggers_configured(self, response_templates):
        """Test template has discovery triggers"""
        template = response_templates['templates']['introduction_discovery']
        triggers = template['triggers']
        
        # Should have multiple triggers
        assert len(triggers) > 0
        
        # Check key triggers
        expected_triggers = [
            'discover cortex',
            'explore cortex',
            'cortex demo',
            'what can you do',
            'cortex capabilities'
        ]
        
        for trigger in expected_triggers:
            assert trigger in triggers, f"Missing trigger: {trigger}"
    
    def test_template_response_type(self, response_templates):
        """Test template response type is interactive"""
        template = response_templates['templates']['introduction_discovery']
        assert template['response_type'] == 'interactive'
    
    def test_template_content_structure(self, response_templates):
        """Test template content has required sections"""
        template = response_templates['templates']['introduction_discovery']
        content = template['content']
        
        # Check for mandatory response format sections
        assert '# 🧠 CORTEX' in content
        assert '## 🎯 My Understanding Of Your Request' in content
        assert '## ⚠️ Challenge' in content
        assert '## 💬 Response' in content
        assert '## 📝 Your Request' in content
        assert '## 🔍 Next Steps' in content
    
    def test_template_content_has_discovery_options(self, response_templates):
        """Test template content includes discovery options"""
        template = response_templates['templates']['introduction_discovery']
        content = template['content']
        
        # Check for key discovery sections
        assert 'Quick Demos' in content
        assert 'Deep Dives' in content
        assert 'Documentation' in content
        assert 'Learning Paths' in content
    
    def test_template_content_has_features(self, response_templates):
        """Test template content mentions key CORTEX features"""
        template = response_templates['templates']['introduction_discovery']
        content = template['content']
        
        # Check for key features mentioned
        assert 'Planning System' in content or 'planning' in content.lower()
        assert 'TDD' in content or 'Test-Driven Development' in content
        assert 'Brain Architecture' in content or 'brain' in content.lower()
        assert 'tutorial' in content.lower()


class TestDiscoveryTriggers:
    """Test discovery triggers are registered"""
    
    @pytest.fixture
    def response_templates(self):
        """Load response templates"""
        template_file = Path("cortex-brain/response-templates.yaml")
        if not template_file.exists():
            pytest.skip("response-templates.yaml not found")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_discovery_triggers_list_exists(self, response_templates):
        """Test discovery_triggers list exists in routing section"""
        assert 'routing' in response_templates
        assert 'discovery_triggers' in response_templates['routing']
    
    def test_discovery_triggers_comprehensive(self, response_templates):
        """Test discovery_triggers list is comprehensive"""
        triggers = response_templates['routing']['discovery_triggers']
        
        # Should have multiple variations
        assert len(triggers) >= 8, "Should have at least 8 trigger variations"
        
        # Check key variations exist
        assert 'discover cortex' in triggers
        assert 'cortex demo' in triggers
        assert 'explore cortex' in triggers


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
