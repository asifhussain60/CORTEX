"""
TemplateParser — parses response-template YAML into ResponseTemplateModel.

Handles YAML files that define composable response blocks, quote
libraries, and formatting standards.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.response_template import ResponseTemplateModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("response-template")
class TemplateParser:
    """Typed parser for response-template schema YAML files.

    Produces a :class:`ResponseTemplateModel` with field-level extraction
    for blocks, zones, and composable sections.
    """

    def parse(self, data: Any, source_file: str) -> ResponseTemplateModel:
        """Parse raw YAML data into a ResponseTemplateModel.

        Args:
            data: Parsed YAML data (expected to be a template dict).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``ResponseTemplateModel`` instance.
        """
        return ResponseTemplateModel.from_data(data=data, source_file=source_file)
