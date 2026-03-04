"""
WorkflowTemplateParser — parses workflow YAML into WorkflowTemplateModel.

Handles YAML files from ``cortex-registry/workflows/templates/`` that
define declarative workflow pipelines with steps, convergence gates,
and trigger keywords.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.workflow import WorkflowTemplateModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("workflow-template")
class WorkflowTemplateParser:
    """Typed parser for workflow-template schema YAML files.

    Produces a :class:`WorkflowTemplateModel` with field-level extraction
    for version, category, steps, convergence gates, and trigger keywords.
    """

    def parse(self, data: Any, source_file: str) -> WorkflowTemplateModel:
        """Parse raw YAML data into a WorkflowTemplateModel.

        Args:
            data: Parsed YAML data (expected to have a ``workflow`` key).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``WorkflowTemplateModel`` instance.
        """
        return WorkflowTemplateModel.from_data(data=data, source_file=source_file)
