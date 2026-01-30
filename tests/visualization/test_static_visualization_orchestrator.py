"""
Test StaticVisualizationOrchestrator (STATIC-VIZ-001).

Tests portfolio-level static HTML + JSON dashboard generation.

AC Coverage:
- VIZ-001-AC01: Generate static HTML dashboards for portfolio view
- VIZ-001-AC02: Export JSON data for external consumption
"""

import pytest
from pathlib import Path
from cortex.visualization.static_visualization_orchestrator import (
    StaticVisualizationOrchestrator,
    DashboardOutput,
)


class TestStaticDashboardGeneration:
    """Test static dashboard generation (VIZ-001-AC01)."""
    
    def test_generate_entry_dashboard(self, tmp_path):
        """Generate entry-level portfolio dashboard."""
        orchestrator = StaticVisualizationOrchestrator(output_dir=tmp_path)
        
        result = orchestrator.generate_entry_dashboard(
            repositories=[
                {"name": "cortex", "path": "/path/to/cortex", "domain": "ai"},
                {"name": "api-gateway", "path": "/path/to/gateway", "domain": "backend"},
            ]
        )
        
        # Should create index.html
        assert (tmp_path / "index.html").exists()
        assert result.html_files["entry"] == tmp_path / "index.html"
        
        # Should have tabs section
        html_content = (tmp_path / "index.html").read_text()
        assert "Repositories" in html_content
        assert "Domains" in html_content
        assert "Quick Links" in html_content
    
    def test_dashboard_includes_repository_list(self, tmp_path):
        """Entry dashboard should list all repositories."""
        orchestrator = StaticVisualizationOrchestrator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "path": "/cortex", "domain": "ai"},
            {"name": "api-gateway", "path": "/gateway", "domain": "backend"},
            {"name": "frontend", "path": "/frontend", "domain": "ui"},
        ]
        
        orchestrator.generate_entry_dashboard(repositories=repos)
        
        html = (tmp_path / "index.html").read_text()
        assert "cortex" in html
        assert "api-gateway" in html
        assert "frontend" in html
    
    def test_dashboard_groups_by_domain(self, tmp_path):
        """Entry dashboard should group repos by domain."""
        orchestrator = StaticVisualizationOrchestrator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai"},
            {"name": "ml-pipeline", "domain": "ai"},
            {"name": "api-gateway", "domain": "backend"},
        ]
        
        orchestrator.generate_entry_dashboard(repositories=repos)
        
        html = (tmp_path / "index.html").read_text()
        # Should have domain headers
        assert "ai" in html.lower() or "AI" in html
        assert "backend" in html.lower() or "Backend" in html


class TestJSONExport:
    """Test JSON data export (VIZ-001-AC02)."""
    
    def test_export_portfolio_json(self, tmp_path):
        """Export portfolio data as JSON."""
        orchestrator = StaticVisualizationOrchestrator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "loc": 50000},
            {"name": "api-gateway", "domain": "backend", "loc": 15000},
        ]
        
        result = orchestrator.export_portfolio_json(repositories=repos)
        
        # Should create portfolio.json
        assert (tmp_path / "portfolio.json").exists()
        assert result.json_files["portfolio"] == tmp_path / "portfolio.json"
    
    def test_json_contains_repository_metadata(self, tmp_path):
        """JSON export should include repository metadata."""
        import json
        
        orchestrator = StaticVisualizationOrchestrator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "loc": 50000, "files": 200},
        ]
        
        orchestrator.export_portfolio_json(repositories=repos)
        
        data = json.loads((tmp_path / "portfolio.json").read_text())
        assert "repositories" in data
        assert len(data["repositories"]) == 1
        assert data["repositories"][0]["name"] == "cortex"
        assert data["repositories"][0]["domain"] == "ai"
    
    def test_json_includes_domain_summary(self, tmp_path):
        """JSON should include domain-level aggregation."""
        import json
        
        orchestrator = StaticVisualizationOrchestrator(output_dir=tmp_path)
        
        repos = [
            {"name": "cortex", "domain": "ai", "loc": 50000},
            {"name": "ml-pipeline", "domain": "ai", "loc": 30000},
            {"name": "api-gateway", "domain": "backend", "loc": 15000},
        ]
        
        orchestrator.export_portfolio_json(repositories=repos)
        
        data = json.loads((tmp_path / "portfolio.json").read_text())
        assert "domains" in data
        assert "ai" in data["domains"]
        assert "backend" in data["domains"]
        # AI domain should aggregate 2 repos
        assert data["domains"]["ai"]["repository_count"] == 2
