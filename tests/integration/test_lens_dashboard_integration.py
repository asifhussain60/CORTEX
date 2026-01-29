"""
Integration Tests for LENS Dashboard.

End-to-end testing of complete dashboard flow:
- Frontend templates ↔ API routes ↔ Backend renderers ↔ LENS analyzers
- D3.js visualizations
- Mermaid diagram rendering
- Performance benchmarks

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-016
"""

import pytest
import time
from pathlib import Path
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestDashboardEndToEnd:
    """End-to-end integration tests."""

    def test_complete_dashboard_flow(self, tmp_path: Path):
        """Test complete flow from API to data generation."""
        from cortex.api.endpoints.lens_dashboard_routes import create_dashboard_router, analyze_repository
        from fastapi import FastAPI
        
        # Create test repository
        repo = tmp_path / "test-repo"
        repo.mkdir()
        (repo / "module.py").write_text("def hello(): pass")
        
        # Create FastAPI app
        app = FastAPI()
        router = create_dashboard_router()
        app.include_router(router)  # Router already has /api/dashboard prefix
        
        client = TestClient(app)
        
        # Test analyze endpoint - repo_path is a query parameter
        response = client.get("/api/dashboard/analyze", params={"repo_path": str(repo)})
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 8 tabs present
        assert "overview" in data
        assert "dependencies" in data
        assert "classes" in data
        assert "timeline" in data
        assert "impact" in data
        assert "brain" in data
        assert "governance" in data
        assert "orchestrators" in data
        assert "_metadata" in data
        assert "classes" in data
        assert "timeline" in data
        assert "impact" in data
        assert "brain" in data
        assert "governance" in data
        assert "orchestrators" in data
        assert "_metadata" in data

    def test_cortex_repository_detection(self, tmp_path: Path):
        """Test CORTEX repository is correctly detected and gets 8 tabs."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        # Create CORTEX-like structure
        cortex_repo = tmp_path / "cortex-test"
        cortex_repo.mkdir()
        (cortex_repo / "cortex_brain").mkdir()
        cortex_dir = cortex_repo / "cortex"
        cortex_dir.mkdir()
        (cortex_dir / "orchestrators").mkdir()
        
        result = analyze_repository(repo_path=str(cortex_repo))
        
        # Should be detected as CORTEX
        assert result["_metadata"]["is_cortex"] is True
        
        # CORTEX-specific tabs should have data
        assert result["brain"] is not None
        assert result["governance"] is not None
        assert result["orchestrators"] is not None

    def test_external_repository_gets_5_tabs(self, tmp_path: Path):
        """Test external repository gets only 5 universal tabs."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        # Create regular repository
        repo = tmp_path / "external-repo"
        repo.mkdir()
        (repo / "app.py").write_text("print('hello')")
        
        result = analyze_repository(repo_path=str(repo))
        
        # Should NOT be detected as CORTEX
        assert result["_metadata"]["is_cortex"] is False
        
        # CORTEX-specific tabs should be None
        assert result["brain"] is None
        assert result["governance"] is None
        assert result["orchestrators"] is None
        
        # Universal tabs should have data
        assert result["overview"] is not None
        assert result["dependencies"] is not None
        assert result["classes"] is not None


class TestRenderersIntegration:
    """Test integration between API and backend renderers."""

    def test_complexity_renderer_integration(self, tmp_path: Path):
        """Test ComplexityRenderer integration via API."""
        from cortex.api.endpoints.lens_dashboard_routes import get_overlay_data
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Create Python file with complexity
        (repo / "complex.py").write_text("""
def complex_function():
    for i in range(10):
        if i % 2 == 0:
            print(i)
        else:
            continue
""")
        
        overlay = get_overlay_data(overlay_type="performance", repo_path=str(repo))
        
        assert "bottlenecks" in overlay
        assert "complexity_hotspots" in overlay
        assert isinstance(overlay["bottlenecks"], list)

    def test_author_network_renderer_integration(self, tmp_path: Path):
        """Test AuthorNetworkRenderer integration via dependencies tab."""
        from cortex.api.endpoints.lens_dashboard_routes import get_tab_data
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Initialize git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)
        
        (repo / "file.py").write_text("print('test')")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=repo, capture_output=True)
        
        data = get_tab_data(tab_id="dependencies", repo_path=str(repo))
        
        assert "nodes" in data
        assert "links" in data
        assert "stats" in data

    def test_mermaid_renderer_integration(self, tmp_path: Path):
        """Test MermaidRenderer integration via classes tab."""
        from cortex.api.endpoints.lens_dashboard_routes import get_tab_data
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Create Python file with class
        (repo / "models.py").write_text("""
class User:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello {self.name}"
""")
        
        data = get_tab_data(tab_id="classes", repo_path=str(repo))
        
        assert "current_diagram" in data
        assert "packages" in data
        assert "class_details" in data
        # Should contain Mermaid diagram
        assert isinstance(data["current_diagram"], str)


class TestLENSAnalyzersIntegration:
    """Test integration with Phase 7.1 LENS Intelligence."""

    def test_git_history_analyzer_integration(self, tmp_path: Path):
        """Test GitHistoryAnalyzer integration."""
        from cortex.api.endpoints.lens_dashboard_routes import get_tab_data
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Initialize git with commits
        import subprocess
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.email", "dev@example.com"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Developer"], cwd=repo, capture_output=True)
        
        (repo / "main.py").write_text("# v1")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Version 1"], cwd=repo, capture_output=True)
        
        data = get_tab_data(tab_id="timeline", repo_path=str(repo))
        
        assert "timeline_data" in data
        assert "authors" in data
        assert "stats" in data

    def test_ast_analyzer_integration(self, tmp_path: Path):
        """Test ASTAnalyzer integration."""
        from cortex.api.endpoints.lens_dashboard_routes import get_tab_data
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        # Create Python file
        (repo / "code.py").write_text("""
def function_one():
    pass

def function_two():
    pass

class MyClass:
    def method(self):
        pass
""")
        
        data = get_tab_data(tab_id="classes", repo_path=str(repo))
        
        # Should have analyzed the file
        assert data is not None
        assert "current_diagram" in data


