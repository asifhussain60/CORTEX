"""
ConfigModel — typed model for configuration YAML artifacts.

Represents YAML files in ``cortex-registry/config/`` that define
system configuration, architecture constants, and file naming rules.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class ConfigModel(BaseRegistryModel):
    """Typed model for configuration YAML artifacts.

    Extends :class:`BaseRegistryModel` with config-specific fields for
    config sections, version, and scope.
    """

    config_version: str = ""
    scope: str = ""
    sections: Dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        source_file: str,
    ) -> "ConfigModel":
        """Create a ConfigModel from parsed YAML data.

        Args:
            data: The parsed YAML dict.
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``ConfigModel`` instance.
        """
        if not isinstance(data, dict):
            data = {}

        # --- Core fields ---
        config_id = str(data.get("repo_id", "") or data.get("id", "") or data.get("name", "") or "")
        config_version = str(data.get("version", ""))
        scope = str(data.get("scope", "") or data.get("repo_type", "") or "")

        # --- ID fallback ---
        if not config_id:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            config_id = f"config-{name_part}"

        # --- Title ---
        title = str(data.get("title", "") or data.get("description", "") or data.get("name", "") or "")
        if not title:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            title = name_part.replace("-", " ").replace("_", " ").title()

        # --- Sections: top-level dict keys that are themselves dicts ---
        skip_keys = {"id", "title", "name", "version", "scope", "description",
                      "repo_id", "repo_name", "repo_type"}
        sections: Dict[str, Any] = {}
        content: Dict[str, Any] = {}
        for k, v in data.items():
            if k in skip_keys:
                continue
            if isinstance(v, dict):
                sections[k] = v
            else:
                content[k] = v

        return cls(
            id=config_id,
            type="config",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata={},
            content=content,
            config_version=config_version,
            scope=scope,
            sections=sections,
        )
