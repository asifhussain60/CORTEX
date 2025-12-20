"""
Integration Tests for Profile Template System (Task 3.5)
TDD RED Phase: End-to-end testing of profile-aware template system
"""
import pytest
from pathlib import Path
from src.setup.models.user_profile import UserProfile
from src.utils.profile_aware_template_selector import ProfileAwareTemplateSelector
from src.utils.multilingual_template_loader import MultilingualTemplateLoader
from src.utils.profile_template_expander import ProfileTemplateExpander


class TestProfileTemplateIntegration:
    """Integration tests for complete profile template flow"""
    
    @pytest.fixture
    def english_beginner_profile(self):
        """English-speaking beginner user"""
        return UserProfile(
            name="Alice",
            preference="verbose",
            role="beginner",
            work_area="web_dev",
            language="en"
        )
    
    @pytest.fixture
    def spanish_expert_profile(self):
        """Spanish-speaking expert user"""
        return UserProfile(
            name="Carlos",
            preference="concise",
            role="expert",
            work_area="devops",
            language="es"
        )
    
    def test_end_to_end_template_selection_and_expansion(self, english_beginner_profile):
        """Test complete flow: profile → selector → loader → expander"""
        # Step 1: Profile-aware selection
        selector = ProfileAwareTemplateSelector(profile=english_beginner_profile)
        selection = selector.select_template("help")
        
        assert selection.language == "en"
        assert selection.verbosity == "verbose"
        assert selection.role == "beginner"
        
        # Step 2: Load multilingual template
        loader = MultilingualTemplateLoader()
        template = loader.get_template("help", language=selection.language, 
                                      verbosity=selection.verbosity)
        
        assert template is not None
        assert len(template) > 0
        
        # Step 3: Expand with profile data
        expander = ProfileTemplateExpander(english_beginner_profile)
        expanded = expander.expand(template)
        
        assert expanded is not None
        assert len(expanded) > 0
    
    def test_spanish_concise_expert_flow(self, spanish_expert_profile):
        """Test flow for Spanish-speaking expert with concise preference"""
        # Selection
        selector = ProfileAwareTemplateSelector(profile=spanish_expert_profile)
        selection = selector.select_template("help")
        
        assert selection.language == "es"
        assert selection.verbosity == "concise"
        assert selection.role == "expert"
        
        # Loading
        loader = MultilingualTemplateLoader()
        template = loader.get_template("help", language="es", verbosity="concise")
        
        assert template is not None
        assert "Ayuda" in template or "ayuda" in template.lower()
        
        # Expansion
        expander = ProfileTemplateExpander(spanish_expert_profile)
        expanded = expander.expand(template)
        
        assert "Carlos" not in expanded  # Name not in help template
        assert expanded is not None
    
    def test_template_with_profile_variables(self, english_beginner_profile):
        """Test template with {{user_name}} and role conditionals"""
        template_content = """
Welcome {{user_name}}!

{{#if role_beginner}}
We'll guide you step-by-step with detailed explanations.
{{/if}}

{{#if role_expert}}
Advanced features available. Check documentation for details.
{{/if}}
"""
        expander = ProfileTemplateExpander(english_beginner_profile)
        result = expander.expand(template_content)
        
        assert "Alice" in result
        assert "step-by-step" in result
        assert "Advanced features" not in result
    
    def test_fallback_to_english_for_unsupported_language(self):
        """Test fallback when language not available in templates"""
        profile = UserProfile(
            name="Yuki",
            preference="balanced",
            role="intermediate",
            work_area="general",
            language="ja"  # Japanese
        )
        
        selector = ProfileAwareTemplateSelector(profile=profile)
        selection = selector.select_template("help")
        
        # Should fallback to English
        assert selection.language == "en"
        
        loader = MultilingualTemplateLoader()
        template = loader.get_template("help", language=selection.language,
                                      verbosity=selection.verbosity)
        
        assert template is not None
        # Should be English content
        assert "help" in template.lower() or "CORTEX" in template
    
    def test_context_override_forces_language(self, spanish_expert_profile):
        """Test context override for language selection"""
        selector = ProfileAwareTemplateSelector(profile=spanish_expert_profile)
        
        # Override to English despite Spanish profile
        selection = selector.select_template("help", context={'force_language': 'en'})
        
        assert selection.language == "en"
        
        loader = MultilingualTemplateLoader()
        template = loader.get_template("help", language="en", verbosity="concise")
        
        assert "Quick Help" in template or "help" in template.lower()
    
    def test_multiple_templates_batch_processing(self, english_beginner_profile):
        """Test batch processing multiple templates"""
        templates = [
            "Hello {{user_name}}!",
            "Your role is {{user_role}}",
            "Preference: {{user_preference}}"
        ]
        
        expander = ProfileTemplateExpander(english_beginner_profile)
        results = expander.batch_expand(templates)
        
        assert len(results) == 3
        assert "Alice" in results[0]
        assert "beginner" in results[1]
        assert "verbose" in results[2]
    
    def test_caching_improves_performance(self, english_beginner_profile):
        """Test that template caching works"""
        selector = ProfileAwareTemplateSelector(profile=english_beginner_profile)
        loader = MultilingualTemplateLoader()
        
        # First load
        template1 = loader.get_template("help", "en", "verbose")
        cache_hits_before = loader.cache_hits
        
        # Second load (should hit cache)
        template2 = loader.get_template("help", "en", "verbose")
        cache_hits_after = loader.cache_hits
        
        assert template1 == template2
        assert cache_hits_after > cache_hits_before
    
    def test_preference_determines_verbosity_level(self):
        """Test that preference correctly maps to verbosity"""
        test_cases = [
            ("concise", "concise"),
            ("balanced", "balanced"),
            ("verbose", "verbose"),
        ]
        
        for preference, expected_verbosity in test_cases:
            profile = UserProfile(
                name="Test",
                preference=preference,
                role="intermediate",
                work_area="general",
                language="en"
            )
            
            selector = ProfileAwareTemplateSelector(profile=profile)
            selection = selector.select_template("help")
            
            assert selection.verbosity == expected_verbosity


