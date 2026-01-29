"""
Tests for LENS Dashboard CLI Commands.

Test Coverage:
- cortex lens dashboard serve [--port 8888]
- cortex lens dashboard serve cortex (direct CORTEX view)
- cortex lens dashboard generate (static generation)
- cortex lens dashboard clean --older-than=30d

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-015
"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock


class TestLensDashboardServeCommand:
    """Test 'cortex lens dashboard serve' command."""

    def test_serve_command_exists(self):
        """Test serve command is registered."""
        from cortex.cli.commands.lens_dashboard import serve
        
        assert serve is not None
        assert callable(serve)

    def test_serve_command_default_port(self):
        """Test serve command uses default port 8888."""
        from cortex.cli.commands.lens_dashboard import serve
        
        runner = CliRunner()
        
        with patch('uvicorn.run') as mock_run:
            result = runner.invoke(serve, ['--no-browser'])
            
            assert result.exit_code == 0
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs['port'] == 8888

    def test_serve_command_custom_port(self):
        """Test serve command with custom port."""
        from cortex.cli.commands.lens_dashboard import serve
        
        runner = CliRunner()
        
        with patch('uvicorn.run') as mock_run:
            result = runner.invoke(serve, ['--port', '9000', '--no-browser'])
            
            assert result.exit_code == 0
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs['port'] == 9000

    def test_serve_command_opens_browser(self):
        """Test serve command opens browser by default."""
        from cortex.cli.commands.lens_dashboard import serve
        
        runner = CliRunner()
        
        with patch('uvicorn.run') as mock_run, \
             patch('webbrowser.open') as mock_browser:
            
            result = runner.invoke(serve, [])
            
            assert result.exit_code == 0
            mock_browser.assert_called_once()

    def test_serve_cortex_command(self):
        """Test 'serve cortex' command for direct CORTEX view."""
        from cortex.cli.commands.lens_dashboard import serve
        
        runner = CliRunner()
        
        with patch('uvicorn.run') as mock_run, \
             patch('webbrowser.open') as mock_browser:
            
            result = runner.invoke(serve, ['cortex'])
            
            assert result.exit_code == 0
            # Should open browser to CORTEX-specific URL
            browser_url = mock_browser.call_args[0][0]
            assert 'cortex' in browser_url.lower() or 'repo=' in browser_url


class TestLensDashboardGenerateCommand:
    """Test 'cortex lens dashboard generate' command."""

    def test_generate_command_exists(self):
        """Test generate command is registered."""
        from cortex.cli.commands.lens_dashboard import generate
        
        assert generate is not None
        assert callable(generate)

    def test_generate_command_creates_html(self, tmp_path: Path):
        """Test generate command creates static HTML."""
        from cortex.cli.commands.lens_dashboard import generate
        
        runner = CliRunner()
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        output = tmp_path / "output"
        
        with patch('cortex.api.endpoints.lens_dashboard_routes.analyze_repository') as mock_analyze:
            mock_analyze.return_value = {
                'overview': {'total_files': 10},
                'dependencies': {'nodes': []},
                'classes': {'packages': []},
                'timeline': {'timeline_data': []},
                'impact': {'blast_radius': 0},
                'brain': None,
                'governance': None,
                'orchestrators': None,
                '_metadata': {'timestamp': '2026-01-29T00:00:00Z'}
            }
            
            result = runner.invoke(generate, [
                '--repo', str(repo_path),
                '--output', str(output)
            ])
            
            assert result.exit_code == 0
            mock_analyze.assert_called_once()

    def test_generate_command_default_output_dir(self, tmp_path: Path):
        """Test generate command uses default output directory."""
        from cortex.cli.commands.lens_dashboard import generate
        
        runner = CliRunner()
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        with patch('cortex.api.endpoints.lens_dashboard_routes.analyze_repository') as mock_analyze:
            
            mock_analyze.return_value = {
                'overview': {}, 'dependencies': {}, 'classes': {},
                'timeline': {}, 'impact': {}, 'brain': None,
                'governance': None, 'orchestrators': None,
                '_metadata': {'timestamp': '2026-01-29T00:00:00Z'}
            }
            
            result = runner.invoke(generate, ['--repo', str(repo_path)])
            
            assert result.exit_code == 0


class TestLensDashboardCleanCommand:
    """Test 'cortex lens dashboard clean' command."""

    def test_clean_command_exists(self):
        """Test clean command is registered."""
        from cortex.cli.commands.lens_dashboard import clean
        
        assert clean is not None
        assert callable(clean)

    def test_clean_command_removes_old_dashboards(self, tmp_path: Path):
        """Test clean command removes dashboards older than threshold."""
        from cortex.cli.commands.lens_dashboard import clean
        import time
        
        runner = CliRunner()
        
        # Create test dashboard directory
        dash_dir = tmp_path / "lens-dashboards"
        dash_dir.mkdir()
        
        # Create old file
        old_file = dash_dir / "old-dashboard.html"
        old_file.write_text("<html></html>")
        # Set modification time to 35 days ago
        old_time = time.time() - (35 * 24 * 60 * 60)
        import os
        os.utime(old_file, (old_time, old_time))
        
        # Create recent file
        recent_file = dash_dir / "recent-dashboard.html"
        recent_file.write_text("<html></html>")
        
        result = runner.invoke(clean, [
            '--directory', str(dash_dir),
            '--older-than', '30'
        ])
        
        assert result.exit_code == 0
        assert not old_file.exists()  # Should be deleted
        assert recent_file.exists()  # Should remain

    def test_clean_command_dry_run(self, tmp_path: Path):
        """Test clean command with --dry-run flag."""
        from cortex.cli.commands.lens_dashboard import clean
        import time
        
        runner = CliRunner()
        
        dash_dir = tmp_path / "lens-dashboards"
        dash_dir.mkdir()
        
        old_file = dash_dir / "old-dashboard.html"
        old_file.write_text("<html></html>")
        old_time = time.time() - (35 * 24 * 60 * 60)
        import os
        os.utime(old_file, (old_time, old_time))
        
        result = runner.invoke(clean, [
            '--directory', str(dash_dir),
            '--older-than', '30',
            '--dry-run'
        ])
        
        assert result.exit_code == 0
        assert old_file.exists()  # Should NOT be deleted in dry-run


class TestLensDashboardGroupCommand:
    """Test 'cortex lens dashboard' command group."""

    def test_dashboard_group_exists(self):
        """Test dashboard command group is registered."""
        from cortex.cli.commands.lens_dashboard import dashboard
        
        assert dashboard is not None
        # Check it's a Click group
        assert hasattr(dashboard, 'commands')

    def test_dashboard_group_has_subcommands(self):
        """Test dashboard group has all expected subcommands."""
        from cortex.cli.commands.lens_dashboard import dashboard
        
        expected_commands = ['serve', 'generate', 'clean']
        
        for cmd in expected_commands:
            assert cmd in dashboard.commands
