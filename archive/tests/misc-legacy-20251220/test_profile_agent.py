"""
Tests for ProfileAgent - User Profile Update Handler
Phase 1: User Profile System enhancements (RED phase)
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import IntentType
from src.cortex_agents.profile_agent import ProfileAgent
from src.tier1.user_profile_manager import TechStackPreset


class TestProfileAgent:
    """Test suite for ProfileAgent"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        
        yield db_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def profile_agent(self, temp_db):
        """Create ProfileAgent instance with temp database"""
        return ProfileAgent(name="TestProfileAgent", db_path=str(temp_db))
    
    def test_can_handle_update_profile_intent(self, profile_agent):
        """RED: Test ProfileAgent recognizes UPDATE_PROFILE intent"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="update my tech stack to Azure"
        )
        
        assert profile_agent.can_handle(request) is True
    
    def test_cannot_handle_other_intents(self, profile_agent):
        """RED: Test ProfileAgent rejects non-profile intents"""
        request = AgentRequest(
            intent=IntentType.CODE,
            context={},
            user_message="create a new file"
        )
        
        assert profile_agent.can_handle(request) is False
    
    def test_update_to_azure_stack(self, profile_agent):
        """RED: Test updating tech stack to Azure preset"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="switch to azure stack"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert "azure" in response.message.lower()
        assert response.result["tech_stack"] == "azure_stack"
    
    def test_update_to_aws_stack(self, profile_agent):
        """RED: Test updating tech stack to AWS preset"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="prefer aws for deployment"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert "aws" in response.message.lower()
        assert response.result["tech_stack"] == "aws_stack"
    
    def test_update_to_gcp_stack(self, profile_agent):
        """RED: Test updating tech stack to GCP preset"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="use gcp stack"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert "gcp" in response.message.lower()
        assert response.result["tech_stack"] == "gcp_stack"
    
    def test_update_to_no_preference(self, profile_agent):
        """RED: Test removing tech stack preference"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="no tech preference"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert response.result["tech_stack"] == "no_preference"
    
    def test_update_interaction_mode(self, profile_agent):
        """RED: Test updating interaction mode"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="change mode to autonomous"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert response.result["interaction_mode"] == "autonomous"
    
    def test_update_experience_level(self, profile_agent):
        """RED: Test updating experience level"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="update experience to senior"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert response.result["experience_level"] == "senior"
    
    def test_custom_tech_stack(self, profile_agent):
        """RED: Test setting custom tech stack"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="custom tech stack: azure cloud, docker containers, jenkins ci/cd"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert response.result["tech_stack"] == "custom"
        assert response.result["tech_stack_config"]["cloud_provider"] == "azure"
    
    def test_multiple_profile_updates(self, profile_agent):
        """RED: Test updating multiple profile fields at once"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="update profile: mode=guided, experience=expert, tech_stack=aws"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is True
        assert response.result["interaction_mode"] == "guided"
        assert response.result["experience_level"] == "expert"
        assert response.result["tech_stack"] == "aws_stack"
    
    def test_invalid_profile_value(self, profile_agent):
        """RED: Test validation of invalid profile values"""
        request = AgentRequest(
            intent=IntentType.UPDATE_PROFILE,
            context={},
            user_message="change mode to invalid_mode"
        )
        
        response = profile_agent.execute(request)
        
        assert response.success is False
        assert "invalid" in response.message.lower()
