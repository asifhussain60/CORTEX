"""
Tests for environment_setup.py monolithic script.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys

from src.operations.environment_setup import (
    EnvironmentSetup,
    SetupResult,
    run_setup
)


class TestSetupResult:
    """Tests for SetupResult dataclass."""
    
    def test_setup_result_creation(self):
        """Test creating a SetupResult."""
        result = SetupResult(success=True, profile='standard')
        
        assert result.success is True
        assert result.profile == 'standard'
        assert isinstance(result.steps_completed, list)
        assert isinstance(result.steps_failed, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.timestamp, datetime)
    
    def test_setup_result_to_dict(self):
        """Test converting SetupResult to dictionary."""
        result = SetupResult(
            success=True,
            profile='minimal',
            steps_completed=['step1', 'step2'],
            warnings=['warning1']
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['profile'] == 'minimal'
        assert result_dict['steps_completed'] == ['step1', 'step2']
        assert result_dict['warnings'] == ['warning1']
        assert 'timestamp' in result_dict
        assert 'platform_info' in result_dict


class TestEnvironmentSetup:
    """Tests for EnvironmentSetup class."""
    
    @pytest.fixture
    def setup_instance(self, tmp_path):
        """Create EnvironmentSetup instance with temp directory."""
        return EnvironmentSetup(project_root=tmp_path)
    
    @pytest.fixture
    def mock_cortex_project(self, tmp_path):
        """Create a mock CORTEX project structure."""
        # Create required directories
        (tmp_path / 'cortex-brain').mkdir()
        (tmp_path / 'src').mkdir()
        (tmp_path / 'tests').mkdir()
        (tmp_path / 'prompts').mkdir()
        (tmp_path / '.github').mkdir()
        
        # Create required files
        (tmp_path / 'README.md').touch()
        (tmp_path / 'requirements.txt').write_text('pytest\n')
        (tmp_path / 'cortex.config.json').write_text('{}')
        
        # Create brain files
        (tmp_path / 'cortex-brain' / 'brain-protection-rules.yaml').touch()
        (tmp_path / 'cortex-brain' / 'knowledge-graph.yaml').touch()
        (tmp_path / 'cortex-brain' / 'response-templates.yaml').touch()
        
        return tmp_path
    
    def test_initialization(self, tmp_path):
        """Test EnvironmentSetup initialization."""
        setup = EnvironmentSetup(project_root=tmp_path)
        
        assert setup.project_root == tmp_path
        assert isinstance(setup.result, SetupResult)
        assert setup.result.success is False
        assert isinstance(setup.start_time, datetime)
    
    def test_initialization_default_path(self):
        """Test EnvironmentSetup with default path."""
        setup = EnvironmentSetup()
        
        assert setup.project_root == Path.cwd()
    
    def test_validate_project_success(self, mock_cortex_project):
        """Test successful project validation."""
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        
        result = setup._validate_project()
        
        assert result is True
        assert 'project_validation' in setup.result.steps_completed
    
    def test_validate_project_missing_directory(self, tmp_path):
        """Test project validation with missing directory."""
        # Create partial structure
        (tmp_path / 'src').mkdir()
        (tmp_path / 'README.md').touch()
        
        setup = EnvironmentSetup(project_root=tmp_path)
        result = setup._validate_project()
        
        assert result is False
        assert 'project_validation' in setup.result.steps_failed
    
    def test_detect_platform(self, setup_instance):
        """Test platform detection."""
        result = setup_instance._detect_platform()
        
        assert result is True
        assert 'platform_detection' in setup_instance.result.steps_completed
        assert 'os' in setup_instance.result.platform_info
        assert 'python_version' in setup_instance.result.platform_info
        assert setup_instance.result.platform_info['os'] in ['mac', 'windows', 'linux', 'unknown']
    
    def test_initialize_brain_success(self, mock_cortex_project):
        """Test successful brain initialization."""
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        
        result = setup._initialize_brain()
        
        assert result is True
        assert 'brain_initialization' in setup.result.steps_completed
    
    def test_initialize_brain_missing_directory(self, tmp_path):
        """Test brain initialization with missing directory."""
        setup = EnvironmentSetup(project_root=tmp_path)
        
        result = setup._initialize_brain()
        
        assert result is False
        assert 'brain_initialization' in setup.result.steps_failed
    
    def test_initialize_brain_missing_files(self, tmp_path):
        """Test brain initialization with missing essential files."""
        (tmp_path / 'cortex-brain').mkdir()
        
        setup = EnvironmentSetup(project_root=tmp_path)
        result = setup._initialize_brain()
        
        assert result is True  # Still succeeds but warns
        assert len(setup.result.warnings) > 0
    
    @patch('subprocess.run')
    def test_sync_git_success(self, mock_run, mock_cortex_project):
        """Test successful git sync."""
        # Create .git directory
        (mock_cortex_project / '.git').mkdir()
        
        # Mock git status (clean)
        mock_run.side_effect = [
            Mock(returncode=0, stdout='', stderr=''),  # git status
            Mock(returncode=0, stdout='Already up to date.', stderr='')  # git pull
        ]
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup._sync_git()
        
        assert result is True
        assert 'git_sync' in setup.result.steps_completed
    
    @patch('subprocess.run')
    def test_sync_git_uncommitted_changes(self, mock_run, mock_cortex_project):
        """Test git sync with uncommitted changes."""
        # Create .git directory
        (mock_cortex_project / '.git').mkdir()
        
        # Mock git status (dirty)
        mock_run.return_value = Mock(returncode=0, stdout='M file.py', stderr='')
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup._sync_git()
        
        assert result is False
        assert len(setup.result.warnings) > 0
    
    def test_setup_virtualenv_already_active(self, setup_instance):
        """Test virtual environment setup when already active."""
        # Mock being in a virtual environment
        with patch.object(sys, 'prefix', '/path/to/venv'):
            with patch.object(sys, 'base_prefix', '/path/to/python'):
                result = setup_instance._setup_virtualenv()
        
        assert result is True
        assert 'virtual_environment' in setup_instance.result.steps_completed
    
    def test_setup_virtualenv_exists(self, tmp_path):
        """Test virtual environment setup when venv exists."""
        (tmp_path / '.venv').mkdir()
        
        setup = EnvironmentSetup(project_root=tmp_path)
        result = setup._setup_virtualenv()
        
        assert result is True
        assert 'virtual_environment' in setup.result.steps_completed
        # No warnings expected when already in a working venv - this is the desired state
    
    @patch('subprocess.run')
    def test_install_dependencies_success(self, mock_run, mock_cortex_project):
        """Test successful dependency installation."""
        # Mock pip commands
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup._install_dependencies()
        
        assert result is True
        assert 'python_dependencies' in setup.result.steps_completed
    
    def test_install_dependencies_missing_file(self, tmp_path):
        """Test dependency installation without requirements.txt."""
        setup = EnvironmentSetup(project_root=tmp_path)
        
        result = setup._install_dependencies()
        
        assert result is False
        assert 'python_dependencies' in setup.result.steps_failed
    
    @patch('subprocess.run')
    def test_install_dependencies_failure(self, mock_run, mock_cortex_project):
        """Test failed dependency installation."""
        # Mock pip upgrade success, install failure
        mock_run.side_effect = [
            Mock(returncode=0, stdout='', stderr=''),  # pip upgrade
            Mock(returncode=1, stdout='', stderr='Error installing')  # install
        ]
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup._install_dependencies()
        
        assert result is False
        assert 'python_dependencies' in setup.result.steps_failed
    
    def test_configure_vision_api(self, setup_instance):
        """Test Vision API configuration (intentionally skips for MVP)."""
        result = setup_instance._configure_vision_api()
        
        assert result is False  # MVP skips this
    
    def test_enable_conversation_tracking_exists(self, mock_cortex_project):
        """Test conversation tracking with existing database."""
        db_path = mock_cortex_project / 'cortex-brain' / 'conversation-history.db'
        db_path.touch()
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup._enable_conversation_tracking()
        
        assert result is True
        assert 'conversation_tracking' in setup.result.steps_completed
    
    def test_enable_conversation_tracking_missing(self, mock_cortex_project):
        """Test conversation tracking without database."""
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup._enable_conversation_tracking()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_verify_tooling_all_available(self, mock_run, setup_instance):
        """Test tooling verification with all tools available."""
        mock_run.return_value = Mock(returncode=0, stdout='version info', stderr='')
        
        result = setup_instance._verify_tooling()
        
        assert result is True
        assert 'tooling_verification' in setup_instance.result.steps_completed
    
    @patch('subprocess.run')
    def test_verify_tooling_some_missing(self, mock_run, setup_instance):
        """Test tooling verification with missing tools."""
        # First call succeeds, rest fail
        mock_run.side_effect = [
            Mock(returncode=0, stdout='', stderr=''),  # git
            Mock(returncode=1, stdout='', stderr=''),  # pytest
            Mock(returncode=1, stdout='', stderr='')   # mkdocs
        ]
        
        result = setup_instance._verify_tooling()
        
        assert result is False
        assert 'tooling_verification' in setup_instance.result.steps_completed
    
    def test_complete_setup(self, mock_cortex_project):
        """Test setup completion."""
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        
        setup._complete_setup()
        
        assert 'setup_completion' in setup.result.steps_completed
        
        # Check report was created
        report_dir = mock_cortex_project / 'cortex-brain' / 'setup-reports'
        assert report_dir.exists()
        assert len(list(report_dir.glob('setup-*.json'))) > 0
    
    @patch.object(EnvironmentSetup, '_validate_project')
    @patch.object(EnvironmentSetup, '_detect_platform')
    @patch.object(EnvironmentSetup, '_setup_virtualenv')
    @patch.object(EnvironmentSetup, '_install_dependencies')
    @patch.object(EnvironmentSetup, '_initialize_brain')
    @patch.object(EnvironmentSetup, '_complete_setup')
    def test_run_minimal_profile_success(
        self, mock_complete, mock_brain, mock_deps, mock_venv, 
        mock_platform, mock_validate, mock_cortex_project
    ):
        """Test running minimal profile successfully."""
        # Mock all steps to succeed
        for mock in [mock_validate, mock_platform, mock_venv, mock_deps, mock_brain]:
            mock.return_value = True
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup.run(profile='minimal')
        
        assert result.success is True
        assert result.profile == 'minimal'
        assert result.duration_seconds > 0
    
    @patch.object(EnvironmentSetup, '_validate_project')
    def test_run_validation_failure(self, mock_validate, mock_cortex_project):
        """Test run with validation failure."""
        mock_validate.return_value = False
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup.run(profile='minimal')
        
        assert result.success is False
    
    @patch.object(EnvironmentSetup, '_validate_project')
    @patch.object(EnvironmentSetup, '_detect_platform')
    @patch.object(EnvironmentSetup, '_setup_virtualenv')
    @patch.object(EnvironmentSetup, '_install_dependencies')
    def test_run_dependency_failure(
        self, mock_deps, mock_venv, mock_platform, mock_validate, mock_cortex_project
    ):
        """Test run with dependency installation failure."""
        mock_validate.return_value = True
        mock_platform.return_value = True
        mock_venv.return_value = True
        mock_deps.return_value = False
        
        setup = EnvironmentSetup(project_root=mock_cortex_project)
        result = setup.run(profile='minimal')
        
        assert result.success is False


class TestRunSetupFunction:
    """Tests for run_setup convenience function."""
    
    @patch.object(EnvironmentSetup, 'run')
    def test_run_setup_default(self, mock_run):
        """Test run_setup with defaults."""
        mock_run.return_value = SetupResult(success=True, profile='standard')
        
        result = run_setup()
        
        assert result.success is True
        mock_run.assert_called_once_with(profile='standard')
    
    @patch.object(EnvironmentSetup, 'run')
    def test_run_setup_custom_profile(self, mock_run, tmp_path):
        """Test run_setup with custom profile."""
        mock_run.return_value = SetupResult(success=True, profile='full')
        
        result = run_setup(profile='full', project_root=tmp_path)
        
        assert result.success is True
        mock_run.assert_called_once_with(profile='full')


class TestIntegration:
    """Integration tests for environment setup."""
    
    @pytest.mark.skipif(
        not Path.cwd().name == 'CORTEX',
        reason="Must run from CORTEX project root"
    )
    def test_real_cortex_validation(self):
        """Test validation against real CORTEX project."""
        setup = EnvironmentSetup()
        
        # Should be able to validate the actual CORTEX project
        result = setup._validate_project()
        assert result is True
    
    @pytest.mark.skipif(
        not Path.cwd().name == 'CORTEX',
        reason="Must run from CORTEX project root"
    )
    def test_real_platform_detection(self):
        """Test platform detection on real system."""
        setup = EnvironmentSetup()
        
        result = setup._detect_platform()
        assert result is True
        assert setup.result.platform_info['os'] in ['mac', 'windows', 'linux']
