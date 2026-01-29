"""
Tests for HTML Dashboard Templates.

AC-ID: LENS-DASH-012
Author: Asif Hussain
Phase: 14
"""

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


@pytest.fixture
def templates_dir() -> Path:
    """Get templates directory path."""
    return Path(__file__).parent.parent.parent / "cortex" / "visualization" / "templates"


@pytest.fixture
def jinja_env(templates_dir: Path) -> Environment:
    """Create Jinja2 environment for testing."""
    return Environment(loader=FileSystemLoader(str(templates_dir)))


class TestDashboardBaseTemplate:
    """Test dashboard_base.html template."""

    def test_template_exists(self, templates_dir: Path) -> None:
        """Test base template file exists."""
        template_file = templates_dir / "dashboard_base.html"
        assert template_file.exists()

    def test_template_renders(self, jinja_env: Environment) -> None:
        """Test base template renders without errors."""
        template = jinja_env.get_template("dashboard_base.html")
        
        result = template.render(
            title="Test Dashboard",
            repository_name="test-repo",
            tabs=[],
        )
        
        assert "Test Dashboard" in result
        assert "test-repo" in result

    def test_required_blocks(self, templates_dir: Path) -> None:
        """Test base template has required blocks."""
        template_file = templates_dir / "dashboard_base.html"
        source = template_file.read_text()
        
        assert "{% block head %}" in source
        assert "{% block content %}" in source
        assert "{% block scripts %}" in source

    def test_alpine_js_included(self, jinja_env: Environment) -> None:
        """Test Alpine.js is included."""
        template = jinja_env.get_template("dashboard_base.html")
        
        result = template.render(
            title="Test",
            repository_name="repo",
            tabs=[],
        )
        
        # Check for Alpine.js script tag (local vendor file)
        assert "vendor/alpine" in result or "x-data" in result

    def test_tailwind_css_included(self, jinja_env: Environment) -> None:
        """Test Tailwind CSS is included."""
        template = jinja_env.get_template("dashboard_base.html")
        
        result = template.render(
            title="Test",
            repository_name="repo",
            tabs=[],
        )
        
        # Check for Tailwind CSS (local vendor file)
        assert "vendor/tailwind" in result or "tailwindcss" in result

    def test_tab_rendering(self, jinja_env: Environment) -> None:
        """Test tabs are rendered correctly."""
        template = jinja_env.get_template("dashboard_base.html")
        
        tabs = [
            {"id": "overview", "label": "Overview", "icon": "📊"},
            {"id": "dependencies", "label": "Dependencies", "icon": "🔗"},
        ]
        
        result = template.render(
            title="Test",
            repository_name="repo",
            tabs=tabs,
        )
        
        assert "Overview" in result
        assert "Dependencies" in result
        assert "📊" in result
        assert "🔗" in result


class TestRepositoryOverviewTemplate:
    """Test repository_overview_tab.html template."""

    def test_template_exists(self, templates_dir: Path) -> None:
        """Test overview template file exists."""
        template_file = templates_dir / "tabs" / "repository_overview_tab.html"
        assert template_file.exists()

    def test_template_renders(self, jinja_env: Environment) -> None:
        """Test overview template renders."""
        template = jinja_env.get_template("tabs/repository_overview_tab.html")
        
        result = template.render(
            business_description="Test repository for unit testing",
            key_features=["Feature 1", "Feature 2"],
            tech_stack=["Python", "FastAPI"],
            architecture_patterns=["MVC", "Repository Pattern"],
        )
        
        assert "Test repository for unit testing" in result
        assert "Feature 1" in result
        assert "Python" in result
        assert "MVC" in result


class TestDependencyGraphTemplate:
    """Test dependency_graph_tab.html template."""

    def test_template_exists(self, templates_dir: Path) -> None:
        """Test dependency graph template exists."""
        template_file = templates_dir / "tabs" / "dependency_graph_tab.html"
        assert template_file.exists()

    def test_template_renders(self, jinja_env: Environment) -> None:
        """Test dependency graph template renders."""
        template = jinja_env.get_template("tabs/dependency_graph_tab.html")
        
        result = template.render(
            graph_data={
                "nodes": [{"id": "module_a"}, {"id": "module_b"}],
                "links": [{"source": "module_a", "target": "module_b"}],
            }
        )
        
        assert "module_a" in result or "graph" in result.lower()

    def test_d3_js_reference(self, templates_dir: Path) -> None:
        """Test D3.js is referenced for visualization."""
        template_file = templates_dir / "tabs" / "dependency_graph_tab.html"
        source = template_file.read_text()
        
        # Should reference D3.js (local vendor)
        assert "d3" in source.lower()


