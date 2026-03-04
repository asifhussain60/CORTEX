"""
GenericModel — fallback model for YAML artifacts with no dedicated parser.

Every YAML that doesn't match a known schema type gets a GenericModel with
schema_warning=True. This ensures the viewer NEVER shows a blank or error
state — it always renders a structured view with a warning banner.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class GenericModel(BaseRegistryModel):
    """Fallback model for unrecognized YAML schemas.

    Wraps the raw parsed data and sets schema_warning=True so the viewer
    can display a warning banner while still rendering structured content.
    """

    raw_data: Any = None
    schema_warning: bool = True

    @classmethod
    def from_data(
        cls,
        data: Any,
        source_file: str,
    ) -> "GenericModel":
        """Create a GenericModel from raw parsed YAML data.

        Args:
            data: The parsed YAML data (dict, list, scalar, or None).
            source_file: Path to the source YAML file.

        Returns:
            A GenericModel instance with all fields populated.
        """
        # Extract ID from data if available
        artifact_id = ""
        if isinstance(data, dict):
            artifact_id = str(
                data.get("id", "")
                or data.get("name", "")
                or ""
            )

        # Derive from filename if no ID in data
        if not artifact_id:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            artifact_id = f"generic-{name_part}"

        # Extract title
        title = ""
        if isinstance(data, dict):
            title = str(
                data.get("title", "")
                or data.get("name", "")
                or data.get("description", "")
                or ""
            )
        if not title:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            title = name_part.replace("-", " ").replace("_", " ").title()

        # Build content from data
        content: Dict[str, Any] = {}
        if isinstance(data, dict):
            content = {k: v for k, v in data.items() if k not in ("id", "title", "name")}
        elif data is not None:
            content = {"raw_value": data}

        return cls(
            id=artifact_id,
            type="generic",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata={},
            content=content,
            raw_data=data,
            schema_warning=True,
        )
