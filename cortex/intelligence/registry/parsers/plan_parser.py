"""
PlanParser — parses phase-plan YAML into PlanModel.

Handles YAML files from ``cortex-registry/planning/phases/`` that define
development phases with gap catalogues, sub-phases, and acceptance criteria.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.plan import PlanModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("plan")
class PlanParser:
    """Typed parser for phase-plan schema YAML files.

    Produces a :class:`PlanModel` with field-level extraction for
    status, priority, phases, sweep catalogue, and acceptance criteria.
    """

    def parse(self, data: Any, source_file: str) -> PlanModel:
        """Parse raw YAML data into a PlanModel.

        Args:
            data: Parsed YAML data (expected to be a plan dict).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``PlanModel`` instance.
        """
        return PlanModel.from_data(data=data, source_file=source_file)
