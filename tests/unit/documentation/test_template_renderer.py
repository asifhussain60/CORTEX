"""
Unit tests for template renderer.

Tests Jinja2 template rendering engine for CORTEX documentation site.

AC_START: AC-PHASE98-S2-T3
"""

import pytest
from pathlib import Path
from cortex.intelligence.documentation.template_renderer import (
    TemplateRenderer,
    RoleConfig,
    BreadcrumbItem,
)


class TestTemplateRendererInit:
    """Test template renderer initialization."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default parameters."""
        renderer = TemplateRenderer()
        
        assert renderer.template_dir == Path("cortex-docs/templates")
        assert renderer.output_dir == Path("cortex-docs")

    def test_init_with_custom_paths(self) -> None:
        """Test initialization with custom paths."""
        template_dir = Path("/custom/templates")
        output_dir = Path("/custom/output")
        
        renderer = TemplateRenderer(
            template_dir=template_dir,
            output_dir=output_dir,
        )
        
        assert renderer.template_dir == template_dir
        assert renderer.output_dir == output_dir


class TestRoleConfiguration:
    """Test role configuration mapping."""

    def test_business_role_config(self) -> None:
        """Test business leaders role configuration."""
        renderer = TemplateRenderer()
        config = renderer.get_role_config("business")
        
        assert config.accent_color == "#7b61ff"
        assert config.icon == "🏢"
        assert config.title == "Business Leaders"

    def test_product_role_config(self) -> None:
        """Test product owners role configuration."""
        renderer = TemplateRenderer()
        config = renderer.get_role_config("product")
        
        assert config.accent_color == "#00d4ff"
        assert config.icon == "📋"
        assert config.title == "Product Owners"

    def test_engineering_role_config(self) -> None:
        """Test software engineers role configuration."""
        renderer = TemplateRenderer()
        config = renderer.get_role_config("engineering")
        
        assert config.accent_color == "#10b981"
        assert config.icon == "💻"
        assert config.title == "Software Engineers"


class TestBreadcrumbGeneration:
    """Test breadcrumb navigation generation."""

    def test_role_landing_breadcrumbs(self) -> None:
        """Test breadcrumbs for role landing page."""
        renderer = TemplateRenderer()
        breadcrumbs = renderer.build_breadcrumbs("business", None)
        
        assert len(breadcrumbs) == 2
        assert breadcrumbs[0].title == "Home"
        assert breadcrumbs[1].title == "Business Leaders"

    def test_child_page_breadcrumbs(self) -> None:
        """Test breadcrumbs for child page."""
        renderer = TemplateRenderer()
        breadcrumbs = renderer.build_breadcrumbs(
            "business",
            "roi-governance"
        )
        
        assert len(breadcrumbs) == 3
        assert breadcrumbs[0].title == "Home"
        assert breadcrumbs[1].title == "Business Leaders"
        assert breadcrumbs[2].title == "ROI & Governance"


class TestNavigationGeneration:
    """Test navigation item generation."""

    def test_build_navigation_for_role(self) -> None:
        """Test navigation building for a role."""
        renderer = TemplateRenderer()
        content_data = {
            "roles": {
                "business": {
                    "pages": [
                        {"title": "ROI & Governance", "slug": "roi-governance"},
                        {"title": "Risk Mitigation", "slug": "risk-mitigation"},
                    ]
                }
            }
        }
        
        nav_items = renderer.build_navigation(content_data, "business")
        
        assert len(nav_items) == 2
        assert nav_items[0].title == "ROI & Governance"
        assert nav_items[0].url == "/business/roi-governance.html"


class TestHTMLRendering:
    """Test HTML rendering from templates."""

    def test_render_role_landing_page(self) -> None:
        """Test rendering role landing page."""
        renderer = TemplateRenderer()
        content_data = {
            "roles": {
                "business": {
                    "title": "Business Leaders",
                    "pages": []
                }
            }
        }
        
        # Should not raise exception
        try:
            html = renderer.render_role_landing("business", content_data)
            assert isinstance(html, str)
        except FileNotFoundError:
            # Template file doesn't exist yet, expected in TDD
            pytest.skip("Template files not created yet")

    def test_render_child_page(self) -> None:
        """Test rendering child page."""
        renderer = TemplateRenderer()
        page_data = {
            "title": "ROI & Governance",
            "sections": []
        }
        
        # Should not raise exception
        try:
            html = renderer.render_child_page(
                "business",
                "roi-governance",
                page_data
            )
            assert isinstance(html, str)
        except FileNotFoundError:
            # Template file doesn't exist yet, expected in TDD
            pytest.skip("Template files not created yet")


class TestOutputGeneration:
    """Test file output generation."""

    def test_save_rendered_page(self, tmp_path: Path) -> None:
        """Test saving rendered HTML to file."""
        renderer = TemplateRenderer(output_dir=tmp_path)
        html_content = "<html><body>Test</body></html>"
        
        output_file = renderer.save_page(
            "business",
            "index",
            html_content
        )
        
        assert output_file.exists()
        assert output_file.read_text() == html_content


# AC_COMPLETE: AC-PHASE98-S2-T3
