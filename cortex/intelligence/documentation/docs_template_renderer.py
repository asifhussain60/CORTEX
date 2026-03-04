"""
Jinja2 template rendering engine for CORTEX documentation site.

Renders glassmorphism-themed HTML from content.json using role-based templates.

CORE-035 note: This renderer (DocsTemplateRenderer) is intentionally separate
from cortex.templates.TemplateRenderer because it is file-system-based, role-aware,
and purpose-built for the cortex-docs HTML site — not a general string renderer.
The legacy class name ``TemplateRenderer`` is preserved as a module-level alias
for backwards compatibility with existing imports and tests.

AC_START: AC-PHASE98-S2-T3
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class RoleConfig:
    """Role-specific configuration."""

    title: str
    accent_color: str
    icon: str
    slug: str


@dataclass
class BreadcrumbItem:
    """Breadcrumb navigation item."""

    title: str
    url: str


@dataclass
class NavigationItem:  # CORE-035-scoped — domain-specific variant
    """Navigation menu item."""

    title: str
    url: str
    icon: str = ""
    active: bool = False


class DocsTemplateRenderer:
    """
    Renders CORTEX documentation site from templates.

    Uses Jinja2 to transform content.json into glassmorphism-themed HTML
    with role-based navigation and responsive design.

    Attributes:
        template_dir: Jinja2 templates directory
        output_dir: Generated HTML output directory
    """

    ROLE_CONFIGS = {
        "business": RoleConfig(
            title="Business Leaders",
            accent_color="#7b61ff",
            icon="🏢",
            slug="business",
        ),
        "product": RoleConfig(
            title="Product Owners",
            accent_color="#00d4ff",
            icon="📋",
            slug="product",
        ),
        "engineering": RoleConfig(
            title="Software Engineers",
            accent_color="#10b981",
            icon="💻",
            slug="engineering",
        ),
    }

    def __init__(
        self,
        template_dir: Path = Path("cortex-docs/templates"),
        output_dir: Path = Path("cortex-docs"),
    ) -> None:
        """
        Initialize template renderer.

        Args:
            template_dir: Jinja2 templates directory
            output_dir: Generated HTML output directory
        """
        self.template_dir = template_dir
        self.output_dir = output_dir

        if JINJA2_AVAILABLE:
            self.env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(["html", "xml"]),
            )
        else:
            self.env = None
            logger.warning("Jinja2 not available, using mock renderer")

    def get_role_config(self, role: str) -> RoleConfig:
        """
        Get configuration for a role.

        Args:
            role: Role slug (business/product/engineering)

        Returns:
            Role configuration

        Raises:
            KeyError: If role not found
        """
        return self.ROLE_CONFIGS[role]

    def build_breadcrumbs(
        self,
        role: str,
        page_slug: Optional[str] = None
    ) -> List[BreadcrumbItem]:
        """
        Build breadcrumb navigation.

        Args:
            role: Role slug
            page_slug: Optional child page slug

        Returns:
            List of breadcrumb items
        """
        config = self.get_role_config(role)
        breadcrumbs = [
            BreadcrumbItem(title="Home", url="/index.html"),
            BreadcrumbItem(
                title=config.title,
                url=f"/{role}/index.html"
            ),
        ]

        if page_slug:
            # Convert slug to title with special handling for acronyms
            # e.g., "roi-governance" → "ROI & Governance"
            parts = page_slug.split("-")
            title_parts = []
            for part in parts:
                if part.upper() in ["ROI", "API", "TDD", "MCP", "STS"]:
                    title_parts.append(part.upper())
                else:
                    title_parts.append(part.capitalize())
            title = " & ".join(title_parts) if len(title_parts) == 2 else " ".join(title_parts)

            breadcrumbs.append(
                BreadcrumbItem(
                    title=title,
                    url=f"/{role}/{page_slug}.html"
                )
            )

        return breadcrumbs

    def build_navigation(
        self,
        content_data: Dict[str, Any],
        role: str,
        active_page: Optional[str] = None
    ) -> List[NavigationItem]:
        """
        Build navigation menu for a role.

        Args:
            content_data: Content.json data
            role: Role slug
            active_page: Currently active page slug

        Returns:
            List of navigation items
        """
        nav_items = []

        role_data = content_data.get("roles", {}).get(role, {})
        pages = role_data.get("pages", [])

        for page in pages:
            nav_items.append(
                NavigationItem(
                    title=page.get("title", ""),
                    url=f"/{role}/{page.get('slug', '')}.html",
                    icon=page.get("icon", ""),
                    active=page.get("slug") == active_page,
                )
            )

        return nav_items

    def render_role_landing(
        self,
        role: str,
        content_data: Dict[str, Any]
    ) -> str:
        """
        Render role landing page.

        Args:
            role: Role slug
            content_data: Content.json data

        Returns:
            Rendered HTML

        Raises:
            FileNotFoundError: If template not found
        """
        if not self.env:
            return f"<html><body>Mock render: {role} landing</body></html>"

        template = self.env.get_template("role-landing.html.j2")
        config = self.get_role_config(role)

        return template.render(
            role=role,
            role_config=config,
            breadcrumbs=self.build_breadcrumbs(role),
            navigation=self.build_navigation(content_data, role),
            content=content_data.get("roles", {}).get(role, {}),
        )

    def render_child_page(
        self,
        role: str,
        page_slug: str,
        page_data: Dict[str, Any],
        content_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render child page.

        Args:
            role: Role slug
            page_slug: Page slug
            page_data: Page-specific data
            content_data: Full content.json (for navigation)

        Returns:
            Rendered HTML

        Raises:
            FileNotFoundError: If template not found
        """
        if not self.env:
            return f"<html><body>Mock render: {role}/{page_slug}</body></html>"

        template = self.env.get_template("child-page.html.j2")
        config = self.get_role_config(role)

        return template.render(
            role=role,
            role_config=config,
            breadcrumbs=self.build_breadcrumbs(role, page_slug),
            navigation=self.build_navigation(content_data or {}, role, page_slug),
            page=page_data,
        )

    def save_page(
        self,
        role: str,
        page_slug: str,
        html_content: str
    ) -> Path:
        """
        Save rendered HTML to file.

        Args:
            role: Role slug
            page_slug: Page slug
            html_content: Rendered HTML

        Returns:
            Path to saved file
        """
        role_dir = self.output_dir / role
        role_dir.mkdir(parents=True, exist_ok=True)

        output_file = role_dir / f"{page_slug}.html"
        output_file.write_text(html_content)

        logger.info(f"Saved: {output_file}")
        return output_file

    def render(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render all pages from content.json.

        Args:
            content_data: Content.json data

        Returns:
            Rendering results
        """
        pages_rendered = []

        for role in self.ROLE_CONFIGS.keys():
            # Render role landing page
            try:
                html = self.render_role_landing(role, content_data)
                output_file = self.save_page(role, "index", html)
                pages_rendered.append(str(output_file))
            except FileNotFoundError:
                logger.warning(f"Template not found for role: {role}")

        return {
            "status": "success",
            "pages": pages_rendered,
        }


# AC_COMPLETE: AC-PHASE98-S2-T3

# ---------------------------------------------------------------------------
# Backwards-compatibility alias (CORE-035)
# ---------------------------------------------------------------------------
# The class was originally named TemplateRenderer.  All existing imports of
# ``from cortex.intelligence.documentation.docs_template_renderer import TemplateRenderer``
# continue to resolve without modification.
TemplateRenderer = DocsTemplateRenderer
