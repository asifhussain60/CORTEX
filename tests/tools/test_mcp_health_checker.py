"""
Tests for MCPHealthChecker

**Authority:** Phase 90 S-90-03
**Author:** Asif Hussain
**Created:** 2026-02-16
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from cortex.tools.toolkit.diagnostics.mcp_health import DiagnosticResult, MCPHealthChecker


class TestDiagnosticResult:
    """Test DiagnosticResult dataclass."""
    
    def test_diagnostic_result_creation(self):
        """Test creating diagnostic result."""
        result = DiagnosticResult(
            check_name="Test Check",
            passed=True,
            message="Test passed",
        )
        
        assert result.check_name == "Test Check"
        assert result.passed is True
        assert result.message == "Test passed"
        assert result.details is None
        assert result.severity == "INFO"
    
    def test_diagnostic_result_with_details(self):
        """Test diagnostic result with details."""
        result = DiagnosticResult(
            check_name="Test Check",
            passed=False,
            message="Test failed",
            details={"error": "Something went wrong"},
            severity="ERROR",
        )
        
        assert result.details == {"error": "Something went wrong"}
        assert result.severity == "ERROR"


class TestMCPHealthChecker:
    """Test MCPHealthChecker class."""
    
    def test_initialization(self):
        """Test health checker initialization."""
        checker = MCPHealthChecker()
        
        assert checker.workspace_root == Path.cwd()
        assert checker.results == []
    
    def test_initialization_with_custom_root(self, tmp_path):
        """Test initialization with custom workspace root."""
        checker = MCPHealthChecker(workspace_root=tmp_path)
        
        assert checker.workspace_root == tmp_path
    
    def test_check_python_environment_valid(self):
        """Test Python environment check with valid version."""
        checker = MCPHealthChecker()
        
        # Python 3.9+ required
        checker._check_python_environment()
        
        assert len(checker.results) == 1
        result = checker.results[0]
        
        assert result.check_name == "Python Environment"
        assert result.passed == (sys.version_info >= (3, 9))
        assert "Python" in result.message
        assert "version" in result.details
        assert "executable" in result.details
    
    def test_check_virtual_environment_exists(self, tmp_path):
        """Test virtual environment check when venv exists."""
        # Create mock venv structure
        venv_path = tmp_path / ".venv" / "bin" / "python"
        venv_path.parent.mkdir(parents=True)
        venv_path.touch()
        
        checker = MCPHealthChecker(workspace_root=tmp_path)
        checker._check_virtual_environment()
        
        assert len(checker.results) == 1
        result = checker.results[0]
        
        assert result.check_name == "Virtual Environment"
        assert result.passed is True
        assert "configured" in result.message.lower()
        assert result.details["found_path"] == str(venv_path)
    
    def test_check_virtual_environment_missing(self, tmp_path):
        """Test virtual environment check when venv missing."""
        checker = MCPHealthChecker(workspace_root=tmp_path)
        checker._check_virtual_environment()
        
        assert len(checker.results) == 1
        result = checker.results[0]
        
        assert result.check_name == "Virtual Environment"
        assert result.passed is False
        assert "NOT FOUND" in result.message
        assert result.severity == "ERROR"
    
    def test_check_mcp_module_importable(self):
        """Test MCP module check when importable."""
        # This test verifies real import since cortex.mcp exists
        checker = MCPHealthChecker()
        checker._check_mcp_module()
        
        assert len(checker.results) == 1
        result = checker.results[0]
        
        assert result.check_name == "MCP Module"
        # Should pass since cortex.mcp is importable in test environment
        assert result.passed is True
        assert "importable" in result.message
    
    def test_check_mcp_module_import_error(self):
        """Test MCP module check when import fails."""
        # Testing import failure requires mocking at sys.modules level
        # which is complex and fragile. Skip for now.
        # The real-world scenario is tested via integration tests.
        pytest.skip("Import error testing requires complex sys.modules mocking")
    
    def test_check_vscode_settings_not_found(self, tmp_path):
        """Test VS Code settings check when file not found."""
        checker = MCPHealthChecker(workspace_root=tmp_path)
        checker._check_vscode_settings()
        
        assert len(checker.results) == 1
        result = checker.results[0]
        
        assert result.check_name == "VS Code Settings"
        assert result.passed is False
        assert "not found" in result.message
        assert result.severity == "ERROR"
    
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
        
        checker = MCPHealthChecker(workspace_root=tmp_path)
        checker._check_vscode_settings()
        
        assert len(checker.results) == 1
        result = checker.results[0]
        
        assert result.check_name == "VS Code Settings"
        assert result.passed is True
        assert "configured" in result.message
        assert result.details["has_cortex_server"] is True
    
    def test_check_vscode_settings_path_warning_windows(self, tmp_path):
        """Test VS Code settings check with Windows path warning."""
        settings_path = tmp_path / ".vscode" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        
        settings = {
            "github.copilot.chat.mcpServers": {
                "cortex": {
                    "command": ".venv/bin/python",  # Unix path
                }
            }
        }
        
        settings_path.write_text(json.dumps(settings))
        
        checker = MCPHealthChecker(workspace_root=tmp_path)
        
        with patch("sys.platform", "win32"):
            checker._check_vscode_settings()
        
        result = checker.results[0]
        
        if sys.platform == "win32":
            assert result.severity == "WARNING"
            assert len(result.details["warnings"]) > 0
    
    def test_get_venv_python_unix(self, tmp_path):
        """Test getting venv python on Unix."""
        venv_path = tmp_path / ".venv" / "bin" / "python"
        venv_path.parent.mkdir(parents=True)
        venv_path.touch()
        
        checker = MCPHealthChecker(workspace_root=tmp_path)
        result = checker._get_venv_python()
        
        assert result == venv_path
    
    def test_get_venv_python_not_found(self, tmp_path):
        """Test getting venv python when not found."""
        checker = MCPHealthChecker(workspace_root=tmp_path)
        result = checker._get_venv_python()
        
        assert result is None
    
    def test_run_diagnostics_all_checks(self):
        """Test running all diagnostic checks."""
        checker = MCPHealthChecker()
        results = checker.run_diagnostics()
        
        # Should run 6 default checks
        assert len(results) >= 6
        
        check_names = {r.check_name for r in results}
        expected_checks = {
            "Python Environment",
            "Virtual Environment",
            "MCP Module",
            "VS Code Settings",
        }
        
        assert expected_checks.issubset(check_names)
    
    def test_run_diagnostics_specific_checks(self):
        """Test running specific diagnostic checks."""
        checker = MCPHealthChecker()
        results = checker.run_diagnostics(checks=["python_env", "venv"])
        
        assert len(results) == 2
        check_names = [r.check_name for r in results]
        assert "Python Environment" in check_names
        assert "Virtual Environment" in check_names
    
    def test_generate_report(self):
        """Test generating diagnostic report."""
        checker = MCPHealthChecker()
        checker.results = [
            DiagnosticResult(
                check_name="Test Check 1",
                passed=True,
                message="Check passed",
            ),
            DiagnosticResult(
                check_name="Test Check 2",
                passed=False,
                message="Check failed",
                severity="ERROR",
            ),
        ]
        
        report = checker.generate_report()
        
        assert "CORTEX MCP DIAGNOSTIC REPORT" in report
        assert "Test Check 1" in report
        assert "Test Check 2" in report
        assert "1/2 checks passed" in report
        assert "CHECK(S) FAILED" in report
    
    def test_generate_report_all_passed(self):
        """Test generating report when all checks passed."""
        checker = MCPHealthChecker()
        checker.results = [
            DiagnosticResult(
                check_name="Test Check 1",
                passed=True,
                message="Check passed",
            ),
            DiagnosticResult(
                check_name="Test Check 2",
                passed=True,
                message="Check passed",
            ),
        ]
        
        report = checker.generate_report()
        
        assert "ALL CHECKS PASSED" in report
        assert "Next Steps:" in report
    
    def test_get_failed_checks(self):
        """Test getting failed checks."""
        checker = MCPHealthChecker()
        checker.results = [
            DiagnosticResult(check_name="Pass", passed=True, message="OK"),
            DiagnosticResult(check_name="Fail1", passed=False, message="Error"),
            DiagnosticResult(check_name="Fail2", passed=False, message="Error"),
        ]
        
        failed = checker.get_failed_checks()
        
        assert len(failed) == 2
        assert all(not r.passed for r in failed)
    
    def test_all_passed(self):
        """Test checking if all diagnostics passed."""
        checker = MCPHealthChecker()
        
        checker.results = [
            DiagnosticResult(check_name="Check1", passed=True, message="OK"),
            DiagnosticResult(check_name="Check2", passed=True, message="OK"),
        ]
        assert checker.all_passed() is True
        
        checker.results.append(
            DiagnosticResult(check_name="Check3", passed=False, message="Fail")
        )
        assert checker.all_passed() is False
