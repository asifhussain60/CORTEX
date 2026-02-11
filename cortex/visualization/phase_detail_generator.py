"""
Phase Detail Page Generator

Generates complete phase detail HTML pages from PhaseDetail schema objects
using Jinja2 templates. Bridges the gap between YAML phase data and rendered HTML.

Authority: ENH-037 (Phase Detail Page Generation)
Features:
- Load Jinja2 templates
- Render from PhaseDetail Pydantic models
- XSS protection via autoescaping
- File generation to cortex-registry dashboard structure

Author: Asif Hussain
Date: 2026-02-05
"""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from cortex.models.phase_detail_schema import PhaseDetail


class PhaseDetailPageGenerator:
    """
    Generate phase detail HTML pages from schema objects.

    Features:
    - Jinja2 template rendering
    - Automatic XSS protection
    - File system generation
    - Template discovery

    Usage:
        generator = PhaseDetailPageGenerator()
        phase_data = PhaseDetail(...)
        output_path = generator.generate(phase_data, Path("output/phase-21/index.html"))
    """

    VERSION = "1.0.0"
    DEFAULT_TEMPLATE_NAME = "phase-detail.html"

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize generator with optional template directory.

        Args:
            template_dir: Directory containing Jinja2 templates
                         (default: cortex-registry/_cortex-master/dashboard/templates/)
        """
        if template_dir is None:
            # Auto-discover template directory
            template_dir = self._find_template_directory()

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _find_template_directory(self) -> Path:
        """
        Auto-discover template directory.

        Returns:
            Path to templates directory

        Raises:
            FileNotFoundError: If template directory not found
        """
        # Try relative to this file
        base = Path(__file__).parent.parent.parent
        template_path = base / "cortex-registry" / "_cortex-master" / "dashboard" / "templates"

        if template_path.exists():
            return template_path

        # Try from current working directory
        template_path = Path.cwd() / "cortex-registry" / "_cortex-master" / "dashboard" / "templates"
        if template_path.exists():
            return template_path

        raise FileNotFoundError(
            f"Could not find phase detail template directory. Tried:\n"
            f"  {base / 'cortex-registry'}\n"
            f"  {Path.cwd() / 'cortex-registry'}"
        )

    def load_template(self, template_path: Optional[Path] = None) -> str:
        """
        Load template content from file.

        Args:
            template_path: Path to template file (default: auto-discover)

        Returns:
            Template content as string
        """
        if template_path is None:
            template_path = self.template_dir / self.DEFAULT_TEMPLATE_NAME

        return template_path.read_text(encoding="utf-8")

    def render(
        self,
        phase_data: PhaseDetail,
        template_name: Optional[str] = None
    ) -> str:
        """
        Render phase detail HTML from data.

        Args:
            phase_data: PhaseDetail model with all data
            template_name: Template filename (default: phase-detail.html)

        Returns:
            Rendered HTML string

        Examples:
            >>> generator = PhaseDetailPageGenerator()
            >>> phase = PhaseDetail(phase_id="PHASE-21", title="JSON-First", ...)
            >>> html = generator.render(phase)
            >>> assert "JSON-First" in html
        """
        if template_name is None:
            template_name = self.DEFAULT_TEMPLATE_NAME

        template = self.env.get_template(template_name)

        # Convert to template context
        context = phase_data.to_html_context()

        # Add helper functions to context
        context['generator_version'] = self.VERSION
        context['get_status_class'] = self._get_status_class
        context['format_percentage'] = self._format_percentage

        return template.render(**context)

    def generate(
        self,
        phase_data: PhaseDetail,
        output_path: Path,
        template_name: Optional[str] = None
    ) -> Path:
        """
        Generate HTML file from phase data.

        Args:
            phase_data: PhaseDetail model
            output_path: Where to write HTML file
            template_name: Template filename (optional)

        Returns:
            Path to generated file

        Examples:
            >>> generator = PhaseDetailPageGenerator()
            >>> output = generator.generate(
            ...     phase_data,
            ...     Path("cortex-registry/_cortex-master/dashboard/phases/phase-21/index.html")
            ... )
            >>> assert output.exists()
        """
        html = self.render(phase_data, template_name)

        # Create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write HTML file
        output_path.write_text(html, encoding="utf-8")

        return output_path

    def generate_batch(
        self,
        phases: list[PhaseDetail],
        output_dir: Path,
        template_name: Optional[str] = None
    ) -> list[Path]:
        """
        Generate multiple phase detail pages.

        Args:
            phases: List of PhaseDetail models
            output_dir: Base directory for phase pages
            template_name: Template filename (optional)

        Returns:
            List of generated file paths

        Examples:
            >>> generator = PhaseDetailPageGenerator()
            >>> phases = [phase1, phase2, phase3]
            >>> paths = generator.generate_batch(
            ...     phases,
            ...     Path("cortex-registry/_cortex-master/dashboard/phases")
            ... )
            >>> assert len(paths) == 3
        """
        generated = []

        for phase in phases:
            # Extract phase number from phase_id (e.g., "PHASE-21" -> "21")
            phase_num = phase.phase_id.split("-")[1] if "-" in phase.phase_id else phase.phase_id
            output_path = output_dir / f"phase-{phase_num}" / "index.html"

            path = self.generate(phase, output_path, template_name)
            generated.append(path)

        return generated

    @staticmethod
    def _get_status_class(status: str) -> str:
        """
        Get CSS class for status badge.

        Args:
            status: Phase status string

        Returns:
            CSS class name
        """
        status_map = {
            "ACTIVE": "badge-active",
            "COMPLETED": "badge-completed",
            "PLANNED": "badge-planned"
        }
        return status_map.get(status.upper(), "badge-default")

    @staticmethod
    def _format_percentage(value: float) -> str:
        """
        Format float as percentage string.

        Args:
            value: Float between 0 and 1

        Returns:
            Formatted percentage (e.g., "92%")
        """
        return f"{int(value * 100)}%"
