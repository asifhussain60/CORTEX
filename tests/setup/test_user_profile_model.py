"""
Test Suite for User Profile Model

Tests Pydantic schema validation for user profiles with multilingual support.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pydantic import ValidationError
from src.setup.models.user_profile import UserProfile, SUPPORTED_LANGUAGES


class TestUserProfileModel:
    """Test UserProfile Pydantic model."""
    
    def test_user_profile_creation_with_all_fields(self):
        """Test creating profile with all required fields."""
        profile = UserProfile(
            name="Asif Hussain",
            preference="concise",
            role="expert",
            work_area="ai_ml",
            language="en"
        )
        
        assert profile.name == "Asif Hussain"
        assert profile.preference == "concise"
        assert profile.role == "expert"
        assert profile.work_area == "ai_ml"
        assert profile.language == "en"
    
    def test_user_profile_with_defaults(self):
        """Test profile creation with default values."""
        profile = UserProfile(
            name="Test User"
        )
        
        assert profile.name == "Test User"
        assert profile.preference == "verbose"  # Default
        assert profile.role == "intermediate"    # Default
        assert profile.work_area == "general"   # Default
        assert profile.language == "en"          # Default
    
    def test_user_profile_invalid_language_code(self):
        """Test validation rejects invalid language codes."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(
                name="Test User",
                language="invalid"
            )
        
        assert "language" in str(exc_info.value).lower()
    
    def test_user_profile_all_supported_languages(self):
        """Test all 12 supported languages are valid."""
        for lang_code in SUPPORTED_LANGUAGES.keys():
            profile = UserProfile(
                name="Test User",
                language=lang_code
            )
            assert profile.language == lang_code
    
    def test_user_profile_preference_validation(self):
        """Test preference field accepts valid values."""
        valid_preferences = ["concise", "verbose", "balanced"]
        
        for pref in valid_preferences:
            profile = UserProfile(
                name="Test User",
                preference=pref
            )
            assert profile.preference == pref
    
    def test_user_profile_invalid_preference(self):
        """Test preference validation rejects invalid values."""
        with pytest.raises(ValidationError):
            UserProfile(
                name="Test User",
                preference="invalid"
            )
    
    def test_user_profile_role_validation(self):
        """Test role field accepts valid values."""
        valid_roles = ["beginner", "intermediate", "expert"]
        
        for role in valid_roles:
            profile = UserProfile(
                name="Test User",
                role=role
            )
            assert profile.role == role
    
    def test_user_profile_invalid_role(self):
        """Test role validation rejects invalid values."""
        with pytest.raises(ValidationError):
            UserProfile(
                name="Test User",
                role="invalid"
            )
    
    def test_user_profile_work_area_validation(self):
        """Test work_area field accepts valid values."""
        valid_areas = ["general", "web_dev", "data_science", "ai_ml", 
                      "devops", "mobile", "backend", "frontend", "fullstack"]
        
        for area in valid_areas:
            profile = UserProfile(
                name="Test User",
                work_area=area
            )
            assert profile.work_area == area
    
    def test_user_profile_to_dict(self):
        """Test conversion to dictionary."""
        profile = UserProfile(
            name="Asif Hussain",
            preference="concise",
            role="expert",
            work_area="ai_ml",
            language="es"
        )
        
        profile_dict = profile.model_dump()
        
        assert profile_dict["name"] == "Asif Hussain"
        assert profile_dict["preference"] == "concise"
        assert profile_dict["role"] == "expert"
        assert profile_dict["work_area"] == "ai_ml"
        assert profile_dict["language"] == "es"
    
    def test_user_profile_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "Test User",
            "preference": "balanced",
            "role": "beginner",
            "work_area": "web_dev",
            "language": "fr"
        }
        
        profile = UserProfile(**data)
        
        assert profile.name == "Test User"
        assert profile.preference == "balanced"
        assert profile.role == "beginner"
        assert profile.work_area == "web_dev"
        assert profile.language == "fr"
    
    def test_supported_languages_structure(self):
        """Test SUPPORTED_LANGUAGES has correct structure."""
        assert len(SUPPORTED_LANGUAGES) == 12
        
        # Check each language has required fields
        for code, info in SUPPORTED_LANGUAGES.items():
            assert "name" in info
            assert "native" in info
            assert len(code) == 2  # ISO 639-1 codes are 2 letters
    
    def test_supported_languages_includes_key_languages(self):
        """Test SUPPORTED_LANGUAGES includes all planned languages."""
        expected_languages = ["en", "es", "fr", "de", "pt", "zh", 
                             "ja", "ko", "hi", "ar", "ru", "it"]
        
        for lang in expected_languages:
            assert lang in SUPPORTED_LANGUAGES, f"Missing language: {lang}"
