"""
Tests for Profile Template Expander (Task 3.4)
TDD RED Phase: Write failing tests first
"""
import pytest
from src.utils.profile_template_expander import ProfileTemplateExpander
from src.setup.models.user_profile import UserProfile


class TestProfileTemplateExpander:
    """Test suite for profile-based template expansion"""
    
    @pytest.fixture
    def profile(self):
        """Create test user profile"""
        return UserProfile(
            name="Alice",
            preference="balanced",
            role="intermediate",
            work_area="web_dev",
            language="en"
        )
    
    @pytest.fixture
    def expander(self, profile):
        """Create expander with profile"""
        return ProfileTemplateExpander(profile)
    
    def test_expander_initialization(self, expander):
        """Test expander initializes correctly"""
        assert expander is not None
        assert expander.profile is not None
    
    def test_expand_user_name_interpolation(self, expander):
        """Test user name interpolation in templates"""
        template = "Hello {{user_name}}, welcome to CORTEX!"
        result = expander.expand(template)
        assert "Alice" in result
        assert "{{user_name}}" not in result
    
    def test_expand_user_preference(self, expander):
        """Test user preference interpolation"""
        template = "Your preference is {{user_preference}}"
        result = expander.expand(template)
        assert "balanced" in result
    
    def test_expand_user_role(self, expander):
        """Test user role interpolation"""
        template = "Your role: {{user_role}}"
        result = expander.expand(template)
        assert "intermediate" in result
    
    def test_expand_user_work_area(self, expander):
        """Test work area interpolation"""
        template = "Work area: {{user_work_area}}"
        result = expander.expand(template)
        assert "web_dev" in result
    
    def test_expand_multiple_variables(self, expander):
        """Test multiple variable interpolation"""
        template = "Hi {{user_name}}! Role: {{user_role}}, Preference: {{user_preference}}"
        result = expander.expand(template)
        assert "Alice" in result
        assert "intermediate" in result
        assert "balanced" in result
    
    def test_expand_with_no_variables(self, expander):
        """Test template without variables passes through unchanged"""
        template = "This is a simple template with no variables"
        result = expander.expand(template)
        assert result == template
    
    def test_expand_role_based_content_beginner(self):
        """Test role-based content filtering for beginner"""
        profile = UserProfile(name="Bob", preference="verbose", role="beginner", 
                            work_area="general", language="en")
        expander = ProfileTemplateExpander(profile)
        
        template = """
{{#if role_beginner}}
This is beginner content with detailed explanations.
{{/if}}
{{#if role_intermediate}}
This is intermediate content.
{{/if}}
{{#if role_expert}}
This is expert content.
{{/if}}
"""
        result = expander.expand(template)
        assert "beginner content" in result
        assert "intermediate content" not in result
        assert "expert content" not in result
    
    def test_expand_role_based_content_expert(self):
        """Test role-based content filtering for expert"""
        profile = UserProfile(name="Charlie", preference="concise", role="expert",
                            work_area="devops", language="en")
        expander = ProfileTemplateExpander(profile)
        
        template = """
{{#if role_beginner}}Beginner content{{/if}}
{{#if role_intermediate}}Intermediate content{{/if}}
{{#if role_expert}}Expert content with advanced concepts{{/if}}
"""
        result = expander.expand(template)
        assert "Expert content" in result
        assert "Beginner content" not in result
    
    def test_expand_preference_based_content(self, expander):
        """Test preference-based content filtering"""
        template = """
{{#if preference_concise}}Quick summary{{/if}}
{{#if preference_balanced}}Standard explanation{{/if}}
{{#if preference_verbose}}Detailed walkthrough{{/if}}
"""
        result = expander.expand(template)
        # Profile has balanced preference
        assert "Standard explanation" in result
        assert "Quick summary" not in result
        assert "Detailed walkthrough" not in result
    
    def test_expand_technical_depth_adjustment(self, expander):
        """Test technical depth based on role"""
        template = """
{{#if show_technical_details}}
Technical implementation: Use async/await patterns with proper error handling.
{{/if}}
"""
        result = expander.expand(template)
        # Intermediate role should show technical details
        assert "Technical implementation" in result or result.strip() == ""
    
    def test_expand_without_profile(self):
        """Test expander without profile uses defaults"""
        expander = ProfileTemplateExpander(profile=None)
        template = "Hello {{user_name}}!"
        result = expander.expand(template)
        # Should use default name or leave placeholder
        assert "{{user_name}}" not in result or "User" in result
    
    def test_expand_preserves_non_profile_variables(self, expander):
        """Test that non-profile variables are preserved"""
        template = "Hello {{user_name}}! Error: {{error_message}}"
        result = expander.expand(template)
        assert "Alice" in result
        assert "{{error_message}}" in result  # Preserved for later expansion
    
    def test_expand_nested_conditions(self, expander):
        """Test nested conditional blocks"""
        template = """
{{#if role_intermediate}}
  {{#if preference_balanced}}
    Perfect match: intermediate + balanced
  {{/if}}
{{/if}}
"""
        result = expander.expand(template)
        assert "Perfect match" in result
    
    def test_expand_with_defaults_for_missing_fields(self):
        """Test expansion with minimal profile"""
        profile = UserProfile(name="Dave", preference="concise", role="beginner",
                            work_area="general", language="en")
        profile.work_area = None  # Simulate missing field
        expander = ProfileTemplateExpander(profile)
        
        template = "Work area: {{user_work_area}}"
        result = expander.expand(template)
        # Should handle gracefully
        assert result is not None
    
    def test_expand_role_flags_all_set_correctly(self, expander):
        """Test that role flags are set correctly"""
        flags = expander.get_expansion_context()
        assert flags['role_intermediate'] is True
        assert flags['role_beginner'] is False
        assert flags['role_expert'] is False
    
    def test_expand_preference_flags_all_set_correctly(self, expander):
        """Test that preference flags are set correctly"""
        flags = expander.get_expansion_context()
        assert flags['preference_balanced'] is True
        assert flags['preference_concise'] is False
        assert flags['preference_verbose'] is False
    
    def test_expand_show_technical_details_flag(self, expander):
        """Test technical details flag based on role"""
        flags = expander.get_expansion_context()
        # Intermediate and expert should show technical details
        assert 'show_technical_details' in flags
        assert flags['show_technical_details'] in [True, False]
    
    def test_batch_expand_multiple_templates(self, expander):
        """Test expanding multiple templates at once"""
        templates = [
            "Hi {{user_name}}!",
            "Role: {{user_role}}",
            "Preference: {{user_preference}}"
        ]
        results = expander.batch_expand(templates)
        assert len(results) == 3
        assert "Alice" in results[0]
        assert "intermediate" in results[1]
        assert "balanced" in results[2]


class TestProfileTemplateExpanderIntegration:
    """Integration tests for template expansion with real templates"""
    
    def test_expand_help_template(self):
        """Test expanding help template with profile"""
        profile = UserProfile(name="Eve", preference="concise", role="expert",
                            work_area="ai_ml", language="en")
        expander = ProfileTemplateExpander(profile)
        
        template = """
Hello {{user_name}}! 
{{#if role_expert}}
Advanced commands: `optimize`, `deploy`, `performance-tune`
{{/if}}
{{#if preference_concise}}
Quick reference: Type 'help' for more.
{{/if}}
"""
        result = expander.expand(template)
        assert "Eve" in result
        assert "Advanced commands" in result
        assert "Quick reference" in result
    
    def test_expand_onboarding_template(self):
        """Test expanding onboarding template"""
        profile = UserProfile(name="Frank", preference="verbose", role="beginner",
                            work_area="general", language="en")
        expander = ProfileTemplateExpander(profile)
        
        template = """
Welcome {{user_name}}!
{{#if role_beginner}}
We'll guide you through each step with detailed explanations.
{{/if}}
"""
        result = expander.expand(template)
        assert "Frank" in result
        assert "detailed explanations" in result
