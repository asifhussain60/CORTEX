"""
KnowledgeParser — parses knowledge-base YAML into KnowledgeModel.

Handles YAML files from ``cortex-registry/knowledge/`` that define
best-practice guides, knowledge indexes, and domain-specific references.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.knowledge import KnowledgeModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("knowledge")
class KnowledgeParser:
    """Typed parser for knowledge-base schema YAML files.

    Produces a :class:`KnowledgeModel` with field-level extraction for
    domains, guides, and keywords.
    """

    def parse(self, data: Any, source_file: str) -> KnowledgeModel:
        """Parse raw YAML data into a KnowledgeModel.

        Args:
            data: Parsed YAML data (expected to be a knowledge dict).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``KnowledgeModel`` instance.
        """
        return KnowledgeModel.from_data(data=data, source_file=source_file)
