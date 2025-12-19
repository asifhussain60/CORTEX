"""
Tests for Environment Diagnostics Orchestrator

Purpose: Validate environment readiness before technical work
Evidence: chat04 - 30min wasted on .NET SDK troubleshooting

Test Strategy:
- RED phase: All tests fail initially
- GREEN phase: Implement minimal code to pass
- REFACTOR phase: Optimize and clean up

Coverage Target: 95%
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess

# Import CheckStatus for all tests
from src.orchestrators.environment_diagnostics_orchestrator import CheckStatus


# Test fixtures
@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess call"""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = "8.0.100"
    mock.stderr = ""
    return mock


@pytest.fixture
def mock_subprocess_failure():
    """Mock failed subprocess call"""
    mock = MagicMock()
    mock.returncode = 1
    mock.stdout = ""
    mock.stderr = "command not found"
    return mock


# =============================================================================
# Test Suite 1: .NET SDK Detection (3 tests)
# =============================================================================

def test_environment_diagnostics_detects_missing_dotnet_sdk():
    """
    RED PHASE TEST
    Should detect when .NET SDK not installed
    Evidence: chat04 lines 50-150 - user couldn't run dotnet tests
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator,
        CheckStatus
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError("dotnet not found")
        
        result = orchestrator.validate_dotnet_sdk()
        
        assert result.status == CheckStatus.BLOCKED, "Should be blocked when SDK missing"
        assert ".NET SDK not found" in result.message
        assert result.remediation is not None


def test_environment_diagnostics_validates_dotnet_version():
    """
    RED PHASE TEST
    Should validate .NET SDK version compatibility
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator,
        CheckStatus
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="6.0.100",  # Old version
            stderr=""
        )
        
        result = orchestrator.validate_dotnet_sdk(min_version="8.0")
        
        assert result.status == CheckStatus.WARNING, "Should warn on incompatible version"
        assert "6.0.100" in result.detected_version
        assert "recommend" in result.message.lower() or "upgrade" in result.remediation.lower()


def test_environment_diagnostics_provides_dotnet_remediation():
    """
    RED PHASE TEST
    Should provide installation guide when SDK missing
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        
        result = orchestrator.validate_dotnet_sdk()
        
        assert "https://dotnet.microsoft.com" in result.remediation
        assert "PATH" in result.remediation
        assert "dotnet --version" in result.remediation


# =============================================================================
# Test Suite 2: Python Environment Detection (3 tests)
# =============================================================================

def test_environment_diagnostics_detects_python_installation():
    """
    RED PHASE TEST
    Should detect Python installation and version
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Python 3.11.5",
            stderr=""
        )
        
        with patch.dict('os.environ', {'VIRTUAL_ENV': '/some/venv'}, clear=False):
            result = orchestrator.validate_python()
        
        assert result.status == CheckStatus.PASS
        assert "3.11.5" in result.detected_version


def test_environment_diagnostics_detects_virtual_environment():
    """
    RED PHASE TEST
    Should detect if running in virtual environment
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch.dict('os.environ', {'VIRTUAL_ENV': '/path/to/venv'}):
        result = orchestrator.validate_python()
        
        assert result.venv_active is True
        assert "/path/to/venv" in result.venv_path


def test_environment_diagnostics_warns_no_virtual_environment():
    """
    RED PHASE TEST
    Should warn if no virtual environment active (best practice)
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch.dict('os.environ', {}, clear=True):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Python 3.9.6",
                stderr=""
            )
            result = orchestrator.validate_python()
        
        assert result.status == CheckStatus.WARNING
        assert "virtual environment" in result.message.lower()
        assert "venv" in result.remediation or "virtualenv" in result.remediation


# =============================================================================
# Test Suite 3: Node.js Detection (3 tests)
# =============================================================================

def test_environment_diagnostics_detects_nodejs():
    """
    RED PHASE TEST
    Should detect Node.js installation
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="v18.17.0",
            stderr=""
        )
        
        result = orchestrator.validate_nodejs()
        
        assert result.status == CheckStatus.PASS
        assert "18.17.0" in result.detected_version


def test_environment_diagnostics_validates_npm_availability():
    """
    RED PHASE TEST
    Should validate npm is available alongside Node.js
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        # Node installed but npm missing
        def side_effect(cmd, *args, **kwargs):
            if 'node' in cmd:
                return MagicMock(returncode=0, stdout="v18.17.0", stderr="")
            elif 'npm' in cmd:
                raise FileNotFoundError("npm not found")
        
        mock_run.side_effect = side_effect
        
        result = orchestrator.validate_nodejs()
        
        assert result.npm_available is False
        assert result.status == CheckStatus.WARNING


def test_environment_diagnostics_skips_nodejs_if_not_required():
    """
    RED PHASE TEST
    Should allow skipping Node.js check if not required for project
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    result = orchestrator.validate_nodejs(required=False)
    
    assert result.status in [CheckStatus.PASS, CheckStatus.SKIPPED]
    assert "not required" in result.message.lower() or result.status == "skipped"


# =============================================================================
# Test Suite 4: Git Detection (3 tests)
# =============================================================================

def test_environment_diagnostics_detects_git_installation():
    """
    RED PHASE TEST
    Should detect Git installation and version
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="git version 2.42.0",
            stderr=""
        )
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True  # In git repo
            result = orchestrator.validate_git()
        
        assert result.status == CheckStatus.PASS
        assert "2.42.0" in result.detected_version


