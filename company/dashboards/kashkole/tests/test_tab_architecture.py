"""
Architecture Tab Tests - CORTEX Phase 18
Tests for Directory Treemap, Dependency Force Graph, Layer Diagram
"""

import pytest
from bs4 import BeautifulSoup


class TestArchitectureTab:
    """Test Architecture tab structure and content"""
    
    def test_architecture_tab_exists(self, dashboard_soup: BeautifulSoup):
        """Architecture tab is present"""
        tab = dashboard_soup.find("div", {"id": "architecture"})
        assert tab is not None, "Architecture tab not found"
    
    def test_directory_treemap_container(self, dashboard_soup: BeautifulSoup):
        """Directory treemap container exists"""
        treemap = dashboard_soup.find(id="directory-treemap")
        assert treemap is not None, "Directory treemap container not found"
    
    def test_dependency_force_graph_container(self, dashboard_soup: BeautifulSoup):
        """Dependency force graph container exists"""
        graph = dashboard_soup.find(id="dependency-force-graph")
        assert graph is not None, "Dependency force graph container not found"
        assert graph.name == "svg", "Dependency graph should be SVG element"
    
    def test_layer_diagram_container(self, dashboard_soup: BeautifulSoup):
        """Layer diagram container exists"""
        diagram = dashboard_soup.find(id="layer-diagram")
        assert diagram is not None, "Layer diagram container not found"
    
    def test_architecture_subtabs_present(self, dashboard_soup: BeautifulSoup):
        """Architecture sub-tabs are present (if implemented)"""
        tab_content = dashboard_soup.find("div", {"id": "architecture"})
        
        # Sub-tabs may be buttons or links with data-subtab attribute
        # For now, just check sections exist
        sections = tab_content.find_all("section", class_="section-panel")
        assert len(sections) >= 3, f"Expected at least 3 sections in architecture tab, found {len(sections)}"


class TestArchitectureVisualizationAccessibility:
    """Test accessibility of architecture visualizations"""
    
    def test_treemap_has_aria_label(self, dashboard_soup: BeautifulSoup):
        """Directory treemap has ARIA label"""
        treemap = dashboard_soup.find(id="directory-treemap")
        if treemap:
            assert treemap.get("role") == "img", "Treemap should have role='img'"
            assert treemap.get("aria-label") is not None, "Treemap should have aria-label"
    
    def test_force_graph_has_aria_label(self, dashboard_soup: BeautifulSoup):
        """Dependency force graph has ARIA label"""
        graph = dashboard_soup.find(id="dependency-force-graph")
        if graph:
            assert graph.get("role") == "img", "Force graph should have role='img'"
            assert graph.get("aria-label") is not None, "Force graph should have aria-label"
    
    def test_layer_diagram_has_aria_label(self, dashboard_soup: BeautifulSoup):
        """Layer diagram has ARIA label"""
        diagram = dashboard_soup.find(id="layer-diagram")
        if diagram:
            assert diagram.get("role") == "img", "Layer diagram should have role='img'"
            assert diagram.get("aria-label") is not None, "Layer diagram should have aria-label"


class TestArchitectureDataBinding:
    """Test data binding for architecture visualizations"""
    
    def test_dashboard_data_object_exists(self, dashboard_html: str):
        """window.dashboardData object is defined"""
        assert "window.dashboardData" in dashboard_html, "Global dashboardData object not found"
    
    def test_directory_tree_data_referenced(self, dashboard_html: str):
        """Directory tree data is referenced in script"""
        assert "dashboardData.directoryTree" in dashboard_html or \
               "directoryTree" in dashboard_html, "Directory tree data not referenced"
    
    def test_dependencies_data_referenced(self, dashboard_html: str):
        """Dependencies data is referenced in script"""
        assert "dashboardData.dependencies" in dashboard_html or \
               "dependencies" in dashboard_html, "Dependencies data not referenced"
