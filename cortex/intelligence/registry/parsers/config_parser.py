"""
ConfigParser — parses configuration YAML into ConfigModel.

Handles YAML files from ``cortex-registry/config/`` that define
system configuration, architecture constants, and file naming rules.
"""

from __future__ import annotations

from typing import Any

from cortex.intelligence.registry.models.config import ConfigModel
from cortex.intelligence.registry.parsers import register_parser


@register_parser("config")
class ConfigParser:
    """Typed parser for configuration schema YAML files.

    Produces a :class:`ConfigModel` with field-level extraction for
    config sections, version, and scope.
    """

    def parse(self, data: Any, source_file: str) -> ConfigModel:
        """Parse raw YAML data into a ConfigModel.

        Args:
            data: Parsed YAML data (expected to be a config dict).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``ConfigModel`` instance.
        """
        return ConfigModel.from_data(data=data, source_file=source_file)
