"""
Tests for User Profile Validator (Task 2.4)
TDD RED Phase: Write failing tests first
"""
import pytest
from unittest.mock import patch, MagicMock
from src.setup.models.user_profile import UserProfile
from src.setup.modules.user_profile_validator import UserProfileValidator


class TestUserProfileValidator:
    """Test suite for user profile validation and smart defaults"""
    
    def test_validator_initialization(self):
        """Test validator can be instantiated"""
        validator = UserProfileValidator()
        assert validator is not None
    
    def test_get_git_user_name_success(self):
        """Test retrieving git user.name successfully"""
        validator = UserProfileValidator()
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout='John Doe\n',
                returncode=0
            )
            name = validator.get_git_user_name()
            assert name == 'John Doe'
    
    def test_get_git_user_name_failure(self):
        """Test git user.name returns None on failure"""
        validator = UserProfileValidator()
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Git not found")
            name = validator.get_git_user_name()
            assert name is None
    
    def test_get_git_user_email_success(self):
        """Test retrieving git user.email successfully"""
        validator = UserProfileValidator()
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout='john@example.com\n',
                returncode=0
            )
            email = validator.get_git_user_email()
            assert email == 'john@example.com'
    
    def test_get_git_user_email_failure(self):
        """Test git user.email returns None on failure"""
        validator = UserProfileValidator()
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout='',
                returncode=1
            )
            email = validator.get_git_user_email()
            assert email is None
    
    def test_validate_profile_success(self):
        """Test validating a valid profile"""
        validator = UserProfileValidator()
        profile = UserProfile(
            name="Test User",
            preference="balanced",
            role="intermediate",
            work_area="web_dev",
            language="en"
        )
        
        is_valid, errors = validator.validate_profile(profile)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_profile_empty_name(self):
        """Test validation fails on empty name"""
        validator = UserProfileValidator()
        
        # Pydantic will raise error, so we test the validator's handling
        # We'll test with a dict that would fail Pydantic validation
        profile_data = {
            "name": "",
            "preference": "balanced",
            "role": "intermediate",
            "work_area": "web_dev",
            "language": "en"
        }
        
        is_valid, errors = validator.validate_profile_data(profile_data)
        assert is_valid is False
        assert any('name' in error.lower() for error in errors)
    
    def test_validate_profile_invalid_preference(self):
        """Test validation fails on invalid preference"""
        validator = UserProfileValidator()
        
        profile_data = {
            "name": "Test",
            "preference": "invalid_value",
            "role": "intermediate",
            "work_area": "web_dev",
            "language": "en"
        }
        
        is_valid, errors = validator.validate_profile_data(profile_data)
        assert is_valid is False
        assert any('preference' in error.lower() for error in errors)
    
    def test_validate_profile_invalid_role(self):
        """Test validation fails on invalid role"""
        validator = UserProfileValidator()
        
        profile_data = {
            "name": "Test",
            "preference": "balanced",
            "role": "master",  # invalid
            "work_area": "web_dev",
            "language": "en"
        }
        
        is_valid, errors = validator.validate_profile_data(profile_data)
        assert is_valid is False
        assert any('role' in error.lower() for error in errors)
    
    def test_validate_profile_invalid_work_area(self):
        """Test validation fails on invalid work_area"""
        validator = UserProfileValidator()
        
        profile_data = {
            "name": "Test",
            "preference": "balanced",
            "role": "intermediate",
            "work_area": "blockchain",  # invalid
            "language": "en"
        }
        
        is_valid, errors = validator.validate_profile_data(profile_data)
        assert is_valid is False
        assert any('work_area' in error.lower() for error in errors)
    
    def test_validate_profile_invalid_language(self):
        """Test validation fails on invalid language"""
        validator = UserProfileValidator()
        
        profile_data = {
            "name": "Test",
            "preference": "balanced",
            "role": "intermediate",
            "work_area": "web_dev",
            "language": "xx"  # invalid
        }
        
        is_valid, errors = validator.validate_profile_data(profile_data)
        assert is_valid is False
        assert any('language' in error.lower() for error in errors)
    
    def test_create_default_profile_with_git_name(self):
        """Test creating default profile uses git user.name"""
        validator = UserProfileValidator()
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout='Git User\n',
                returncode=0
            )
            profile = validator.create_default_profile()
            
            assert profile.name == 'Git User'
            assert profile.preference == 'verbose'
            assert profile.role == 'intermediate'
            assert profile.work_area == 'general'
            assert profile.language == 'en'
    
    def test_create_default_profile_without_git(self):
        """Test creating default profile without git config"""
        validator = UserProfileValidator()
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Git not found")
            profile = validator.create_default_profile()
            
            assert profile.name == 'User'
            assert profile.preference == 'verbose'
            assert profile.role == 'intermediate'
    
    def test_apply_smart_defaults_fills_missing(self):
        """Test applying smart defaults fills in missing fields"""
        validator = UserProfileValidator()
        
        # Incomplete profile data
        profile_data = {
            "name": "Test User"
        }
        
        with patch.object(validator, 'get_git_user_name', return_value='Git User'):
            complete_data = validator.apply_smart_defaults(profile_data)
            
            assert complete_data['name'] == 'Test User'
            assert complete_data['preference'] == 'verbose'
            assert complete_data['role'] == 'intermediate'
            assert complete_data['work_area'] == 'general'
            assert complete_data['language'] == 'en'
    
    def test_apply_smart_defaults_preserves_existing(self):
        """Test applying smart defaults preserves existing values"""
        validator = UserProfileValidator()
        
        profile_data = {
            "name": "Test User",
            "preference": "concise",
            "role": "expert"
        }
        
        complete_data = validator.apply_smart_defaults(profile_data)
        
        assert complete_data['preference'] == 'concise'
        assert complete_data['role'] == 'expert'
        assert complete_data['work_area'] == 'general'  # default
    
    def test_sanitize_name_trims_whitespace(self):
        """Test sanitizing name removes extra whitespace"""
        validator = UserProfileValidator()
        sanitized = validator.sanitize_name("  John   Doe  ")
        assert sanitized == "John Doe"
    
    def test_sanitize_name_handles_empty(self):
        """Test sanitizing empty name returns None"""
        validator = UserProfileValidator()
        sanitized = validator.sanitize_name("")
        assert sanitized is None
        
        sanitized = validator.sanitize_name("   ")
        assert sanitized is None
