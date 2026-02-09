"""
Phase 54-A S3 - Jinja2 Template Renderer Tests
Tests for dashboard template rendering

AC_START: AC-PHASE54A-S3-TESTS
Description: 10 unit tests for template renderer
Authority: phase-54-A-incremental-onboarding-refactor.yaml
TDD: Tests written first (2026-02-09)
"""

import pytest
from pathlib import Path

from cortex.templates.dashboard_renderer import DashboardTemplateRenderer


class TestDashboardTemplateRenderer:
    """Tests for DashboardTemplateRenderer."""
    
    @pytest.fixture
    def template_dir(self, tmp_path):
        """Create temporary template directory with MVP template."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal MVP template for testing
        template_file = template_dir / "onboarding_dashboard.html.j2"
        template_content = """<!DOCTYPE html>
<html>
<head><title>{{ repository_name }}</title></head>
<body>
<h1>{{ repository_name }}</h1>
{% if overview %}
<p>Files: {{ overview.file_count }}</p>
<p>Test Framework: {{ overview.test_framework }}</p>
{% endif %}
{% for threat in threats %}
<div class="threat">{{ threat.title }} - {{ threat.level }}</div>
{% endfor %}
{% if narrative %}
<h2>{{ narrative.title }}</h2>
<p>{{ narrative.description }}</p>
{% endif %}
{% if dependencies %}
<p>Dependencies: {{ dependencies.dependency_count }}</p>
{% endif %}
</body>
</html>"""
        template_file.write_text(template_content)
        
        return template_dir
    
    @pytest.fixture
    def renderer(self, template_dir):
        """Create renderer instance."""
        return DashboardTemplateRenderer(template_dir)
    
    @pytest.fixture
    def sample_data(self):
        """Sample dashboard data."""
        return {
            "overview": {
                "file_count": 142,
                "has_tests": True,
                "test_framework": "pytest",
                "has_docs": True,
            },
            "threats": [
                {"level": "P0", "title": "Secret found", "description": "Hardcoded password"},
                {"level": "P1", "title": "SQL Injection", "description": "Unsafe query"},
            ],
            "narrative": {
                "title": "Test Repository",
                "description": "A test project",
                "value_proposition": "Improve code quality",
                "confidence": 0.85,
            },
            "dependencies": {
                "dependency_count": 15,
                "runtime_count": 12,
                "dev_count": 3,
                "dependencies": [
                    {"name": "pytest", "version": "7.0.0"},
                    {"name": "requests", "version": "2.28.0"},
                ],
            },
        }
    
    def test_renderer_initialization(self, renderer, template_dir):
        """Test renderer initializes with template directory."""
        assert renderer.template_dir == template_dir
        assert template_dir.exists()
    
    def test_template_file_exists(self, renderer):
        """Test MVP template file exists in renderer directory."""
        template_path = renderer.template_dir / "onboarding_dashboard.html.j2"
        # Template should exist (created in fixture)
        assert template_path.exists()
    
    def test_render_dashboard_success(self, renderer, sample_data):
        """Test successful dashboard rendering."""
        result = renderer.render_dashboard(
            repository_name="test-repo",
            repository_overview=sample_data["overview"],
            security_threats=sample_data["threats"],
            business_narrative=sample_data["narrative"],
            dependency_graph=sample_data["dependencies"],
        )
        
        assert result.is_ok()
        html = result.unwrap()
        assert len(html) > 0
        assert "test-repo" in html
    
    def test_render_contains_overview_data(self, renderer, sample_data):
        """Test rendered HTML contains overview data."""
        result = renderer.render_dashboard(
            repository_name="test-repo",
            repository_overview=sample_data["overview"],
            security_threats=[],
            business_narrative={},
            dependency_graph={},
        )
        
        html = result.unwrap()
        assert "142" in html  # file_count
        assert "pytest" in html  # test_framework
    
    def test_render_contains_threats(self, renderer, sample_data):
        """Test rendered HTML contains security threats."""
        result = renderer.render_dashboard(
            repository_name="test-repo",
            repository_overview={},
            security_threats=sample_data["threats"],
            business_narrative={},
            dependency_graph={},
        )
        
        html = result.unwrap()
        assert "Secret found" in html
        assert "SQL Injection" in html
        assert "P0" in html
        assert "P1" in html
    
    def test_render_contains_narrative(self, renderer, sample_data):
        """Test rendered HTML contains business narrative."""
        result = renderer.render_dashboard(
            repository_name="test-repo",
            repository_overview={},
            security_threats=[],
            business_narrative=sample_data["narrative"],
            dependency_graph={},
        )
        
        html = result.unwrap()
        assert "Test Repository" in html
        # The MVP template may not include value_proposition, just check title and description
        assert "A test project" in html
    
    def test_render_contains_dependencies(self, renderer, sample_data):
        """Test rendered HTML contains dependencies."""
        result = renderer.render_dashboard(
            repository_name="test-repo",
            repository_overview={},
            security_threats=[],
            business_narrative={},
            dependency_graph=sample_data["dependencies"],
        )
        
        html = result.unwrap()
        # MVP template shows dependency_count, not individual dependency names
        assert "15" in html  # dependency_count
    
    def test_write_dashboard_success(self, renderer, sample_data, tmp_path):
        """Test writing dashboard to file."""
        result = renderer.render_dashboard(
            repository_name="test-repo",
            repository_overview=sample_data["overview"],
            security_threats=sample_data["threats"],
            business_narrative=sample_data["narrative"],
            dependency_graph=sample_data["dependencies"],
        )
        
        html = result.unwrap()
        output_path = tmp_path / "dashboard.html"
        
        write_result = renderer.write_dashboard(html, output_path)
        assert write_result.is_ok()
        assert output_path.exists()
    
    def test_custom_filters(self, renderer):
        """Test custom Jinja2 filters."""
        # Test format_count filter
        formatted = renderer._format_count(1000)
        assert formatted == "1,000"
        
        # Test severity_color filter
        color_p0 = renderer._severity_color("P0")
        assert color_p0 == "#FF6B6B"
        
        color_p1 = renderer._severity_color("P1")
        assert color_p1 == "#FFA07A"
    
    def test_template_with_empty_data(self, renderer):
        """Test rendering with empty/missing data."""
        result = renderer.render_dashboard(
            repository_name="empty-repo",
            repository_overview=None,
            security_threats=[],
            business_narrative=None,
            dependency_graph=None,
        )
        
        assert result.is_ok()
        html = result.unwrap()
        assert "empty-repo" in html
        assert len(html) > 0


class TestCustomFilters:
    """Tests for custom Jinja2 filters."""
    
    @pytest.fixture
    def renderer(self, tmp_path):
        """Create renderer instance."""
        return DashboardTemplateRenderer(tmp_path)
    
    def test_format_count_filter(self, renderer):
        """Test number formatting filter."""
        assert renderer._format_count(0) == "0"
        assert renderer._format_count(999) == "999"
        assert renderer._format_count(1000) == "1,000"
        assert renderer._format_count(1000000) == "1,000,000"
    
    def test_format_date_filter(self, renderer):
        """Test date formatting filter."""
        date_str = "2026-02-09T00:00:00"
        formatted = renderer._format_date(date_str)
        assert "February" in formatted
        assert "09" in formatted
        assert "2026" in formatted
    
    def test_severity_color_filter(self, renderer):
        """Test severity color mapping."""
        assert renderer._severity_color("P0") == "#FF6B6B"
        assert renderer._severity_color("P1") == "#FFA07A"
        assert renderer._severity_color("P2") == "#FFD93D"
        assert renderer._severity_color("unknown") == "#888888"


# AC_COMPLETE: AC-PHASE54A-S3-TESTS ✅
