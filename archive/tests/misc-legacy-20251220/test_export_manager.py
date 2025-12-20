"""
Tests for export_manager.py - Multi-format export functionality.

Coverage target: 80%+ (14 tests for 333 LOC)
Focus areas:
- JSON export
- Markdown export  
- CSV metrics export
- Distribution packaging
- Edge cases

Author: Asif Hussain
Date: December 2025
"""

import json
import pytest
from pathlib import Path
from src.cortex_lens.generators.export_manager import ExportManager


# ========== Fixtures ==========

@pytest.fixture
def manager():
    """Create export manager instance."""
    return ExportManager()


@pytest.fixture
def sample_data():
    """Sample analysis data for export tests."""
    return {
        'classification': {'repo_type': 'fullstack_web', 'primary_language': 'Python'},
        'health': {
            'total_files': 100,
            'total_lines': 5000,
            'health_score': 75,
            'language_map': {'Python': 60, 'JavaScript': 40}
        },
        'security': {
            'vulnerabilities_found': 2,
            'findings': [
                {'severity': 'HIGH', 'type': 'SQL Injection', 'file': 'db.py', 'line': 10}
            ]
        },
        'complexity': {
            'hotspots': [
                {'name': 'func1', 'file': 'app.py', 'cyclomatic': 15, 'cognitive': 20}
            ]
        },
        'dependencies': {
            'packages': {
                'django': {'version': '4.2', 'type': 'direct'}
            }
        }
    }


# ========== JSON Export Tests ==========

class TestJSONExport:
    """Test JSON export functionality."""
    
    def test_export_json_creates_file(self, manager, sample_data, tmp_path):
        """Test JSON export creates file."""
        output_path = tmp_path / "analysis.json"
        
        result = manager.export_json(sample_data, output_path)
        
        assert result.exists()
        assert result == output_path
    
    def test_export_json_creates_directory(self, manager, sample_data, tmp_path):
        """Test JSON export creates parent directories."""
        output_path = tmp_path / "nested" / "dir" / "analysis.json"
        
        result = manager.export_json(sample_data, output_path)
        
        assert result.exists()
        assert output_path.parent.exists()
    
    def test_export_json_valid_content(self, manager, sample_data, tmp_path):
        """Test JSON export produces valid JSON."""
        output_path = tmp_path / "analysis.json"
        
        manager.export_json(sample_data, output_path)
        
        # Should be parseable JSON
        with open(output_path, encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert loaded['health']['total_files'] == 100
        assert loaded['classification']['primary_language'] == 'Python'
    
    def test_export_json_pretty_formatted(self, manager, sample_data, tmp_path):
        """Test JSON is indented for readability."""
        output_path = tmp_path / "analysis.json"
        
        manager.export_json(sample_data, output_path)
        
        content = output_path.read_text(encoding='utf-8')
        # Pretty-printed JSON has newlines
        assert content.count('\n') > 5


# ========== Markdown Export Tests ==========

class TestMarkdownExport:
    """Test Markdown export functionality."""
    
    def test_export_markdown_creates_file(self, manager, sample_data, tmp_path):
        """Test Markdown export creates file."""
        output_path = tmp_path / "report.md"
        
        result = manager.export_markdown(sample_data, output_path, "TestRepo")
        
        assert result.exists()
        assert result == output_path
    
    def test_export_markdown_contains_repository_name(self, manager, sample_data, tmp_path):
        """Test Markdown contains repository name."""
        output_path = tmp_path / "report.md"
        
        manager.export_markdown(sample_data, output_path, "MyAwesomeRepo")
        
        content = output_path.read_text(encoding='utf-8')
        assert 'MyAwesomeRepo' in content
    
    def test_export_markdown_contains_metrics(self, manager, sample_data, tmp_path):
        """Test Markdown contains key metrics."""
        output_path = tmp_path / "report.md"
        
        manager.export_markdown(sample_data, output_path, "TestRepo")
        
        content = output_path.read_text(encoding='utf-8')
        # Should contain health metrics
        assert '100' in content or 'files' in content.lower()
        assert '75' in content or 'health' in content.lower()


# ========== CSV Export Tests ==========

class TestCSVExport:
    """Test CSV metrics export functionality."""
    
    def test_export_csv_creates_files(self, manager, sample_data, tmp_path):
        """Test CSV export creates multiple CSV files."""
        output_dir = tmp_path / "csv_output"
        
        results = manager.export_csv_metrics(sample_data, output_dir)
        
        assert len(results) > 0
        assert all(path.exists() for path in results)
        assert all(path.suffix == '.csv' for path in results)
    
    def test_export_csv_creates_directory(self, manager, sample_data, tmp_path):
        """Test CSV export creates output directory."""
        output_dir = tmp_path / "nested" / "csv"
        
        manager.export_csv_metrics(sample_data, output_dir)
        
        assert output_dir.exists()


# ========== Distribution Package Tests ==========

class TestDistributionPackage:
    """Test distribution package creation."""
    
    def test_create_package_with_dashboard(self, manager, tmp_path):
        """Test creating ZIP package from dashboard directory."""
        # Create mock dashboard directory
        dashboard_dir = tmp_path / "dashboard"
        dashboard_dir.mkdir()
        (dashboard_dir / "index.html").write_text("<html></html>")
        (dashboard_dir / "style.css").write_text("body {}")
        
        output_path = tmp_path / "package.zip"
        result = manager.create_distribution_package(dashboard_dir, output_path)
        
        assert result.exists()
        assert result.suffix == '.zip'


# ========== Edge Cases Tests ==========

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_export_json_empty_data(self, manager, tmp_path):
        """Test JSON export with empty data."""
        output_path = tmp_path / "empty.json"
        
        result = manager.export_json({}, output_path)
        
        assert result.exists()
        content = output_path.read_text(encoding='utf-8')
        assert content.strip() == '{}'
    
    def test_export_markdown_minimal_data(self, manager, tmp_path):
        """Test Markdown export with minimal data."""
        output_path = tmp_path / "minimal.md"
        minimal_data = {'classification': {}}
        
        result = manager.export_markdown(minimal_data, output_path, "Minimal")
        
        assert result.exists()
    
    def test_export_csv_missing_sections(self, manager, tmp_path):
        """Test CSV export handles missing data sections gracefully."""
        output_dir = tmp_path / "csv"
        minimal_data = {'health': {}}
        
        # Should not crash
        results = manager.export_csv_metrics(minimal_data, output_dir)
        
        # May return empty list or files with headers only
        assert isinstance(results, list)