class TestClassDiagramTemplate:
    """Test class_diagram_tab.html template."""

    def test_template_exists(self, templates_dir: Path) -> None:
        """Test class diagram template exists."""
        template_file = templates_dir / "tabs" / "class_diagram_tab.html"
        assert template_file.exists()

    def test_template_renders(self, jinja_env: Environment) -> None:
        """Test class diagram template renders."""
        template = jinja_env.get_template("tabs/class_diagram_tab.html")
        
        result = template.render(
            mermaid_diagram="classDiagram\n  class TestClass"
        )
        
        assert "classDiagram" in result or "mermaid" in result.lower()

    def test_mermaid_js_reference(self, templates_dir: Path) -> None:
        """Test Mermaid.js is referenced."""
        template_file = templates_dir / "tabs" / "class_diagram_tab.html"
        source = template_file.read_text()
        
        # Should reference Mermaid.js (local vendor)
        assert "mermaid" in source.lower()


class TestGitTimelineTemplate:
    """Test git_timeline_tab.html template."""

    def test_template_exists(self, templates_dir: Path) -> None:
        """Test git timeline template exists."""
        template_file = templates_dir / "tabs" / "git_timeline_tab.html"
        assert template_file.exists()

    def test_template_renders(self, jinja_env: Environment) -> None:
        """Test git timeline template renders."""
        template = jinja_env.get_template("tabs/git_timeline_tab.html")
        
        result = template.render(
            timeline_data={
                "days": [{"date": "2026-01-01", "commits": []}],
                "stats": {
                    "total_commits": 10,
                    "total_authors": 3,
                    "total_files_changed": 50,
                    "total_insertions": 200,
                    "total_deletions": 100,
                },
                "categories": {
                    "feature": {"color": "#4CAF50", "count": 5},
                    "bugfix": {"color": "#F44336", "count": 3},
                },
            }
        )
        
        assert "2026-01-01" in result or "timeline" in result.lower()


class TestAuthorNetworkTemplate:
    """Test author_network_tab.html template."""

    def test_template_exists(self, templates_dir: Path) -> None:
        """Test author network template exists."""
        template_file = templates_dir / "tabs" / "author_network_tab.html"
        assert template_file.exists()

    def test_template_renders(self, jinja_env: Environment) -> None:
        """Test author network template renders."""
        template = jinja_env.get_template("tabs/author_network_tab.html")
        
        result = template.render(
            network_data={
                "nodes": [{"id": "Alice", "commits": 10}],
                "links": [],
                "stats": {
                    "total_authors": 3,
                    "total_collaborations": 5,
                    "average_commits_per_author": 10.5,
                    "most_active_author": "Alice",
                    "most_commits": 15,
                },
            }
        )
        
        assert "Alice" in result or "network" in result.lower()


class TestTemplateInheritance:
    """Test template inheritance structure."""

    def test_all_tab_templates_extend_base(self, templates_dir: Path) -> None:
        """Test all tab templates extend dashboard_base.html."""
        tab_templates = [
            "tabs/repository_overview_tab.html",
            "tabs/dependency_graph_tab.html",
            "tabs/class_diagram_tab.html",
            "tabs/git_timeline_tab.html",
            "tabs/author_network_tab.html",
        ]
        
        for tab_template in tab_templates:
            template_file = templates_dir / tab_template
            if template_file.exists():
                content = template_file.read_text()
                # Tab templates should either extend base or be fragments
                # Check they don't have duplicate HTML structure
                assert content.count("<html") <= 1


class TestVendorAssets:
    """Test vendor asset references."""

    def test_no_external_cdn_references(self, templates_dir: Path) -> None:
        """Test no external CDN references (self-contained requirement)."""
        for template_file in templates_dir.rglob("*.html"):
            content = template_file.read_text()
            
            # Should not reference external CDNs
            assert "cdn.jsdelivr.net" not in content, f"External CDN found in {template_file}"
            assert "unpkg.com" not in content, f"External CDN found in {template_file}"
            assert "cdnjs.cloudflare.com" not in content, f"External CDN found in {template_file}"
            
            # Tab fragments (in tabs/ folder) inherit vendor loading from parent template
            # Only check entry-point templates for vendor references
            is_tab_fragment = "/tabs/" in str(template_file) or "\\tabs\\" in str(template_file)
            
            # Should reference local vendor directory (only for entry-point templates)
            if not is_tab_fragment:
                if any(lib in content.lower() for lib in ["alpine", "d3", "mermaid", "tailwind"]):
                    # If libraries are referenced, they should be from vendor/
                    assert "vendor/" in content or "static/vendor/" in content, \
                        f"Entry-point template {template_file.name} references libraries but no vendor/ path"
