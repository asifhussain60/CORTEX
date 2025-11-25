"""
Test Template Trigger Routing

Verifies that different user requests match different response templates
based on trigger phrases defined in response-templates.yaml.

This test validates that the template system is NOT always falling back
to the default template.

Author: Asif Hussain
Copyright: © 2024-2025
"""

import pytest
from pathlib import Path
from src.response_templates.template_loader import TemplateLoader


class TestTemplateTriggerRouting:
    """Test that different triggers route to different templates"""
    
    @pytest.fixture
    def loader(self):
        """Initialize template loader"""
        template_file = Path("cortex-brain/templates/response-templates.yaml")
        loader = TemplateLoader(template_file)
        loader.load_templates()
        return loader
    
    def test_help_trigger_routes_to_help_table(self, loader):
        """'help' should match help_table template"""
        template = loader.find_by_trigger("help")
        assert template is not None, "No template found for 'help'"
        assert template.template_id == "help_table", \
            f"Expected help_table, got {template.template_id}"
    
    def test_status_trigger_routes_to_status_check(self, loader):
        """'status' should match status_check template"""
        template = loader.find_by_trigger("status")
        assert template is not None, "No template found for 'status'"
        assert template.template_id == "status_check", \
            f"Expected status_check, got {template.template_id}"
    
    def test_plan_trigger_routes_to_work_planner(self, loader):
        """'plan a feature' should match work_planner_success template"""
        template = loader.find_by_trigger("plan a feature")
        assert template is not None, "No template found for 'plan a feature'"
        assert template.template_id == "work_planner_success", \
            f"Expected work_planner_success, got {template.template_id}"
    
    def test_export_brain_trigger_routes_correctly(self, loader):
        """'export brain' should match brain_export_guide template"""
        template = loader.find_by_trigger("export brain")
        assert template is not None, "No template found for 'export brain'"
        assert template.template_id == "brain_export_guide", \
            f"Expected brain_export_guide, got {template.template_id}"
    
    def test_import_brain_trigger_routes_correctly(self, loader):
        """'import brain' should match brain_import_guide template"""
        template = loader.find_by_trigger("import brain")
        assert template is not None, "No template found for 'import brain'"
        assert template.template_id == "brain_import_guide", \
            f"Expected brain_import_guide, got {template.template_id}"
    
    def test_enhance_trigger_routes_correctly(self, loader):
        """'enhance existing' should match enhance_existing template"""
        template = loader.find_by_trigger("enhance existing")
        assert template is not None, "No template found for 'enhance existing'"
        assert template.template_id == "enhance_existing", \
            f"Expected enhance_existing, got {template.template_id}"
    
    def test_random_request_uses_fallback(self, loader):
        """Unknown triggers should use fallback template"""
        template = loader.find_by_trigger("some completely random request that has no trigger")
        # Either finds nothing (None) or finds fallback
        if template:
            # Fallback template should have '*' as trigger
            assert '*' in template.triggers or template.template_id == "fallback"
    
    def test_all_templates_have_triggers(self, loader):
        """All templates should have at least one trigger defined (except special indicator templates)"""
        all_templates = loader.list_templates()
        templates_without_triggers = []
        
        # Confidence templates are special indicators, not user-triggered
        special_templates = ['confidence_high', 'confidence_medium', 'confidence_low', 'confidence_none']
        
        for template in all_templates:
            if not template.triggers and template.template_id not in special_templates:
                templates_without_triggers.append(template.template_id)
        
        assert len(templates_without_triggers) == 0, \
            f"Templates without triggers: {templates_without_triggers}"
    
    def test_template_content_differs(self, loader):
        """Different templates should have different content"""
        help_template = loader.find_by_trigger("help")
        status_template = loader.find_by_trigger("status")
        plan_template = loader.find_by_trigger("plan a feature")
        
        assert help_template is not None
        assert status_template is not None
        assert plan_template is not None
        
        # Content should be different
        assert help_template.content != status_template.content
        assert help_template.content != plan_template.content
        assert status_template.content != plan_template.content
    
    def test_trigger_indexing_works(self, loader):
        """Trigger index should enable fast lookups"""
        # Test exact match
        template = loader.find_by_trigger("help")
        assert template is not None
        assert template.template_id == "help_table"
        
        # Test fuzzy match (contains)
        template = loader.find_by_trigger("i want to plan something")
        assert template is not None
        assert template.template_id == "work_planner_success"
    
    def test_case_insensitive_matching(self, loader):
        """Trigger matching should be case insensitive"""
        lower_case = loader.find_by_trigger("help")
        upper_case = loader.find_by_trigger("HELP")
        mixed_case = loader.find_by_trigger("Help")
        
        assert lower_case is not None
        assert upper_case is not None
        assert mixed_case is not None
        
        assert lower_case.template_id == upper_case.template_id == mixed_case.template_id
    
    def test_multiple_triggers_same_template(self, loader):
        """One template can have multiple trigger phrases"""
        # work_planner_success has many triggers: plan, let's plan, planning, etc.
        triggers = ["plan", "let's plan", "planning", "help me plan"]
        templates = [loader.find_by_trigger(t) for t in triggers]
        
        # All should find the same template
        template_ids = set(t.template_id for t in templates if t)
        assert len(template_ids) == 1, \
            f"Multiple triggers should map to same template, got: {template_ids}"
        assert "work_planner_success" in template_ids


class TestTemplateLoadingPerformance:
    """Test template loading performance"""
    
    @pytest.fixture
    def loader(self):
        """Initialize template loader"""
        template_file = Path("cortex-brain/templates/response-templates.yaml")
        return TemplateLoader(template_file)
    
    def test_lazy_loading(self, loader):
        """Templates should not be loaded until requested"""
        # Before loading
        assert not loader._loaded
        assert len(loader._templates) == 0
        
        # After loading
        loader.load_templates()
        assert loader._loaded
        assert len(loader._templates) > 0
    
    def test_caching(self, loader):
        """Subsequent loads should use cache"""
        import time
        
        # First load
        start = time.time()
        loader.load_templates()
        first_load_time = time.time() - start
        
        # Reset internal state but keep cache
        loader._loaded = False
        
        # Second load (should be faster due to OS file cache)
        start = time.time()
        loader.load_templates()
        second_load_time = time.time() - start
        
        # Second load should be comparable or faster
        # (file system cache helps)
        assert second_load_time <= first_load_time * 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
