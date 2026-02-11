"""
Jinja2 Template Renderer - MVP Implementation (Phase 54-A S3)

AC_START: AC-PHASE54A-S3-001
Description: Single MVP template for dashboard rendering
Authority: phase-54-A-incremental-onboarding-refactor.yaml, S3 task
Approach: Minimal viable product - 1 template, not full library
"""

from pathlib import Path
from typing import Any, Dict, Optional

import jinja2

from cortex.brain.core.result import Err, Ok, Result


class DashboardTemplateRenderer:
    """
    Jinja2 template renderer for dashboard HTML generation.

    MVP approach:
    - Single template: onboarding_dashboard.html.j2
    - Focus on dashboard rendering, not templating library
    - Enables future template library expansion
    """

    def __init__(self, template_dir: Optional[Path] = None) -> None:
        """
        Initialize renderer.

        Args:
            template_dir: Directory containing templates (default: cortex/templates/dashboards/)
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "dashboards"

        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self._add_filters()

    def _add_filters(self) -> None:
        """Add custom Jinja2 filters."""
        self.env.filters['format_count'] = self._format_count
        self.env.filters['format_date'] = self._format_date
        self.env.filters['severity_color'] = self._severity_color

    def render_dashboard(
        self,
        repository_name: str,
        repository_overview: Dict[str, Any],
        security_threats: list,
        business_narrative: Dict[str, Any],
        dependency_graph: Dict[str, Any],
    ) -> Result[str]:
        """
        Render dashboard HTML.

        Args:
            repository_name: Repository name
            repository_overview: Overview data
            security_threats: List of threats
            business_narrative: Business narrative data
            dependency_graph: Dependency graph data

        Returns:
            Result containing rendered HTML or error
        """
        try:
            # Ensure template exists
            template_name = "onboarding_dashboard.html.j2"
            template_path = self.template_dir / template_name

            if not template_path.exists():
                return Err(f"Template not found: {template_path}")

            # Get template
            template = self.env.get_template(template_name)

            # Prepare context
            context = {
                "repository_name": repository_name,
                "overview": repository_overview,
                "threats": security_threats,
                "narrative": business_narrative,
                "dependencies": dependency_graph,
                "threat_count": len(security_threats),
                "p0_threats": len([t for t in security_threats if t.get("level") == "P0"]),
                "p1_threats": len([t for t in security_threats if t.get("level") == "P1"]),
                "p2_threats": len([t for t in security_threats if t.get("level") == "P2"]),
            }

            # Render
            html = template.render(context)
            return Ok(html)

        except jinja2.TemplateNotFound as e:
            return Err(f"Template not found: {str(e)}")
        except jinja2.TemplateSyntaxError as e:
            return Err(f"Template syntax error: {str(e)}")
        except Exception as e:
            return Err(f"Failed to render dashboard: {str(e)}")

    def write_dashboard(
        self,
        html_content: str,
        output_path: Path,
    ) -> Result[Path]:
        """
        Write dashboard HTML to file.

        Args:
            html_content: Rendered HTML
            output_path: Path to write HTML file

        Returns:
            Result containing output path or error
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content)
            return Ok(output_path)

        except Exception as e:
            return Err(f"Failed to write dashboard: {str(e)}")

    @staticmethod
    def _format_count(value: int) -> str:
        """Format large numbers with commas."""
        return f"{value:,}"

    @staticmethod
    def _format_date(date_str: str) -> str:
        """Format ISO date to readable format."""
        if not date_str:
            return "Unknown"
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%B %d, %Y")
        except Exception:
            return date_str

    @staticmethod
    def _severity_color(severity: str) -> str:
        """Map severity level to color."""
        colors = {
            "P0": "#FF6B6B",  # Red
            "P1": "#FFA07A",  # Orange
            "P2": "#FFD93D",  # Yellow
        }
        return colors.get(severity, "#888888")


# AC_COMPLETE: AC-PHASE54A-S3-001 ✅
