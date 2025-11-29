"""
Tests for User Profile System - Tech Stack Preference Feature
Phase 1: User Profile System enhancements (RED phase)
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any

from src.tier1.user_profile_manager import UserProfileManager, TechStackPreset


class TestTechStackPreference:
    """Test suite for tech stack preference functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        
        yield db_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def profile_manager(self, temp_db):
        """Create UserProfileManager instance with temp database"""
        return UserProfileManager(temp_db)
    
    def test_preset_azure_stack(self, profile_manager):
        """RED: Test Azure stack preset configuration"""
        # This should fail - UserProfileManager doesn't exist yet
        preset = TechStackPreset.AZURE_STACK
        
        result = profile_manager.set_tech_stack_preset(preset)
        
        assert result is True
        
        profile = profile_manager.get_profile()
        assert profile is not None
        assert profile["tech_stack_preference"]["cloud_provider"] == "azure"
        assert profile["tech_stack_preference"]["container_platform"] == "aks"
        assert profile["tech_stack_preference"]["ci_cd"] == "azure_devops"
        assert profile["tech_stack_preference"]["iac"] == "arm"
    
    def test_preset_aws_stack(self, profile_manager):
        """RED: Test AWS stack preset configuration"""
        preset = TechStackPreset.AWS_STACK
        
        result = profile_manager.set_tech_stack_preset(preset)
        
        assert result is True
        
        profile = profile_manager.get_profile()
        assert profile["tech_stack_preference"]["cloud_provider"] == "aws"
        assert profile["tech_stack_preference"]["container_platform"] == "eks"
        assert profile["tech_stack_preference"]["ci_cd"] == "github_actions"
        assert profile["tech_stack_preference"]["iac"] == "terraform"
    
    def test_preset_gcp_stack(self, profile_manager):
        """RED: Test GCP stack preset configuration"""
        preset = TechStackPreset.GCP_STACK
        
        result = profile_manager.set_tech_stack_preset(preset)
        
        assert result is True
        
        profile = profile_manager.get_profile()
        assert profile["tech_stack_preference"]["cloud_provider"] == "gcp"
        assert profile["tech_stack_preference"]["container_platform"] == "gke"
        assert profile["tech_stack_preference"]["ci_cd"] == "cloud_build"
    
    def test_preset_no_preference(self, profile_manager):
        """RED: Test no preference (CORTEX decides)"""
        preset = TechStackPreset.NO_PREFERENCE
        
        result = profile_manager.set_tech_stack_preset(preset)
        
        assert result is True
        
        profile = profile_manager.get_profile()
        # No preference means tech_stack_preference should be None
        assert profile["tech_stack_preference"] is None
    
    def test_preset_custom(self, profile_manager):
        """RED: Test custom configuration"""
        custom_config = {
            "cloud_provider": "azure",
            "container_platform": "docker",
            "ci_cd": "jenkins",
            "iac": "terraform",
            "architecture": "hybrid"
        }
        
        result = profile_manager.set_tech_stack_custom(custom_config)
        
        assert result is True
        
        profile = profile_manager.get_profile()
        assert profile["tech_stack_preference"] == custom_config
    
    def test_get_tech_stack_preference(self, profile_manager):
        """RED: Test retrieving only tech stack preference"""
        preset = TechStackPreset.AZURE_STACK
        profile_manager.set_tech_stack_preset(preset)
        
        tech_stack = profile_manager.get_tech_stack_preference()
        
        assert tech_stack is not None
        assert tech_stack["cloud_provider"] == "azure"
    
    def test_update_tech_stack_preference(self, profile_manager):
        """RED: Test updating existing tech stack preference"""
        # Set initial preset
        profile_manager.set_tech_stack_preset(TechStackPreset.AZURE_STACK)
        
        # Update to AWS
        result = profile_manager.update_tech_stack_preset(TechStackPreset.AWS_STACK)
        
        assert result is True
        
        tech_stack = profile_manager.get_tech_stack_preference()
        assert tech_stack["cloud_provider"] == "aws"
    
    def test_clear_tech_stack_preference(self, profile_manager):
        """RED: Test clearing tech stack preference"""
        # Set a preset first
        profile_manager.set_tech_stack_preset(TechStackPreset.AZURE_STACK)
        
        # Clear it
        result = profile_manager.clear_tech_stack_preference()
        
        assert result is True
        
        tech_stack = profile_manager.get_tech_stack_preference()
        assert tech_stack is None
    
    def test_invalid_custom_config(self, profile_manager):
        """RED: Test validation of custom configuration"""
        invalid_config = {
            "cloud_provider": "invalid_provider",  # Invalid value
            "container_platform": "kubernetes"
        }
        
        with pytest.raises(ValueError, match="Invalid cloud_provider"):
            profile_manager.set_tech_stack_custom(invalid_config)
    
    def test_preset_enum_values(self):
        """RED: Test TechStackPreset enum has all required values"""
        assert hasattr(TechStackPreset, "AZURE_STACK")
        assert hasattr(TechStackPreset, "AWS_STACK")
        assert hasattr(TechStackPreset, "GCP_STACK")
        assert hasattr(TechStackPreset, "NO_PREFERENCE")
        assert hasattr(TechStackPreset, "CUSTOM")
    
    def test_tech_stack_persistence(self, profile_manager):
        """RED: Test tech stack preference persists across manager instances"""
        # Set preference
        profile_manager.set_tech_stack_preset(TechStackPreset.AZURE_STACK)
        
        # Create new manager instance with same database
        new_manager = UserProfileManager(profile_manager.db_path)
        
        # Should retrieve same preference
        tech_stack = new_manager.get_tech_stack_preference()
        assert tech_stack["cloud_provider"] == "azure"
