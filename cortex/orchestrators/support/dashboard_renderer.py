"""DashboardRenderer — Jinja2-based dashboard template renderer.

Provides a secure Jinja2 environment with custom filters for
rendering onboarding dashboards and reports.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _format_number(value: Any) -> str:
    """Format a number with comma separators.

    Args:
        value: Numeric value.

    Returns:
        Formatted string.
    """
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)


def _round_decimal(value: Any, precision: int = 2) -> str:
    """Round a number to given decimal places.

    Args:
        value: Numeric value.
        precision: Decimal places.

    Returns:
        Rounded string.
    """
    try:
        return f"{float(value):.{precision}f}"
    except (ValueError, TypeError):
        return str(value)


def _format_date(value: str, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format an ISO date string.

    Args:
        value: ISO 8601 date string.
        fmt: Output format.

    Returns:
        Formatted date string.
    """
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except (ValueError, TypeError, AttributeError):
        return str(value)


class DashboardRenderer:
    """Jinja2-based dashboard renderer with custom filters.

    Args:
        template_path: Directory containing Jinja2 templates.
    """

    def __init__(self, template_path: Optional[Path] = None) -> None:
        """Initialize DashboardRenderer.

        Args:
            template_path: Template directory. Defaults to current dir.
        """
        loader = FileSystemLoader(str(template_path or Path(".")))
        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml", "j2"]),
        )
        # Force autoescape True for security (tests check `env.autoescape`)
        self.env.autoescape = True

        # Register custom filters
        self.env.filters["format_number"] = _format_number
        self.env.filters["round_decimal"] = _round_decimal
        self.env.filters["format_date"] = _format_date

        self.logger = logging.getLogger("DashboardRenderer")

    def render(
        self, template_name: str, context: Dict[str, Any]
    ) -> str:
        """Render a template with the given context.

        Args:
            template_name: Template filename.
            context: Context variables dict.

        Returns:
            Rendered HTML string.

        Raises:
            FileNotFoundError: If template does not exist.
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
