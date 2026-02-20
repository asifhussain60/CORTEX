"""
Tests for SetupVerifier

**Authority:** Phase 90 S-90-04
**Author:** Asif Hussain
**Created:** 2026-02-16
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.tools.toolkit.setup.verifier import SetupVerifier, VerificationResult


class TestVerificationResult:
    """Test VerificationResult dataclass."""
    
    def test_verification_result_creation(self):
        """Test creating verification result."""
        result = VerificationResult(
            check_name="Test Check",
            passed=True,
            message="Check passed",
        )
        
        assert result.check_name == "Test Check"
        assert result.passed is True
        assert result.message == "Check passed"
        assert result.details is None
        assert result.severity == "INFO"


class TestSetupVerifier:
    """Test SetupVerifier class."""
    
    def test_initialization(self):
        """Test setup verifier initialization."""
        verifier = SetupVerifier()
        
        assert verifier.workspace_root == Path.cwd()
        assert verifier.platform in ["Windows", "Darwin", "Linux"]
        assert verifier.results == []
    
    def test_initialization_with_custom_root(self, tmp_path):
        """Test initialization with custom workspace root."""
        verifier = SetupVerifier(workspace_root=tmp_path)
        
        assert verifier.workspace_root == tmp_path
    
    def test_check_python_version(self):
        """Test Python version check."""
        verifier = SetupVerifier()
        verifier._check_python_version()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "Python Version"
        assert result.passed == (sys.version_info[:2] >= (3, 9))
        assert "Python" in result.message
    
    def test_check_virtual_environment_exists(self, tmp_path):
        """Test virtual environment check when venv exists."""
        # Create mock venv structure
        venv_path = tmp_path / ".venv" / "bin" / "python"
        venv_path.parent.mkdir(parents=True)
        venv_path.touch()
        
        verifier = SetupVerifier(workspace_root=tmp_path)
        verifier._check_virtual_environment()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "Virtual Environment"
        assert result.passed is True
        assert "configured" in result.message.lower()
    
    def test_check_virtual_environment_missing(self, tmp_path):
        """Test virtual environment check when venv missing."""
        verifier = SetupVerifier(workspace_root=tmp_path)
        verifier._check_virtual_environment()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "Virtual Environment"
        assert result.passed is False
        assert "NOT FOUND" in result.message
    
    def test_check_dependencies(self):
        """Test dependencies check."""
        verifier = SetupVerifier()
        verifier._check_dependencies()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "Dependencies"
        # Should have at least pytest and pyyaml installed in test environment
        assert "installed" in result.details
        assert "missing" in result.details
    
    def test_check_vscode_settings_not_found(self, tmp_path):
        """Test VS Code settings check when file not found."""
        verifier = SetupVerifier(workspace_root=tmp_path)
        verifier._check_vscode_settings()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "VS Code Settings"
        assert result.passed is False
        assert "not found" in result.message
    
    def test_check_vscode_settings_valid_config(self, tmp_path):
        """Test VS Code settings check with valid MCP config."""
        settings_path = tmp_path / ".vscode" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        
        settings = {
            "github.copilot.chat.mcpServers": {
                "cortex": {
                    "command": ".venv/bin/python",
                    "args": ["-m", "cortex.mcp"],
                }
            }
        }
        
        settings_path.write_text(json.dumps(settings))
        
        verifier = SetupVerifier(workspace_root=tmp_path)
        verifier._check_vscode_settings()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "VS Code Settings"
        assert result.passed is True
        assert "configured" in result.message
    
    def test_check_mcp_configuration(self):
        """Test MCP configuration check."""
        verifier = SetupVerifier()
        verifier._check_mcp_configuration()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "MCP Configuration"
        # cortex.mcp should be importable in test environment
        assert result.passed is True
    
    def test_check_git_configuration_not_git_repo(self, tmp_path):
        """Test git configuration check when not a git repo."""
        verifier = SetupVerifier(workspace_root=tmp_path)
        verifier._check_git_configuration()
        
        assert len(verifier.results) == 1
        result = verifier.results[0]
        
        assert result.check_name == "Git Configuration"
        assert result.passed is False
        assert "Not a git repository" in result.message
    
    def test_get_venv_paths_unix(self, tmp_path):
        """Test getting venv paths on Unix."""
        verifier = SetupVerifier(workspace_root=tmp_path)
        
        with patch.object(verifier, "platform", "Darwin"):
            paths = verifier._get_venv_paths()
        
        assert len(paths) == 1
        assert "bin/python" in str(paths[0])
    
    def test_get_venv_paths_windows(self, tmp_path):
        """Test getting venv paths on Windows."""
        verifier = SetupVerifier(workspace_root=tmp_path)
        
        with patch.object(verifier, "platform", "Windows"):
            paths = verifier._get_venv_paths()
        
        assert len(paths) == 1
        assert "Scripts\\python.exe" in str(paths[0]) or "Scripts/python.exe" in str(paths[0])
    
    def test_verify_environment(self):
        """Test running full environment verification."""
        verifier = SetupVerifier()
        results = verifier.verify_environment()
        
        # Should run 6 checks
        assert len(results) >= 6
        
        check_names = {r.check_name for r in results}
        expected_checks = {
            "Python Version",
            "Virtual Environment",
            "Dependencies",
            "VS Code Settings",
            "MCP Configuration",
            "Git Configuration",
        }
        
        assert expected_checks.issubset(check_names)
    
    def test_generate_report(self):
        """Test generating verification report."""
        verifier = SetupVerifier()
        verifier.results = [
            VerificationResult(
                check_name="Test Check 1",
                passed=True,
                message="Check passed",
            ),
            VerificationResult(
                check_name="Test Check 2",
                passed=False,
                message="Check failed",
                severity="ERROR",
            ),
        ]
        
        report = verifier.generate_report()
        
        assert "CORTEX SETUP VERIFICATION REPORT" in report
        assert "Test Check 1" in report
        assert "Test Check 2" in report
        assert "1/2 checks passed" in report
        assert "CHECK(S) FAILED" in report
    
    def test_generate_report_all_passed(self):
        """Test generating report when all checks passed."""
        verifier = SetupVerifier()
        verifier.results = [
            VerificationResult(
                check_name="Test Check 1",
                passed=True,
                message="Check passed",
            ),
            VerificationResult(
                check_name="Test Check 2",
                passed=True,
                message="Check passed",
            ),
        ]
        
        report = verifier.generate_report()
        
        assert "ENVIRONMENT READY" in report
        assert "Next Steps:" in report
    
    def test_all_passed(self):
        """Test checking if all verifications passed."""
        verifier = SetupVerifier()
        
        verifier.results = [
            VerificationResult(check_name="Check1", passed=True, message="OK"),
            VerificationResult(check_name="Check2", passed=True, message="OK"),
        ]
        assert verifier.all_passed() is True
        
        verifier.results.append(
            VerificationResult(check_name="Check3", passed=False, message="Fail")
        )
        assert verifier.all_passed() is False
    
    def test_get_failed_checks(self):
        """Test getting failed checks."""
        verifier = SetupVerifier()
        verifier.results = [
            VerificationResult(check_name="Pass", passed=True, message="OK"),
            VerificationResult(check_name="Fail1", passed=False, message="Error"),
            VerificationResult(check_name="Fail2", passed=False, message="Error"),
        ]
        
        failed = verifier.get_failed_checks()
        
        assert len(failed) == 2
        assert all(not r.passed for r in failed)
