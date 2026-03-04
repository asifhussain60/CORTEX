"""
GovernanceRuleModel — typed model for governance-rule YAML artifacts.

Represents YAML files in ``cortex-registry/core/`` and
``cortex-registry/governance/`` that define CORE rules, enforcement
policies, and compliance requirements.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class GovernanceRuleModel(BaseRegistryModel):
    """Typed model for governance-rule YAML artifacts.

    Extends :class:`BaseRegistryModel` with governance-specific fields
    for domain, category, severity, enforcement mode, and individual rules.
    """

    domain: str = ""
    category: str = ""
    severity: str = ""
    enforcement_mode: str = ""
    rules: List[Dict[str, Any]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        source_file: str,
    ) -> "GovernanceRuleModel":
        """Create a GovernanceRuleModel from parsed YAML data.

        Args:
            data: The parsed YAML dict.
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``GovernanceRuleModel`` instance.
        """
        if not isinstance(data, dict):
            data = {}

        # --- Extract fields ---
        domain = str(data.get("domain", ""))
        category = str(data.get("category", ""))
        rules_raw: List[Dict[str, Any]] = data.get("rules", [])
        if not isinstance(rules_raw, list):
            rules_raw = []

        # Enforcement mode from meta block or top-level
        meta = data.get("meta", {})
        if isinstance(meta, dict):
            enforcement_mode = str(meta.get("enforcement_mode", ""))
        else:
            enforcement_mode = ""
        if not enforcement_mode:
            enforcement_mode = str(data.get("enforcement_mode", ""))

        # Severity: top-level > max rule severity
        severity = str(data.get("severity", ""))
        if not severity and rules_raw:
            severities = [str(r.get("severity", "")) for r in rules_raw if isinstance(r, dict)]
            severities = [s for s in severities if s]
            if severities:
                severity = severities[0]

        # --- ID ---
        artifact_id = str(data.get("id", "") or data.get("name", "") or "")
        if not artifact_id:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            artifact_id = f"governance-{name_part}"

        # --- Title ---
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

        # --- Content (everything except extracted top-level keys) ---
        skip_keys = {"id", "title", "name", "domain", "category", "rules",
                      "severity", "enforcement_mode", "meta"}
        content = {k: v for k, v in data.items() if k not in skip_keys}

        return cls(
            id=artifact_id,
            type="governance-rule",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata=meta if isinstance(meta, dict) else {},
            content=content,
            domain=domain,
            category=category,
            severity=severity,
            enforcement_mode=enforcement_mode,
            rules=rules_raw,
        )
