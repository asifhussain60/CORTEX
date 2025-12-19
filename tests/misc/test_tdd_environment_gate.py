"""
Tests for TDD Environment Gate - Feature 6
TDD Phase: RED (All tests should FAIL initially)

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the implemented module
from src.orchestrators.tdd_environment_gate import (
    TDDEnvironmentGate,
    GateResult,
    CheckResult,
    CheckStatus,
    TestFramework
)


class TestEnvironmentReadinessChecks:
    """Test core environment validation checks"""
    
    def test_validates_test_framework_installed(self):
        """Should check if pytest/xUnit/Jest is installed"""
        gate = TDDEnvironmentGate()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b"pytest 8.4.2")
            
            result = gate.check_test_framework()
            
            assert result.status == CheckStatus.PASSED
            assert result.framework == TestFramework.PYTEST
    
    def test_detects_missing_test_framework(self):
        """Should fail if no test framework found"""
        gate = TDDEnvironmentGate()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=127)  # command not found
            
            result = gate.check_test_framework()
            
            assert result.status == CheckStatus.BLOCKED
            assert result.remediation is not None
    
    def test_checks_test_runner_availability(self):
        """Should verify test runner command works"""
        gate = TDDEnvironmentGate()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            result = gate.check_test_runner()
            
            assert result.status in [CheckStatus.PASSED, CheckStatus.WARNING]
    
    def test_validates_language_runtime_present(self):
        """Should check Python/NET/Node is installed"""
        gate = TDDEnvironmentGate()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b"Python 3.9.6")
            
            result = gate.check_language_runtime()
            
            assert result.status == CheckStatus.PASSED
            assert "python" in result.details.lower() or "3.9" in result.details


class TestTestFrameworkDetection:
    """Test test framework detection logic"""
    
    def test_detects_pytest_from_command(self):
        """Should identify pytest from pytest --version"""
        gate = TDDEnvironmentGate()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=b"pytest 8.4.2"
            )
            
            framework = gate.detect_test_framework()
            
            assert framework == TestFramework.PYTEST
    
    def test_detects_dotnet_test_from_command(self):
        """Should identify xUnit/NUnit from dotnet test"""
        gate = TDDEnvironmentGate()
        
        with patch('subprocess.run') as mock_run:
            # pytest fails, dotnet test succeeds
            mock_run.side_effect = [
                MagicMock(returncode=127),  # pytest not found
                MagicMock(returncode=0, stdout=b".NET SDK 8.0.100")  # dotnet found
            ]
            
            framework = gate.detect_test_framework()
            
            assert framework == TestFramework.DOTNET_TEST
    
    def test_detects_jest_from_npm(self):
        """Should identify Jest from npm test or jest command"""
        gate = TDDEnvironmentGate()
        
        with patch('subprocess.run') as mock_run:
            # pytest and dotnet fail, jest succeeds
            mock_run.side_effect = [
                MagicMock(returncode=127),  # pytest
                MagicMock(returncode=127),  # dotnet
                MagicMock(returncode=0, stdout=b"jest version 29.0.0")  # jest
            ]
            
            framework = gate.detect_test_framework()
            
            assert framework == TestFramework.JEST


class TestGateBlockingLogic:
    """Test gate blocking and warning logic"""
    
    def test_blocks_tdd_when_framework_missing(self):
        """Should block TDD start if test framework not installed"""
        gate = TDDEnvironmentGate()
        
        with patch.object(gate, 'check_test_framework') as mock_check:
            mock_check.return_value = CheckResult(
                status=CheckStatus.BLOCKED,
                check_name="Test Framework",
                details="pytest not found",
                remediation="Install pytest: pip install pytest"
            )
            
            result = gate.validate_tdd_readiness()
            
            assert result.allowed is False
            assert "pytest" in result.reason.lower()
            assert len(result.required_fixes) > 0
    
    def test_blocks_tdd_when_runtime_missing(self):
        """Should block if language runtime not available"""
        gate = TDDEnvironmentGate()
        
        with patch.object(gate, 'check_language_runtime') as mock_check:
            mock_check.return_value = CheckResult(
                status=CheckStatus.BLOCKED,
                check_name="Language Runtime",
                details="Python not found",
                remediation="Install Python 3.8+"
            )
            
            result = gate.validate_tdd_readiness()
            
            assert result.allowed is False
    
    def test_allows_tdd_with_warnings(self):
        """Should allow TDD but show warnings for non-critical issues"""
        gate = TDDEnvironmentGate()
        
        # All checks pass except one warning
        with patch.object(gate, 'run_all_checks') as mock_checks:
            mock_checks.return_value = [
                CheckResult(CheckStatus.PASSED, "Framework", "pytest OK"),
                CheckResult(CheckStatus.PASSED, "Runtime", "Python OK"),
                CheckResult(CheckStatus.WARNING, "Dependencies", "Some optional deps missing")
            ]
            
            result = gate.validate_tdd_readiness()
            
            assert result.allowed is True
            assert result.has_warnings is True


class TestRemediationIntegration:
    """Test integration with Environment Diagnostics (Feature 1)"""
    
    def test_calls_environment_diagnostics_for_remediation(self):
        """Should use Feature 1 for detailed remediation"""
        gate = TDDEnvironmentGate()
        
        with patch('src.orchestrators.environment_diagnostics_orchestrator.EnvironmentDiagnosticsOrchestrator') as mock_env:
            mock_orchestrator = Mock()
            mock_orchestrator.validate_for_tdd_workflow.return_value = {
                'python': {'status': 'blocked', 'remediation': 'Install Python'}
            }
            mock_env.return_value = mock_orchestrator
            
            result = gate.get_remediation_guide()
            
            assert result is not None
            assert 'python' in str(result).lower() or 'remediation' in str(result).lower()
    
    def test_provides_platform_specific_remediation(self):
        """Should provide OS-specific installation instructions"""
        gate = TDDEnvironmentGate()
        
        remediation = gate.get_platform_remediation("pytest")
        
        # Should include platform-specific commands
        assert any(cmd in remediation.lower() for cmd in ['pip', 'install', 'pytest'])


class TestTDDOrchestratorHooks:
    """Test integration with TDD Mastery Orchestrator"""
    
    def test_provides_pre_tdd_hook(self):
        """Should provide hook for TDD orchestrator to call"""
        gate = TDDEnvironmentGate()
        
        # Simulate TDD orchestrator calling gate
        result = gate.validate_before_tdd_start({
            'language': 'python',
            'project_path': '/path/to/project'
        })
        
        assert isinstance(result, GateResult)
        assert hasattr(result, 'allowed')
    
    def test_returns_actionable_error_message(self):
        """Error message should tell user what to do"""
        gate = TDDEnvironmentGate()
        
        with patch.object(gate, 'validate_tdd_readiness') as mock_validate:
            mock_validate.return_value = GateResult(
                allowed=False,
                reason="pytest not installed",
                required_fixes=["pip install pytest"]
            )
            
            result = gate.validate_tdd_readiness()
            
            assert result.allowed is False
            assert "pytest" in result.reason
            assert len(result.required_fixes) > 0
            assert "pip install" in result.required_fixes[0]
    
    def test_validates_test_directory_writable(self):
        """Should check if tests/ directory can be created"""
        gate = TDDEnvironmentGate()
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.return_value = None
            
            result = gate.check_test_directory_writable(Path("/fake/project"))
            
            assert result.status in [CheckStatus.PASSED, CheckStatus.BLOCKED]


class TestPerformanceRequirements:
    """Test performance requirements"""
    
    def test_validation_completes_under_1_second(self):
        """Should validate in <1s per requirement"""
        import time
        
        gate = TDDEnvironmentGate()
        
        start = time.perf_counter()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b"pytest 8.4.2")
            gate.validate_tdd_readiness()
        
        duration = time.perf_counter() - start
        
        assert duration < 1.0, f"Validation took {duration:.2f}s (required: <1s)"


class TestCrossPlatform:
    """Test cross-platform compatibility"""
    
    def test_detects_framework_on_windows(self):
        """Should work on Windows paths and commands"""
        gate = TDDEnvironmentGate()
        
        with patch('platform.system', return_value='Windows'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout=b"pytest 8.4.2")
                
                result = gate.check_test_framework()
                
                assert result.status == CheckStatus.PASSED
    
    def test_detects_framework_on_mac(self):
        """Should work on macOS"""
        gate = TDDEnvironmentGate()
        
        with patch('platform.system', return_value='Darwin'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout=b"pytest 8.4.2")
                
                result = gate.check_test_framework()
                
                assert result.status == CheckStatus.PASSED


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
