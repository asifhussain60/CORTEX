"""
GenericParser — parses any YAML into a GenericModel.

This is the fallback parser used when no dedicated parser is registered
for a given schema type. It guarantees that every YAML file produces
a valid, renderable model — no blank or error states.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.generic import GenericModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("generic")
class GenericParser:
    """Fallback parser that wraps any YAML data in a GenericModel.

    The GenericModel carries ``schema_warning=True`` so the viewer
    can display a "no typed parser" banner while still rendering
    structured content.
    """

    def parse(self, data: Any, source_file: str) -> GenericModel:
        """Parse raw YAML data into a GenericModel.

        Args:
            data: Parsed YAML data (dict, list, scalar, or None).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``GenericModel`` instance.
        """
        return GenericModel.from_data(data=data, source_file=source_file)
