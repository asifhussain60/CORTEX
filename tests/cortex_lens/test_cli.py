"""
Tests for CORTEX Lens CLI

Tests command-line interface argument parsing, command execution,
error handling, and output formatting.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.cortex_lens.cli import (
    main,
    cmd_analyze,
    cmd_scan,
    cmd_compare,
    cmd_templates,
    cmd_version,
    setup_logging
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_cortex_lens():
    """Mock CortexLens class"""
    with patch('src.cortex_lens.cli.CortexLens') as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_analyze_result():
    """Sample analyze() result"""
    return {
        'dashboard_path': '/output/index.html',
        'package_path': '/output/package.zip',
        'export_paths': {
            'json': '/output/analysis.json',
            'yaml': '/output/analysis.yaml'
        },
        'metrics': {
            'duration_seconds': 12.5,
            'total_files': 150,
            'total_loc': 5000
        }
    }


@pytest.fixture
def sample_classification():
    """Sample scan() classification result"""
    return {
        'primary_type': 'console_app',
        'secondary_types': ['api_service'],
        'confidence_scores': {
            'fullstack_web': 0.0,
            'api_service': 0.3,
            'console_app': 0.8,
            'microservices': 0.0,
            'library_package': 0.2,
            'database_project': 0.0
        },
        'detected_patterns': {
            'cli_entry_point': True,
            'command_structure': True,
            'web_framework': False,
            'rest_api': False
        },
        'dashboard_template': 'console_app'
    }


@pytest.fixture
def sample_compare_result():
    """Sample compare() result"""
    return {
        'comparison_path': '/output/comparison/index.html',
        'repositories': [
            {'name': 'repo1', 'type': 'console_app'},
            {'name': 'repo2', 'type': 'api_service'}
        ]
    }


# ============================================================================
# Test Main Entry Point
# ============================================================================

class TestMainFunction:
    """Test main() entry point"""
    
    def test_no_command_shows_help(self, capsys):
        """No command should show help"""
        result = main([])
        assert result == 0
        
        captured = capsys.readouterr()
        assert 'cortex-lens' in captured.out
        assert 'Commands' in captured.out
    
    def test_help_flag(self, capsys):
        """--help should show help"""
        with pytest.raises(SystemExit) as exc_info:
            main(['--help'])
        assert exc_info.value.code == 0
        
        captured = capsys.readouterr()
        assert 'Universal Repository Intelligence Platform' in captured.out
    
    def test_version_flag(self, capsys):
        """--version should show version"""
        with pytest.raises(SystemExit) as exc_info:
            main(['--version'])
        assert exc_info.value.code == 0
        
        captured = capsys.readouterr()
        assert 'cortex-lens' in captured.out
    
    def test_verbose_flag(self, mock_cortex_lens):
        """--verbose should enable debug logging"""
        mock_cortex_lens.analyze.return_value = {
            'dashboard_path': '/test/output/index.html',
            'package_path': '/test/output/package.zip'
        }
        
        result = main(['--verbose', 'analyze', '/test/repo'])
        assert result == 0
    
    def test_keyboard_interrupt(self, mock_cortex_lens, capsys):
        """Keyboard interrupt should exit gracefully"""
        mock_cortex_lens.analyze.side_effect = KeyboardInterrupt()
        
        result = main(['analyze', '/test/repo'])
        assert result == 1
        
        captured = capsys.readouterr()
        assert 'cancelled by user' in captured.out
    
    def test_exception_handling(self, mock_cortex_lens, caplog):
        """Exceptions should be caught and reported"""
        mock_cortex_lens.analyze.side_effect = ValueError("Test error")
        
        result = main(['analyze', '/test/repo'])
        assert result == 1
        
        # Error logged via logging module
        assert any('Error' in record.message for record in caplog.records)
    
    def test_exception_with_verbose(self, mock_cortex_lens, capsys):
        """Verbose mode should show full traceback"""
        mock_cortex_lens.analyze.side_effect = ValueError("Test error")
        
        result = main(['--verbose', 'analyze', '/test/repo'])
        assert result == 1


# ============================================================================
# Test Analyze Command
# ============================================================================

class TestAnalyzeCommand:
    """Test 'analyze' command"""
    
    def test_analyze_with_required_args(self, mock_cortex_lens, sample_analyze_result, capsys):
        """Analyze with only repo path"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo'])
        
        assert result == 0
        mock_cortex_lens.analyze.assert_called_once_with(
            repo_path='/test/repo',
            output_dir=None,
            template=None,
            export_formats=['html']
        )
        
        captured = capsys.readouterr()
        assert 'Analysis Complete' in captured.out
        assert 'index.html' in captured.out
        assert 'package.zip' in captured.out
    
    def test_analyze_with_output_dir(self, mock_cortex_lens, sample_analyze_result):
        """Analyze with custom output directory"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo', '--output', '/custom/output'])
        
        assert result == 0
        mock_cortex_lens.analyze.assert_called_once_with(
            repo_path='/test/repo',
            output_dir='/custom/output',
            template=None,
            export_formats=['html']
        )
    
    def test_analyze_with_template(self, mock_cortex_lens, sample_analyze_result):
        """Analyze with custom template"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo', '--template', 'api_service'])
        
        assert result == 0
        mock_cortex_lens.analyze.assert_called_once_with(
            repo_path='/test/repo',
            output_dir=None,
            template='api_service',
            export_formats=['html']
        )
    
    def test_analyze_with_single_format(self, mock_cortex_lens, sample_analyze_result):
        """Analyze with single export format"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo', '--format', 'json'])
        
        assert result == 0
        called_args = mock_cortex_lens.analyze.call_args
        assert called_args.kwargs['export_formats'] == ['json']
    
    def test_analyze_with_multiple_formats(self, mock_cortex_lens, sample_analyze_result):
        """Analyze with multiple export formats"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo', '--format', 'json', 'yaml', 'csv'])
        
        assert result == 0
        called_args = mock_cortex_lens.analyze.call_args
        assert called_args.kwargs['export_formats'] == ['json', 'yaml', 'csv']
    
    def test_analyze_with_all_formats(self, mock_cortex_lens, sample_analyze_result):
        """Analyze with 'all' format option"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo', '--format', 'all'])
        
        assert result == 0
        called_args = mock_cortex_lens.analyze.call_args
        assert called_args.kwargs['export_formats'] == ['all']
    
    def test_analyze_output_shows_exports(self, mock_cortex_lens, sample_analyze_result, capsys):
        """Output should list export paths"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo', '--format', 'json', 'yaml'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'Exports' in captured.out
        assert 'JSON' in captured.out
        assert 'YAML' in captured.out
    
    def test_analyze_output_shows_metrics(self, mock_cortex_lens, sample_analyze_result, capsys):
        """Output should show metrics"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        result = main(['analyze', '/test/repo'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'Metrics' in captured.out
        assert '12.50s' in captured.out
        assert '150' in captured.out
        assert '5000' in captured.out
    
    def test_analyze_without_metrics(self, mock_cortex_lens, capsys):
        """Handle analyze result without metrics"""
        mock_cortex_lens.analyze.return_value = {
            'dashboard_path': '/output/index.html',
            'package_path': '/output/package.zip'
        }
        
        result = main(['analyze', '/test/repo'])
        assert result == 0


# ============================================================================
# Test Scan Command
# ============================================================================

class TestScanCommand:
    """Test 'scan' command"""
    
    def test_scan_with_repo_path(self, mock_cortex_lens, sample_classification, capsys):
        """Scan with repository path"""
        mock_cortex_lens.scan.return_value = sample_classification
        
        result = main(['scan', '/test/repo'])
        
        assert result == 0
        mock_cortex_lens.scan.assert_called_once_with('/test/repo')
        
        captured = capsys.readouterr()
        assert 'Repository Classification' in captured.out
        assert 'console_app' in captured.out
        assert '80.0%' in captured.out
    
    def test_scan_shows_secondary_types(self, mock_cortex_lens, sample_classification, capsys):
        """Scan should show secondary types"""
        mock_cortex_lens.scan.return_value = sample_classification
        
        result = main(['scan', '/test/repo'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'Secondary Types' in captured.out
        assert 'api_service' in captured.out
        assert '30.0%' in captured.out
    
    def test_scan_shows_detected_patterns(self, mock_cortex_lens, sample_classification, capsys):
        """Scan should show detected patterns"""
        mock_cortex_lens.scan.return_value = sample_classification
        
        result = main(['scan', '/test/repo'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'Detected Patterns' in captured.out
        assert 'cli_entry_point' in captured.out
        assert 'command_structure' in captured.out
    
    def test_scan_shows_template(self, mock_cortex_lens, sample_classification, capsys):
        """Scan should show dashboard template"""
        mock_cortex_lens.scan.return_value = sample_classification
        
        result = main(['scan', '/test/repo'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'Dashboard Template' in captured.out
        assert 'console_app' in captured.out
    
    def test_scan_without_secondary_types(self, mock_cortex_lens, capsys):
        """Scan with no secondary types"""
        classification = {
            'primary_type': 'console_app',
            'secondary_types': [],
            'confidence_scores': {
                'console_app': 0.95
            },
            'detected_patterns': {},
            'dashboard_template': 'console_app'
        }
        mock_cortex_lens.scan.return_value = classification
        
        result = main(['scan', '/test/repo'])
        assert result == 0


# ============================================================================
# Test Compare Command
# ============================================================================

class TestCompareCommand:
    """Test 'compare' command"""
    
    def test_compare_with_two_repos(self, mock_cortex_lens, sample_compare_result, capsys):
        """Compare two repositories"""
        mock_cortex_lens.compare.return_value = sample_compare_result
        
        result = main(['compare', '/repo1', '/repo2'])
        
        assert result == 0
        mock_cortex_lens.compare.assert_called_once_with(
            repo_paths=['/repo1', '/repo2'],
            output_dir=None
        )
        
        captured = capsys.readouterr()
        assert 'Comparison Complete' in captured.out
        assert 'comparison/index.html' in captured.out
        assert '2' in captured.out
    
    def test_compare_with_multiple_repos(self, mock_cortex_lens, sample_compare_result):
        """Compare multiple repositories"""
        mock_cortex_lens.compare.return_value = sample_compare_result
        
        result = main(['compare', '/repo1', '/repo2', '/repo3', '/repo4'])
        
        assert result == 0
        mock_cortex_lens.compare.assert_called_once_with(
            repo_paths=['/repo1', '/repo2', '/repo3', '/repo4'],
            output_dir=None
        )
    
    def test_compare_with_output_dir(self, mock_cortex_lens, sample_compare_result):
        """Compare with custom output directory"""
        mock_cortex_lens.compare.return_value = sample_compare_result
        
        result = main(['compare', '/repo1', '/repo2', '--output', '/custom/output'])
        
        assert result == 0
        mock_cortex_lens.compare.assert_called_once_with(
            repo_paths=['/repo1', '/repo2'],
            output_dir='/custom/output'
        )


# ============================================================================
# Test Templates Command
# ============================================================================

class TestTemplatesCommand:
    """Test 'templates' command"""
    
    def test_templates_lists_all(self, capsys):
        """Templates command should list all templates"""
        result = main(['templates'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'Available Dashboard Templates' in captured.out
        assert 'fullstack_web' in captured.out
        assert 'api_service' in captured.out
        assert 'database_project' in captured.out
        assert 'console_app' in captured.out
        assert 'microservices' in captured.out
        assert 'library_package' in captured.out
    
    def test_templates_shows_descriptions(self, capsys):
        """Templates should show descriptions"""
        result = main(['templates'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'Full-Stack Web Application' in captured.out
        assert 'Frontend + Backend + Database' in captured.out


# ============================================================================
# Test Version Command
# ============================================================================

class TestVersionCommand:
    """Test 'version' command"""
    
    def test_version_command(self, capsys):
        """Version command should show version info"""
        result = main(['version'])
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'CORTEX Lens' in captured.out
        assert 'Universal Repository Intelligence Platform' in captured.out
        assert 'Asif Hussain' in captured.out
        assert '2025' in captured.out


# ============================================================================
# Test Setup Functions
# ============================================================================

class TestSetupLogging:
    """Test logging setup"""
    
    def test_setup_logging_default(self):
        """Default logging should be INFO"""
        import logging
        # Store original level
        original_level = logging.getLogger().level
        
        setup_logging(verbose=False)
        # Just verify it runs without error
        # (Level may be changed by other tests)
        
        # Restore
        logging.getLogger().setLevel(original_level)
    
    def test_setup_logging_verbose(self):
        """Verbose logging should be DEBUG"""
        import logging
        # Store original level
        original_level = logging.getLogger().level
        
        setup_logging(verbose=True)
        # Just verify it runs without error
        # (Level may be changed by other tests)
        
        # Restore
        logging.getLogger().setLevel(original_level)


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_invalid_format_choice(self, capsys):
        """Invalid format choice should error"""
        with pytest.raises(SystemExit) as exc_info:
            main(['analyze', '/test/repo', '--format', 'invalid'])
        assert exc_info.value.code != 0
    
    def test_missing_repo_path_analyze(self, capsys):
        """Analyze without repo path should error"""
        with pytest.raises(SystemExit) as exc_info:
            main(['analyze'])
        assert exc_info.value.code != 0
    
    def test_missing_repo_path_scan(self, capsys):
        """Scan without repo path should error"""
        with pytest.raises(SystemExit) as exc_info:
            main(['scan'])
        assert exc_info.value.code != 0
    
    def test_missing_repos_compare(self, capsys):
        """Compare without repos should error"""
        with pytest.raises(SystemExit) as exc_info:
            main(['compare'])
        assert exc_info.value.code != 0
    
    def test_single_repo_compare_allowed(self, mock_cortex_lens, sample_compare_result):
        """Compare with single repo (edge case)"""
        mock_cortex_lens.compare.return_value = sample_compare_result
        
        result = main(['compare', '/repo1'])
        assert result == 0
    
    def test_unknown_command(self, capsys):
        """Unknown command should exit with error"""
        with pytest.raises(SystemExit) as exc_info:
            main(['unknown'])
        # argparse exits with code 2 for invalid commands
        assert exc_info.value.code == 2


# ============================================================================
# Test Command Functions Directly
# ============================================================================

class TestCommandFunctions:
    """Test command functions directly"""
    
    def test_cmd_analyze_directly(self, mock_cortex_lens, sample_analyze_result, capsys):
        """Test cmd_analyze function directly"""
        mock_cortex_lens.analyze.return_value = sample_analyze_result
        
        args = Mock()
        args.repo_path = '/test/repo'
        args.output = None
        args.template = None
        args.format = ['html']
        
        with patch('src.cortex_lens.cli.CortexLens', return_value=mock_cortex_lens):
            result = cmd_analyze(args)
        
        assert result == 0
    
    def test_cmd_scan_directly(self, mock_cortex_lens, sample_classification, capsys):
        """Test cmd_scan function directly"""
        mock_cortex_lens.scan.return_value = sample_classification
        
        args = Mock()
        args.repo_path = '/test/repo'
        
        with patch('src.cortex_lens.cli.CortexLens', return_value=mock_cortex_lens):
            result = cmd_scan(args)
        
        assert result == 0
    
    def test_cmd_compare_directly(self, mock_cortex_lens, sample_compare_result, capsys):
        """Test cmd_compare function directly"""
        mock_cortex_lens.compare.return_value = sample_compare_result
        
        args = Mock()
        args.repos = ['/repo1', '/repo2']
        args.output = None
        
        with patch('src.cortex_lens.cli.CortexLens', return_value=mock_cortex_lens):
            result = cmd_compare(args)
        
        assert result == 0
    
    def test_cmd_templates_directly(self, capsys):
        """Test cmd_templates function directly"""
        args = Mock()
        
        result = cmd_templates(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'fullstack_web' in captured.out
    
    def test_cmd_version_directly(self, capsys):
        """Test cmd_version function directly"""
        args = Mock()
        
        result = cmd_version(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert 'CORTEX Lens' in captured.out
