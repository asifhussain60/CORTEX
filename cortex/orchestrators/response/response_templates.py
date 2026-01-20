"""Response Templates - Template management for responses.

Manages response templates for consistent formatting.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum


class TemplateType(Enum):
    """Template types."""

    STRUCTURED = "structured"
    FREEFORM = "freeform"
    HYBRID = "hybrid"
    CUSTOM = "custom"


@dataclass
class Template:
    """Response template.

    Attributes:
        template_id: Unique template identifier.
        name: Template name.
        template_type: Type of template.
        content: Template content.
        parameters: Required parameters.
    """

    template_id: str
    name: str
    template_type: TemplateType
    content: str
    parameters: List[str] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.parameters is None:
            self.parameters = []


class ResponseTemplates:
    """Manages response templates."""

    def __init__(self) -> None:
        """Initialize template manager."""
        self.templates: Dict[str, Template] = {}

    def register_template(self, template: Template) -> None:
        """Register a response template.

        Args:
            template: Template to register.
        """
        self.templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template.

        Args:
            template_id: Template ID.

        Returns:
            Template or None.
        """
        return self.templates.get(template_id)

    def render_template(
        self, template_id: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Render a template with parameters.

        Args:
            template_id: Template ID.
            parameters: Template parameters.

        Returns:
            Rendered content or None.
        """
        template = self.get_template(template_id)
        if not template:
            return None

        content = template.content
        if parameters:
            for key, value in parameters.items():
                content = content.replace(f"{{{key}}}", str(value))

        return content

    def get_templates_by_type(self, template_type: TemplateType) -> List[Template]:
        """Get templates by type.

        Args:
            template_type: Template type.

        Returns:
            List of templates.
        """
        return [t for t in self.templates.values() if t.template_type == template_type]


__all__ = [
    "ResponseTemplates",
    "Template",
    "TemplateType",
]
