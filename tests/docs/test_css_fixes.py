"""
Tests for CSS styling fixes on documentation site.

Validates that:
1. Page title "Welcome to CORTEX" has proper dark color
2. No black bar appears on left sidebar
3. Styles persist after MkDocs rebuild
"""
import subprocess
import re
from pathlib import Path
from playwright.sync_api import sync_playwright


class TestCSSFixes:
    """Test suite for MkDocs CSS styling fixes."""
    
    @staticmethod
    def rebuild_docs():
        """Force rebuild of documentation site."""
        result = subprocess.run(
            ["mkdocs", "build", "--clean"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"MkDocs build failed: {result.stderr}"
    
    @staticmethod
    def start_server():
        """Start MkDocs server in background."""
        process = subprocess.Popen(
            ["mkdocs", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    
    def test_page_title_color_is_dark(self):
        """Verify 'Welcome to CORTEX' title has dark, visible color."""
        self.rebuild_docs()
        server = self.start_server()
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto("http://127.0.0.1:8000")
                
                # Find the page title
                title = page.locator("h1").first
                
                # Get computed color
                color = page.evaluate(
                    "(el) => window.getComputedStyle(el).color",
                    title.element_handle()
                )
                
                # Parse RGB values
                rgb = re.findall(r'\d+', color)
                r, g, b = map(int, rgb)
                
                # Ensure dark color (low RGB values)
                assert r < 100 and g < 100 and b < 100, \
                    f"Title color too light: rgb({r}, {g}, {b})"
                
                browser.close()
        finally:
            server.terminate()
    
    def test_sidebar_has_no_black_bar(self):
        """Verify left sidebar has no dark header/black bar."""
        self.rebuild_docs()
        server = self.start_server()
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto("http://127.0.0.1:8000")
                
                # Find sidebar primary element
                sidebar = page.locator(".md-sidebar--primary")
                
                # Check background color
                bg_color = page.evaluate(
                    "(el) => window.getComputedStyle(el).backgroundColor",
                    sidebar.element_handle()
                )
                
                # Should be transparent or very light
                assert "rgba(0, 0, 0, 0)" in bg_color or \
                       "transparent" in bg_color or \
                       "rgb(255, 255, 255)" in bg_color, \
                    f"Sidebar has dark background: {bg_color}"
                
                browser.close()
        finally:
            server.terminate()
    
    def test_css_file_contains_fixes(self):
        """Verify custom.css contains the required style rules."""
        css_file = Path("docs/stylesheets/custom.css")
        css_content = css_file.read_text()
        
        # Check for title color fix
        assert ".md-typeset h1" in css_content, \
            "Missing h1 title styling"
        assert "#1F2937" in css_content or "rgb(31, 41, 55)" in css_content, \
            "Missing dark color for title"
        
        # Check for sidebar fix
        assert ".md-sidebar--primary" in css_content, \
            "Missing sidebar styling"
        assert "transparent" in css_content, \
            "Missing transparent background for sidebar"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
