"""
Tests for SKULL Protection page UI elements.
Validates metric tiles, navigation buttons, and visual balance.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup
import re


@pytest.fixture
def skull_protection_html():
    """Load the skull-protection.html file."""
    html_path = Path(__file__).parent.parent / "docs" / "architecture" / "skull-protection.html"
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def soup(skull_protection_html):
    """Parse HTML with BeautifulSoup."""
    return BeautifulSoup(skull_protection_html, 'html.parser')


class TestMetricTiles:
    """Test metric tile sizing and content."""
    
    def test_metric_cards_exist(self, soup):
        """Verify all 5 metric cards are present."""
        metric_cards = soup.find_all(class_='metric-card')
        assert len(metric_cards) == 5, f"Expected 5 metric cards, found {len(metric_cards)}"
    
    def test_metric_values_correct(self, soup):
        """Verify metric values match expected data."""
        expected_values = ['0', '15', '118', '65', '<1ms']
        metric_values = soup.find_all(class_='metric-value')
        actual_values = [mv.get_text(strip=True) for mv in metric_values]
        
        for expected in expected_values:
            assert expected in actual_values, f"Missing metric value: {expected}"
    
    def test_metric_labels_correct(self, soup):
        """Verify metric labels match expected labels."""
        expected_labels = ['BREACHES', 'LAYERS', 'RULES', 'INSTINCTS', 'RESPONSE']
        metric_labels = soup.find_all(class_='metric-label')
        actual_labels = [ml.get_text(strip=True).upper() for ml in metric_labels]
        
        for expected in expected_labels:
            assert expected in actual_labels, f"Missing metric label: {expected}"
    
    def test_metric_card_sizing_css(self, skull_protection_html):
        """Verify metric cards have increased sizing in CSS."""
        # Check for enlarged padding
        assert 'padding: var(--spacing-xl) var(--spacing-2xl)' in skull_protection_html, \
            "Metric cards should have increased padding"
        
        # Check for increased min-width
        assert 'min-width: 140px' in skull_protection_html, \
            "Metric cards should have min-width of 140px"
    
    def test_metric_value_font_size(self, skull_protection_html):
        """Verify metric values have larger font size."""
        assert 'font-size: var(--font-3xl)' in skull_protection_html, \
            "Metric values should use font-3xl"
    
    def test_metric_label_font_size(self, skull_protection_html):
        """Verify metric labels have appropriate font size."""
        assert 'font-size: var(--font-sm)' in skull_protection_html, \
            "Metric labels should use font-sm"


class TestNavigationButtons:
    """Test navigation button balance and styling."""
    
    def test_nav_footer_exists(self, soup):
        """Verify navigation footer exists."""
        nav_footer = soup.find(class_='nav-footer')
        assert nav_footer is not None, "Navigation footer should exist"
    
    def test_both_nav_links_exist(self, soup):
        """Verify both navigation links are present."""
        nav_links = soup.find_all(class_='nav-link')
        assert len(nav_links) == 2, f"Expected 2 nav links, found {len(nav_links)}"
    
    def test_prev_link_content(self, soup):
        """Verify previous link has correct text and href."""
        prev_link = soup.find(class_='prev')
        assert prev_link is not None, "Previous link should exist"
        assert 'Architecture Overview' in prev_link.get_text(), "Previous link should mention Architecture Overview"
        assert prev_link.get('href') == 'index.html', "Previous link should point to index.html"
    
    def test_next_link_content(self, soup):
        """Verify next link has correct text and href."""
        next_link = soup.find(class_='next')
        assert next_link is not None, "Next link should exist"
        assert 'Knowledge Graph' in next_link.get_text(), "Next link should mention Knowledge Graph"
        assert next_link.get('href') == 'knowledge-graph.html', "Next link should point to knowledge-graph.html"
    
    def test_nav_buttons_visually_balanced(self, soup):
        """Verify navigation buttons have equal min-width for visual balance."""
        nav_links = soup.find_all(class_='nav-link')
        
        for link in nav_links:
            style = link.get('style', '')
            assert 'min-width: 220px' in style, \
                f"Nav link should have min-width: 220px for visual balance. Found style: {style}"
            assert 'text-align: center' in style, \
                f"Nav link should have text-align: center. Found style: {style}"
    
    def test_nav_footer_layout(self, soup):
        """Verify nav footer uses flexbox with space-between."""
        nav_footer = soup.find(class_='nav-footer')
        style = nav_footer.get('style', '')
        
        assert 'display: flex' in style, "Nav footer should use flexbox"
        assert 'justify-content: space-between' in style, "Nav footer should use space-between"
        assert 'max-width: 1200px' in style, "Nav footer should have max-width for proper centering"
    
    def test_nav_footer_spacing(self, soup):
        """Verify nav footer has proper bottom margin."""
        nav_footer = soup.find(class_='nav-footer')
        style = nav_footer.get('style', '')
        
        assert 'margin:' in style and 'auto' in style, \
            "Nav footer should be centered with margin auto"


class TestPageIntegrity:
    """Test overall page structure and integrity."""
    
    def test_page_title(self, soup):
        """Verify page has correct title."""
        title = soup.find('title')
        assert title is not None, "Page should have a title"
        assert 'SKULL Protection' in title.get_text(), "Title should mention SKULL Protection"
    
    def test_hero_section_exists(self, soup):
        """Verify hero section exists with correct title."""
        hero_title = soup.find(class_='hero-title')
        assert hero_title is not None, "Hero title should exist"
        assert 'SKULL Protection System' in hero_title.get_text(), "Hero should show correct title"
    
    def test_hero_subtitle_metrics(self, soup):
        """Verify hero subtitle contains correct metrics."""
        hero_subtitle = soup.find(class_='hero-subtitle')
        assert hero_subtitle is not None, "Hero subtitle should exist"
        
        subtitle_text = hero_subtitle.get_text()
        assert '15-layer' in subtitle_text, "Subtitle should mention 15 layers"
        assert '118 immutable rules' in subtitle_text, "Subtitle should mention 118 rules"
        assert '65 tier-0 instincts' in subtitle_text, "Subtitle should mention 65 instincts"
    
    def test_d3_script_loaded(self, skull_protection_html):
        """Verify D3.js is loaded for visualizations."""
        assert 'd3.v7.min.js' in skull_protection_html, "D3.js v7 should be loaded"
    
    def test_glassmorphism_css_loaded(self, skull_protection_html):
        """Verify glassmorphism CSS files are loaded."""
        assert 'variables.css' in skull_protection_html, "variables.css should be loaded"
        assert 'glass-patterns.css' in skull_protection_html, "glass-patterns.css should be loaded"
        assert 'micro-interactions.css' in skull_protection_html, "micro-interactions.css should be loaded"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
