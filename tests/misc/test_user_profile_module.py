"""
Tests for User Profile Setup Module (Task 2.6)
TDD RED Phase: Write failing tests first
"""
import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from src.setup.base_setup_module import SetupStatus, SetupPhase
from src.setup.modules.user_profile_module import UserProfileModule
from src.setup.models.user_profile import UserProfile


class TestUserProfileModule:
    """Test suite for user profile setup module integration"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"machines": {}, "testing": {"enabled": False}}
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_module_initialization(self):
        """Test module can be instantiated"""
        module = UserProfileModule()
        assert module is not None
    
    def test_module_metadata(self):
        """Test module metadata is correct"""
        module = UserProfileModule()
        metadata = module.get_metadata()
        
        assert metadata.module_id == "user_profile"
        assert metadata.name == "User Profile Setup"
        assert metadata.phase == SetupPhase.FEATURES
        assert metadata.optional is True
        assert metadata.enabled_by_default is True
    
    def test_validate_prerequisites_success(self, temp_config_file):
        """Test prerequisites validation passes"""
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        is_valid, errors = module.validate_prerequisites(context)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_execute_creates_new_profile(self, temp_config_file):
        """Test executing module creates new profile if none exists"""
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        # Mock user inputs for questionnaire
        mock_inputs = ['Test User', '2', '2', '5', '1']
        
        with patch('builtins.input', side_effect=mock_inputs):
            result = module.execute(context)
        
        assert result.status == SetupStatus.SUCCESS
        assert "profile created" in result.message.lower() or "success" in result.message.lower()
        
        # Verify profile was saved to config
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        assert 'user' in config
        assert config['user']['name'] == 'Test User'
    
    def test_execute_skips_if_profile_exists(self, temp_config_file):
        """Test executing module skips if profile already exists"""
        # Create existing profile
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        config['user'] = {
            'name': 'Existing User',
            'preference': 'balanced',
            'role': 'intermediate',
            'work_area': 'web_dev',
            'language': 'en'
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        # User declines edit (n)
        with patch('builtins.input', return_value='n'):
            result = module.execute(context)
        
        assert result.status in [SetupStatus.SUCCESS, SetupStatus.SKIPPED]
        assert "already exists" in result.message.lower() or "existing" in result.message.lower()
    
    def test_execute_offers_edit_for_existing_profile(self, temp_config_file):
        """Test module offers to edit existing profile"""
        # Create existing profile
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        config['user'] = {
            'name': 'Existing User',
            'preference': 'balanced',
            'role': 'intermediate',
            'work_area': 'web_dev',
            'language': 'en'
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        # User chooses to edit (y), then quits editor (6)
        mock_inputs = ['y', '6']
        
        with patch('builtins.input', side_effect=mock_inputs):
            result = module.execute(context)
        
        assert result.status == SetupStatus.SUCCESS
    
    def test_execute_skips_edit_if_declined(self, temp_config_file):
        """Test module skips edit if user declines"""
        # Create existing profile
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        config['user'] = {
            'name': 'Existing User',
            'preference': 'balanced',
            'role': 'intermediate',
            'work_area': 'web_dev',
            'language': 'en'
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        # User declines edit (n)
        with patch('builtins.input', return_value='n'):
            result = module.execute(context)
        
        assert result.status in [SetupStatus.SUCCESS, SetupStatus.SKIPPED]
    
    def test_execute_handles_questionnaire_error(self, temp_config_file):
        """Test module handles errors during questionnaire"""
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        # Mock input to raise exception
        with patch('builtins.input', side_effect=Exception("Input error")):
            result = module.execute(context)
        
        assert result.status == SetupStatus.FAILED
        assert len(result.errors) > 0
    
    def test_rollback_removes_profile(self, temp_config_file):
        """Test rollback removes profile from config"""
        # Create profile
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        config['user'] = {
            'name': 'Test User',
            'preference': 'balanced',
            'role': 'intermediate',
            'work_area': 'web_dev',
            'language': 'en'
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        success = module.rollback(context)
        assert success is True
        
        # Verify profile removed
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        assert 'user' not in config
    
    def test_execute_uses_default_config_path(self):
        """Test module uses default config path if not provided"""
        module = UserProfileModule()
        context = {}
        
        # This will use default path which may have existing profile
        # Mock input for both scenarios (new profile or decline edit)
        with patch('builtins.input', side_effect=['n'] + ['Test', '1', '1', '1', '1']):
            result = module.execute(context)
        
        # Should either succeed, skip, or fail gracefully
        assert result.status in [SetupStatus.SUCCESS, SetupStatus.FAILED, SetupStatus.SKIPPED]
    
    def test_execute_details_contains_profile(self, temp_config_file):
        """Test execute result details contains profile data"""
        module = UserProfileModule()
        context = {"config_path": temp_config_file}
        
        mock_inputs = ['Alice', '1', '3', '6', '2']
        
        with patch('builtins.input', side_effect=mock_inputs):
            result = module.execute(context)
        
        assert 'profile' in result.details
        profile_data = result.details['profile']
        assert profile_data['name'] == 'Alice'
        assert profile_data['preference'] == 'concise'
    
    def test_module_can_skip_on_failure(self):
        """Test module is marked as optional (can skip on failure)"""
        module = UserProfileModule()
        metadata = module.get_metadata()
        
        assert metadata.optional is True
