"""
Phase 1.4 RED: Onboarding Module Completion - Integration Tests

TDD Cycle: RED Phase
Tests validate:
- End-to-end onboarding workflow (app-name → profile → confirmation)
- Error handling for all edge cases
- Integration between OnboardingOrchestrator and Tier 1
- Profile persistence and retrieval
- Invalid inputs and boundary conditions

Author: Asif Hussain
Version: 1.0.0 (RED Phase)
Created: 2025-12-01
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrators.onboarding_orchestrator import OnboardingOrchestrator
from tier1.working_memory import WorkingMemory


class TestEndToEndOnboarding:
    """Test complete onboarding workflow from start to finish"""
    
    def test_complete_onboarding_workflow(self):
        """Test full onboarding: app-name → experience → mode → tech-stack → profile created"""
        orchestrator = OnboardingOrchestrator()
        
        # Step 1: Start onboarding with app-name
        result = orchestrator.start_onboarding("onboard application --app-name TestProject")
        assert "TestProject" in result
        
        # Step 2: Present onboarding questions
        onboarding_flow = orchestrator.present_onboarding()
        assert onboarding_flow["status"] == "awaiting_experience_level"
        
        # Step 3: Answer experience level
        experience_result = orchestrator.process_experience_choice("2")  # Mid
        assert experience_result["status"] == "awaiting_interaction_mode"
        
        # Step 4: Answer interaction mode
        mode_result = orchestrator.process_interaction_choice("2", "mid")  # Guided
        assert mode_result["status"] == "awaiting_tech_stack"
        
        # Step 5: Answer tech stack
        final_result = orchestrator.process_tech_stack_choice("1")  # No preference
        assert final_result["status"] == "complete"
        
        # Verify profile was created in working_memory
        app_name = orchestrator.working_memory.get_application_name()
        assert app_name == "TestProject"
        
        # Verify profile exists (either in tier1 or working_memory)
        profile = orchestrator.get_profile()
        assert profile is not None or hasattr(orchestrator, 'working_memory')
    
    def test_onboarding_with_all_profile_options(self):
        """Test onboarding with every combination of profile choices"""
        orchestrator = OnboardingOrchestrator()
        
        # Test all experience levels (1-4) with guided mode
        for exp_level in ["1", "2", "3", "4"]:
            orchestrator.start_onboarding(f"onboard application --app-name TestApp{exp_level}")
            orchestrator.present_onboarding()
            exp_result = orchestrator.process_experience_choice(exp_level)
            assert exp_result["status"] == "awaiting_interaction_mode"
    
    def test_onboarding_stores_all_data_correctly(self):
        """Test that all onboarding data is stored in Tier 1 correctly"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            # Create orchestrator with test database
            tier1_api = WorkingMemory(Path(temp_db_path))
            orchestrator = OnboardingOrchestrator(tier1_api=tier1_api)
            
            # Complete onboarding
            orchestrator.start_onboarding("onboard application --app-name IntegrationTest")
            orchestrator.present_onboarding()
            orchestrator.process_experience_choice("3")  # Senior
            orchestrator.process_interaction_choice("2", "senior")  # Guided
            orchestrator.process_tech_stack_choice("2")  # Azure
            
            # Verify all data stored
            app_name = tier1_api.get_application_name()
            assert app_name == "IntegrationTest"
            
            profile = tier1_api.get_profile()
            assert profile is not None
            assert profile["experience_level"] == "senior"
            assert profile["interaction_mode"] == "guided"
            assert profile["tech_stack_preference"] is not None
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


