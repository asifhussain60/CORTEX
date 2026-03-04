"""
PatternModel — typed model for enterprise pattern YAML artifacts.

Represents YAML files in ``cortex-registry/patterns/`` that document
design patterns (GoF and CORTEX-specific) used across the codebase.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class PatternModel(BaseRegistryModel):
    """Typed model for enterprise pattern YAML artifacts.

    Extends :class:`BaseRegistryModel` with pattern-specific fields
    for pattern type, participants, usage, and anti-patterns.
    """

    pattern_name: str = ""
    pattern_type: str = ""
    description: str = ""
    cortex_usage: List[str] = dataclasses.field(default_factory=list)
    participants: Dict[str, Any] = dataclasses.field(default_factory=dict)
    when_to_use: List[str] = dataclasses.field(default_factory=list)
    anti_patterns: List[str] = dataclasses.field(default_factory=list)
    file_references: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        source_file: str,
    ) -> "PatternModel":
        """Create a PatternModel from parsed YAML data.

        Args:
            data: The parsed YAML dict (may have top-level ``pattern`` key).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``PatternModel`` instance.
        """
        if not isinstance(data, dict):
            data = {}

        # Unwrap top-level ``pattern`` key if present
        pat = data.get("pattern", data)
        if not isinstance(pat, dict):
            pat = {}

        # --- Core fields ---
        pattern_name = str(pat.get("name", ""))
        pattern_type = str(pat.get("type", ""))
        description = str(pat.get("description", "")).strip()

        # --- Lists ---
        cortex_usage = pat.get("cortex_usage", [])
        if not isinstance(cortex_usage, list):
            cortex_usage = []

        when_to_use = pat.get("when_to_use", [])
        if not isinstance(when_to_use, list):
            when_to_use = []

        anti_patterns = pat.get("anti_patterns", [])
        if not isinstance(anti_patterns, list):
            anti_patterns = []

        file_references = pat.get("references", [])
        if not isinstance(file_references, list):
            file_references = []

        # --- Participants ---
        participants = pat.get("participants", {})
        if not isinstance(participants, dict):
            participants = {}

        # --- ID ---
        artifact_id = str(pat.get("id", ""))
        if not artifact_id:
            # Derive from pattern name or filename
            if pattern_name:
                artifact_id = pattern_name.lower().replace(" ", "-")
            else:
                basename = os.path.basename(source_file)
                name_part = os.path.splitext(basename)[0]
                artifact_id = f"pattern-{name_part}"

        # --- Title ---
        title = pattern_name or ""
        if not title:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            title = name_part.replace("-", " ").replace("_", " ").title()

        # --- Content (extra fields) ---
        skip_keys = {"name", "type", "description", "cortex_usage", "participants",
                      "when_to_use", "anti_patterns", "references", "id"}
        content = {k: v for k, v in pat.items() if k not in skip_keys}

        return cls(
            id=artifact_id,
            type="pattern",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata={},
            content=content,
            pattern_name=pattern_name,
            pattern_type=pattern_type,
            description=description,
            cortex_usage=cortex_usage,
            participants=participants,
            when_to_use=when_to_use,
            anti_patterns=anti_patterns,
            file_references=file_references,
        )
