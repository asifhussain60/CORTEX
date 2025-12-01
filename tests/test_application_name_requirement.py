"""
Phase 1.3 RED: Application Name Requirement Tests

TDD Cycle: RED Phase
Tests validate:
- --app-name parameter requirement for onboarding
- Application name storage in Tier 1 working memory
- Intent router recognition of app-name requirement
- Error messages for missing app-name
- Help text updates

Author: Asif Hussain
Version: 1.0.0 (RED Phase)
Created: 2025-12-01
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrators.onboarding_orchestrator import OnboardingOrchestrator


class TestApplicationNameParameter:
    """Test --app-name parameter requirement"""
    
    def test_onboarding_requires_app_name_parameter(self):
        """Test that onboarding requires --app-name parameter"""
        orchestrator = OnboardingOrchestrator()
        
        # Should fail without app-name
        with pytest.raises(ValueError, match="--app-name parameter is required"):
            orchestrator.start_onboarding("onboard application")
    
    def test_onboarding_accepts_valid_app_name(self):
        """Test that onboarding accepts valid --app-name"""
        orchestrator = OnboardingOrchestrator()
        
        # Should succeed with app-name
        result = orchestrator.start_onboarding("onboard application --app-name MyProject")
        
        assert result is not None
        assert "MyProject" in result or "application name" in result.lower()
    
    def test_app_name_extraction_from_command(self):
        """Test extraction of app name from various command formats"""
        orchestrator = OnboardingOrchestrator()
        
        test_cases = [
            ("onboard application --app-name MyProject", "MyProject"),
            ("onboard application --app-name 'My Project'", "My Project"),
            ("onboard application --app-name \"Complex-Name_123\"", "Complex-Name_123"),
        ]
        
        for command, expected_name in test_cases:
            extracted = orchestrator._extract_app_name(command)
            assert extracted == expected_name, f"Failed to extract '{expected_name}' from '{command}'"
    
    def test_app_name_validation_rules(self):
        """Test application name validation rules"""
        orchestrator = OnboardingOrchestrator()
        
        # Valid names
        valid_names = ["MyProject", "project-name", "Project_123", "My Project"]
        for name in valid_names:
            assert orchestrator._validate_app_name(name) is True
        
        # Invalid names
        invalid_names = ["", "   ", "a", "ab"]  # Empty, whitespace-only, too short
        for name in invalid_names:
            assert orchestrator._validate_app_name(name) is False


class TestTier1Storage:
    """Test application name storage in Tier 1 working memory"""
    
    def test_app_name_stored_in_tier1(self):
        """Test that application name is stored in Tier 1"""
        # Create a temporary database for testing
        import tempfile
        import os
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            from src.tier1.working_memory import WorkingMemory
            wm = WorkingMemory(Path(temp_db_path))
            
            # Store application name
            result = wm.store_application_name("TestApp")
            assert result is True
            
            # Verify it was stored
            retrieved = wm.get_application_name()
            assert retrieved == "TestApp"
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_app_name_retrieved_from_tier1(self):
        """Test that application name can be retrieved from Tier 1"""
        import tempfile
        import os
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            from src.tier1.working_memory import WorkingMemory
            wm = WorkingMemory(Path(temp_db_path))
            
            # Store and retrieve
            wm.store_application_name("StoredApp")
            retrieved = wm.get_application_name()
            
            assert retrieved == "StoredApp"
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_app_name_persists_across_sessions(self):
        """Test that application name persists in Tier 1 database"""
        import tempfile
        import os
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            from src.tier1.working_memory import WorkingMemory
            
            # First session - store name
            wm1 = WorkingMemory(Path(temp_db_path))
            wm1.store_application_name("PersistentApp")
            del wm1  # Simulate session end
            
            # Second session - retrieve name
            wm2 = WorkingMemory(Path(temp_db_path))
            retrieved = wm2.get_application_name()
            
            assert retrieved == "PersistentApp"
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


class TestIntentRouterIntegration:
    """Test intent router recognizes app-name requirement"""
    
    def test_intent_router_requires_app_name_for_onboarding(self):
        """Test that intent router checks for --app-name in onboarding commands"""
        from cortex_agents.intent_router import IntentRouter
        
        # IntentRouter requires name parameter
        router = IntentRouter(name="TestRouter")
        
        # Should validate app-name presence
        result = router.validate_onboarding_command("onboard application")
        assert result is not True and "app-name" in str(result)
        
        result = router.validate_onboarding_command("onboard application --app-name Test")
        assert result is True
    
    def test_intent_router_extracts_app_name(self):
        """Test that intent router extracts app-name for downstream use"""
        from cortex_agents.intent_router import IntentRouter
        
        # IntentRouter requires name parameter
        router = IntentRouter(name="TestRouter")
        
        command = "onboard application --app-name MyApp"
        intent_data = router.parse_command(command)
        
        assert intent_data.get('app_name') == "MyApp"
        assert intent_data.get('intent') == 'onboard'


class TestErrorMessages:
    """Test error messages for missing or invalid app-name"""
    
    def test_missing_app_name_error_message(self):
        """Test clear error message when --app-name is missing"""
        orchestrator = OnboardingOrchestrator()
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.start_onboarding("onboard application")
        
        error_msg = str(exc_info.value)
        assert "--app-name" in error_msg
        assert "required" in error_msg.lower()
        assert "example" in error_msg.lower() or "usage" in error_msg.lower()
    
    def test_invalid_app_name_error_message(self):
        """Test clear error message when app-name is invalid"""
        orchestrator = OnboardingOrchestrator()
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.start_onboarding("onboard application --app-name ab")
        
        error_msg = str(exc_info.value)
        assert "invalid" in error_msg.lower() or "must be" in error_msg.lower()
        assert "3 characters" in error_msg or "too short" in error_msg.lower()
    
    def test_error_message_includes_help_text(self):
        """Test that error message includes help text"""
        orchestrator = OnboardingOrchestrator()
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.start_onboarding("onboard application")
        
        error_msg = str(exc_info.value)
        assert "onboard application --app-name <name>" in error_msg or \
               "Usage:" in error_msg


class TestHelpTextUpdates:
    """Test help text updates for application name requirement"""
    
    def test_help_command_shows_app_name_requirement(self):
        """Test that help command shows --app-name requirement"""
        # This will be in response templates
        from pathlib import Path
        import yaml
        
        templates_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
        
        if not templates_path.exists():
            pytest.skip("response-templates.yaml not found")
        
        with open(templates_path, encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        # Check onboarding template mentions --app-name
        onboarding_template = templates.get('templates', {}).get('onboarding', {})
        content = str(onboarding_template.get('response_content', ''))
        
        assert "--app-name" in content or "application name" in content.lower()
    
    def test_onboarding_triggers_include_app_name_format(self):
        """Test that onboarding triggers show app-name format"""
        from pathlib import Path
        import yaml
        
        templates_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
        
        if not templates_path.exists():
            pytest.skip("response-templates.yaml not found")
        
        with open(templates_path, encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        onboarding_template = templates.get('templates', {}).get('onboarding', {})
        triggers = onboarding_template.get('triggers', [])
        
        # At least one trigger should show format with app-name
        has_app_name_format = any('--app-name' in trigger or '<name>' in trigger 
                                   for trigger in triggers)
        
        assert has_app_name_format or \
               "app-name" in str(onboarding_template.get('response_content', '')).lower()


class TestApplicationNameUsage:
    """Test that CORTEX uses application name in subsequent interactions"""
    
    @patch('orchestrators.onboarding_orchestrator.WorkingMemory')
    def test_cortex_uses_app_name_in_responses(self, mock_working_memory):
        """Test that CORTEX includes application name in responses"""
        mock_wm = Mock()
        mock_wm.get_application_name.return_value = "MyProject"
        mock_working_memory.return_value = mock_wm
        
        orchestrator = OnboardingOrchestrator()
        orchestrator.start_onboarding("onboard application --app-name MyProject")
        
        # Get a response that should include app name
        response = orchestrator.generate_welcome_message()
        
        assert "MyProject" in response
    
    @patch('orchestrators.onboarding_orchestrator.WorkingMemory')
    def test_app_name_available_to_all_orchestrators(self, mock_working_memory):
        """Test that application name is accessible from any orchestrator"""
        mock_wm = Mock()
        mock_wm.get_application_name.return_value = "SharedApp"
        mock_working_memory.return_value = mock_wm
        
        # Should be accessible without re-initialization
        orchestrator = OnboardingOrchestrator()
        name = orchestrator.get_application_name()
        
        assert name == "SharedApp"


class TestEdgeCases:
    """Test edge cases for application name handling"""
    
    def test_app_name_with_special_characters(self):
        """Test application names with special characters"""
        orchestrator = OnboardingOrchestrator()
        
        special_names = [
            "Project-Name",
            "Project_Name",
            "Project.Name",
            "Project Name",  # Space
            "Project-2024",
        ]
        
        for name in special_names:
            # Should either accept or reject consistently
            is_valid = orchestrator._validate_app_name(name)
            assert isinstance(is_valid, bool)
    
    def test_app_name_case_preservation(self):
        """Test that application name case is preserved"""
        orchestrator = OnboardingOrchestrator()
        
        test_names = ["MyProject", "myproject", "MYPROJECT", "MyPrOjEcT"]
        
        for name in test_names:
            extracted = orchestrator._extract_app_name(f"onboard application --app-name {name}")
            assert extracted == name  # Exact case match
    
    def test_multiple_app_name_parameters(self):
        """Test handling of multiple --app-name parameters"""
        orchestrator = OnboardingOrchestrator()
        
        # Should either take first, last, or error
        command = "onboard application --app-name First --app-name Second"
        
        with pytest.raises(ValueError):
            orchestrator.start_onboarding(command)
    
    def test_app_name_update_after_onboarding(self):
        """Test that application name can be updated after initial onboarding"""
        orchestrator = OnboardingOrchestrator()
        
        # Initial onboarding
        orchestrator.start_onboarding("onboard application --app-name OldName")
        
        # Update name
        result = orchestrator.update_application_name("NewName")
        
        assert result is True
        assert orchestrator.get_application_name() == "NewName"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
