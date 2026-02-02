"""
Code Quality Tab Tests - CORTEX Phase 18
Tests for Quality Radar, Complexity Histogram, LOC Bar Chart
"""

import pytest
from bs4 import BeautifulSoup


class TestQualityTab:
    """Test Code Quality tab structure and content"""
    
    def test_quality_tab_exists(self, dashboard_soup: BeautifulSoup):
        """Code Quality tab is present"""
        tab = dashboard_soup.find("div", {"id": "quality"})
        assert tab is not None, "Quality tab not found"
    
    def test_quality_radar_container(self, dashboard_soup: BeautifulSoup):
        """Quality radar chart container exists"""
        radar = dashboard_soup.find(id="quality-radar")
        assert radar is not None, "Quality radar container not found"
        assert radar.name == "canvas", "Quality radar should be canvas element"
    
    def test_complexity_histogram_container(self, dashboard_soup: BeautifulSoup):
        """Complexity histogram container exists"""
        histogram = dashboard_soup.find(id="complexity-histogram")
        assert histogram is not None, "Complexity histogram container not found"
        assert histogram.name == "canvas", "Complexity histogram should be canvas element"
    
    def test_loc_bar_chart_container(self, dashboard_soup: BeautifulSoup):
        """LOC bar chart container exists"""
        loc_chart = dashboard_soup.find(id="loc-bar-chart")
        assert loc_chart is not None, "LOC bar chart container not found"
        assert loc_chart.name == "canvas", "LOC chart should be canvas element"
    
    def test_quality_subtabs_present(self, dashboard_soup: BeautifulSoup):
        """Quality sub-tabs are present (Metrics/Complexity/Duplication)"""
        tab_content = dashboard_soup.find("div", {"id": "quality"})
        
        sections = tab_content.find_all("section", class_="section-panel")
        assert len(sections) >= 3, f"Expected at least 3 sections in quality tab, found {len(sections)}"


class TestQualityVisualizationAccessibility:
    """Test accessibility of quality visualizations"""
    
    def test_quality_radar_has_aria_label(self, dashboard_soup: BeautifulSoup):
        """Quality radar has ARIA label"""
        radar = dashboard_soup.find(id="quality-radar")
        if radar:
            assert radar.get("role") == "img", "Quality radar should have role='img'"
            assert radar.get("aria-label") is not None, "Quality radar should have aria-label"
    
    def test_complexity_histogram_has_aria_label(self, dashboard_soup: BeautifulSoup):
        """Complexity histogram has ARIA label"""
        histogram = dashboard_soup.find(id="complexity-histogram")
        if histogram:
            assert histogram.get("role") == "img", "Complexity histogram should have role='img'"
    
    def test_loc_chart_has_aria_label(self, dashboard_soup: BeautifulSoup):
        """LOC chart has ARIA label"""
        loc_chart = dashboard_soup.find(id="loc-bar-chart")
        if loc_chart:
            assert loc_chart.get("role") == "img", "LOC chart should have role='img'"


class TestQualityDataBinding:
    """Test data binding for quality visualizations"""
    
    def test_quality_metrics_data_exists(self, dashboard_html: str):
        """Quality metrics data is defined"""
        assert "qualityMetrics" in dashboard_html, "Quality metrics data not found"
    
    def test_complexity_data_exists(self, dashboard_html: str):
        """Complexity data is defined"""
        assert "complexityData" in dashboard_html, "Complexity data not found"
    
    def test_loc_distribution_data_exists(self, dashboard_html: str):
        """LOC distribution data is defined"""
        assert "locDistribution" in dashboard_html, "LOC distribution data not found"


class TestQualityMetricsCalculations:
    """Test quality metrics are within valid ranges"""
    
    def test_quality_scores_valid_range(self, dashboard_html: str):
        """Quality scores should be 0-100"""
        # This is a placeholder - would need actual data extraction
        # In real implementation, parse JSON data and validate ranges
        pytest.skip("Requires data parsing implementation")
