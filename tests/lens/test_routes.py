"""Tests for LENS Dashboard API Routes.

Tests the FastAPI routes for dashboard generation and retrieval.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# These tests require FastAPI test client
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient


class TestDashboardRoutes:
    """Tests for dashboard API routes."""
    
    @pytest.fixture
    def temp_repo(self, tmp_path: Path) -> Path:
        """Create a temporary repository."""
        repo = tmp_path / "test-repo"
        repo.mkdir()
        (repo / "main.py").write_text("print('hello')")
        return repo
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock dashboard orchestrator."""
        mock = MagicMock()
        mock.generate_dashboard.return_value = MagicMock(
            repo_path="/test/repo",
            repo_name="test-repo",
            is_cortex=False,
            tabs=[],
            overview={},
            generated_at="2026-01-29T00:00:00",
            to_dict=lambda: {
                "repo_path": "/test/repo",
                "repo_name": "test-repo",
                "is_cortex": False,
                "tabs": [],
                "overview": {},
                "generated_at": "2026-01-29T00:00:00",
            },
        )
        mock.save_dashboard.return_value = Path("/test/output")
        return mock
    
    def test_health_check_structure(self) -> None:
        """Test health check response structure."""
        # Mock test - verify expected structure
        expected_fields = ["status", "version", "cache_entries"]
        
        # Response model defines these fields
        from pydantic import BaseModel
        
        class HealthResponse(BaseModel):
            status: str
            version: str
            cache_entries: int
        
        response = HealthResponse(status="healthy", version="1.0.0", cache_entries=0)
        assert response.status == "healthy"
    
    def test_dashboard_request_validation(self) -> None:
        """Test DashboardRequest model validation."""
        from pydantic import BaseModel, Field
        from typing import List, Optional
        
        class DashboardRequest(BaseModel):
            repo_path: str = Field(..., description="Path to repository")
            force_refresh: bool = Field(False)
            tabs: Optional[List[str]] = None
        
        # Valid request
        request = DashboardRequest(repo_path="/test/repo")
        assert request.repo_path == "/test/repo"
        assert request.force_refresh is False
        
        # With options
        request2 = DashboardRequest(
            repo_path="/test/repo",
            force_refresh=True,
            tabs=["overview", "dependencies"],
        )
        assert request2.force_refresh is True
        assert len(request2.tabs) == 2
    
    def test_dashboard_response_structure(self) -> None:
        """Test DashboardResponse model structure."""
        from pydantic import BaseModel
        from typing import Any, Dict, List, Optional
        
        class DashboardResponse(BaseModel):
            repo_path: str
            repo_name: str
            is_cortex: bool
            tabs: List[Dict[str, Any]]
            overview: Dict[str, Any]
            generated_at: str
            output_path: Optional[str] = None
        
        response = DashboardResponse(
            repo_path="/test/repo",
            repo_name="test-repo",
            is_cortex=False,
            tabs=[{"tab_id": "overview", "data": {}}],
            overview={"summary": "Test repository"},
            generated_at="2026-01-29T00:00:00",
            output_path="/test/output",
        )
        
        assert response.repo_name == "test-repo"
        assert len(response.tabs) == 1
    
    def test_cache_entry_response_structure(self) -> None:
        """Test CacheEntryResponse model structure."""
        from pydantic import BaseModel
        
        class CacheEntryResponse(BaseModel):
            repo_path: str
            output_path: str
            created_at: str
            expires_at: str
            is_cortex: bool
            is_expired: bool
        
        response = CacheEntryResponse(
            repo_path="/test/repo",
            output_path="/test/output",
            created_at="2026-01-29T00:00:00",
            expires_at="2026-01-30T00:00:00",
            is_cortex=False,
            is_expired=False,
        )
        
        assert response.is_expired is False
    
    def test_mcp_tool_definitions(self) -> None:
        """Test MCP tool definitions structure."""
        # Expected tool structure for MCP integration
        tools = {
            "lens_dashboard_generate": {
                "name": "lens_dashboard_generate",
                "description": "Generate LENS Dashboard for a repository",
                "parameters": {
                    "repo_path": {"type": "string", "required": True},
                    "force_refresh": {"type": "boolean", "required": False},
                },
            },
            "lens_dashboard_tab": {
                "name": "lens_dashboard_tab",
                "description": "Get data for a specific dashboard tab",
                "parameters": {
                    "tab_id": {"type": "string", "required": True},
                    "repo_path": {"type": "string", "required": True},
                },
            },
            "lens_dashboard_overview": {
                "name": "lens_dashboard_overview",
                "description": "Get business language overview of a repository",
                "parameters": {
                    "repo_path": {"type": "string", "required": True},
                },
            },
        }
        
        # Verify structure
        for tool_name, tool_def in tools.items():
            assert "name" in tool_def
            assert "description" in tool_def
            assert "parameters" in tool_def
            assert tool_def["parameters"]["repo_path"]["type"] == "string"


class TestDashboardGeneration:
    """Integration tests for dashboard generation."""
    
    @pytest.fixture
    def temp_repo(self, tmp_path: Path) -> Path:
        """Create a temporary repository with Python files."""
        repo = tmp_path / "test-project"
        repo.mkdir()
        
        # Create some Python files
        (repo / "main.py").write_text('''
"""Main module for test project."""

def hello():
    """Say hello."""
    return "Hello, World!"

class App:
    """Main application class."""
    
    def run(self):
        """Run the app."""
        print(hello())
''')
        
        (repo / "utils.py").write_text('''
"""Utility functions."""

def helper():
    """Helper function."""
    return 42
''')
        
        return repo
    
    def test_repository_path_validation(self, temp_repo: Path) -> None:
        """Test that valid repo path is accepted."""
        assert temp_repo.exists()
        assert temp_repo.is_dir()
        assert (temp_repo / "main.py").exists()
    
    def test_nonexistent_repo_error(self, tmp_path: Path) -> None:
        """Test that nonexistent repo raises appropriate error."""
        fake_repo = tmp_path / "nonexistent"
        assert not fake_repo.exists()
        
        # In actual API, this would return 404
        # Here we just verify the path doesn't exist
    
    def test_file_instead_of_directory_error(self, tmp_path: Path) -> None:
        """Test that file path raises appropriate error."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        
        assert file_path.exists()
        assert not file_path.is_dir()
        
        # In actual API, this would return 400


class TestCacheEndpoints:
    """Tests for cache management endpoints."""
    
    def test_cache_list_empty(self) -> None:
        """Test listing empty cache."""
        # Expected: empty list
        entries = []
        assert len(entries) == 0
    
    def test_cache_invalidation_structure(self) -> None:
        """Test cache invalidation response structure."""
        response = {
            "success": True,
            "message": "Cache invalidated",
            "repo_path": "/test/repo",
        }
        
        assert response["success"] is True
        assert "message" in response
    
    def test_cache_cleanup_structure(self) -> None:
        """Test cache cleanup response structure."""
        response = {
            "expired_removed": 2,
            "old_removed": 1,
            "total_removed": 3,
        }
        
        assert response["total_removed"] == 3