class TestPerformanceBenchmarks:
    """Performance benchmarks for dashboard analysis."""

    def test_small_repository_performance(self, tmp_path: Path):
        """Test analysis completes quickly for small repos."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        repo = tmp_path / "small-repo"
        repo.mkdir()
        
        # Create 5 Python files
        for i in range(5):
            (repo / f"module{i}.py").write_text(f"def func{i}(): pass")
        
        start_time = time.time()
        result = analyze_repository(repo_path=str(repo))
        elapsed = time.time() - start_time
        
        # Should complete in < 2 seconds
        assert elapsed < 2.0
        assert result["_metadata"]["analysis_time_ms"] < 2000

    def test_medium_repository_performance(self, tmp_path: Path):
        """Test analysis completes reasonably for medium repos."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        repo = tmp_path / "medium-repo"
        repo.mkdir()
        
        # Create 20 Python files with some complexity
        for i in range(20):
            (repo / f"module{i}.py").write_text(f"""
def function_{i}_a():
    return {i}

def function_{i}_b():
    return {i} * 2

class Class{i}:
    def method(self):
        pass
""")
        
        start_time = time.time()
        result = analyze_repository(repo_path=str(repo))
        elapsed = time.time() - start_time
        
        # Should complete in < 5 seconds
        assert elapsed < 5.0
        assert result["_metadata"]["analysis_time_ms"] < 5000


class TestErrorHandlingIntegration:
    """Test error handling across integration points."""

    def test_malformed_python_file_handling(self, tmp_path: Path):
        """Test graceful handling of malformed Python files."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        repo = tmp_path / "broken-repo"
        repo.mkdir()
        
        # Create malformed Python file
        (repo / "broken.py").write_text("def broken(:\n    invalid syntax")
        
        # Should not crash
        result = analyze_repository(repo_path=str(repo))
        
        assert result is not None
        assert "overview" in result

    def test_non_git_repository_handling(self, tmp_path: Path):
        """Test handling of non-git repositories."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        repo = tmp_path / "no-git"
        repo.mkdir()
        (repo / "file.py").write_text("print('test')")
        
        # Should work without git
        result = analyze_repository(repo_path=str(repo))
        
        assert result is not None
        assert result["overview"]["contributors"] == 0

    def test_empty_repository_handling(self, tmp_path: Path):
        """Test handling of empty repositories."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        repo = tmp_path / "empty-repo"
        repo.mkdir()
        
        # Completely empty
        result = analyze_repository(repo_path=str(repo))
        
        assert result is not None
        assert result["overview"]["total_files"] == 0


class TestCLIIntegration:
    """Test CLI command integration with API."""

    def test_cli_serve_integration(self):
        """Test serve command creates working FastAPI app."""
        from cortex.cli.commands.lens_dashboard import serve
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        with patch('uvicorn.run') as mock_run:
            result = runner.invoke(serve, ['--no-browser'])
            
            assert result.exit_code == 0
            mock_run.assert_called_once()
            
            # Verify app is created correctly
            call_args = mock_run.call_args
            app = call_args[0][0]
            assert hasattr(app, 'routes')

    def test_cli_generate_integration(self, tmp_path: Path):
        """Test generate command creates complete files."""
        from cortex.cli.commands.lens_dashboard import generate
        from click.testing import CliRunner
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        (repo / "app.py").write_text("print('test')")
        
        output = tmp_path / "output"
        
        runner = CliRunner()
        
        with patch('cortex.api.endpoints.lens_dashboard_routes.analyze_repository') as mock_analyze:
            mock_analyze.return_value = {
                'overview': {'total_files': 1},
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
                '--repo', str(repo),
                '--output', str(output)
            ])
            
            assert result.exit_code == 0
            assert output.exists()
            
            # Check JSON file was created
            json_files = list(output.glob("*.json"))
            assert len(json_files) >= 1


class TestDataConsistency:
    """Test data consistency across different access methods."""

    def test_analyze_vs_tab_data_consistency(self, tmp_path: Path):
        """Test analyze endpoint and tab endpoint return consistent data."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository, get_tab_data
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        (repo / "module.py").write_text("def test(): pass")
        
        # Get full analysis
        full_data = analyze_repository(repo_path=str(repo))
        
        # Get individual tab
        overview_data = get_tab_data(tab_id="overview", repo_path=str(repo))
        
        # Both should be dicts
        assert isinstance(overview_data, dict)
        assert isinstance(full_data["overview"], dict)
        
        # Overview data should match
        assert overview_data["total_files"] == full_data["overview"]["total_files"]
        assert "is_cortex" in overview_data
        assert overview_data["is_cortex"] == full_data["overview"]["is_cortex"]

    def test_metadata_consistency(self, tmp_path: Path):
        """Test metadata is consistent across requests."""
        from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
        
        repo = tmp_path / "test-repo"
        repo.mkdir()
        
        result1 = analyze_repository(repo_path=str(repo))
        result2 = analyze_repository(repo_path=str(repo))
        
        # Metadata structure should be consistent
        assert set(result1["_metadata"].keys()) == set(result2["_metadata"].keys())
        assert result1["_metadata"]["repo_path"] == result2["_metadata"]["repo_path"]
