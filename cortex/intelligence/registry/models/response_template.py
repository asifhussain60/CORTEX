"""
ResponseTemplateModel — typed model for response-template YAML artifacts.

Represents YAML files that define composable response blocks, quote
libraries, and formatting standards.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class ResponseTemplateModel(BaseRegistryModel):
    """Typed model for response-template YAML artifacts.

    Extends :class:`BaseRegistryModel` with template-specific fields
    for blocks, zones, and composable sections.
    """

    template_version: str = ""
    blocks: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    zones: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    composable_sections: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        source_file: str,
    ) -> "ResponseTemplateModel":
        """Create a ResponseTemplateModel from parsed YAML data.

        Args:
            data: The parsed YAML dict.
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``ResponseTemplateModel`` instance.
        """
        if not isinstance(data, dict):
            data = {}

        # --- Core fields ---
        template_id = str(data.get("id", "") or data.get("name", "") or "")
        template_version = str(data.get("version", "") or data.get("schema_version", "") or "")

        # --- Blocks ---
        blocks = data.get("blocks", [])
        if not isinstance(blocks, list):
            blocks = []

        # --- Zones ---
        zones = data.get("zones", [])
        if not isinstance(zones, list):
            zones = []

        # --- Composable sections ---
        composable_sections = data.get("composable_sections", [])
        if not isinstance(composable_sections, list):
            composable_sections = []

        # --- ID fallback ---
        if not template_id:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            template_id = f"template-{name_part}"

        # --- Title ---
        title = str(data.get("title", "") or data.get("name", "") or "")
        if not title:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            title = name_part.replace("-", " ").replace("_", " ").title()

        # --- Content ---
        skip_keys = {"id", "title", "name", "version", "schema_version",
                      "blocks", "zones", "composable_sections"}
        content = {k: v for k, v in data.items() if k not in skip_keys}

        return cls(
            id=template_id,
            type="response-template",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata={},
            content=content,
            template_version=template_version,
            blocks=blocks,
            zones=zones,
            composable_sections=composable_sections,
        )
