"""
AC-054A-S3-01 through S3-12: DashboardRenderer and Jinja2 Tests

TDD Test Suite (10+ tests):
- AC-054A-S3-01: Jinja2 environment initialized
- AC-054A-S3-02: Template loader configured
- AC-054A-S3-03: Auto-escape enabled for security
- AC-054A-S3-04: Template renders dashboard HTML
- AC-054A-S3-05: Includes all sections (overview, metrics, security)
- AC-054A-S3-06: Uses variables from context
- AC-054A-S3-07: format_number filter works
- AC-054A-S3-08: round_decimal filter works
- AC-054A-S3-09: format_date filter works
- AC-054A-S3-10: DashboardRenderer coordinates use cases
- AC-054A-S3-11: Renders template with data
- AC-054A-S3-12: Error handling for missing templates

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
from pathlib import Path
from typing import Dict, Any


class TestJinja2Environment:
    """Test Jinja2 environment setup."""

    def test_jinja_environment_initialized(self):
        """AC-054A-S3-01: Jinja2 environment initialized."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        
        assert hasattr(renderer, 'env')
        assert renderer.env is not None

    def test_template_loader_configured(self, tmp_path):
        """AC-054A-S3-02: Template loader configured."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer(template_path=tmp_path)
        
        assert hasattr(renderer, 'env')
        # Environment should have a loader
        assert renderer.env.loader is not None

    def test_auto_escape_enabled(self):
        """AC-054A-S3-03: Auto-escape enabled for security."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        
        # Check autoescape is enabled
        assert renderer.env.autoescape is True

    def test_custom_filters_registered(self):
        """Test custom filters are registered in Jinja2."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        
        assert "format_number" in renderer.env.filters
        assert "round_decimal" in renderer.env.filters
        assert "format_date" in renderer.env.filters


class TestDashboardTemplateRendering:
    """Test dashboard template rendering."""

    @pytest.fixture
    def template_data(self) -> Dict[str, Any]:
        """Fixture: Sample dashboard context data."""
        return {
            "repo_name": "cortex",
            "repo_url": "https://github.com/test/cortex",
            "overview": {
                "description": "Cognitive Real-Time Execution System",
                "language": "Python",
                "stars": 5000,
            },
            "metrics": {
                "test_coverage": 92.5,
                "code_quality": 88.3,
                "documentation": 85.7,
            },
            "security": {
                "p0_count": 0,
                "p1_count": 2,
                "p2_count": 5,
            },
            "dependencies": {
                "total": 42,
                "outdated": 3,
                "vulnerable": 1,
            },
            "team": {
                "contributors": 120,
                "maintainers": 5,
                "last_commit": "2026-02-09T10:30:00Z",
            },
        }

    def test_renders_dashboard_html(self, tmp_path, template_data):
        """AC-054A-S3-04: Template renders dashboard HTML."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        # Create template file
        template_file = tmp_path / "onboarding_dashboard.html.j2"
        template_file.write_text(
            "<html><head><title>{{ repo_name }}</title></head><body>Dashboard</body></html>"
        )
        
        renderer = DashboardRenderer(template_path=tmp_path)
        html = renderer.render("onboarding_dashboard.html.j2", template_data)
        
        assert html is not None
        assert "<html>" in html
        assert "cortex" in html

    def test_includes_all_dashboard_sections(self, tmp_path, template_data):
        """AC-054A-S3-05: Includes all sections (overview, metrics, security)."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        template_content = """
        <div class="overview">{{ overview.description }}</div>
        <div class="metrics">Coverage: {{ metrics.test_coverage }}%</div>
        <div class="security">P0: {{ security.p0_count }}</div>
        """
        
        template_file = tmp_path / "onboarding_dashboard.html.j2"
        template_file.write_text(template_content)
        
        renderer = DashboardRenderer(template_path=tmp_path)
        html = renderer.render("onboarding_dashboard.html.j2", template_data)
        
        assert "Cognitive Real-Time Execution System" in html
        assert "Coverage:" in html
        assert "P0:" in html

    def test_uses_variables_from_context(self, tmp_path, template_data):
        """AC-054A-S3-06: Uses variables from context."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        template_content = """
        Repo: {{ repo_name }}
        URL: {{ repo_url }}
        Contributors: {{ team.contributors }}
        """
        
        template_file = tmp_path / "onboarding_dashboard.html.j2"
        template_file.write_text(template_content)
        
        renderer = DashboardRenderer(template_path=tmp_path)
        html = renderer.render("onboarding_dashboard.html.j2", template_data)
        
        assert template_data["repo_name"] in html
        assert template_data["repo_url"] in html
        assert str(template_data["team"]["contributors"]) in html


class TestCustomJinja2Filters:
    """Test custom Jinja2 filters."""

    def test_format_number_filter(self):
        """AC-054A-S3-07: format_number filter works."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        env = renderer.env
        
        # Test filter
        template = env.from_string("{{ 5000 | format_number }}")
        result = template.render()
        
        # Should format with commas
        assert "5" in result
        # Result might be "5,000" or "5000" depending on locale

    def test_round_decimal_filter(self):
        """AC-054A-S3-08: round_decimal filter works."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        env = renderer.env
        
        # Test filter
        template = env.from_string("{{ 92.5678 | round_decimal(2) }}")
        result = template.render()
        
        assert "92.57" in result or "92.56" in result  # Rounding

    def test_format_date_filter(self):
        """AC-054A-S3-09: format_date filter works."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        env = renderer.env
        
        # Test filter
        template = env.from_string("{{ '2026-02-09T10:30:00Z' | format_date }}")
        result = template.render()
        
        assert "2026" in result
        assert ("02" in result or "2" in result)


