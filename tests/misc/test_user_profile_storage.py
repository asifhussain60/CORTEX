"""
Tests for User Profile Storage Module (Task 2.3)
TDD RED Phase: Write failing tests first
"""
import pytest
import json
import os
import tempfile
from pathlib import Path
from src.setup.models.user_profile import UserProfile
from src.setup.modules.user_profile_storage import UserProfileStorage


class TestUserProfileStorage:
    """Test suite for user profile storage operations"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Start with minimal valid config
            config = {
                "machines": {},
                "testing": {"enabled": False}
            }
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def sample_profile(self):
        """Create sample user profile for testing"""
        return UserProfile(
            name="Test User",
            preference="balanced",
            role="intermediate",
            work_area="web_dev",
            language="en"
        )
    
    def test_storage_initialization(self, temp_config_file):
        """Test storage can be instantiated with config path"""
        storage = UserProfileStorage(temp_config_file)
        assert storage is not None
        assert storage.config_path == temp_config_file
    
    def test_save_profile_creates_user_section(self, temp_config_file, sample_profile):
        """Test saving profile creates 'user' section in config"""
        storage = UserProfileStorage(temp_config_file)
        storage.save_profile(sample_profile)
        
        # Read config and verify
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        assert 'user' in config
        assert config['user']['name'] == 'Test User'
        assert config['user']['preference'] == 'balanced'
    
    def test_save_profile_preserves_existing_config(self, temp_config_file, sample_profile):
        """Test saving profile preserves other config sections"""
        # Add custom section to config
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        config['custom_section'] = {'key': 'value'}
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        # Save profile
        storage = UserProfileStorage(temp_config_file)
        storage.save_profile(sample_profile)
        
        # Verify custom section preserved
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        assert 'custom_section' in config
        assert config['custom_section']['key'] == 'value'
        assert 'user' in config
    
    def test_load_profile_returns_user_profile(self, temp_config_file, sample_profile):
        """Test loading profile returns UserProfile object"""
        # Save profile first
        storage = UserProfileStorage(temp_config_file)
        storage.save_profile(sample_profile)
        
        # Load and verify
        loaded_profile = storage.load_profile()
        
        assert isinstance(loaded_profile, UserProfile)
        assert loaded_profile.name == sample_profile.name
        assert loaded_profile.preference == sample_profile.preference
        assert loaded_profile.role == sample_profile.role
        assert loaded_profile.work_area == sample_profile.work_area
        assert loaded_profile.language == sample_profile.language
    
    def test_load_profile_returns_none_if_no_user_section(self, temp_config_file):
        """Test loading profile returns None if 'user' section missing"""
        storage = UserProfileStorage(temp_config_file)
        loaded_profile = storage.load_profile()
        
        assert loaded_profile is None
    
    def test_load_profile_returns_none_if_config_missing(self):
        """Test loading profile returns None if config file doesn't exist"""
        storage = UserProfileStorage('/nonexistent/path/cortex.config.json')
        loaded_profile = storage.load_profile()
        
        assert loaded_profile is None
    
    def test_profile_exists_returns_true_when_present(self, temp_config_file, sample_profile):
        """Test profile_exists returns True when profile saved"""
        storage = UserProfileStorage(temp_config_file)
        storage.save_profile(sample_profile)
        
        assert storage.profile_exists() is True
    
    def test_profile_exists_returns_false_when_missing(self, temp_config_file):
        """Test profile_exists returns False when no profile"""
        storage = UserProfileStorage(temp_config_file)
        
        assert storage.profile_exists() is False
    
    def test_update_profile_modifies_existing(self, temp_config_file, sample_profile):
        """Test updating profile modifies existing user section"""
        storage = UserProfileStorage(temp_config_file)
        storage.save_profile(sample_profile)
        
        # Update profile
        updated_profile = UserProfile(
            name="Updated User",
            preference="concise",
            role="expert",
            work_area="ai_ml",
            language="es"
        )
        storage.save_profile(updated_profile)
        
        # Verify update
        loaded_profile = storage.load_profile()
        assert loaded_profile.name == "Updated User"
        assert loaded_profile.preference == "concise"
        assert loaded_profile.role == "expert"
    
    def test_save_profile_formats_json_readable(self, temp_config_file, sample_profile):
        """Test saved JSON is formatted with indentation"""
        storage = UserProfileStorage(temp_config_file)
        storage.save_profile(sample_profile)
        
        # Read raw file content
        with open(temp_config_file, 'r') as f:
            content = f.read()
        
        # Verify formatting (should have newlines and indentation)
        assert '\n' in content
        assert '  ' in content  # 2-space indentation
    
    def test_save_profile_creates_config_if_missing(self, sample_profile):
        """Test saving profile creates config file if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'cortex.config.json')
            
            storage = UserProfileStorage(config_path)
            storage.save_profile(sample_profile)
            
            # Verify file created
            assert os.path.exists(config_path)
            
            # Verify content
            loaded_profile = storage.load_profile()
            assert loaded_profile.name == sample_profile.name
    
    def test_get_config_path_default(self):
        """Test getting default config path"""
        storage = UserProfileStorage()
        
        # Should use CORTEX repo's cortex.config.json
        assert storage.config_path.endswith('cortex.config.json')
        assert 'CORTEX' in storage.config_path
    
    def test_save_profile_with_special_characters(self, temp_config_file):
        """Test saving profile with special characters in name"""
        profile = UserProfile(
            name="José García-Müller",
            preference="verbose",
            role="beginner",
            work_area="general",
            language="es"
        )
        
        storage = UserProfileStorage(temp_config_file)
        storage.save_profile(profile)
        
        # Verify special characters preserved
        loaded_profile = storage.load_profile()
        assert loaded_profile.name == "José García-Müller"
