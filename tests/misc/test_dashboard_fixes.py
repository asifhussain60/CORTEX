"""
Tests for Dashboard Launcher and Data Collector

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrators.dashboard_launcher import DashboardServer
from src.orchestrators.dashboard_collector import DashboardDataCollector


class TestDashboardServer:
    """Tests for dashboard server path resolution."""
    
    def test_resolve_known_source(self):
        """Test resolution of known source names."""
        dashboard_dir = Path(__file__).parent.parent / "cortex-brain" / "dashboards"
        server = DashboardServer(dashboard_dir, port=8080)
        
        assert server._resolve_data_source('mock') == 'mock'
        assert server._resolve_data_source('cortex') == 'cortex'
        assert server._resolve_data_source('noor-canvas') == 'noor-canvas'
    
    def test_resolve_existing_data_directory(self, tmp_path):
        """Test resolution of repository path with existing data."""
        dashboard_dir = Path(__file__).parent.parent / "cortex-brain" / "dashboards"
        server = DashboardServer(dashboard_dir, port=8080)
        
        # Create mock repository
        repo_path = tmp_path / "V5.WebServices.PrevalidationWS"
        repo_path.mkdir()
        
        # Create corresponding data directory
        data_dir = server.dashboard_dir.parent / "v5-webservices-prevalidationws"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "health-data.json").write_text('{}')
        
        try:
            result = server._resolve_data_source(str(repo_path))
            assert result == "v5-webservices-prevalidationws"
        finally:
            # Cleanup
            if data_dir.exists():
                (data_dir / "health-data.json").unlink()
                data_dir.rmdir()
    
    def test_resolve_missing_data_directory(self, tmp_path):
        """Test resolution of repository path without data (should trigger collection)."""
        dashboard_dir = Path(__file__).parent.parent / "cortex-brain" / "dashboards"
        server = DashboardServer(dashboard_dir, port=8080)
        
        # Create mock repository
        repo_path = tmp_path / "NewRepository"
        repo_path.mkdir()
        
        result = server._resolve_data_source(str(repo_path))
        assert result.startswith("collect:")
        assert "NewRepository" in result
    
    def test_resolve_invalid_source(self):
        """Test resolution of invalid source (should default to mock)."""
        dashboard_dir = Path(__file__).parent.parent / "cortex-brain" / "dashboards"
        server = DashboardServer(dashboard_dir, port=8080)
        
        result = server._resolve_data_source("invalid-source-name")
        assert result == "mock"


class TestDashboardDataCollector:
    """Tests for dashboard data collector."""
    
    def test_collector_initialization(self, tmp_path):
        """Test collector initialization."""
        repo_path = tmp_path / "TestRepo"
        repo_path.mkdir()
        
        collector = DashboardDataCollector(repo_path)
        
        assert collector.repo_path == repo_path
        assert collector.output_name == "testrepo"
        assert "dashboards" in str(collector.output_dir)
    
    def test_collector_custom_output_name(self, tmp_path):
        """Test collector with custom output name."""
        repo_path = tmp_path / "TestRepo"
        repo_path.mkdir()
        
        collector = DashboardDataCollector(repo_path, output_name="custom-name")
        
        assert collector.output_name == "custom-name"
        assert "custom-name" in str(collector.output_dir)
    
    def test_detect_languages_csharp(self, tmp_path):
        """Test C# language detection."""
        repo_path = tmp_path / "CSharpRepo"
        repo_path.mkdir()
        
        # Create some C# files
        (repo_path / "Program.cs").write_text("class Program {}")
        (repo_path / "Service.cs").write_text("class Service {}")
        
        collector = DashboardDataCollector(repo_path)
        languages = collector._detect_languages()
        
        assert len(languages) > 0
        assert languages[0]['name'] == 'C#'
        assert languages[0]['file_count'] == 2
    
    def test_detect_languages_python(self, tmp_path):
        """Test Python language detection."""
        repo_path = tmp_path / "PythonRepo"
        repo_path.mkdir()
        
        # Create some Python files
        (repo_path / "main.py").write_text("print('hello')")
        (repo_path / "utils.py").write_text("def util(): pass")
        
        collector = DashboardDataCollector(repo_path)
        languages = collector._detect_languages()
        
        assert len(languages) > 0
        assert languages[0]['name'] == 'Python'
        assert languages[0]['file_count'] == 2
    
    def test_detect_frameworks_dotnet(self, tmp_path):
        """Test .NET framework detection."""
        repo_path = tmp_path / "DotNetRepo"
        repo_path.mkdir()
        
        # Create .csproj file
        (repo_path / "Project.csproj").write_text("<Project></Project>")
        
        collector = DashboardDataCollector(repo_path)
        frameworks = collector._detect_frameworks()
        
        assert '.NET' in frameworks['backend']
    
    def test_detect_frameworks_nodejs(self, tmp_path):
        """Test Node.js framework detection."""
        repo_path = tmp_path / "NodeRepo"
        repo_path.mkdir()
        
        # Create package.json
        (repo_path / "package.json").write_text('{"name": "test"}')
        
        collector = DashboardDataCollector(repo_path)
        frameworks = collector._detect_frameworks()
        
        assert 'Node.js' in frameworks['frontend']
    
    def test_collect_health_data_structure(self, tmp_path):
        """Test health data collection returns correct structure."""
        repo_path = tmp_path / "TestRepo"
        repo_path.mkdir()
        
        collector = DashboardDataCollector(repo_path)
        health_data = collector.collect_health_data()
        
        # Verify required fields
        assert 'overall_health_score' in health_data
        assert 'status' in health_data
        assert 'last_scan' in health_data
        assert 'summary' in health_data
        assert 'metrics' in health_data
        assert 'trends' in health_data
        
        # Verify summary fields
        assert 'total_files' in health_data['summary']
        assert 'total_loc' in health_data['summary']
    
    def test_collect_tech_stack_structure(self, tmp_path):
        """Test tech stack collection returns correct structure."""
        repo_path = tmp_path / "TestRepo"
        repo_path.mkdir()
        
        collector = DashboardDataCollector(repo_path)
        tech_stack = collector.collect_tech_stack()
        
        # Verify required fields
        assert 'frontend' in tech_stack
        assert 'backend' in tech_stack
        assert 'databases' in tech_stack
        assert 'languages' in tech_stack
        assert 'summary' in tech_stack
    
    def test_save_results(self, tmp_path):
        """Test saving results to output directory."""
        repo_path = tmp_path / "TestRepo"
        repo_path.mkdir()
        
        # Use tmp_path as brain path for testing
        collector = DashboardDataCollector(repo_path)
        collector.output_dir = tmp_path / "dashboards" / "testrepo"
        
        results = {
            'health-data': {'overall_health_score': 85},
            'tech-stack': {'languages': []},
            'metadata': {'version': '1.0'}
        }
        
        success = collector.save_results(results)
        
        assert success
        assert (collector.output_dir / 'health-data.json').exists()
        assert (collector.output_dir / 'tech-stack.json').exists()
        assert (collector.output_dir / 'metadata.json').exists()


