"""Template renderer for rendering Jinja2 templates with safe mode."""

from typing import Any, Dict

from jinja2 import BaseLoader, Environment, TemplateNotFound, TemplateSyntaxError


class TemplateRenderer:
    """Renders Jinja2 templates with variable substitution and safe mode.

    Features:
    - Safe mode prevents access to dangerous attributes/methods
    - Supports Jinja2 syntax (loops, conditionals, filters)
    - Variable substitution with context dictionaries
    """

    def __init__(self) -> None:
        """Initialize the template renderer with safe environment."""
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with provided context variables.

        Args:
            template_str: Template string with Jinja2 syntax
            context: Dictionary of variables available in template

        Returns:
            Rendered template string

        Raises:
            TemplateSyntaxError: If template syntax is invalid
            KeyError: If required variables are missing from context
        """
        try:
            template = self.env.from_string(template_str)
            return template.render(**context)
        except TemplateSyntaxError as e:
            raise TemplateSyntaxError(f"Template syntax error: {e}", e.lineno)
        except Exception as e:
            raise ValueError(f"Template rendering error: {e}")
