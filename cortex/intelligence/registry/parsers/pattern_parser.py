"""
PatternParser — parses pattern YAML into PatternModel.

Handles YAML files from ``cortex-registry/patterns/`` that document
enterprise design patterns (GoF and CORTEX-specific) used across
the codebase.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.pattern import PatternModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("pattern")
class PatternParser:
    """Typed parser for pattern schema YAML files.

    Produces a :class:`PatternModel` with field-level extraction for
    pattern type, participants, usage examples, and anti-patterns.
    """

    def parse(self, data: Any, source_file: str) -> PatternModel:
        """Parse raw YAML data into a PatternModel.

        Args:
            data: Parsed YAML data (expected to have a ``pattern`` key).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``PatternModel`` instance.
        """
        return PatternModel.from_data(data=data, source_file=source_file)
