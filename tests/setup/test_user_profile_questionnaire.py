"""
Tests for User Profile Questionnaire Module (Task 2.2)
TDD RED Phase: Write failing tests first
"""
import pytest
from unittest.mock import patch, MagicMock
from src.setup.models.user_profile import UserProfile
from src.setup.modules.user_profile_questionnaire import UserProfileQuestionnaire


class TestUserProfileQuestionnaire:
    """Test suite for interactive user profile questionnaire"""
    
    def test_questionnaire_initialization(self):
        """Test questionnaire can be instantiated"""
        questionnaire = UserProfileQuestionnaire()
        assert questionnaire is not None
    
    def test_ask_name_valid_input(self):
        """Test asking for user name with valid input"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value='John Doe'):
            name = questionnaire.ask_name()
            assert name == 'John Doe'
    
    def test_ask_name_empty_uses_default(self):
        """Test empty name uses default from git config"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value=''):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    stdout='Jane Smith\n',
                    returncode=0
                )
                name = questionnaire.ask_name()
                assert name == 'Jane Smith'
    
    def test_ask_preference_valid_choice(self):
        """Test asking for response preference with valid choice"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value='2'):
            preference = questionnaire.ask_preference()
            assert preference == 'balanced'
    
    def test_ask_preference_invalid_then_valid(self):
        """Test preference validation with retry on invalid input"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', side_effect=['5', '1']):
            preference = questionnaire.ask_preference()
            assert preference == 'concise'
    
    def test_ask_role_valid_choice(self):
        """Test asking for user role with valid choice"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value='3'):
            role = questionnaire.ask_role()
            assert role == 'expert'
    
    def test_ask_role_default_on_empty(self):
        """Test role uses default (intermediate) on empty input"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value=''):
            role = questionnaire.ask_role()
            assert role == 'intermediate'
    
    def test_ask_work_area_valid_choice(self):
        """Test asking for work area with valid choice"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value='5'):
            work_area = questionnaire.ask_work_area()
            assert work_area == 'data_science'
    
    def test_ask_work_area_invalid_then_valid(self):
        """Test work area validation with retry"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', side_effect=['15', '2']):
            work_area = questionnaire.ask_work_area()
            assert work_area == 'backend'
    
    def test_ask_language_valid_choice(self):
        """Test asking for language with valid choice"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value='3'):
            language = questionnaire.ask_language()
            assert language == 'fr'
    
    def test_ask_language_displays_native_names(self):
        """Test language options show native names"""
        questionnaire = UserProfileQuestionnaire()
        # This test will verify the display includes native names like "English (English)"
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print') as mock_print:
                language = questionnaire.ask_language()
                # Verify native names are printed
                calls = [str(call) for call in mock_print.call_args_list]
                assert any('English (English)' in call for call in calls)
    
    def test_ask_language_default_on_empty(self):
        """Test language uses default (en) on empty input"""
        questionnaire = UserProfileQuestionnaire()
        with patch('builtins.input', return_value=''):
            language = questionnaire.ask_language()
            assert language == 'en'
    
    def test_run_questionnaire_creates_profile(self):
        """Test full questionnaire run creates UserProfile"""
        questionnaire = UserProfileQuestionnaire()
        mock_inputs = ['John Doe', '2', '3', '5', '1']
        
        with patch('builtins.input', side_effect=mock_inputs):
            profile = questionnaire.run()
            
            assert isinstance(profile, UserProfile)
            assert profile.name == 'John Doe'
            assert profile.preference == 'balanced'
            assert profile.role == 'expert'
            assert profile.work_area == 'data_science'
            assert profile.language == 'en'
    
    def test_run_questionnaire_with_defaults(self):
        """Test questionnaire with all default values"""
        questionnaire = UserProfileQuestionnaire()
        mock_inputs = ['', '', '', '', '']
        
        with patch('builtins.input', side_effect=mock_inputs):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    stdout='Git User\n',
                    returncode=0
                )
                profile = questionnaire.run()
                
                assert isinstance(profile, UserProfile)
                assert profile.name == 'Git User'
                assert profile.preference == 'verbose'
                assert profile.role == 'intermediate'
                assert profile.work_area == 'general'
                assert profile.language == 'en'
    
    def test_run_questionnaire_displays_welcome(self):
        """Test questionnaire displays welcome message"""
        questionnaire = UserProfileQuestionnaire()
        mock_inputs = ['Test User', '1', '1', '1', '1']
        
        with patch('builtins.input', side_effect=mock_inputs):
            with patch('builtins.print') as mock_print:
                profile = questionnaire.run()
                
                # Verify welcome message printed
                calls = [str(call) for call in mock_print.call_args_list]
                assert any('User Profile Setup' in call or 'profile' in call.lower() for call in calls)
    
    def test_run_questionnaire_displays_summary(self):
        """Test questionnaire displays profile summary at end"""
        questionnaire = UserProfileQuestionnaire()
        mock_inputs = ['Alice', '1', '2', '6', '2']
        
        with patch('builtins.input', side_effect=mock_inputs):
            with patch('builtins.print') as mock_print:
                profile = questionnaire.run()
                
                # Verify summary contains profile details
                calls = [str(call) for call in mock_print.call_args_list]
                assert any('Alice' in call for call in calls)
                assert any('concise' in call for call in calls)
