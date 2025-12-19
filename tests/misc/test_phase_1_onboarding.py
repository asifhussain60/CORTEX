"""
Test suite for Phase 1 Onboarding Enhancements
Tests Phase 1.2 (notifications) and Phase 1.3 (app name requirement)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrators.onboarding_orchestrator import OnboardingOrchestrator


class TestLongRunningNotifications:
    """Test Phase 1.2: Long-running operation notifications"""
    
    @patch('builtins.print')
    def test_shows_expectation_message_on_onboarding_start(self, mock_print):
        """Should display 10-minute notification when onboarding starts"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        # Start onboarding with valid app name
        result = orchestrator.start_onboarding("onboard application --app-name TestApp")
        
        # Verify print was called with notification message
        assert mock_print.called, "Should print notification"
        call_args = str(mock_print.call_args)
        assert "10" in call_args or "Application Onboarding" in call_args, \
            "Notification should mention duration or operation"
    
    @patch('builtins.print')
    def test_notification_includes_coffee_suggestion(self, mock_print):
        """Should suggest coffee break for 10-minute operation"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        orchestrator.start_onboarding("onboard application --app-name TestApp")
        
        call_args = str(mock_print.call_args)
        assert "coffee" in call_args.lower() or "☕" in call_args, \
            "Should suggest coffee break"


class TestApplicationNameRequirement:
    """Test Phase 1.3: Application name parameter requirement"""
    
    def test_requires_app_name_parameter(self):
        """Should raise error if --app-name is missing"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        with pytest.raises(ValueError, match="--app-name parameter is required"):
            orchestrator.start_onboarding("onboard application")
    
    def test_validates_app_name_minimum_length(self):
        """Should reject app names shorter than 3 characters"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        with pytest.raises(ValueError, match="at least 3 characters"):
            orchestrator.start_onboarding("onboard application --app-name ab")
    
    def test_accepts_valid_app_name(self):
        """Should accept app name with 3+ characters"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        result = orchestrator.start_onboarding("onboard application --app-name TestApp")
        
        assert "TestApp" in result, "Should confirm app name"
        assert mock_tier1.store_application_name.called, \
            "Should store app name in Tier 1"
    
    def test_extracts_app_name_from_command(self):
        """Should extract app name from various command formats"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        # Test unquoted
        result1 = orchestrator.start_onboarding("onboard application --app-name MyApp")
        assert "MyApp" in result1
        
        # Test with quotes
        result2 = orchestrator.start_onboarding('onboard application --app-name "My App"')
        assert "My App" in result2
    
    def test_stores_app_name_in_tier1(self):
        """Should call store_application_name on Tier 1 API"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        orchestrator.start_onboarding("onboard application --app-name MyProject")
        
        mock_tier1.store_application_name.assert_called_once_with("MyProject")
    
    def test_returns_confirmation_message(self):
        """Should return confirmation with application name"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        result = orchestrator.start_onboarding("onboard application --app-name MyProject")
        
        assert "MyProject" in result, "Should include app name"
        assert "started" in result.lower(), "Should confirm start"
    
    def test_help_text_shows_usage(self):
        """Error message should show correct usage"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        try:
            orchestrator.start_onboarding("onboard application")
        except ValueError as e:
            error_msg = str(e)
            assert "onboard application --app-name <name>" in error_msg
            assert "Example:" in error_msg


class TestApplicationNameValidation:
    """Test application name validation logic"""
    
    def test_validates_minimum_length(self):
        """Should validate 3-character minimum"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        # Valid: 3 characters
        assert orchestrator._validate_app_name("abc") == True
        
        # Invalid: 2 characters
        assert orchestrator._validate_app_name("ab") == False
        
        # Invalid: empty
        assert orchestrator._validate_app_name("") == False
    
    def test_handles_special_characters(self):
        """Should accept app names with special characters"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        # Should accept hyphens, underscores, spaces
        assert orchestrator._validate_app_name("My-App") == True
        assert orchestrator._validate_app_name("My_App") == True
        assert orchestrator._validate_app_name("My App") == True


class TestApplicationNameExtraction:
    """Test app name extraction from commands"""
    
    def test_extracts_unquoted_name(self):
        """Should extract simple unquoted app name"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        name = orchestrator._extract_app_name("onboard application --app-name MyApp")
        assert name == "MyApp"
    
    def test_extracts_double_quoted_name(self):
        """Should extract app name with double quotes"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        name = orchestrator._extract_app_name('onboard application --app-name "My App"')
        assert name == "My App"
    
    def test_extracts_single_quoted_name(self):
        """Should extract app name with single quotes"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        name = orchestrator._extract_app_name("onboard application --app-name 'My App'")
        assert name == "My App"
    
    def test_returns_none_if_missing(self):
        """Should return None if --app-name not in command"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        name = orchestrator._extract_app_name("onboard application")
        assert name is None
    
    def test_raises_error_on_multiple_parameters(self):
        """Should raise error if multiple --app-name parameters"""
        mock_tier1 = Mock()
        orchestrator = OnboardingOrchestrator(tier1_api=mock_tier1)
        
        with pytest.raises(ValueError, match="Multiple --app-name parameters"):
            orchestrator._extract_app_name(
                "onboard application --app-name App1 --app-name App2"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