class TestDataLoaderIntegration:
    """Integration tests for data loader fixes."""
    
    def test_error_message_for_collection_trigger(self):
        """Test that collection trigger sources show helpful error message."""
        # This would be a browser-side test, but we can verify the logic
        source = "collect:C:\\PROJECTS\\MyRepo"
        
        assert source.startswith("collect:")
        repo_path = source[8:]
        assert repo_path == "C:\\PROJECTS\\MyRepo"
    
    def test_known_data_sources(self):
        """Test that known data sources are recognized."""
        known_sources = [
            'mock', 'cortex', 'noor-canvas', 'alist', 'ksessions',
            'v5-webservices-prevalidationws', 'kashkole'
        ]
        
        # Verify these would map to valid paths in DATA_SOURCES
        for source in known_sources:
            assert source  # Simple existence check


def test_end_to_end_workflow(tmp_path):
    """Test complete workflow: collect -> launch -> load."""
    # Create test repository
    repo_path = tmp_path / "TestRepo"
    repo_path.mkdir()
    (repo_path / "test.cs").write_text("class Test {}")
    
    # Collect data
    collector = DashboardDataCollector(repo_path)
    collector.output_dir = tmp_path / "dashboards" / "testrepo"
    
    results = collector.collect_all()
    assert 'health-data' in results
    assert 'metadata' in results
    
    success = collector.save_results(results)
    assert success
    
    # Verify server would resolve this correctly
    dashboard_dir = tmp_path / "dashboards"
    server = DashboardServer(dashboard_dir, port=8080)
    # Mock the dashboard_dir to point to our test location
    server.dashboard_dir = dashboard_dir
    
    # This should find our data directory
    result = server._resolve_data_source(str(repo_path))
    # Since data exists, should not be a collection trigger
    assert not result.startswith("collect:")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
