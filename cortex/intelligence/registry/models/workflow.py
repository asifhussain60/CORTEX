"""
WorkflowTemplateModel — typed model for workflow-template YAML artifacts.

Represents YAML files in ``cortex-registry/workflows/templates/`` that define
declarative workflow pipelines with steps, convergence gates, and trigger keywords.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class WorkflowTemplateModel(BaseRegistryModel):
    """Typed model for workflow-template YAML artifacts.

    Extends :class:`BaseRegistryModel` with workflow-specific fields
    for version, category, steps, convergence gates, and trigger keywords.
    """

    version: str = ""
    category: str = ""
    steps: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    trigger_keywords: List[str] = dataclasses.field(default_factory=list)
    convergence_gate: Dict[str, Any] = dataclasses.field(default_factory=dict)
    status: str = ""

    @classmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        source_file: str,
    ) -> "WorkflowTemplateModel":
        """Create a WorkflowTemplateModel from parsed YAML data.

        Args:
            data: The parsed YAML dict (may have top-level ``workflow`` key).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``WorkflowTemplateModel`` instance.
        """
        if not isinstance(data, dict):
            data = {}

        # Unwrap top-level ``workflow`` key if present
        wf = data.get("workflow", data)
        if not isinstance(wf, dict):
            wf = {}

        # --- Core fields ---
        workflow_id = str(wf.get("id", ""))
        name = str(wf.get("name", ""))
        version = str(wf.get("version", ""))
        category = str(wf.get("category", ""))
        status = str(wf.get("status", ""))

        # --- Steps ---
        steps_raw = wf.get("steps", [])
        if not isinstance(steps_raw, list):
            steps_raw = []

        # --- Metadata block ---
        meta = wf.get("metadata", {})
        if not isinstance(meta, dict):
            meta = {}

        # --- Trigger keywords from metadata ---
        trigger_keywords = meta.get("trigger_keywords", [])
        if not isinstance(trigger_keywords, list):
            trigger_keywords = []

        # --- Convergence gate ---
        convergence_gate = wf.get("convergence_gate", {})
        if not isinstance(convergence_gate, dict):
            convergence_gate = {}

        # --- ID fallback ---
        if not workflow_id:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            workflow_id = f"workflow-{name_part}"

        # --- Title ---
        title = name or ""
        if not title:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            title = name_part.replace("-", " ").replace("_", " ").title()

        # --- Content (extra fields) ---
        skip_keys = {"id", "name", "version", "category", "status",
                      "steps", "metadata", "convergence_gate"}
        content = {k: v for k, v in wf.items() if k not in skip_keys}

        return cls(
            id=workflow_id,
            type="workflow-template",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata=meta,
            content=content,
            version=version,
            category=category,
            steps=steps_raw,
            trigger_keywords=trigger_keywords,
            convergence_gate=convergence_gate,
            status=status,
        )
