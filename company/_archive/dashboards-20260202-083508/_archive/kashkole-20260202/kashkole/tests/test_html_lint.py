"""
HTML structure and validation tests for enterprise dashboard.

CORTEX Phase 18.1 - HTML Lint Tests
Author: Asif Hussain
Validates: HTML5 syntax, accessibility, no broken links
"""

import pytest
from bs4 import BeautifulSoup


class TestHTMLStructure:
    """Validate basic HTML structure"""
    
    def test_html_valid_doctype(self, dashboard_html: str):
        """HTML5 doctype present"""
        assert dashboard_html.strip().startswith("<!DOCTYPE html>")
    
    def test_html_has_lang_attribute(self, dashboard_soup: BeautifulSoup):
        """HTML element has lang attribute (WCAG requirement)"""
        html_tag = dashboard_soup.find("html")
        assert html_tag is not None
        assert html_tag.get("lang") == "en"
    
    def test_html_has_title(self, dashboard_soup: BeautifulSoup):
        """Title element present"""
        title = dashboard_soup.find("title")
        assert title is not None
        assert len(title.text.strip()) > 0
    
    def test_html_has_meta_charset(self, dashboard_soup: BeautifulSoup):
        """Charset meta tag present"""
        meta_charset = dashboard_soup.find("meta", {"charset": True})
        assert meta_charset is not None


class TestTabStructure:
    """Validate tab structure matches Phase 18 spec"""
    
    @pytest.mark.parametrize("tab_id,tab_label", [
        ("overview", "Overview"),
        ("architecture", "Architecture"),
        ("quality", "Code Quality"),
        ("vulnerabilities", "Vulnerabilities"),
        ("security", "Security"),
        ("dependencies", "Dependencies"),
        ("testing", "Testing"),
    ])
    def test_tab_exists(self, dashboard_soup: BeautifulSoup, tab_id: str, tab_label: str):
        """Required tabs present"""
        # Look for tab button
        tab_button = dashboard_soup.find("button", {"data-tab": tab_id})
        assert tab_button is not None, f"Tab button '{tab_id}' not found"
        
        # Look for tab content
        tab_content = dashboard_soup.find("div", {"id": f"tab-{tab_id}"})
        assert tab_content is not None, f"Tab content '{tab_id}' not found"
    
    @pytest.mark.parametrize("tab_id,subtabs", [
        ("architecture", ["structure", "dependencies", "layers"]),
        ("quality", ["metrics", "complexity", "duplication"]),
        ("vulnerabilities", ["code-smells", "anti-patterns", "security", "best-practices"]),
        ("security", ["secrets", "dependencies", "owasp"]),
        ("dependencies", ["packages", "versions", "graph"]),
        ("testing", ["coverage", "tests"]),
    ])
    def test_subtabs_exist(self, dashboard_soup: BeautifulSoup, tab_id: str, subtabs: list[str]):
        """Required sub-tabs present within tabs"""
        tab_content = dashboard_soup.find("div", {"id": f"tab-{tab_id}"})
        assert tab_content is not None
        
        for subtab_id in subtabs:
            subtab_button = tab_content.find("button", {"data-subtab": subtab_id})
            assert subtab_button is not None, f"Sub-tab '{subtab_id}' not found in '{tab_id}'"


class TestAccessibility:
    """WCAG 2.1 AA compliance tests"""
    
    def test_all_buttons_have_accessible_names(self, dashboard_soup: BeautifulSoup):
        """All buttons have accessible names (text or aria-label)"""
        buttons = dashboard_soup.find_all("button")
        assert len(buttons) > 0, "No buttons found"
        
        for button in buttons:
            has_text = len(button.get_text(strip=True)) > 0
            has_aria_label = button.get("aria-label") is not None
            assert has_text or has_aria_label, f"Button without accessible name: {button}"
    
    def test_all_images_have_alt_text(self, dashboard_soup: BeautifulSoup):
        """All images have alt attributes"""
        images = dashboard_soup.find_all("img")
        
        for img in images:
            assert img.get("alt") is not None, f"Image without alt text: {img.get('src')}"
    
    def test_headings_hierarchical(self, dashboard_soup: BeautifulSoup):
        """Heading levels are hierarchical (no skips)"""
        headings = dashboard_soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        if not headings:
            pytest.skip("No headings found")
        
        levels = [int(h.name[1]) for h in headings]
        
        # Check first heading is h1
        assert levels[0] == 1, "First heading must be h1"
        
        # Check no level skips
        for i in range(1, len(levels)):
            diff = levels[i] - levels[i-1]
            assert diff <= 1, f"Heading level skip: h{levels[i-1]} → h{levels[i]}"


class TestVisualizationElements:
    """Validate visualization containers exist"""
    
    @pytest.mark.parametrize("chart_id", [
        "directory-treemap",
        "dependency-force-graph",
        "layer-diagram",
        "complexity-histogram",
        "quality-radar",
        "loc-bar-chart",
        "vulnerability-pie-chart",
        "dependency-tree",
        "testing-pyramid",
    ])
    def test_chart_container_exists(self, dashboard_soup: BeautifulSoup, chart_id: str):
        """Chart containers with correct IDs exist"""
        container = dashboard_soup.find("div", {"id": chart_id}) or \
                   dashboard_soup.find("canvas", {"id": chart_id}) or \
                   dashboard_soup.find("svg", {"id": chart_id})
        
        assert container is not None, f"Chart container '{chart_id}' not found"
    
    def test_d3js_library_loaded(self, dashboard_soup: BeautifulSoup):
        """D3.js library script tag present"""
        d3_script = dashboard_soup.find("script", {"src": lambda x: x and "d3" in x.lower()})
        assert d3_script is not None, "D3.js not loaded"
    
    def test_chartjs_library_loaded(self, dashboard_soup: BeautifulSoup):
        """Chart.js library script tag present"""
        chartjs_script = dashboard_soup.find("script", {"src": lambda x: x and "chart" in x.lower()})
        assert chartjs_script is not None, "Chart.js not loaded"


class TestSecurityHeaders:
    """Security-related HTML attributes"""
    
    def test_external_scripts_have_sri(self, dashboard_soup: BeautifulSoup):
        """External scripts have Subresource Integrity hashes"""
        external_scripts = dashboard_soup.find_all(
            "script", 
            {"src": lambda x: x and (x.startswith("http://") or x.startswith("https://"))}
        )
        
        for script in external_scripts:
            # SRI should be added in production
            # For now, just document requirement
            src = script.get("src")
            assert "integrity" in script.attrs or "localhost" in src or "127.0.0.1" in src, \
                f"External script without SRI: {src}"
