"""
Documentation UI Tests

Tests for visual elements, theme rendering, and UI components.
"""

import pytest
from pathlib import Path


class TestDocumentationUI:
    """Test documentation UI elements."""
    
    def test_cortex_logo_displays(self):
        """Verify CORTEX logo renders in documentation."""
        logo_path = Path("docs/assets/images/cortex-logo-200.png")
        
        assert logo_path.exists(), "Logo must exist"
        assert logo_path.stat().st_size > 1000, "Logo should be a valid image file"
        
        # Verify it's referenced in mkdocs config
        with open("mkdocs.yml") as f:
            config = f.read()
        
        assert "cortex-logo-200.png" in config, "Logo must be referenced in mkdocs.yml"
    
    def test_favicon_configured(self):
        """Verify favicon is properly configured."""
        favicon_path = Path("docs/assets/images/CORTEX-logo-64.png")
        
        assert favicon_path.exists(), "Favicon must exist"
        
        with open("mkdocs.yml") as f:
            config = f.read()
        
        assert "CORTEX-logo-64.png" in config, "Favicon must be referenced"
    
    def test_custom_css_exists(self):
        """Verify custom CSS file exists."""
        css_path = Path("docs/stylesheets/cortex-glassmorphism.css")
        
        assert css_path.exists(), "Custom CSS must exist"
        assert css_path.stat().st_size > 0, "CSS file must not be empty"
    
    def test_mermaid_javascript_configured(self):
        """Verify Mermaid.js is configured for diagrams."""
        with open("mkdocs.yml") as f:
            config = f.read()
        
        assert "mermaid" in config.lower(), "Mermaid must be configured"
        assert "cdn.jsdelivr.net/npm/mermaid" in config, "Mermaid CDN must be referenced"
    
    def test_theme_material_configured(self):
        """Verify Material theme is properly configured."""
        with open("mkdocs.yml") as f:
            config = f.read()
        
        assert "material" in config, "Material theme must be configured"
        assert "logo:" in config, "Theme logo must be configured"
        assert "favicon:" in config, "Theme favicon must be configured"


class TestDocumentationNavigation:
    """Test documentation navigation structure."""
    
    def test_navigation_structure_valid(self):
        """Verify navigation hierarchy is valid."""
        with open("mkdocs.yml") as f:
            lines = f.readlines()
        
        in_nav = False
        indent_levels = []
        
        for line in lines:
            if line.strip().startswith("nav:"):
                in_nav = True
                continue
            
            if in_nav:
                if line and not line[0].isspace():
                    # End of nav section
                    break
                
                if line.strip() and ":" in line and not line.strip().startswith("#"):
                    indent = len(line) - len(line.lstrip())
                    indent_levels.append(indent)
        
        # Verify indentation is consistent
        if indent_levels:
            indent_diffs = [indent_levels[i+1] - indent_levels[i] 
                          for i in range(len(indent_levels)-1)]
            
            # All differences should be multiples of 2 (YAML indentation)
            for diff in indent_diffs:
                if diff != 0:
                    assert abs(diff) % 2 == 0, f"Invalid YAML indentation: {diff}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