def test_environment_diagnostics_validates_git_repository():
    """
    RED PHASE TEST
    Should check if current directory is a git repository
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="git version 2.50.1 (Apple Git-155)",
            stderr=""
        )
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False  # No .git folder
            result = orchestrator.validate_git()
        
        assert result.is_git_repo is False
        assert result.status == CheckStatus.WARNING
        assert "git init" in result.remediation


def test_environment_diagnostics_checks_git_configuration():
    """
    RED PHASE TEST
    Should validate git user.name and user.email configured
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        # Git installed but not configured
        def side_effect(cmd, *args, **kwargs):
            if '--version' in cmd:
                return MagicMock(returncode=0, stdout="git version 2.42.0", stderr="")
            elif 'user.name' in cmd or 'user.email' in cmd:
                return MagicMock(returncode=1, stdout="", stderr="not set")
        
        mock_run.side_effect = side_effect
        
        result = orchestrator.validate_git()
        
        assert result.configured is False
        assert "git config" in result.remediation


# =============================================================================
# Test Suite 5: Write Permissions (3 tests)
# =============================================================================

def test_environment_diagnostics_validates_output_directory_writable():
    """
    RED PHASE TEST
    Should check write permissions to output directories
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('pathlib.Path.touch') as mock_touch:
        mock_touch.side_effect = PermissionError("Access denied")
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = orchestrator.validate_write_permissions(
                directories=["./output", "./logs"]
            )
        
        assert result.status == CheckStatus.BLOCKED
        assert "permission denied" in result.message.lower()


def test_environment_diagnostics_creates_missing_directories():
    """
    RED PHASE TEST
    Should offer to create missing output directories
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = False
        
        result = orchestrator.validate_write_permissions(
            directories=["./output"],
            create_if_missing=False
        )
        
        assert result.missing_directories == ["./output"]
        assert "create" in result.remediation.lower()


def test_environment_diagnostics_provides_permission_fix_commands():
    """
    RED PHASE TEST
    Should provide platform-specific permission fix commands
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('pathlib.Path.touch') as mock_touch:
        mock_touch.side_effect = PermissionError()
        
        result = orchestrator.validate_write_permissions(directories=["./output"])
        
        # Should provide chmod (Unix) or icacls (Windows) commands
        assert "chmod" in result.remediation or "icacls" in result.remediation


# =============================================================================
# Test Suite 6: Remediation Guide System (3 tests)
# =============================================================================

def test_environment_diagnostics_generates_comprehensive_remediation():
    """
    RED PHASE TEST
    Should generate step-by-step remediation guide for all failures
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        
        result = orchestrator.run_full_diagnostics()
        
        assert result.status == CheckStatus.BLOCKED
        assert len(result.failed_checks) > 0
        assert result.remediation_guide is not None
        assert "Step 1" in result.remediation_guide
        assert "download" in result.remediation_guide.lower()


def test_environment_diagnostics_adapts_remediation_to_platform():
    """
    RED PHASE TEST
    Should provide platform-specific remediation (Windows/Mac/Linux)
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    # Create new instance to get Windows platform
    with patch('platform.system', return_value="Windows"):
        orchestrator = EnvironmentDiagnosticsOrchestrator()
        result = orchestrator.generate_remediation(check_name="dotnet_sdk")
        
        # Windows-specific instructions
        assert ".exe" in result or "Control Panel" in result


def test_environment_diagnostics_includes_download_links():
    """
    RED PHASE TEST
    Should include official download links in remediation
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    result = orchestrator.generate_remediation(check_name="dotnet_sdk")
    
    assert "https://" in result
    assert "dotnet.microsoft.com" in result or "microsoft.com" in result


# =============================================================================
# Test Suite 7: Integration Tests (2 tests)
# =============================================================================

def test_environment_diagnostics_integrates_with_tdd_orchestrator():
    """
    RED PHASE INTEGRATION TEST
    Should integrate with TDD Mastery Orchestrator
    Must validate environment before TDD workflow starts
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    # Simulate TDD orchestrator calling diagnostics
    result = orchestrator.validate_for_tdd_workflow()
    
    # Should check test framework, runner, dependencies
    assert hasattr(result, 'test_framework_ready')
    assert hasattr(result, 'test_runner_available')
    assert hasattr(result, 'dependencies_installed')


def test_environment_diagnostics_execution_time_under_2_seconds():
    """
    RED PHASE PERFORMANCE TEST
    Should complete full diagnostics in <2 seconds
    """
    import time
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    
    start = time.time()
    result = orchestrator.run_full_diagnostics()
    duration = time.time() - start
    
    assert duration < 2.0, f"Diagnostics took {duration}s, should be <2s"


# =============================================================================
# Test Suite 8: Output Format (2 tests)
# =============================================================================

def test_environment_diagnostics_returns_structured_result():
    """
    RED PHASE TEST
    Should return structured result matching YAML schema
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    result = orchestrator.run_full_diagnostics()
    
    # Validate structure
    assert hasattr(result, 'status')
    assert result.status in [CheckStatus.PASS, CheckStatus.WARNING, CheckStatus.BLOCKED]
    assert hasattr(result, 'summary')
    assert hasattr(result, 'details')
    assert isinstance(result.details, list)
    assert hasattr(result, 'recommendations')
    assert hasattr(result, 'blocking_issues')


def test_environment_diagnostics_provides_actionable_summary():
    """
    RED PHASE TEST
    Should provide clear actionable summary
    """
    from src.orchestrators.environment_diagnostics_orchestrator import (
        EnvironmentDiagnosticsOrchestrator
    )
    
    orchestrator = EnvironmentDiagnosticsOrchestrator()
    result = orchestrator.run_full_diagnostics()
    
    assert result.summary is not None
    assert len(result.summary) > 0
    # Should mention number of checks passed/failed
    assert "check" in result.summary.lower() or "validation" in result.summary.lower()
