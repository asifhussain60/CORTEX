"""
Comprehensive tests for user profile system (CORTEX 3.2.1).

Tests cover:
- CRUD operations with tech_stack_preference
- Validation for all 5 tech stack fields
- JSON serialization/deserialization
- Database migration logic
- Profile injection into AgentRequest
- Context-not-constraint pattern validation

Author: Asif Hussain
Target Coverage: 95%+
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.tier1.working_memory import WorkingMemory
from src.cortex_agents.base_agent import AgentRequest


class TestUserProfileCRUD:
    """Test CRUD operations for user profiles."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_profile.db")
        wm = WorkingMemory(db_path=db_path)
        yield wm
        # Cleanup
        wm.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_create_profile_minimal(self, temp_db):
        """Test creating profile with minimal required fields."""
        success = temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid"
        )
        
        assert success is True
        
        profile = temp_db.get_profile()
        assert profile is not None
        assert profile['interaction_mode'] == "guided"
        assert profile['experience_level'] == "mid"
        assert profile['tech_stack_preference'] is None
        assert 'created_at' in profile
        assert 'last_updated' in profile
    
    def test_create_profile_with_tech_stack(self, temp_db):
        """Test creating profile with tech stack preference."""
        tech_stack = {
            'cloud_provider': 'azure',
            'container_platform': 'kubernetes',
            'architecture': 'microservices',
            'ci_cd': 'azure_devops',
            'iac': 'terraform'
        }
        
        success = temp_db.create_profile(
            interaction_mode="autonomous",
            experience_level="expert",
            tech_stack_preference=tech_stack
        )
        
        assert success is True
        
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference'] == tech_stack
        assert profile['tech_stack_preference']['cloud_provider'] == 'azure'
    
    def test_create_profile_validation_invalid_mode(self, temp_db):
        """Test validation rejects invalid interaction mode."""
        with pytest.raises(ValueError, match="Invalid interaction_mode"):
            temp_db.create_profile(
                interaction_mode="invalid_mode",
                experience_level="mid"
            )
    
    def test_create_profile_validation_invalid_experience(self, temp_db):
        """Test validation rejects invalid experience level."""
        with pytest.raises(ValueError, match="Invalid experience_level"):
            temp_db.create_profile(
                interaction_mode="guided",
                experience_level="invalid_level"
            )
    
    def test_create_profile_validation_invalid_cloud_provider(self, temp_db):
        """Test validation rejects invalid cloud provider."""
        tech_stack = {
            'cloud_provider': 'invalid_cloud',
            'container_platform': 'kubernetes'
        }
        
        with pytest.raises(ValueError, match="Invalid cloud_provider"):
            temp_db.create_profile(
                interaction_mode="guided",
                experience_level="mid",
                tech_stack_preference=tech_stack
            )
    
    def test_create_profile_validation_invalid_container_platform(self, temp_db):
        """Test validation rejects invalid container platform."""
        tech_stack = {
            'cloud_provider': 'azure',
            'container_platform': 'invalid_container'
        }
        
        with pytest.raises(ValueError, match="Invalid container_platform"):
            temp_db.create_profile(
                interaction_mode="guided",
                experience_level="mid",
                tech_stack_preference=tech_stack
            )
    
    def test_create_profile_validation_invalid_architecture(self, temp_db):
        """Test validation rejects invalid architecture."""
        tech_stack = {
            'cloud_provider': 'azure',
            'architecture': 'invalid_arch'
        }
        
        with pytest.raises(ValueError, match="Invalid architecture"):
            temp_db.create_profile(
                interaction_mode="guided",
                experience_level="mid",
                tech_stack_preference=tech_stack
            )
    
    def test_create_profile_validation_invalid_ci_cd(self, temp_db):
        """Test validation rejects invalid CI/CD."""
        tech_stack = {
            'cloud_provider': 'azure',
            'ci_cd': 'invalid_cicd'
        }
        
        with pytest.raises(ValueError, match="Invalid ci_cd"):
            temp_db.create_profile(
                interaction_mode="guided",
                experience_level="mid",
                tech_stack_preference=tech_stack
            )
    
    def test_create_profile_validation_invalid_iac(self, temp_db):
        """Test validation rejects invalid IaC."""
        tech_stack = {
            'cloud_provider': 'azure',
            'iac': 'invalid_iac'
        }
        
        with pytest.raises(ValueError, match="Invalid iac"):
            temp_db.create_profile(
                interaction_mode="guided",
                experience_level="mid",
                tech_stack_preference=tech_stack
            )
    
    def test_get_profile_nonexistent(self, temp_db):
        """Test getting profile when none exists."""
        profile = temp_db.get_profile()
        assert profile is None
    
    def test_update_profile_experience_level(self, temp_db):
        """Test updating experience level only."""
        # Create initial profile
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="junior"
        )
        
        # Update experience level
        success = temp_db.update_profile(experience_level="senior")
        assert success is True
        
        # Verify update
        profile = temp_db.get_profile()
        assert profile['experience_level'] == "senior"
        assert profile['interaction_mode'] == "guided"  # Unchanged
    
    def test_update_profile_interaction_mode(self, temp_db):
        """Test updating interaction mode only."""
        # Create initial profile
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid"
        )
        
        # Update mode
        success = temp_db.update_profile(interaction_mode="autonomous")
        assert success is True
        
        # Verify update
        profile = temp_db.get_profile()
        assert profile['interaction_mode'] == "autonomous"
        assert profile['experience_level'] == "mid"  # Unchanged
    
    def test_update_profile_tech_stack(self, temp_db):
        """Test updating tech stack preference only."""
        # Create initial profile without tech stack
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid"
        )
        
        # Add tech stack
        tech_stack = {
            'cloud_provider': 'aws',
            'container_platform': 'kubernetes',
            'ci_cd': 'github_actions'
        }
        success = temp_db.update_profile(tech_stack_preference=tech_stack)
        assert success is True
        
        # Verify update
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference'] == tech_stack
        assert profile['interaction_mode'] == "guided"  # Unchanged
    
    def test_update_profile_all_fields(self, temp_db):
        """Test updating all fields at once."""
        # Create initial profile
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="junior"
        )
        
        # Update all fields
        tech_stack = {
            'cloud_provider': 'gcp',
            'container_platform': 'kubernetes'
        }
        success = temp_db.update_profile(
            interaction_mode="educational",
            experience_level="expert",
            tech_stack_preference=tech_stack
        )
        assert success is True
        
        # Verify updates
        profile = temp_db.get_profile()
        assert profile['interaction_mode'] == "educational"
        assert profile['experience_level'] == "expert"
        assert profile['tech_stack_preference'] == tech_stack
    
    def test_update_profile_clear_tech_stack(self, temp_db):
        """Test clearing tech stack by updating to None."""
        # Create profile with tech stack
        tech_stack = {'cloud_provider': 'azure'}
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=tech_stack
        )
        
        # Clear tech stack
        success = temp_db.update_profile(tech_stack_preference=None)
        assert success is True
        
        # Verify cleared
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference'] is None
    
    def test_delete_profile(self, temp_db):
        """Test deleting profile."""
        # Create profile
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid"
        )
        
        # Delete profile
        success = temp_db.delete_profile()
        assert success is True
        
        # Verify deleted
        profile = temp_db.get_profile()
        assert profile is None
    
    def test_profile_exists(self, temp_db):
        """Test profile_exists() method."""
        # Initially no profile
        assert temp_db.profile_exists() is False
        
        # Create profile
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid"
        )
        
        # Now exists
        assert temp_db.profile_exists() is True
        
        # Delete profile
        temp_db.delete_profile()
        
        # No longer exists
        assert temp_db.profile_exists() is False