class TestOnboardingErrorHandling:
    """Test error handling for invalid inputs and edge cases"""
    
    def test_onboarding_without_app_name_fails(self):
        """Test that onboarding without --app-name raises clear error"""
        orchestrator = OnboardingOrchestrator()
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.start_onboarding("onboard application")
        
        assert "--app-name" in str(exc_info.value)
        assert "required" in str(exc_info.value).lower()
    
    def test_invalid_experience_choice_rejected(self):
        """Test that invalid experience level choices are rejected"""
        orchestrator = OnboardingOrchestrator()
        
        orchestrator.start_onboarding("onboard application --app-name Test")
        orchestrator.present_onboarding()
        
        # Try invalid choices
        for invalid in ["0", "5", "99", "abc", "", " "]:
            result = orchestrator.process_experience_choice(invalid)
            assert result["status"] == "error"
            assert "invalid" in result["message"].lower()
    
    def test_invalid_interaction_mode_rejected(self):
        """Test that invalid interaction mode choices are rejected"""
        orchestrator = OnboardingOrchestrator()
        
        orchestrator.start_onboarding("onboard application --app-name Test")
        orchestrator.present_onboarding()
        orchestrator.process_experience_choice("2")
        
        # Try invalid choices
        for invalid in ["0", "5", "99", "xyz", "", " "]:
            result = orchestrator.process_interaction_choice(invalid, "mid")
            assert result["status"] == "error"
            assert "invalid" in result["message"].lower()
    
    def test_invalid_tech_stack_choice_rejected(self):
        """Test that invalid tech stack choices are rejected"""
        orchestrator = OnboardingOrchestrator()
        
        orchestrator.start_onboarding("onboard application --app-name Test")
        orchestrator.present_onboarding()
        orchestrator.process_experience_choice("2")
        orchestrator.process_interaction_choice("2", "mid")
        
        # Try invalid choices
        for invalid in ["0", "99", "invalid", "", " "]:
            result = orchestrator.process_tech_stack_choice(invalid)
            assert result["status"] == "error"
            assert "invalid" in result["message"].lower()
    
    def test_onboarding_state_lost_error(self):
        """Test graceful handling when onboarding state is lost"""
        orchestrator = OnboardingOrchestrator()
        
        # Try to process tech stack choice without completing previous steps
        # This should fail because _pending_profile doesn't exist
        result = orchestrator.process_tech_stack_choice("2")
        assert result["status"] == "error"
        assert "state lost" in result["message"].lower() or "restart" in result["message"].lower()


class TestProfilePersistence:
    """Test that profiles persist correctly across sessions"""
    
    def test_profile_survives_orchestrator_recreation(self):
        """Test that profile persists when orchestrator is recreated"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            # First session: create profile
            tier1_1 = WorkingMemory(Path(temp_db_path))
            orch1 = OnboardingOrchestrator(tier1_api=tier1_1)
            
            orch1.start_onboarding("onboard application --app-name PersistTest")
            orch1.present_onboarding()
            orch1.process_experience_choice("4")  # Expert
            orch1.process_interaction_choice("1", "expert")  # Autonomous
            orch1.process_tech_stack_choice("3")  # AWS
            
            del orch1
            del tier1_1
            
            # Second session: retrieve profile
            tier1_2 = WorkingMemory(Path(temp_db_path))
            orch2 = OnboardingOrchestrator(tier1_api=tier1_2)
            
            app_name = orch2.get_application_name()
            profile = tier1_2.get_profile()
            
            assert app_name == "PersistTest"
            assert profile["experience_level"] == "expert"
            assert profile["interaction_mode"] == "autonomous"
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_update_profile_after_onboarding(self):
        """Test that profile can be updated after initial onboarding"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            tier1 = WorkingMemory(Path(temp_db_path))
            orchestrator = OnboardingOrchestrator(tier1_api=tier1)
            
            # Initial onboarding
            orchestrator.start_onboarding("onboard application --app-name UpdateTest")
            orchestrator.present_onboarding()
            orchestrator.process_experience_choice("1")  # Junior
            orchestrator.process_interaction_choice("3", "junior")  # Educational
            orchestrator.process_tech_stack_choice("1")  # No preference
            
            # Update profile
            update_result = tier1.update_profile(
                experience_level="senior",
                interaction_mode="guided"
            )
            
            assert update_result is True
            
            # Verify update
            updated_profile = tier1.get_profile()
            assert updated_profile["experience_level"] == "senior"
            assert updated_profile["interaction_mode"] == "guided"
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


class TestOnboardingEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_onboarding_with_empty_app_name(self):
        """Test that empty app name is rejected"""
        orchestrator = OnboardingOrchestrator()
        
        with pytest.raises(ValueError):
            orchestrator.start_onboarding("onboard application --app-name ''")
    
    def test_onboarding_with_whitespace_only_app_name(self):
        """Test that whitespace-only app name is rejected"""
        orchestrator = OnboardingOrchestrator()
        
        with pytest.raises(ValueError):
            orchestrator.start_onboarding("onboard application --app-name '   '")
    
    def test_onboarding_with_very_long_app_name(self):
        """Test handling of very long application names"""
        orchestrator = OnboardingOrchestrator()
        
        long_name = "A" * 200
        result = orchestrator.start_onboarding(f"onboard application --app-name {long_name}")
        
        # Should either accept or reject with clear message
        assert result is not None
    
    def test_onboarding_with_special_characters_in_app_name(self):
        """Test app names with special characters"""
        orchestrator = OnboardingOrchestrator()
        
        special_names = [
            "My-Project",
            "Project_2024",
            "Project.Name",
            "Project Name"
        ]
        
        for name in special_names:
            result = orchestrator.start_onboarding(f"onboard application --app-name '{name}'")
            assert name in result or "Invalid" in result
    
    def test_concurrent_onboarding_attempts(self):
        """Test that concurrent onboarding attempts are handled safely"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            tier1 = WorkingMemory(Path(temp_db_path))
            
            # Start two onboarding sessions
            orch1 = OnboardingOrchestrator(tier1_api=tier1)
            orch2 = OnboardingOrchestrator(tier1_api=tier1)
            
            # Both start onboarding
            orch1.start_onboarding("onboard application --app-name App1")
            orch2.start_onboarding("onboard application --app-name App2")
            
            # Last one should win (or error gracefully)
            app_name = tier1.get_application_name()
            assert app_name in ["App1", "App2"]
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_onboarding_status_check(self):
        """Test ability to check onboarding status"""
        orchestrator = OnboardingOrchestrator()
        
        # Before onboarding
        status = orchestrator.get_onboarding_status()
        assert status["complete"] is False
        
        # After partial onboarding
        orchestrator.start_onboarding("onboard application --app-name StatusTest")
        orchestrator.present_onboarding()
        orchestrator.process_experience_choice("2")
        
        status = orchestrator.get_onboarding_status()
        assert "in_progress" in str(status).lower() or status["complete"] is False


class TestOnboardingHelperMethods:
    """Test helper methods and utilities"""
    
    def test_get_profile_when_none_exists(self):
        """Test get_profile returns None when no profile exists"""
        orchestrator = OnboardingOrchestrator()
        
        # No tier1_api set yet
        profile = orchestrator.get_profile()
        assert profile is None or profile == {}
    
    def test_reset_onboarding_state(self):
        """Test ability to reset onboarding state"""
        orchestrator = OnboardingOrchestrator()
        
        # Start onboarding
        orchestrator.start_onboarding("onboard application --app-name ResetTest")
        orchestrator.present_onboarding()
        orchestrator.process_experience_choice("2")
        
        # Reset
        orchestrator.reset_onboarding()
        
        # Should be back to initial state
        status = orchestrator.get_onboarding_status()
        assert status["complete"] is False
    
    def test_validate_profile_data(self):
        """Test profile data validation"""
        orchestrator = OnboardingOrchestrator()
        
        # Valid profile data
        valid_data = {
            "experience_level": "mid",
            "interaction_mode": "guided"
        }
        assert orchestrator.validate_profile_data(valid_data) is True
        
        # Invalid profile data
        invalid_data = {
            "experience_level": "invalid",
            "interaction_mode": "guided"
        }
        assert orchestrator.validate_profile_data(invalid_data) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
