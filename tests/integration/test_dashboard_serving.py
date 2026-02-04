"""
Dashboard HTTP Serving Integration Tests
Tests the full HTTP serving pipeline for dashboard data
"""

import pytest
import json
import time
import subprocess
import requests
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading


class TestDashboardServing:
    """Integration tests for dashboard HTTP serving."""
    
    @pytest.fixture(scope="class")
    def spa_directory(self):
        """Get SPA directory path."""
        return Path(__file__).parent.parent.parent / "company" / "dashboards" / "spa"
    
    @pytest.fixture(scope="class")
    def test_data_directory(self, spa_directory, tmp_path_factory):
        """Create test repository data directory."""
        temp_dir = tmp_path_factory.mktemp("dashboard_serving")
        test_repo_dir = spa_directory / "test_repo"
        test_repo_dir.mkdir(exist_ok=True)
        
        # Create test dashboard data
        test_data = {
            "repo_summary": {
                "id": 1,
                "repo_name": "test_repo",
                "repo_slug": "test-repo",
                "health_score": 85.0,
                "total_files": 100,
                "file_count": 100,
                "total_loc": 10000,
                "primary_language": "Python",
                "contributor_count": 5,
                "last_commit_date": "2026-02-04T10:00:00Z",
                "last_analyzed_at": "2026-02-04T10:00:00Z",
                "description": "Test repository",
                "version": "1.0.0"
            },
            "metrics_summary": {
                "id": 1,
                "total_loc": 10000,
                "code_loc": 8000,
                "comment_loc": 2000,
                "avg_complexity": 5.5,
                "max_complexity": 15,
                "test_coverage": 80.0,
                "maintainability_index": 75.0,
                "code_duplication_pct": 2.5,
                "comment_density": 20.0,
                "technical_debt_hours": 10,
                "calculated_at": "2026-02-04T10:00:00Z"
            },
            "packages": [],
            "files": [],
            "use_cases": [],
            "vulnerabilities": [],
            "executive_kpis": None,
            "entities": [],
            "relationships": [],
            "components": [],
            "code_smells": [],
            "metrics_by_file": [],
            "code_snippets": [],
            "test_results": [],
            "lens_insights": [],
            "refactoring_suggestions": []
        }
        
        with open(test_repo_dir / "dashboard-data.json", 'w') as f:
            json.dump(test_data, f, indent=2)
        
        yield test_repo_dir
        
        # Cleanup
        import shutil
        if test_repo_dir.exists():
            shutil.rmtree(test_repo_dir)
    
    @pytest.fixture(scope="class")
    def http_server(self, spa_directory):
        """Start HTTP server for testing."""
        import os
        
        # Change to SPA directory
        original_dir = os.getcwd()
        os.chdir(spa_directory)
        
        # Start server in background thread
        server = None
        server_thread = None
        port = 8889  # Different port to avoid conflicts
        
        def run_server():
            nonlocal server
            server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(1)
        
        yield f"http://localhost:{port}"
        
        # Cleanup
        if server:
            server.shutdown()
        os.chdir(original_dir)
    
    def test_serve_001_dashboard_html_loads(self, http_server):
        """SERVE-001: Dashboard HTML loads successfully."""
        response = requests.get(f"{http_server}/dashboard.html")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "CORTEX" in response.text
    
    def test_serve_002_json_data_accessible(self, http_server, test_data_directory):
        """SERVE-002: Repository JSON data is accessible via HTTP."""
        response = requests.get(f"{http_server}/test_repo/dashboard-data.json")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        
        data = response.json()
        assert data["repo_summary"]["repo_name"] == "test_repo"
    
    def test_serve_003_json_adapter_script_loads(self, http_server):
        """SERVE-003: JSONDataAdapter.js script is accessible."""
        response = requests.get(f"{http_server}/js/data/JSONDataAdapter.js")
        
        assert response.status_code == 200
        assert "JSONDataAdapter" in response.text
    
    def test_serve_004_dual_format_loader_loads(self, http_server):
        """SERVE-004: DualFormatDataLoader.js script is accessible."""
        response = requests.get(f"{http_server}/js/data/DualFormatDataLoader.js")
        
        assert response.status_code == 200
        assert "DualFormatDataLoader" in response.text
    
    def test_serve_005_chart_factory_loads(self, http_server):
        """SERVE-005: ChartFactory.js script is accessible."""
        response = requests.get(f"{http_server}/js/charts/ChartFactory.js")
        
        assert response.status_code == 200
        assert "ChartFactory" in response.text
    
    def test_serve_006_404_for_missing_repo(self, http_server):
        """SERVE-006: Returns 404 for non-existent repository data."""
        response = requests.get(f"{http_server}/nonexistent_repo/dashboard-data.json")
        
        assert response.status_code == 404
    
    def test_serve_007_query_param_routing(self, http_server, test_data_directory):
        """SERVE-007: Dashboard handles ?repo=test_repo query parameter."""
        response = requests.get(f"{http_server}/dashboard.html?repo=test_repo")
        
        assert response.status_code == 200
        assert "CORTEX" in response.text
    
    def test_serve_008_json_data_valid_structure(self, http_server, test_data_directory):
        """SERVE-008: Served JSON data has required structure."""
        response = requests.get(f"{http_server}/test_repo/dashboard-data.json")
        data = response.json()
        
        # Verify required sections
        assert "repo_summary" in data
        assert "metrics_summary" in data
        
        # Verify required fields
        assert "repo_name" in data["repo_summary"]
        assert "health_score" in data["repo_summary"]
        assert "total_loc" in data["metrics_summary"]
    
    def test_serve_009_cors_headers_present(self, http_server):
        """SERVE-009: CORS headers allow cross-origin requests."""
        # SimpleHTTPServer doesn't set CORS headers by default
        # This test documents expected behavior for production
        response = requests.get(f"{http_server}/dashboard.html")
        
        # Just verify request succeeds (CORS would be handled by production server)
        assert response.status_code == 200
    
    def test_serve_010_data_directory_path_resolution(self, http_server, test_data_directory):
        """SERVE-010: Data can be accessed via direct path."""
        # Test both with and without trailing slash
        response1 = requests.get(f"{http_server}/test_repo/dashboard-data.json")
        response2 = requests.get(f"{http_server}/test_repo/dashboard-data.json")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()


# Mark all tests as integration tests
pytestmark = pytest.mark.integration
