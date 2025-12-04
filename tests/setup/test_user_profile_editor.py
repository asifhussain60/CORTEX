"""
Tests for User Profile Editor Module (Task 2.5)
TDD RED Phase: Write failing tests first
"""
import pytest
from unittest.mock import patch, MagicMock
from src.setup.models.user_profile import UserProfile
from src.setup.modules.user_profile_editor import UserProfileEditor


class TestUserProfileEditor:
    """Test suite for user profile editing functionality"""
    
    @pytest.fixture
    def sample_profile(self):
        """Create sample user profile for testing"""
        return UserProfile(
            name="Original User",
            preference="balanced",
            role="intermediate",
            work_area="web_dev",
            language="en"
        )
    
    def test_editor_initialization(self, sample_profile):
        """Test editor can be instantiated with profile"""
        editor = UserProfileEditor(sample_profile)
        assert editor is not None
        assert editor.profile == sample_profile
    
    def test_edit_name(self, sample_profile):
        """Test editing user name"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value='New Name'):
            updated_profile = editor.edit_name()
            assert updated_profile.name == 'New Name'
            assert updated_profile.preference == sample_profile.preference  # unchanged
    
    def test_edit_name_empty_keeps_current(self, sample_profile):
        """Test empty input keeps current name"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value=''):
            updated_profile = editor.edit_name()
            assert updated_profile.name == 'Original User'
    
    def test_edit_preference(self, sample_profile):
        """Test editing response preference"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value='1'):  # concise
            updated_profile = editor.edit_preference()
            assert updated_profile.preference == 'concise'
    
    def test_edit_preference_invalid_then_valid(self, sample_profile):
        """Test preference editing with validation retry"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', side_effect=['5', '3']):
            updated_profile = editor.edit_preference()
            assert updated_profile.preference == 'verbose'
    
    def test_edit_role(self, sample_profile):
        """Test editing user role"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value='3'):  # expert
            updated_profile = editor.edit_role()
            assert updated_profile.role == 'expert'
    
    def test_edit_role_empty_keeps_current(self, sample_profile):
        """Test empty input keeps current role"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value=''):
            updated_profile = editor.edit_role()
            assert updated_profile.role == 'intermediate'
    
    def test_edit_work_area(self, sample_profile):
        """Test editing work area"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value='5'):  # data_science
            updated_profile = editor.edit_work_area()
            assert updated_profile.work_area == 'data_science'
    
    def test_edit_language(self, sample_profile):
        """Test editing preferred language"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value='2'):  # Spanish
            updated_profile = editor.edit_language()
            assert updated_profile.language == 'es'
    
    def test_edit_language_empty_keeps_current(self, sample_profile):
        """Test empty input keeps current language"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.input', return_value=''):
            updated_profile = editor.edit_language()
            assert updated_profile.language == 'en'
    
    def test_show_menu_displays_options(self, sample_profile):
        """Test menu displays all edit options"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.print') as mock_print:
            editor.show_menu()
            
            # Verify menu items printed
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('Name' in call or 'name' in call.lower() for call in calls)
            assert any('Preference' in call or 'preference' in call.lower() for call in calls)
            assert any('Role' in call or 'role' in call.lower() for call in calls)
    
    def test_run_interactive_edit_single_field(self, sample_profile):
        """Test interactive edit of single field"""
        editor = UserProfileEditor(sample_profile)
        # Select name (1), enter new name, quit (6)
        mock_inputs = ['1', 'Updated Name', '6']
        
        with patch('builtins.input', side_effect=mock_inputs):
            updated_profile = editor.run()
            assert updated_profile.name == 'Updated Name'
    
    def test_run_interactive_edit_multiple_fields(self, sample_profile):
        """Test interactive edit of multiple fields"""
        editor = UserProfileEditor(sample_profile)
        # Select preference (2), choose concise (1), select role (3), choose expert (3), quit (6)
        mock_inputs = ['2', '1', '3', '3', '6']
        
        with patch('builtins.input', side_effect=mock_inputs):
            updated_profile = editor.run()
            assert updated_profile.preference == 'concise'
            assert updated_profile.role == 'expert'
    
    def test_run_interactive_invalid_menu_choice(self, sample_profile):
        """Test invalid menu choice handling"""
        editor = UserProfileEditor(sample_profile)
        # Select invalid (9), then quit (6)
        mock_inputs = ['9', '6']
        
        with patch('builtins.input', side_effect=mock_inputs):
            with patch('builtins.print') as mock_print:
                updated_profile = editor.run()
                
                # Verify error message printed
                calls = [str(call) for call in mock_print.call_args_list]
                assert any('invalid' in call.lower() or 'error' in call.lower() for call in calls)
    
    def test_show_current_profile(self, sample_profile):
        """Test displaying current profile"""
        editor = UserProfileEditor(sample_profile)
        with patch('builtins.print') as mock_print:
            editor.show_current_profile()
            
            # Verify profile details printed
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('Original User' in call for call in calls)
            assert any('balanced' in call for call in calls)
            assert any('intermediate' in call for call in calls)
    
    def test_edit_all_fields_sequentially(self, sample_profile):
        """Test editing all fields in sequence"""
        editor = UserProfileEditor(sample_profile)
        
        # Edit name
        with patch('builtins.input', return_value='Alice'):
            editor.profile = editor.edit_name()
        
        # Edit preference
        with patch('builtins.input', return_value='1'):
            editor.profile = editor.edit_preference()
        
        # Edit role
        with patch('builtins.input', return_value='3'):
            editor.profile = editor.edit_role()
        
        # Edit work area
        with patch('builtins.input', return_value='6'):
            editor.profile = editor.edit_work_area()
        
        # Edit language
        with patch('builtins.input', return_value='3'):
            editor.profile = editor.edit_language()
        
        # Verify all changes
        assert editor.profile.name == 'Alice'
        assert editor.profile.preference == 'concise'
        assert editor.profile.role == 'expert'
        assert editor.profile.work_area == 'ai_ml'
        assert editor.profile.language == 'fr'
