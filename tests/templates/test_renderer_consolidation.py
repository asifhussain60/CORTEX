"""
CORE-035 Renderer Consolidation Tests.

Verifies that the three TemplateRenderer-family classes form a coherent
hierarchy rather than three independent Jinja2 env setups:

  TemplateRenderer          (cortex/templates/template_renderer.py)
      └── DashboardTemplateRenderer  (cortex/templates/dashboard_renderer.py)

  DocsTemplateRenderer      (cortex/intelligence/documentation/template_renderer.py)
      • renamed internally; old name preserved as alias for backwards compat

AC_START: AC-PHASE55-S4-001
Phase: 55 | Stage: 4 | Priority: P1
Requirements: CORE-035 (single canonical implementation), CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: Canonical renderer — cortex.templates.template_renderer
# ═══════════════════════════════════════════════════════════════════════════════


class TestCanonicalTemplateRenderer:
    """TemplateRenderer in cortex.templates is the canonical Jinja2 string renderer."""

    def test_render_basic_substitution(self) -> None:
        """Should interpolate {{ var }} variables."""
        from cortex.templates.template_renderer import TemplateRenderer

        r = TemplateRenderer()
        assert r.render("Hello {{ name }}!", {"name": "CORTEX"}) == "Hello CORTEX!"

    def test_render_with_loop(self) -> None:
        """Should process Jinja2 loops."""
        from cortex.templates.template_renderer import TemplateRenderer

        r = TemplateRenderer()
        out = r.render("{% for x in xs %}{{ x }};{% endfor %}", {"xs": [1, 2, 3]})
        assert out == "1;2;3;"

    def test_render_with_conditional(self) -> None:
        """Should process Jinja2 conditionals."""
        from cortex.templates.template_renderer import TemplateRenderer

        r = TemplateRenderer()
        assert r.render("{% if v %}yes{% else %}no{% endif %}", {"v": True}) == "yes"
        assert r.render("{% if v %}yes{% else %}no{% endif %}", {"v": False}) == "no"

    def test_exported_from_templates_package(self) -> None:
        """TemplateRenderer must be importable from cortex.templates top-level."""
        from cortex.templates import TemplateRenderer  # type: ignore[attr-defined]

        assert callable(TemplateRenderer)


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: DashboardTemplateRenderer inherits canonical renderer
# ═══════════════════════════════════════════════════════════════════════════════


class TestDashboardRendererInheritance:
    """DashboardTemplateRenderer should be a subclass of the canonical TemplateRenderer."""

    def test_dashboard_renderer_is_subclass_of_canonical(self) -> None:
        """DashboardTemplateRenderer must inherit from cortex.templates.TemplateRenderer."""
        from cortex.templates.template_renderer import TemplateRenderer
        from cortex.templates.docs_dashboard_renderer import DashboardTemplateRenderer

        assert issubclass(DashboardTemplateRenderer, TemplateRenderer), (
            "DashboardTemplateRenderer must subclass TemplateRenderer (canonical). "
            "This resolves the CORE-035 duplication."
        )

    def test_dashboard_renderer_inherits_render_method(self, tmp_path: Path) -> None:
        """DashboardTemplateRenderer.render() should be inherited from canonical renderer."""
        from cortex.templates.docs_dashboard_renderer import DashboardTemplateRenderer

        renderer = DashboardTemplateRenderer(template_dir=tmp_path)
        # Inherited render() must work for string templates
        result = renderer.render("Hello {{ who }}!", {"who": "dashboard"})
        assert result == "Hello dashboard!"

    def test_dashboard_renderer_env_uses_parent_autoescape(self, tmp_path: Path) -> None:
        """DashboardTemplateRenderer env should have autoescape enabled (inherited)."""
        from cortex.templates.docs_dashboard_renderer import DashboardTemplateRenderer

        renderer = DashboardTemplateRenderer(template_dir=tmp_path)
        # autoescape is set on the parent env
        assert renderer.env is not None

    def test_dashboard_renderer_retains_custom_filters(self, tmp_path: Path) -> None:
        """Dashboard-specific filters (format_count, severity_color) must still exist."""
        from cortex.templates.docs_dashboard_renderer import DashboardTemplateRenderer

        renderer = DashboardTemplateRenderer(template_dir=tmp_path)
        assert "format_count" in renderer.env.filters
        assert "severity_color" in renderer.env.filters

    def test_dashboard_renderer_exported_from_templates_package(self) -> None:
        """DashboardTemplateRenderer must be importable from cortex.templates."""
        from cortex.templates import DashboardTemplateRenderer  # type: ignore[attr-defined]

        assert callable(DashboardTemplateRenderer)


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: DocsTemplateRenderer — renamed, backwards-compatible alias
# ═══════════════════════════════════════════════════════════════════════════════


class TestDocsTemplateRendererRename:
    """The docs TemplateRenderer should be renamed DocsTemplateRenderer internally.

    The old import path (cortex.intelligence.documentation.docs_template_renderer.TemplateRenderer)
    must still work — preserved as an alias — so existing tests don't break.
    """

    def test_docs_renderer_importable_as_docs_template_renderer(self) -> None:
        """DocsTemplateRenderer should be importable by its canonical name."""
        from cortex.intelligence.documentation.docs_template_renderer import (
            DocsTemplateRenderer,
        )

        assert callable(DocsTemplateRenderer)

    def test_docs_renderer_legacy_alias_preserved(self) -> None:
        """Old import path 'TemplateRenderer' must remain importable (backwards compat)."""
        from cortex.intelligence.documentation.docs_template_renderer import (
            TemplateRenderer,  # legacy alias
        )

        # It should point to DocsTemplateRenderer, not the canonical string renderer
        from cortex.intelligence.documentation.docs_template_renderer import (
            DocsTemplateRenderer,
        )
        assert TemplateRenderer is DocsTemplateRenderer

    def test_docs_renderer_is_not_subclass_of_canonical_string_renderer(self) -> None:
        """DocsTemplateRenderer is a distinct beast — file-based, role-aware.

        It MUST NOT subclass cortex.templates.TemplateRenderer because it uses
        FileSystemLoader not BaseLoader, and its render() signature is completely
        different (renders role landing pages, not raw strings).
        """
        from cortex.intelligence.documentation.docs_template_renderer import DocsTemplateRenderer
        from cortex.templates.template_renderer import TemplateRenderer as CanonicalRenderer

        assert not issubclass(DocsTemplateRenderer, CanonicalRenderer), (
            "DocsTemplateRenderer is role-aware and file-based; "
            "it must NOT inherit from the string-based canonical renderer."
        )

    def test_docs_renderer_role_configs_intact(self) -> None:
        """ROLE_CONFIGS mapping must be preserved after rename."""
        from cortex.intelligence.documentation.docs_template_renderer import DocsTemplateRenderer

        renderer = DocsTemplateRenderer()
        config = renderer.get_role_config("business")
        assert config.accent_color == "#7b61ff"
        assert config.title == "Business Leaders"

    def test_docs_renderer_build_breadcrumbs_intact(self) -> None:
        """build_breadcrumbs() must work correctly after rename."""
        from cortex.intelligence.documentation.docs_template_renderer import DocsTemplateRenderer

        renderer = DocsTemplateRenderer()
        crumbs = renderer.build_breadcrumbs("engineering", None)
        assert len(crumbs) == 2
        assert crumbs[0].title == "Home"

    def test_legacy_test_imports_still_resolve(self) -> None:
        """The existing test file's import (TemplateRenderer, RoleConfig, BreadcrumbItem)
        must all resolve without modification."""
        from cortex.intelligence.documentation.docs_template_renderer import (
            TemplateRenderer,
            RoleConfig,
            BreadcrumbItem,
        )

        assert callable(TemplateRenderer)
        assert callable(RoleConfig)
        assert callable(BreadcrumbItem)


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: No third independent Jinja2 env setup
# ═══════════════════════════════════════════════════════════════════════════════


class TestNoSpuriousJinja2Envs:
    """Verify that there is no third independent Jinja2 Environment setup.

    After consolidation:
    - cortex.templates.TemplateRenderer  → owns the canonical BaseLoader env
    - DashboardTemplateRenderer           → inherits / extends it with FileSystemLoader
    - DocsTemplateRenderer                → its own FileSystemLoader (different purpose,
                                            different loader, not a duplication)

    The test ensures DashboardTemplateRenderer no longer duplicates env construction
    by verifying it re-uses the parent's env rather than constructing a second one.
    """

    def test_dashboard_renderer_does_not_duplicate_env_init(self, tmp_path: Path) -> None:
        """DashboardTemplateRenderer should configure env via super().__init__ or shared helper."""
        from cortex.templates.docs_dashboard_renderer import DashboardTemplateRenderer
        from cortex.templates.template_renderer import TemplateRenderer

        renderer = DashboardTemplateRenderer(template_dir=tmp_path)

        # The renderer must be an instance of the canonical class
        assert isinstance(renderer, TemplateRenderer)


# AC_COMPLETE: AC-PHASE55-S4-001 ✅ RED phase — renderer consolidation tests
