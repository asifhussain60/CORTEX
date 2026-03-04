"""
PlanModel — typed model for phase-plan YAML artifacts.

Represents YAML files in ``cortex-registry/planning/phases/`` that define
development phases with gap catalogues, sub-phases, TDD cycles, and
acceptance criteria.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class PlanModel(BaseRegistryModel):
    """Typed model for phase-plan YAML artifacts.

    Extends :class:`BaseRegistryModel` with plan-specific fields for
    status, priority, phases, gap catalogue, and acceptance criteria.
    """

    version: str = ""
    status: str = ""
    priority: str = ""
    phases: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    sweep_catalogue: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    acceptance_criteria: List[str] = dataclasses.field(default_factory=list)
    depends_on: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        source_file: str,
    ) -> "PlanModel":
        """Create a PlanModel from parsed YAML data.

        Args:
            data: The parsed YAML dict.
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``PlanModel`` instance.
        """
        if not isinstance(data, dict):
            data = {}

        # --- Core fields ---
        plan_id = str(data.get("id", ""))
        title = str(data.get("title", ""))
        version = str(data.get("version", ""))
        status = str(data.get("status", ""))
        priority = str(data.get("priority", ""))

        # --- Lists ---
        phases = data.get("phases", [])
        if not isinstance(phases, list):
            phases = []

        sweep_catalogue = data.get("sweep_catalogue", [])
        if not isinstance(sweep_catalogue, list):
            sweep_catalogue = []

        acceptance_criteria = data.get("acceptance_criteria", [])
        if not isinstance(acceptance_criteria, list):
            acceptance_criteria = []

        depends_on = data.get("depends_on", [])
        if not isinstance(depends_on, list):
            depends_on = []

        # --- ID fallback ---
        if not plan_id:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            plan_id = f"plan-{name_part}"

        # --- Title fallback ---
        if not title:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            title = name_part.replace("-", " ").replace("_", " ").title()

        # --- Metadata ---
        governance_authority = data.get("governance_authority", [])
        meta: Dict[str, Any] = {}
        if isinstance(governance_authority, list):
            meta["governance_authority"] = governance_authority
        created = data.get("created", "")
        if created:
            meta["created"] = str(created)

        # --- Content (extra fields) ---
        skip_keys = {"id", "title", "version", "status", "priority", "phases",
                      "sweep_catalogue", "acceptance_criteria", "depends_on",
                      "governance_authority", "created"}
        content = {k: v for k, v in data.items() if k not in skip_keys}

        return cls(
            id=plan_id,
            type="plan",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata=meta,
            content=content,
            version=version,
            status=status,
            priority=priority,
            phases=phases,
            sweep_catalogue=sweep_catalogue,
            acceptance_criteria=acceptance_criteria,
            depends_on=depends_on,
        )
