"""
Tests for User Profile CLI Commands (Task 2.7)
TDD RED Phase: Write failing tests first
"""
import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from src.setup.modules.user_profile_cli import UserProfileCLI, ProfileCommands


class TestUserProfileCLI:
    """Test suite for user profile CLI commands"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "machines": {},
                "testing": {"enabled": False},
                "user": {
                    "name": "Test User",
                    "preference": "balanced",
                    "role": "intermediate",
                    "work_area": "web_dev",
                    "language": "en"
                }
            }
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_cli_initialization(self):
        """Test CLI can be instantiated"""
        cli = UserProfileCLI()
        assert cli is not None
    
    def test_show_command_displays_profile(self, temp_config_file):
        """Test 'show' command displays current profile"""
        cli = UserProfileCLI(temp_config_file)
        
        with patch('builtins.print') as mock_print:
            exit_code = cli.show()
            
            # Verify profile details printed (check call args)
            printed_text = ' '.join(str(call[0][0]) if call[0] else '' for call in mock_print.call_args_list)
            assert 'Test User' in printed_text
            assert 'Balanced' in printed_text or 'balanced' in printed_text.lower()
            assert exit_code == 0
    
    def test_show_command_no_profile(self):
        """Test 'show' command when no profile exists"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"machines": {}, "testing": {"enabled": False}}
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        try:
            cli = UserProfileCLI(temp_path)
            
            with patch('builtins.print') as mock_print:
                exit_code = cli.show()
                
                # Verify error message printed
                printed_text = ' '.join(str(call[0][0]) if call[0] else '' for call in mock_print.call_args_list)
                assert 'no' in printed_text.lower() and 'profile' in printed_text.lower()
                assert exit_code == 1
        finally:
            os.unlink(temp_path)
    
    def test_edit_command_opens_editor(self, temp_config_file):
        """Test 'edit' command opens interactive editor"""
        cli = UserProfileCLI(temp_config_file)
        
        # Mock editor interactions: quit immediately (6)
        with patch('builtins.input', return_value='6'):
            exit_code = cli.edit()
            
            assert exit_code == 0
    
    def test_edit_command_no_profile(self):
        """Test 'edit' command when no profile exists"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"machines": {}, "testing": {"enabled": False}}
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        try:
            cli = UserProfileCLI(temp_path)
            
            with patch('builtins.print') as mock_print:
                exit_code = cli.edit()
                
                # Verify error message
                printed_text = ' '.join(str(call[0][0]) if call[0] else '' for call in mock_print.call_args_list)
                assert 'no' in printed_text.lower() and 'profile' in printed_text.lower()
                assert exit_code == 1
        finally:
            os.unlink(temp_path)
    
    def test_edit_command_saves_changes(self, temp_config_file):
        """Test 'edit' command saves profile changes"""
        cli = UserProfileCLI(temp_config_file)
        
        # Mock editing name (1), enter new name, quit (6)
        with patch('builtins.input', side_effect=['1', 'Updated Name', '6']):
            exit_code = cli.edit()
            
            assert exit_code == 0
            
            # Verify changes saved
            with open(temp_config_file, 'r') as f:
                config = json.load(f)
            
            assert config['user']['name'] == 'Updated Name'
    
    def test_create_command_runs_questionnaire(self):
        """Test 'create' command runs interactive questionnaire"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"machines": {}, "testing": {"enabled": False}}
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        try:
            cli = UserProfileCLI(temp_path)
            
            # Mock questionnaire inputs
            mock_inputs = ['New User', '1', '3', '6', '2']
            
            with patch('builtins.input', side_effect=mock_inputs):
                exit_code = cli.create()
                
                assert exit_code == 0
                
                # Verify profile created
                with open(temp_path, 'r') as f:
                    config = json.load(f)
                
                assert 'user' in config
                assert config['user']['name'] == 'New User'
        finally:
            os.unlink(temp_path)
    
    def test_create_command_refuses_if_exists(self, temp_config_file):
        """Test 'create' command refuses if profile already exists"""
        cli = UserProfileCLI(temp_config_file)
        
        with patch('builtins.print') as mock_print:
            exit_code = cli.create()
            
            # Verify error message
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('already exists' in call.lower() or 'exists' in call.lower() for call in calls)
            assert exit_code == 1
    
    def test_delete_command_removes_profile(self, temp_config_file):
        """Test 'delete' command removes profile"""
        cli = UserProfileCLI(temp_config_file)
        
        # Confirm deletion (y)
        with patch('builtins.input', return_value='y'):
            exit_code = cli.delete()
            
            assert exit_code == 0
            
            # Verify profile removed
            with open(temp_config_file, 'r') as f:
                config = json.load(f)
            
            assert 'user' not in config
    
    def test_delete_command_cancels_on_no(self, temp_config_file):
        """Test 'delete' command cancels on 'n' input"""
        cli = UserProfileCLI(temp_config_file)
        
        # Cancel deletion (n)
        with patch('builtins.input', return_value='n'):
            exit_code = cli.delete()
            
            # Verify profile still exists
            with open(temp_config_file, 'r') as f:
                config = json.load(f)
            
            assert 'user' in config
            assert config['user']['name'] == 'Test User'
    
    def test_delete_command_no_profile(self):
        """Test 'delete' command when no profile exists"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"machines": {}, "testing": {"enabled": False}}
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        try:
            cli = UserProfileCLI(temp_path)
            
            with patch('builtins.print') as mock_print:
                exit_code = cli.delete()
                
                # Verify error message
                printed_text = ' '.join(str(call[0][0]) if call[0] else '' for call in mock_print.call_args_list)
                assert 'no' in printed_text.lower() and 'profile' in printed_text.lower()
                assert exit_code == 1
        finally:
            os.unlink(temp_path)
    
    def test_profile_commands_enum(self):
        """Test ProfileCommands enum has expected commands"""
        assert hasattr(ProfileCommands, 'SHOW')
        assert hasattr(ProfileCommands, 'EDIT')
        assert hasattr(ProfileCommands, 'CREATE')
        assert hasattr(ProfileCommands, 'DELETE')
    
    def test_cli_uses_default_config_path(self):
        """Test CLI uses default config path if not provided"""
        cli = UserProfileCLI()
        
        # Should use default CORTEX config path
        assert cli.config_path is not None
        assert 'cortex.config.json' in cli.config_path
