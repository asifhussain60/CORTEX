"""
Tests for LENS Dashboard CLI Commands.

AC-ID: LENS-DASH-014
Author: Asif Hussain
Phase: 14
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from cortex.cli.lens_dashboard import (
    dashboard,
    generate,
    serve,
    list_cmd,
)


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_orchestrator():
    """Mock LENSVisualizationOrchestrator."""
    with patch("cortex.cli.lens_dashboard.LENSVisualizationOrchestrator") as mock:
        orchestrator = Mock()
        orchestrator.generate_dashboard.return_value = Path("/tmp/dashboard")
        mock.return_value = orchestrator
        yield orchestrator


class TestDashboardGenerateCommand:
    """Test 'cortex lens dashboard generate' command."""

    def test_generate_success(
        self, runner: CliRunner, mock_orchestrator, tmp_path: Path
    ) -> None:
        """Test successful dashboard generation."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        result = runner.invoke(generate, [str(repo_path)])
        
        assert result.exit_code == 0
        assert "generated successfully" in result.output.lower()

    def test_generate_with_output_path(
        self, runner: CliRunner, mock_orchestrator, tmp_path: Path
    ) -> None:
        """Test generation with custom output path."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        output_path = tmp_path / "custom-output"
        
        result = runner.invoke(
            generate,
            [str(repo_path), "--output", str(output_path)],
        )
        
        assert result.exit_code == 0

    def test_generate_invalid_path(self, runner: CliRunner) -> None:
        """Test error with invalid repository path."""
        result = runner.invoke(generate, ["/nonexistent/path"])
        
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_generate_current_directory(
        self, runner: CliRunner, mock_orchestrator, tmp_path: Path, monkeypatch
    ) -> None:
        """Test generation for current directory (no path argument)."""
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(generate)
        
        assert result.exit_code == 0


class TestDashboardServeCommand:
    """Test 'cortex lens dashboard serve' command."""

    def test_serve_default_port(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test serving dashboard on default port."""
        # Create a fake dashboard directory
        dashboard_dir = tmp_path / "test-dashboard"
        dashboard_dir.mkdir()
        (dashboard_dir / "index.html").write_text("<html></html>")
        
        with patch("cortex.visualization.spa.static_server.serve") as mock_serve:
            result = runner.invoke(
                serve,
                ["--path", str(dashboard_dir)],
            )
            
            # Should start server
            mock_serve.assert_called_once()
            call_args = mock_serve.call_args
            assert call_args[0][0] == dashboard_dir  # Dashboard path
            assert call_args[0][1] == 8080  # Default port
            assert call_args[0][2] is True  # CORS enabled

    def test_serve_custom_port(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test serving dashboard on custom port."""
        dashboard_dir = tmp_path / "test-dashboard"
        dashboard_dir.mkdir()
        (dashboard_dir / "index.html").write_text("<html></html>")
        
        with patch("cortex.visualization.spa.static_server.serve") as mock_serve:
            result = runner.invoke(
                serve,
                ["--port", "9000", "--path", str(dashboard_dir)],
            )
            
            mock_serve.assert_called_once()
            call_args = mock_serve.call_args
            assert call_args[0][1] == 9000  # Custom port

    def test_serve_no_cors(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test serving dashboard with CORS disabled."""
        dashboard_dir = tmp_path / "test-dashboard"
        dashboard_dir.mkdir()
        (dashboard_dir / "index.html").write_text("<html></html>")
        
        with patch("cortex.visualization.spa.static_server.serve") as mock_serve:
            result = runner.invoke(
                serve,
                ["--no-cors", "--path", str(dashboard_dir)],
            )
            
            mock_serve.assert_called_once()
            call_args = mock_serve.call_args
            assert call_args[0][2] is False  # CORS disabled

    def test_serve_no_dashboards(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test serve command with no dashboards."""
        with patch("cortex.cli.lens_dashboard.DASHBOARD_ROOT", tmp_path):
            result = runner.invoke(serve)
            
            assert result.exit_code == 0
            assert "No dashboards found" in result.output

    def test_serve_invalid_dashboard_no_index(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test serve command with invalid dashboard (no index.html)."""
        dashboard_dir = tmp_path / "invalid-dashboard"
        dashboard_dir.mkdir()
        
        result = runner.invoke(
            serve,
            ["--path", str(dashboard_dir)],
        )
        
        assert result.exit_code == 0
        assert "Invalid dashboard directory" in result.output
        assert "Missing index.html" in result.output


class TestDashboardListCommand:
    """Test 'cortex lens dashboard list' command."""

    def test_list_empty(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test listing dashboards when none exist."""
        with patch("cortex.cli.lens_dashboard.DASHBOARD_ROOT", tmp_path):
            result = runner.invoke(list_cmd)
        
        assert result.exit_code == 0
        assert "no dashboards" in result.output.lower() or "0" in result.output

    def test_list_dashboards(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test listing existing dashboards."""
        # Create mock dashboards
        (tmp_path / "repo1").mkdir()
        (tmp_path / "repo2").mkdir()
        (tmp_path / "repo3").mkdir()
        
        with patch("cortex.cli.lens_dashboard.DASHBOARD_ROOT", tmp_path):
            result = runner.invoke(list_cmd)
        
        assert result.exit_code == 0
        assert "repo1" in result.output
        assert "repo2" in result.output
        assert "repo3" in result.output


class TestDashboardGroupCommand:
    """Test 'cortex lens dashboard' group command."""

    def test_dashboard_help(self, runner: CliRunner) -> None:
        """Test dashboard command shows help."""
        result = runner.invoke(dashboard, ["--help"])
        
        assert result.exit_code == 0
        assert "dashboard" in result.output.lower()
        assert "generate" in result.output.lower()
        assert "serve" in result.output.lower()

    def test_dashboard_no_subcommand(self, runner: CliRunner) -> None:
        """Test dashboard command without subcommand."""
        result = runner.invoke(dashboard)
        
        # Should show help or error
        assert result.exit_code in [0, 2]


class TestVerboseOutput:
    """Test verbose output flag."""

    def test_generate_verbose(
        self, runner: CliRunner, mock_orchestrator, tmp_path: Path
    ) -> None:
        """Test verbose output during generation."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        result = runner.invoke(generate, [str(repo_path), "--verbose"])
        
        assert result.exit_code == 0
        # Verbose output should contain additional details
        # Actual implementation may vary


class TestErrorHandling:
    """Test CLI error handling."""

    def test_generate_orchestrator_error(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test error handling when orchestrator fails."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        with patch("cortex.cli.lens_dashboard.LENSVisualizationOrchestrator") as mock:
            mock.return_value.generate_dashboard.side_effect = Exception("Test error")
            
            result = runner.invoke(generate, [str(repo_path)])
        
        assert result.exit_code != 0
        assert "error" in result.output.lower()
