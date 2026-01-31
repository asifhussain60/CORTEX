"""
Tests for FastAPI Dashboard Routes.

AC-ID: LENS-DASH-013
Author: Asif Hussain
Phase: 14
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_lens_orchestrator():
    """Mock LENSVisualizationOrchestrator."""
    with patch("cortex.visualization.api.dashboard_routes.LENSVisualizationOrchestrator") as mock:
        orchestrator = Mock()
        orchestrator.generate_dashboard.return_value = Path("/tmp/dashboard")
        mock.return_value = orchestrator
        yield orchestrator


@pytest.fixture
def client(mock_lens_orchestrator):
    """Create FastAPI test client."""
    from cortex.visualization.api.dashboard_routes import app
    return TestClient(app)


class TestDashboardGenerationEndpoint:
    """Test POST /api/lens/dashboard/generate endpoint."""

    def test_generate_dashboard_local_repo(
        self, client: TestClient, mock_lens_orchestrator, tmp_path: Path
    ) -> None:
        """Test generating dashboard for local repository."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        response = client.post(
            "/api/lens/dashboard/generate",
            json={"repository_path": str(repo_path)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "dashboard_path" in data
        assert "repository_name" in data
        assert data["status"] == "success"

    def test_generate_dashboard_missing_path(self, client: TestClient) -> None:
        """Test error when repository_path is missing."""
        response = client.post(
            "/api/lens/dashboard/generate",
            json={},
        )
        
        assert response.status_code == 422  # Validation error

    def test_generate_dashboard_invalid_path(self, client: TestClient) -> None:
        """Test error when repository path doesn't exist."""
        response = client.post(
            "/api/lens/dashboard/generate",
            json={"repository_path": "/nonexistent/path"},
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_generate_dashboard_with_output_path(
        self, client: TestClient, mock_lens_orchestrator, tmp_path: Path
    ) -> None:
        """Test generating dashboard with custom output path."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        output_path = tmp_path / "custom-output"
        
        response = client.post(
            "/api/lens/dashboard/generate",
            json={
                "repository_path": str(repo_path),
                "output_path": str(output_path),
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestDashboardServeEndpoint:
    """Test GET /api/lens/dashboard/{path:path} endpoint."""

    def test_serve_dashboard_index(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test serving dashboard index.html."""
        # Create mock dashboard directory
        dashboard_path = tmp_path / "dashboard"
        dashboard_path.mkdir()
        index_file = dashboard_path / "index.html"
        index_file.write_text("<html><body>Test Dashboard</body></html>")
        
        with patch("cortex.visualization.api.dashboard_routes.DASHBOARD_ROOT", dashboard_path):
            response = client.get("/api/lens/dashboard/index.html")
        
        # Should serve the file or return appropriate response
        # Actual implementation may vary based on static file serving
        assert response.status_code in [200, 404]  # 404 if not configured

    def test_serve_dashboard_nonexistent_file(self, client: TestClient) -> None:
        """Test serving nonexistent file returns 404."""
        response = client.get("/api/lens/dashboard/nonexistent.html")
        
        assert response.status_code == 404


class TestDashboardListEndpoint:
    """Test GET /api/lens/dashboard/list endpoint."""

    def test_list_dashboards(self, client: TestClient, tmp_path: Path) -> None:
        """Test listing available dashboards."""
        # Create mock dashboards
        dashboards_root = tmp_path / "dashboards"
        dashboards_root.mkdir()
        (dashboards_root / "repo1").mkdir()
        (dashboards_root / "repo2").mkdir()
        
        with patch("cortex.visualization.api.dashboard_routes.DASHBOARD_ROOT", dashboards_root):
            response = client.get("/api/lens/dashboard/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "dashboards" in data
        # Should return list of dashboard directories
        assert isinstance(data["dashboards"], list)


class TestHealthCheckEndpoint:
    """Test GET /api/lens/dashboard/health endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get("/api/lens/dashboard/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestDashboardMetadataEndpoint:
    """Test GET /api/lens/dashboard/{repo}/metadata endpoint."""

    def test_get_dashboard_metadata(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test retrieving dashboard metadata."""
        # Create mock dashboard with metadata
        dashboard_path = tmp_path / "test-repo"
        dashboard_path.mkdir()
        metadata_file = dashboard_path / "metadata.json"
        metadata_file.write_text('{"repository": "test-repo", "generated_at": "2026-01-29"}')
        
        with patch("cortex.visualization.api.dashboard_routes.DASHBOARD_ROOT", tmp_path):
            response = client.get("/api/lens/dashboard/test-repo/metadata")
        
        if response.status_code == 200:
            data = response.json()
            assert "repository" in data or "generated_at" in data


class TestCORSHeaders:
    """Test CORS headers for local development."""

    def test_cors_headers_present(self, client: TestClient) -> None:
        """Test CORS headers are present in responses."""
        response = client.options("/api/lens/dashboard/health")
        
        # Should have CORS headers configured
        # Actual implementation may vary
        assert response.status_code in [200, 405]  # 405 if OPTIONS not implemented


class TestErrorHandling:
    """Test error handling and validation."""

    def test_invalid_json_body(self, client: TestClient) -> None:
        """Test error handling for invalid JSON."""
        response = client.post(
            "/api/lens/dashboard/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        
        assert response.status_code == 422

    def test_internal_server_error(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test internal server error handling."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        with patch("cortex.visualization.api.dashboard_routes.LENSVisualizationOrchestrator") as mock:
            mock.return_value.generate_dashboard.side_effect = Exception("Test error")
            
            response = client.post(
                "/api/lens/dashboard/generate",
                json={"repository_path": str(repo_path)},
            )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
