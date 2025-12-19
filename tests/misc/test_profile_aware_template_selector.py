"""
Tests for Profile-Aware Template Selector (Task 3.1)
TDD RED Phase: Write failing tests first
"""
import pytest
from unittest.mock import patch, MagicMock
from src.setup.models.user_profile import UserProfile
from src.utils.profile_aware_template_selector import ProfileAwareTemplateSelector


class TestProfileAwareTemplateSelector:
    """Test suite for profile-aware template selection"""
    
    @pytest.fixture
    def english_profile(self):
        """Create English user profile"""
        return UserProfile(
            name="Test User",
            preference="balanced",
            role="intermediate",
            work_area="web_dev",
            language="en"
        )
    
    @pytest.fixture
    def spanish_profile(self):
        """Create Spanish user profile"""
        return UserProfile(
            name="Usuario Prueba",
            preference="verbose",
            role="beginner",
            work_area="general",
            language="es"
        )
    
    @pytest.fixture
    def concise_profile(self):
        """Create concise preference profile"""
        return UserProfile(
            name="Brief User",
            preference="concise",
            role="expert",
            work_area="ai_ml",
            language="en"
        )
    
    def test_selector_initialization(self):
        """Test selector can be instantiated"""
        selector = ProfileAwareTemplateSelector()
        assert selector is not None
    
    def test_selector_with_profile(self, english_profile):
        """Test selector accepts user profile"""
        selector = ProfileAwareTemplateSelector(profile=english_profile)
        assert selector.profile == english_profile
    
    def test_select_template_uses_profile_language(self, spanish_profile):
        """Test template selection uses profile language"""
        selector = ProfileAwareTemplateSelector(profile=spanish_profile)
        
        result = selector.select_template("help", context={})
        
        # Should select Spanish template
        assert result.language == "es"
        assert "template" in result.template_id
    
    def test_select_template_fallback_to_english(self):
        """Test fallback to English when profile language not available"""
        # Create profile with unsupported language
        profile = UserProfile(
            name="Test",
            preference="balanced",
            role="intermediate",
            work_area="general",
            language="zh"  # Chinese
        )
        
        selector = ProfileAwareTemplateSelector(profile=profile)
        
        result = selector.select_template("help", context={})
        
        # Should fallback to English
        assert result.language == "en"
    
    def test_select_template_filters_by_verbosity(self, concise_profile):
        """Test template selection filters by verbosity preference"""
        selector = ProfileAwareTemplateSelector(profile=concise_profile)
        
        result = selector.select_template("explain setup", context={})
        
        # Should select concise variant
        assert result.verbosity == "concise"
        assert "concise" in result.template_id or result.verbosity == "concise"
    
    def test_select_template_balanced_verbosity(self, english_profile):
        """Test balanced verbosity preference"""
        selector = ProfileAwareTemplateSelector(profile=english_profile)
        
        result = selector.select_template("help", context={})
        
        # Should select balanced variant
        assert result.verbosity in ["balanced", "verbose"]  # Balanced or default
    
    def test_select_template_without_profile(self):
        """Test template selection without profile uses defaults"""
        with patch('src.utils.profile_aware_template_selector.UserProfileStorage') as mock_storage:
            mock_storage.return_value.load_profile.return_value = None
            selector = ProfileAwareTemplateSelector()
            
            result = selector.select_template("help", context={})
            
            # Should use default language (English) and verbosity (verbose)
            assert result.language == "en"
            assert result.verbosity == "verbose"
    
    def test_select_template_role_aware(self):
        """Test template selection considers user role"""
        # Expert user
        expert_profile = UserProfile(
            name="Expert",
            preference="concise",
            role="expert",
            work_area="ai_ml",
            language="en"
        )
        
        selector = ProfileAwareTemplateSelector(profile=expert_profile)
        result = selector.select_template("explain concept", context={})
        
        # Expert templates should be more technical
        assert result.role == "expert"
    
    def test_get_available_languages(self):
        """Test getting list of available template languages"""
        selector = ProfileAwareTemplateSelector()
        
        languages = selector.get_available_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "es" in languages
        assert len(languages) >= 2  # At least English and Spanish
    
    def test_get_template_variants(self):
        """Test getting available template variants"""
        selector = ProfileAwareTemplateSelector()
        
        variants = selector.get_template_variants("help")
        
        assert isinstance(variants, dict)
        assert "languages" in variants
        assert "verbosity_levels" in variants
    
    def test_select_template_with_context_override(self, english_profile):
        """Test context can override profile preferences"""
        selector = ProfileAwareTemplateSelector(profile=english_profile)
        
        # Context overrides language
        result = selector.select_template(
            "help",
            context={"force_language": "es", "force_verbosity": "concise"}
        )
        
        assert result.language == "es"
        assert result.verbosity == "concise"
    
    def test_select_template_caches_results(self, english_profile):
        """Test template selection caching for performance"""
        selector = ProfileAwareTemplateSelector(profile=english_profile)
        
        # First call
        result1 = selector.select_template("help", context={})
        
        # Second call with same input
        result2 = selector.select_template("help", context={})
        
        # Should return same template ID
        assert result1.template_id == result2.template_id
    
    def test_load_profile_from_storage(self):
        """Test loading profile from storage automatically"""
        with patch('src.utils.profile_aware_template_selector.UserProfileStorage') as mock_storage:
            mock_profile = UserProfile(
                name="Stored User",
                preference="concise",
                role="intermediate",
                work_area="web_dev",
                language="fr"
            )
            mock_storage.return_value.load_profile.return_value = mock_profile
            
            selector = ProfileAwareTemplateSelector()
            
            # Should load profile from storage
            assert selector.profile is not None
            assert selector.profile.language == "fr"
    
    def test_template_selection_result_structure(self, english_profile):
        """Test selection result has expected structure"""
        selector = ProfileAwareTemplateSelector(profile=english_profile)
        
        result = selector.select_template("help", context={})
        
        assert hasattr(result, 'template_id')
        assert hasattr(result, 'language')
        assert hasattr(result, 'verbosity')
        assert hasattr(result, 'role')
        assert hasattr(result, 'confidence')
