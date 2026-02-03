"""Tests for cortex_verify_environment MCP tool.

Tests the environment verification MCP tool that wraps verify_environment.py
and exposes environment checks via MCP protocol.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cortex.mcp.tools.environment import (
    cortex_verify_environment,
    EnvironmentStatus,
    EnvironmentCheckResult,
)


class TestEnvironmentMCPTool:
    """Test cortex_verify_environment MCP tool."""

    def test_tool_metadata(self) -> None:
        """Test that tool has proper metadata for MCP catalog."""
        assert cortex_verify_environment.__name__ == "cortex_verify_environment"
        assert hasattr(cortex_verify_environment, "__doc__")
        assert "environment" in cortex_verify_environment.__doc__.lower()

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_environment_ready_all_checks_pass(self, mock_verifier: Mock) -> None:
        """Test READY status when all checks pass."""
        # Mock verifier results
        mock_instance = Mock()
        mock_instance.results = []
        mock_instance.critical_failures = 0
        mock_instance.warnings = 0
        mock_instance.run_all_checks.return_value = 0
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=True)

        assert result.status == EnvironmentStatus.READY
        assert result.python_version is not None
        assert len(result.missing_packages) == 0
        assert len(result.recommendations) == 0

    @patch("cortex.mcp.tools.environment.sys.version_info", (3, 8, 0))
    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_missing_python_version_too_old(self, mock_verifier: Mock) -> None:
        """Test MISSING_PYTHON status when Python version < 3.9."""
        mock_instance = Mock()
        mock_instance.results = []
        mock_instance.critical_failures = 1
        mock_instance.warnings = 0
        mock_instance.run_all_checks.return_value = 1
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=True)

        assert result.status == EnvironmentStatus.MISSING_PYTHON
        assert "3.8" in result.python_version
        assert "upgrade" in result.recommendations[0].lower()

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_missing_dependencies_detected(self, mock_verifier: Mock) -> None:
        """Test MISSING_DEPS status when packages are missing."""
        from cortex.scripts.verify_environment import CheckResult

        mock_instance = Mock()
        mock_instance.results = [
            CheckResult(
                name="Core Dependencies",
                passed=False,
                message="Missing: pyyaml, pydantic",
                severity="error"
            )
        ]
        mock_instance.critical_failures = 1
        mock_instance.warnings = 0
        mock_instance.run_all_checks.return_value = 1
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=True)

        assert result.status == EnvironmentStatus.MISSING_DEPS
        assert "pyyaml" in result.missing_packages
        assert "pydantic" in result.missing_packages

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_partial_status_warnings_only(self, mock_verifier: Mock) -> None:
        """Test PARTIAL status when only warnings present."""
        mock_instance = Mock()
        mock_instance.results = []
        mock_instance.critical_failures = 0
        mock_instance.warnings = 2
        mock_instance.run_all_checks.return_value = 2
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=True)

        assert result.status == EnvironmentStatus.PARTIAL
        assert len(result.recommendations) > 0

    @patch("cortex.mcp.tools.environment.subprocess.run")
    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_auto_fix_installs_missing_packages(
        self, mock_verifier: Mock, mock_subprocess: Mock
    ) -> None:
        """Test auto_fix=True attempts pip install for missing packages."""
        from cortex.scripts.verify_environment import CheckResult

        mock_instance = Mock()
        mock_instance.results = [
            CheckResult(
                name="Core Dependencies",
                passed=False,
                message="Missing: pyyaml",
                severity="error"
            )
        ]
        mock_instance.critical_failures = 1
        mock_instance.warnings = 0
        mock_instance.run_all_checks.return_value = 1
        mock_verifier.return_value = mock_instance

        # Mock successful pip install
        mock_subprocess.return_value = Mock(returncode=0)

        result = cortex_verify_environment(auto_fix=True, verbose=True)

        # Verify pip install was called
        mock_subprocess.assert_called()
        assert "pip" in str(mock_subprocess.call_args)
        assert "install" in str(mock_subprocess.call_args)

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_verbose_false_omits_details(self, mock_verifier: Mock) -> None:
        """Test verbose=False returns minimal information."""
        mock_instance = Mock()
        mock_instance.results = []
        mock_instance.critical_failures = 0
        mock_instance.warnings = 0
        mock_instance.run_all_checks.return_value = 0
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=False)

        assert result.status == EnvironmentStatus.READY
        assert result.details is None or len(result.details) == 0

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_python_version_extracted_correctly(self, mock_verifier: Mock) -> None:
        """Test Python version string is extracted correctly."""
        mock_instance = Mock()
        mock_instance.results = []
        mock_instance.critical_failures = 0
        mock_instance.warnings = 0
        mock_instance.run_all_checks.return_value = 0
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=True)

        # Should match format "3.x.x"
        assert result.python_version.startswith("3.")
        parts = result.python_version.split(".")
        assert len(parts) >= 2

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_recommendations_for_quality_tools(self, mock_verifier: Mock) -> None:
        """Test recommendations include quality tools installation."""
        from cortex.scripts.verify_environment import CheckResult

        mock_instance = Mock()
        mock_instance.results = [
            CheckResult(
                name="Quality Tools",
                passed=False,
                message="Missing: black, mypy",
                severity="warning"
            )
        ]
        mock_instance.critical_failures = 0
        mock_instance.warnings = 1
        mock_instance.run_all_checks.return_value = 2
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=True)

        assert result.status == EnvironmentStatus.PARTIAL
        assert any("quality" in rec.lower() for rec in result.recommendations)

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_mcp_tool_decorator_present(self, mock_verifier: Mock) -> None:
        """Test that @mcp_tool decorator is applied."""
        # Check if function has MCP metadata
        assert hasattr(cortex_verify_environment, "__wrapped__") or \
               hasattr(cortex_verify_environment, "_mcp_metadata")

    def test_environment_status_enum_values(self) -> None:
        """Test EnvironmentStatus enum has expected values."""
        assert EnvironmentStatus.READY == "READY"
        assert EnvironmentStatus.MISSING_PYTHON == "MISSING_PYTHON"
        assert EnvironmentStatus.MISSING_DEPS == "MISSING_DEPS"
        assert EnvironmentStatus.PARTIAL == "PARTIAL"

    @patch("cortex.mcp.tools.environment.EnvironmentVerifier")
    def test_result_serializable_to_json(self, mock_verifier: Mock) -> None:
        """Test EnvironmentCheckResult can be serialized to JSON."""
        import json

        mock_instance = Mock()
        mock_instance.results = []
        mock_instance.critical_failures = 0
        mock_instance.warnings = 0
        mock_instance.run_all_checks.return_value = 0
        mock_verifier.return_value = mock_instance

        result = cortex_verify_environment(auto_fix=False, verbose=True)

        # Convert to dict and serialize
        result_dict = {
            "status": result.status,
            "python_version": result.python_version,
            "missing_packages": result.missing_packages,
            "recommendations": result.recommendations,
        }
        json_str = json.dumps(result_dict)
        assert json_str is not None
        assert "READY" in json_str