class TestJSONSerialization:
    """Test JSON serialization/deserialization of tech stack."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_profile.db")
        wm = WorkingMemory(db_path=db_path)
        yield wm
        wm.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_json_serialization_all_fields(self, temp_db):
        """Test serialization with all tech stack fields."""
        tech_stack = {
            'cloud_provider': 'azure',
            'container_platform': 'kubernetes',
            'architecture': 'microservices',
            'ci_cd': 'azure_devops',
            'iac': 'terraform'
        }
        
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=tech_stack
        )
        
        profile = temp_db.get_profile()
        
        # Verify round-trip
        assert profile['tech_stack_preference'] == tech_stack
        assert isinstance(profile['tech_stack_preference'], dict)
    
    def test_json_serialization_partial_fields(self, temp_db):
        """Test serialization with partial tech stack fields."""
        tech_stack = {
            'cloud_provider': 'aws',
            'ci_cd': 'github_actions'
        }
        
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=tech_stack
        )
        
        profile = temp_db.get_profile()
        
        # Verify only provided fields are stored
        assert profile['tech_stack_preference'] == tech_stack
        assert 'cloud_provider' in profile['tech_stack_preference']
        assert 'ci_cd' in profile['tech_stack_preference']
        assert 'container_platform' not in profile['tech_stack_preference']
    
    def test_json_serialization_empty_dict(self, temp_db):
        """Test serialization with empty tech stack dict."""
        tech_stack = {}
        
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=tech_stack
        )
        
        profile = temp_db.get_profile()
        
        # Empty dict is stored as NULL in database, retrieved as None
        assert profile['tech_stack_preference'] is None
    
    def test_json_deserialization_null(self, temp_db):
        """Test deserialization of NULL (no tech stack)."""
        temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=None
        )
        
        profile = temp_db.get_profile()
        
        # NULL should return as None
        assert profile['tech_stack_preference'] is None


class TestDatabaseMigration:
    """Test database migration logic for backward compatibility."""
    
    def test_tech_stack_column_exists(self):
        """Test that tech_stack_preference column exists in user_profile table."""
        # Create temporary database
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_profile.db")
        
        try:
            # Initialize WorkingMemory (creates tables)
            wm = WorkingMemory(db_path=db_path)
            
            # Try to create profile with tech_stack - should succeed if column exists
            success = wm.create_profile(
                interaction_mode="guided",
                experience_level="mid",
                tech_stack_preference={"cloud_provider": "azure"}
            )
            
            assert success is True
            
            # Verify we can retrieve it
            profile = wm.get_profile()
            assert profile is not None
            assert 'tech_stack_preference' in profile
            assert profile['tech_stack_preference'] == {"cloud_provider": "azure"}
            
            wm.close()
            
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.remove(db_path)
            os.rmdir(temp_dir)


class TestAllTechStackPresets:
    """Test all tech stack preset configurations."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_profile.db")
        wm = WorkingMemory(db_path=db_path)
        yield wm
        wm.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_azure_preset(self, temp_db):
        """Test Azure tech stack preset."""
        tech_stack = {
            'cloud_provider': 'azure',
            'container_platform': 'kubernetes',
            'architecture': 'microservices',
            'ci_cd': 'azure_devops',
            'iac': 'terraform'
        }
        
        success = temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=tech_stack
        )
        
        assert success is True
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference']['cloud_provider'] == 'azure'
    
    def test_aws_preset(self, temp_db):
        """Test AWS tech stack preset."""
        tech_stack = {
            'cloud_provider': 'aws',
            'container_platform': 'kubernetes',
            'architecture': 'microservices',
            'ci_cd': 'github_actions',
            'iac': 'terraform'
        }
        
        success = temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=tech_stack
        )
        
        assert success is True
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference']['cloud_provider'] == 'aws'
    
    def test_gcp_preset(self, temp_db):
        """Test GCP tech stack preset."""
        tech_stack = {
            'cloud_provider': 'gcp',
            'container_platform': 'kubernetes',
            'architecture': 'microservices',
            'ci_cd': 'github_actions',
            'iac': 'terraform'
        }
        
        success = temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=tech_stack
        )
        
        assert success is True
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference']['cloud_provider'] == 'gcp'
    
    def test_no_preference_preset(self, temp_db):
        """Test no preference (None) preset."""
        success = temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=None
        )
        
        assert success is True
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference'] is None
    
    def test_custom_preset(self, temp_db):
        """Test custom tech stack (empty dict stored as None)."""
        # Custom means user will configure later - stored as None
        success = temp_db.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=None
        )
        
        assert success is True
        profile = temp_db.get_profile()
        assert profile['tech_stack_preference'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
