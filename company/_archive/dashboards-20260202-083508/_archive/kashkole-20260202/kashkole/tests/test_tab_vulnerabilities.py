"""
Vulnerabilities Tab Tests - CORTEX Phase 18
Tests for NEW Vulnerabilities tab with 4 sub-tabs
"""

import pytest
from bs4 import BeautifulSoup


class TestVulnerabilitiesTab:
    """Test Vulnerabilities tab structure (NEW in Phase 18)"""
    
    def test_vulnerabilities_tab_exists(self, dashboard_soup: BeautifulSoup):
        """Vulnerabilities tab is present"""
        tab = dashboard_soup.find("div", {"id": "vulnerabilities"})
        assert tab is not None, "Vulnerabilities tab not found (NEW tab required by Phase 18)"
    
    def test_vulnerability_pie_chart_container(self, dashboard_soup: BeautifulSoup):
        """Vulnerability pie chart container exists"""
        pie_chart = dashboard_soup.find(id="vulnerability-pie-chart")
        assert pie_chart is not None, "Vulnerability pie chart container not found"
        assert pie_chart.name == "canvas", "Vulnerability pie chart should be canvas element"
    
    def test_vulnerabilities_subtabs_present(self, dashboard_soup: BeautifulSoup):
        """Four sub-tabs required: Code Smells, Anti-Patterns, Security, Best Practices"""
        tab_content = dashboard_soup.find("div", {"id": "vulnerabilities"})
        
        if tab_content:
            # Check for sub-tab buttons or sections
            subtab_buttons = tab_content.find_all("button", {"data-subtab": True})
            
            expected_subtabs = ["code-smells", "anti-patterns", "security", "best-practices"]
            found_subtabs = [btn.get("data-subtab") for btn in subtab_buttons]
            
            # If no sub-tab buttons, check for section titles
            if not found_subtabs:
                sections = tab_content.find_all("section", class_="section-panel")
                assert len(sections) >= 4, f"Expected at least 4 sections in vulnerabilities tab, found {len(sections)}"
            else:
                for expected in expected_subtabs:
                    assert expected in found_subtabs, f"Sub-tab '{expected}' not found"
    
    def test_vulnerability_summary_metrics(self, dashboard_soup: BeautifulSoup):
        """Vulnerability summary metrics displayed"""
        tab_content = dashboard_soup.find("div", {"id": "vulnerabilities"})
        
        if tab_content:
            metric_cards = tab_content.find_all("div", class_="metric-card")
            assert len(metric_cards) >= 4, f"Expected 4 metric cards for vulnerabilities, found {len(metric_cards)}"


class TestVulnerabilitiesVisualizationAccessibility:
    """Test accessibility of vulnerabilities visualizations"""
    
    def test_vulnerability_pie_has_aria_label(self, dashboard_soup: BeautifulSoup):
        """Vulnerability pie chart has ARIA label"""
        pie_chart = dashboard_soup.find(id="vulnerability-pie-chart")
        if pie_chart:
            assert pie_chart.get("role") == "img", "Vulnerability pie should have role='img'"
            assert pie_chart.get("aria-label") is not None, "Vulnerability pie should have aria-label"


class TestVulnerabilitiesDataBinding:
    """Test data binding for vulnerabilities visualizations"""
    
    def test_vulnerabilities_data_exists(self, dashboard_html: str):
        """Vulnerabilities data object is defined"""
        assert "vulnerabilities" in dashboard_html, "Vulnerabilities data not found"
    
    def test_code_smells_data_referenced(self, dashboard_html: str):
        """Code smells count is referenced"""
        assert "codeSmells" in dashboard_html or "code_smells" in dashboard_html, \
            "Code smells data not referenced"
    
    def test_anti_patterns_data_referenced(self, dashboard_html: str):
        """Anti-patterns count is referenced"""
        assert "antiPatterns" in dashboard_html or "anti_patterns" in dashboard_html, \
            "Anti-patterns data not referenced"
    
    def test_security_issues_data_referenced(self, dashboard_html: str):
        """Security issues count is referenced"""
        assert "securityIssues" in dashboard_html or "security_issues" in dashboard_html, \
            "Security issues data not referenced"


class TestVulnerabilityDetection:
    """Test vulnerability detection logic (from CORTEX best-practices YAMLs)"""
    
    def test_god_object_detection_mentioned(self, dashboard_html: str):
        """God Object detection mentioned (from engineering-anti-patterns.yaml)"""
        # Should reference God Object as a code smell
        assert "God Object" in dashboard_html or "god object" in dashboard_html.lower(), \
            "God Object detection not mentioned"
    
    def test_owasp_references(self, dashboard_html: str):
        """OWASP Top 10 referenced (from owasp-top-10.yaml)"""
        # Should mention OWASP or specific vulnerabilities
        assert "OWASP" in dashboard_html or "owasp" in dashboard_html.lower(), \
            "OWASP not referenced"


class TestVulnerabilitySeverityIndicators:
    """Test severity indicators for vulnerabilities"""
    
    def test_severity_indicators_present(self, dashboard_soup: BeautifulSoup):
        """Severity indicators (P0/P1/P2 or Critical/High/Medium/Low) present"""
        tab_content = dashboard_soup.find("div", {"id": "vulnerabilities"})
        
        if tab_content:
            # Look for severity badges/indicators
            text_content = tab_content.get_text().upper()
            
            has_severity = any(severity in text_content for severity in 
                              ["HIGH", "MEDIUM", "LOW", "CRITICAL", "P0", "P1", "P2"])
            
            assert has_severity, "No severity indicators found in vulnerabilities tab"