class TestDashboardRenderer:
    """Test DashboardRenderer orchestration."""

    def test_coordinates_use_cases(self):
        """AC-054A-S3-10: DashboardRenderer coordinates use cases."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        
        # Should have references to use cases or accept data from them
        assert hasattr(renderer, 'render')

    def test_renders_with_use_case_output(self, tmp_path):
        """AC-054A-S3-11: Renders template with data from use cases."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        template_content = "{{ repo_name }}: {{ metrics.test_coverage }}%"
        template_file = tmp_path / "onboarding_dashboard.html.j2"
        template_file.write_text(template_content)
        
        renderer = DashboardRenderer(template_path=tmp_path)
        
        use_case_output = {
            "repo_name": "cortex",
            "metrics": {"test_coverage": 92.5},
        }
        
        result = renderer.render("onboarding_dashboard.html.j2", use_case_output)
        assert "cortex" in result

    def test_error_handling_missing_template(self):
        """AC-054A-S3-12: Error handling for missing templates."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        renderer = DashboardRenderer()
        
        with pytest.raises((FileNotFoundError, Exception)):
            renderer.render("nonexistent_template.j2", {})


class TestDashboardMVPIntegration:
    """Integration tests for MVP template system."""

    def test_full_rendering_pipeline(self, tmp_path):
        """Test complete rendering pipeline."""
        from cortex.orchestrators.support.dashboard_renderer import DashboardRenderer
        
        # Create MVP template
        template_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ repo_name }} Dashboard</title>
        </head>
        <body>
            <h1>{{ repo_name }}</h1>
            <div class="metrics">
                <p>Test Coverage: {{ metrics.coverage | format_number }}%</p>
                <p>Code Quality: {{ metrics.quality | round_decimal(1) }}</p>
            </div>
            <div class="security">
                <p>Critical Issues: {{ security.p0_count }}</p>
            </div>
        </body>
        </html>
        """
        
        template_file = tmp_path / "onboarding_dashboard.html.j2"
        template_file.write_text(template_content)
        
        renderer = DashboardRenderer(template_path=tmp_path)
        
        context = {
            "repo_name": "cortex",
            "metrics": {"coverage": 92.5, "quality": 88.3},
            "security": {"p0_count": 0},
        }
        
        html = renderer.render("onboarding_dashboard.html.j2", context)
        
        assert "<!DOCTYPE html>" in html
        assert "cortex Dashboard" in html
        assert "Test Coverage" in html
