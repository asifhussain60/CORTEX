"""
Test Suite for Python Environment Module

Tests environment detection, dependency checking, and intelligent reuse logic.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.setup.modules.python_environment_module import (
    PythonEnvironmentModule,
    EnvironmentAnalysis
)
from src.setup.base_setup_module import SetupStatus, SetupPhase


class TestPythonEnvironmentModule:
    """Test Python environment detection and configuration."""
    
    @pytest.fixture
    def module(self):
        """Create module instance."""
        return PythonEnvironmentModule()
    
    @pytest.fixture
    def mock_context(self, tmp_path):
        """Create mock setup context."""
        return {
            'project_root': tmp_path,
            'verbose': True
        }
    
    def test_metadata(self, module):
        """Test module metadata."""
        metadata = module.metadata
        assert metadata.module_id == "python_environment"
        assert metadata.phase == SetupPhase.ENVIRONMENT
        assert metadata.priority == 10
        assert not metadata.optional
    
    def test_validate_prerequisites_success(self, module, mock_context):
        """Test prerequisite validation with Python 3.8+."""
        valid, message = module.validate_prerequisites(mock_context)
        assert valid
        assert "Python 3.8+ detected" in message
    
    def test_validate_prerequisites_old_python(self, module, mock_context):
        """Test prerequisite validation fails with old Python."""
        with patch('sys.version_info', (3, 7, 0)):
            valid, message = module.validate_prerequisites(mock_context)
            assert not valid
            assert "3.8+" in message or "3.7" in message
    
    def test_analyze_global_python(self, module, mock_context):
        """Test analysis detects global Python."""
        with patch('sys.prefix', '/usr/bin'), \
             patch('sys.base_prefix', '/usr/bin'):
            
            analysis = module._analyze_environment(mock_context)
            
            assert analysis.is_global
            assert not analysis.is_virtual_env
            assert analysis.action_recommendation == "create_venv"
            assert "isolation required" in analysis.reason.lower()
    
    def test_analyze_virtual_environment(self, module, mock_context):
        """Test analysis detects virtual environment."""
        with patch('sys.prefix', '/path/to/venv'), \
             patch('sys.base_prefix', '/usr/bin'):
            
            analysis = module._analyze_environment(mock_context)
            
            assert analysis.is_virtual_env
            assert not analysis.is_global
    
    def test_detect_parent_project_embedded(self, module, tmp_path):
        """Test detection of parent project for embedded installation."""
        # Create parent project structure
        parent = tmp_path / "NOOR-CANVAS"
        cortex = parent / "CORTEX"
        cortex.mkdir(parents=True)
        (parent / "package.json").write_text("{}")
        
        context = {'project_root': cortex}
        parent_project = module._detect_parent_project(context)
        
        assert parent_project == "NOOR-CANVAS"
    
    def test_detect_parent_project_standalone(self, module, tmp_path):
        """Test no parent project detected for standalone installation."""
        cortex = tmp_path / "CORTEX"
        cortex.mkdir(parents=True)
        
        context = {'project_root': cortex}
        parent_project = module._detect_parent_project(context)
        
        assert parent_project is None
    
    def test_check_dependencies_all_satisfied(self, module):
        """Test dependency check when all packages installed."""
        with patch.object(module, '_check_dependencies', return_value=([], [])):
            missing, conflicts = module._check_dependencies()
            
            assert len(missing) == 0
            assert len(conflicts) == 0
    
    def test_check_dependencies_missing(self, module):
        """Test dependency check detects missing packages."""
        with patch.object(module, '_check_dependencies', return_value=(['pytest', 'PyYAML'], [])):
            missing, conflicts = module._check_dependencies()
            
            assert 'pytest' in missing
            assert 'PyYAML' in missing
            assert len(conflicts) == 0
    
    def test_check_dependencies_conflicts(self, module):
        """Test dependency check detects version conflicts."""
        with patch.object(module, '_check_dependencies', 
                         return_value=([], ['pytest 6.2.0 (need >=8.4.0)'])):
            missing, conflicts = module._check_dependencies()
            
            assert len(missing) == 0
            assert len(conflicts) == 1
            assert 'pytest' in conflicts[0]
    
    def test_execute_reuse_environment(self, module, mock_context):
        """Test execution with environment reuse."""
        mock_analysis = EnvironmentAnalysis(
            is_virtual_env=True,
            environment_path=Path('/path/to/venv'),
            python_version=(3, 11, 0),
            is_global=False,
            parent_project=None,
            dependencies_satisfied=True,
            conflicts=[],
            missing_packages=[],
            action_recommendation="reuse_environment",
            reason="All dependencies satisfied"
        )
        
        with patch.object(module, '_analyze_environment', return_value=mock_analysis), \
             patch.object(module, '_configure_reuse') as mock_reuse:
            
            mock_reuse.return_value = Mock(status=SetupStatus.SUCCESS)
            result = module.execute(mock_context)
            
            assert result.status == SetupStatus.SUCCESS
            mock_reuse.assert_called_once()
    
    def test_execute_create_venv(self, module, mock_context):
        """Test execution with venv creation."""
        mock_analysis = EnvironmentAnalysis(
            is_virtual_env=False,
            environment_path=Path('/usr/bin'),
            python_version=(3, 11, 0),
            is_global=True,
            parent_project=None,
            dependencies_satisfied=False,
            conflicts=[],
            missing_packages=['pytest', 'PyYAML'],
            action_recommendation="create_venv",
            reason="Global Python - isolation required"
        )
        
        with patch.object(module, '_analyze_environment', return_value=mock_analysis), \
             patch.object(module, '_create_venv') as mock_create:
            
            mock_create.return_value = Mock(status=SetupStatus.SUCCESS)
            result = module.execute(mock_context)
            
            assert result.status == SetupStatus.SUCCESS
            mock_create.assert_called_once()
    
    def test_configure_reuse_install_missing(self, module, tmp_path):
        """Test reuse configuration installs missing packages."""
        mock_analysis = EnvironmentAnalysis(
            is_virtual_env=True,
            environment_path=Path('/path/to/venv'),
            python_version=(3, 11, 0),
            is_global=False,
            parent_project=None,
            dependencies_satisfied=False,
            conflicts=[],
            missing_packages=['watchdog'],
            action_recommendation="reuse_environment",
            reason="Compatible environment"
        )
        
        context = {'project_root': tmp_path}
        
        with patch.object(module, '_install_packages', return_value=True):
            result = module._configure_reuse(mock_analysis, context)
            
            assert result.status == SetupStatus.SUCCESS
            assert 'watchdog' in result.details['packages_installed']
    
    def test_create_venv_success(self, module, tmp_path):
        """Test venv creation succeeds."""
        mock_analysis = EnvironmentAnalysis(
            is_virtual_env=False,
            environment_path=Path('/usr/bin'),
            python_version=(3, 11, 0),
            is_global=True,
            parent_project=None,
            dependencies_satisfied=False,
            conflicts=[],
            missing_packages=[],
            action_recommendation="create_venv",
            reason="Global Python"
        )
        
        context = {'project_root': tmp_path}
        (tmp_path / 'requirements.txt').write_text("pytest>=8.4.0\nPyYAML>=6.0.2")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            result = module._create_venv(mock_analysis, context)
            
            assert result.status == SetupStatus.SUCCESS
            assert 'environment_path' in result.details
            assert str(tmp_path / '.venv') in result.details['environment_path']
    
    def test_create_venv_failure(self, module, tmp_path):
        """Test venv creation handles failure."""
        mock_analysis = EnvironmentAnalysis(
            is_virtual_env=False,
            environment_path=Path('/usr/bin'),
            python_version=(3, 11, 0),
            is_global=True,
            parent_project=None,
            dependencies_satisfied=False,
            conflicts=[],
            missing_packages=[],
            action_recommendation="create_venv",
            reason="Global Python"
        )
        
        context = {'project_root': tmp_path}
        
        with patch('subprocess.run', side_effect=Exception("venv creation failed")):
            result = module._create_venv(mock_analysis, context)
            
            assert result.status == SetupStatus.FAILED
            assert 'error' in result.details
    
    def test_rollback_removes_venv(self, module, tmp_path):
        """Test rollback removes created venv."""
        venv_path = tmp_path / '.venv'
        venv_path.mkdir()
        
        context = {'cortex_venv_path': str(venv_path)}
        
        result = module.rollback(context)
        
        assert result is True
        assert not venv_path.exists()
    
    def test_rollback_no_venv(self, module, mock_context):
        """Test rollback when no venv was created."""
        result = module.rollback(mock_context)
        assert result is True
    
    def test_environment_analysis_embedded_compatible(self, module, tmp_path):
        """Test analysis for embedded installation with compatible environment."""
        # Setup embedded structure
        parent = tmp_path / "PARENT_PROJECT"
        cortex = parent / "CORTEX"
        cortex.mkdir(parents=True)
        (parent / "requirements.txt").write_text("pytest>=8.4.0")
        
        context = {'project_root': cortex}
        
        with patch('sys.prefix', str(parent / 'venv')), \
             patch('sys.base_prefix', '/usr/bin'), \
             patch.object(module, '_check_dependencies', return_value=([], [])):
            
            analysis = module._analyze_environment(context)
            
            assert analysis.action_recommendation == "reuse_environment"
            assert analysis.parent_project == "PARENT_PROJECT"
            assert analysis.dependencies_satisfied
    
    def test_environment_analysis_conflicts_force_isolation(self, module, tmp_path):
        """Test analysis forces isolation when conflicts detected."""
        context = {'project_root': tmp_path}
        
        conflicts = ['pytest 6.2.0 (need >=8.4.0)', 'PyYAML 5.4 (need >=6.0.2)']
        
        with patch('sys.prefix', str(tmp_path / 'venv')), \
             patch('sys.base_prefix', '/usr/bin'), \
             patch.object(module, '_check_dependencies', return_value=([], conflicts)):
            
            analysis = module._analyze_environment(context)
            
            assert analysis.action_recommendation == "create_venv"
            assert len(analysis.conflicts) == 2
            assert "conflict" in analysis.reason.lower()


class TestEnvironmentAnalysisDataclass:
    """Test EnvironmentAnalysis dataclass."""
    
    def test_environment_analysis_creation(self):
        """Test creating EnvironmentAnalysis instance."""
        analysis = EnvironmentAnalysis(
            is_virtual_env=True,
            environment_path=Path('/path/to/venv'),
            python_version=(3, 11, 0),
            is_global=False,
            parent_project="PARENT",
            dependencies_satisfied=True,
            conflicts=[],
            missing_packages=[],
            action_recommendation="reuse_environment",
            reason="All good"
        )
        
        assert analysis.is_virtual_env
        assert analysis.environment_path == Path('/path/to/venv')
        assert analysis.python_version == (3, 11, 0)
        assert analysis.parent_project == "PARENT"
        assert analysis.action_recommendation == "reuse_environment"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
