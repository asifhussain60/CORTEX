"""
GovernanceRuleParser — parses governance YAML into GovernanceRuleModel.

Handles YAML files from ``cortex-registry/core/`` and
``cortex-registry/governance/`` that contain governance rules with
enforcement policies, severity levels, and compliance requirements.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.governance import GovernanceRuleModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("governance-rule")
class GovernanceRuleParser:
    """Typed parser for governance-rule schema YAML files.

    Produces a :class:`GovernanceRuleModel` with field-level extraction
    for domain, category, severity, enforcement mode, and individual rules.
    """

    def parse(self, data: Any, source_file: str) -> GovernanceRuleModel:
        """Parse raw YAML data into a GovernanceRuleModel.

        Args:
            data: Parsed YAML data (expected to be a dict with ``rules`` key).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``GovernanceRuleModel`` instance.
        """
        return GovernanceRuleModel.from_data(data=data, source_file=source_file)
