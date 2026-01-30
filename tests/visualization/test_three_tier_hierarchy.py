"""Test 3-Tier Dashboard Hierarchy (STATIC-VIZ-004)."""
import pytest
from pathlib import Path
from cortex.visualization.three_tier_hierarchy import ThreeTierHierarchy

class TestHierarchyGeneration:
    def test_create_entry_dashboard(self, tmp_path):
        hierarchy = ThreeTierHierarchy(output_dir=tmp_path)
        hierarchy.generate_entry_level()
        assert (tmp_path / "index.html").exists()
    
    def test_create_domain_dashboards(self, tmp_path):
        hierarchy = ThreeTierHierarchy(output_dir=tmp_path)
        hierarchy.generate_domain_level("ai", [{"name": "cortex"}])
        assert (tmp_path / "domains" / "ai" / "index.html").exists()
    
    def test_create_repository_dashboards(self, tmp_path):
        hierarchy = ThreeTierHierarchy(output_dir=tmp_path)
        hierarchy.generate_repository_level("cortex", {"domain": "ai"})
        assert (tmp_path / "repositories" / "cortex" / "index.html").exists()
    
    def test_breadcrumb_navigation(self, tmp_path):
        hierarchy = ThreeTierHierarchy(output_dir=tmp_path)
        hierarchy.generate_repository_level("cortex", {"domain": "ai"})
        html = (tmp_path / "repositories" / "cortex" / "index.html").read_text()
        assert "Entry" in html or "breadcrumb" in html.lower()
