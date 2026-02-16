"""
Unit tests for toolkit diagnostics module.

Tests MCP diagnostics consolidation functionality.

AC_START: AC-P90-S2-T1
"""

import pytest
from pathlib import Path
from cortex.toolkit.diagnostics import (
    MCPDiagnostics,
    DiagnosticResult,
    DiagnosticLevel,
)


class TestMCPDiagnostics:
    """Test MCP diagnostics functionality."""

    def test_check_mcp_server_running(self) -> None:
        """Test MCP server running check."""
        diagnostics = MCPDiagnostics()
        result = diagnostics.check_server_running()
        
        assert isinstance(result, DiagnosticResult)
        assert result.check_name == "mcp_server_running"
        assert result.level in [DiagnosticLevel.OK, DiagnosticLevel.WARNING, DiagnosticLevel.ERROR]

    def test_check_mcp_tools_available(self) -> None:
        """Test MCP tools availability check."""
        diagnostics = MCPDiagnostics()
        result = diagnostics.check_tools_available()
        
        assert isinstance(result, DiagnosticResult)
        assert result.check_name == "mcp_tools_available"
        # Either passed OR has details explaining failure
        assert result.passed or result.recommendation

    def test_check_settings_json_configured(self) -> None:
        """Test .vscode/settings.json configuration check."""
        diagnostics = MCPDiagnostics()
        result = diagnostics.check_settings_configured()
        
        assert isinstance(result, DiagnosticResult)
        assert result.check_name == "settings_configured"

    def test_run_full_diagnostics(self) -> None:
        """Test full diagnostic suite."""
        diagnostics = MCPDiagnostics()
        results = diagnostics.run_full_diagnostics()
        
        assert len(results) >= 3
        assert all(isinstance(r, DiagnosticResult) for r in results)
        
        # Should include key checks
        check_names = [r.check_name for r in results]
        assert "mcp_server_running" in check_names
        assert "mcp_tools_available" in check_names
        assert "settings_configured" in check_names

    def test_diagnostic_result_serialization(self) -> None:
        """Test diagnostic result can be serialized."""
        result = DiagnosticResult(
            check_name="test_check",
            passed=True,
            level=DiagnosticLevel.OK,
            message="Test passed",
            details={"info": "test details"},
        )
        
        serialized = result.to_dict()
        
        assert serialized["check_name"] == "test_check"
        assert serialized["passed"] is True
        assert serialized["level"] == "ok"
        assert serialized["message"] == "Test passed"
        assert serialized["details"]["info"] == "test details"


class TestDiagnosticReporting:
    """Test diagnostic report generation."""

    def test_generate_summary_report(self) -> None:
        """Test summary report generation."""
        diagnostics = MCPDiagnostics()
        results = diagnostics.run_full_diagnostics()
        summary = diagnostics.generate_summary(results)
        
        assert "total_checks" in summary
        assert "passed_checks" in summary
        assert "failed_checks" in summary
        assert "warnings" in summary
        assert summary["total_checks"] == len(results)

    def test_report_includes_recommendations(self) -> None:
        """Test report includes fix recommendations."""
        diagnostics = MCPDiagnostics()
        results = diagnostics.run_full_diagnostics()
        report = diagnostics.generate_report(results)
        
        assert "recommendations" in report
        
        # If any checks failed, should have recommendations
        failed = [r for r in results if not r.passed]
        if failed:
            assert len(report["recommendations"]) > 0


# AC_COMPLETE: AC-P90-S2-T1
