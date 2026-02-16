"""
Unit tests for toolkit setup module.

Tests setup verification and environment configuration.

AC_START: AC-P90-S3-T1
"""

import pytest
from pathlib import Path
from cortex.toolkit.setup import (
    SetupVerifier,
    SetupResult,
    SetupCheck,
)


class TestSetupVerifier:
    """Test setup verification functionality."""

    def test_check_virtual_environment(self) -> None:
        """Test virtual environment activation check."""
        verifier = SetupVerifier()
        result = verifier.check_virtual_environment()
        
        assert isinstance(result, SetupResult)
        assert result.check == SetupCheck.VIRTUAL_ENV
        assert isinstance(result.passed, bool)

    def test_check_dependencies_installed(self) -> None:
        """Test Python dependencies check."""
        verifier = SetupVerifier()
        result = verifier.check_dependencies()
        
        assert isinstance(result, SetupResult)
        assert result.check == SetupCheck.DEPENDENCIES
        assert "yaml" in result.message.lower() or result.passed

    def test_check_mcp_configured(self) -> None:
        """Test MCP server configuration check."""
        verifier = SetupVerifier()
        result = verifier.check_mcp_configuration()
        
        assert isinstance(result, SetupResult)
        assert result.check == SetupCheck.MCP_CONFIG

    def test_check_vscode_settings(self) -> None:
        """Test VS Code settings.json check."""
        verifier = SetupVerifier()
        result = verifier.check_vscode_settings()
        
        assert isinstance(result, SetupResult)
        assert result.check == SetupCheck.VSCODE_SETTINGS

    def test_run_full_verification(self) -> None:
        """Test full setup verification suite."""
        verifier = SetupVerifier()
        results = verifier.run_full_verification()
        
        assert len(results) >= 4
        assert all(isinstance(r, SetupResult) for r in results)
        
        # Should include key checks
        checks = [r.check for r in results]
        assert SetupCheck.VIRTUAL_ENV in checks
        assert SetupCheck.DEPENDENCIES in checks
        assert SetupCheck.MCP_CONFIG in checks


class TestSetupAutoFix:
    """Test automatic setup fixes."""

    def test_can_autofix_dependencies(self) -> None:
        """Test dependency auto-fix capability detection."""
        verifier = SetupVerifier()
        
        # Check if auto-fix is available
        result = verifier.check_dependencies()
        
        if not result.passed:
            assert result.autofix_available is not None

    def test_generate_fix_commands(self) -> None:
        """Test fix command generation."""
        verifier = SetupVerifier()
        results = verifier.run_full_verification()
        
        failed = [r for r in results if not r.passed]
        
        for result in failed:
            if result.autofix_available:
                commands = verifier.generate_fix_commands(result)
                assert len(commands) > 0
                assert all(isinstance(cmd, str) for cmd in commands)


class TestSetupReporting:
    """Test setup report generation."""

    def test_generate_setup_report(self) -> None:
        """Test setup report generation."""
        verifier = SetupVerifier()
        results = verifier.run_full_verification()
        report = verifier.generate_report(results)
        
        assert "summary" in report
        assert "checks" in report
        assert "recommendations" in report

    def test_report_includes_environment_info(self) -> None:
        """Test report includes environment details."""
        verifier = SetupVerifier()
        results = verifier.run_full_verification()
        report = verifier.generate_report(results)
        
        assert "environment" in report
        env = report["environment"]
        assert "python_version" in env
        assert "platform" in env


# AC_COMPLETE: AC-P90-S3-T1