class TestProfileTemplateSystemIntegration:
    """System-level integration tests"""
    
    def test_all_template_types_available(self):
        """Test that all core template types are available"""
        loader = MultilingualTemplateLoader()
        
        core_templates = ["help", "onboarding", "feedback", "tutorial", "error", "success"]
        
        for template_name in core_templates:
            template = loader.get_template(template_name, "en", "balanced")
            assert template is not None, f"Template {template_name} should exist"
            assert len(template) > 0, f"Template {template_name} should not be empty"
    
    def test_all_languages_have_help_template(self):
        """Test that all supported languages have help template"""
        loader = MultilingualTemplateLoader()
        languages = loader.get_supported_languages()
        
        for lang in languages:
            template = loader.get_template("help", lang, "balanced")
            # English fallback should work
            assert template is not None, f"Help template should exist for {lang}"
    
    def test_role_based_content_filtering_works(self):
        """Test that role-based conditionals filter correctly"""
        profiles = [
            UserProfile(name="B", preference="balanced", role="beginner", work_area="general", language="en"),
            UserProfile(name="I", preference="balanced", role="intermediate", work_area="general", language="en"),
            UserProfile(name="E", preference="balanced", role="expert", work_area="general", language="en"),
        ]
        
        template = """
{{#if role_beginner}}Beginner content{{/if}}
{{#if role_intermediate}}Intermediate content{{/if}}
{{#if role_expert}}Expert content{{/if}}
"""
        
        for profile in profiles:
            expander = ProfileTemplateExpander(profile)
            result = expander.expand(template)
            
            if profile.role == "beginner":
                assert "Beginner content" in result
                assert "Intermediate content" not in result
            elif profile.role == "intermediate":
                assert "Intermediate content" in result
                assert "Beginner content" not in result
            elif profile.role == "expert":
                assert "Expert content" in result
                assert "Beginner content" not in result
    
    def test_template_system_handles_missing_profile(self):
        """Test graceful degradation without profile"""
        # Mock storage to return None
        from unittest.mock import patch
        
        with patch('src.utils.profile_aware_template_selector.UserProfileStorage') as mock_storage:
            mock_storage.return_value.load_profile.return_value = None
            
            selector = ProfileAwareTemplateSelector(profile=None)
            selection = selector.select_template("help")
            
            # Should use defaults
            assert selection.language == "en"
            assert selection.verbosity == "verbose"
            assert selection.role == "intermediate"
            
            loader = MultilingualTemplateLoader()
            template = loader.get_template("help", "en", "verbose")
            
            assert template is not None
            
            expander = ProfileTemplateExpander(profile=None)
            expanded = expander.expand(template)
            
            assert expanded is not None
    
    def test_template_variables_preserve_non_profile_vars(self):
        """Test that non-profile variables are preserved for later expansion"""
        profile = UserProfile(name="Test", preference="balanced", role="intermediate",
                            work_area="general", language="en")
        
        template = "Hello {{user_name}}! Error: {{error_message}}, Code: {{error_code}}"
        
        expander = ProfileTemplateExpander(profile)
        result = expander.expand(template)
        
        # Profile variable should be expanded
        assert "Test" in result
        assert "{{user_name}}" not in result
        
        # Non-profile variables should be preserved
        assert "{{error_message}}" in result
        assert "{{error_code}}" in result
    
    def test_nested_conditionals_work_correctly(self):
        """Test nested role and preference conditionals"""
        profile = UserProfile(name="Alice", preference="concise", role="expert",
                            work_area="ai_ml", language="en")
        
        template = """
{{#if role_expert}}
  {{#if preference_concise}}
    Advanced commands: optimize, deploy, tune
  {{/if}}
  {{#if preference_verbose}}
    Detailed expert documentation available
  {{/if}}
{{/if}}
"""
        
        expander = ProfileTemplateExpander(profile)
        result = expander.expand(template)
        
        assert "Advanced commands" in result
        assert "Detailed expert" not in result
    
    def test_template_id_construction(self):
        """Test that template IDs are constructed correctly"""
        profile = UserProfile(name="Test", preference="balanced", role="intermediate",
                            work_area="general", language="es")
        
        selector = ProfileAwareTemplateSelector(profile=profile)
        selection = selector.select_template("help")
        
        # Template ID format may include additional prefixes
        assert "help" in selection.template_id
        assert "es" in selection.template_id
        assert "balanced" in selection.template_id
        assert selection.language == "es"
        assert selection.verbosity == "balanced"
