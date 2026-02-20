"""
Tier1Injector — injects project-specific tier-1 governance rules.

Authority: CORE-035 (single canonical implementation)
AC-ID: AC-DEP-004-02
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "finops": {
        "profile": "finops",
        "rules": ["FIN-001", "FIN-002", "FIN-003", "AUDIT-001"],
        "description": "Financial operations governance profile",
    },
    "auth": {
        "profile": "auth",
        "rules": ["AUTH-001", "AUTH-002", "SEC-001", "SEC-002"],
        "description": "Authentication & session governance profile",
    },
    "general": {
        "profile": "general",
        "rules": ["GEN-001"],
        "description": "General purpose governance profile",
    },
}

# Tier-0 rule prefixes that must not be overridden
_TIER0_PREFIXES = ("CORE-",)


class Tier1Injector:
    """Loads profile templates and injects tier-1 governance rules into projects.

    Tier-0 rules (CORE-*) cannot be overridden by any tier-1 profile.
    """

    def __init__(self) -> None:
        """Initialise the injector."""
        self._custom_templates: Dict[str, Dict[str, Any]] = {}

    # ── Public API ───────────────────────────────────────────────────

    def inject_tier1(
        self,
        project_path: str,
        project_type: str = "general",
    ) -> Dict[str, Any]:
        """Load and return the tier-1 profile for a project.

        Args:
            project_path: Absolute path to the project directory.
            project_type: Profile type (``"finops"``, ``"auth"``, …).

        Returns:
            Profile dict with ``profile`` and ``rules`` keys.
        """
        return self._load_template(project_type)

    def get_template(self, project_type: str) -> Dict[str, Any]:
        """Return the governance template for a given project type.

        Args:
            project_type: Profile key (e.g. ``"finops"``).

        Returns:
            Template dict (falls back to ``"general"`` if not found).
        """
        if project_type in self._custom_templates:
            return dict(self._custom_templates[project_type])
        return dict(_TEMPLATES.get(project_type, _TEMPLATES["general"]))

    def validate_tier0_compatibility(
        self,
        tier1_rules: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check that tier-1 rules do not attempt to override tier-0.

        Args:
            tier1_rules: Dict with a ``"rules"`` list.

        Returns:
            Result dict with ``compatible`` (bool) and optional ``conflicts`` list.
        """
        rules = tier1_rules.get("rules", [])
        violations = [
            r for r in rules
            if any(r.startswith(prefix) for prefix in _TIER0_PREFIXES)
            and "override" in r.lower()
        ]
        if violations:
            return {"compatible": False, "conflicts": violations}
        return {"compatible": True, "conflicts": []}

    def detect_conflicts(self, rules: Dict[str, Any]) -> List[str]:
        """Detect conflicting rules within a rule set.

        Two rules conflict when they share a base ID but carry opposing
        suffixes (e.g. ``RULE-001-allow`` and ``RULE-001-deny``).

        Args:
            rules: Dict with a ``"rules"`` list.

        Returns:
            List of conflicting rule identifiers (empty if none).
        """
        rule_list = rules.get("rules", [])
        conflicts: List[str] = []
        for rule in rule_list:
            base = re.sub(r"-(allow|deny)$", "", rule, flags=re.IGNORECASE)
            if base != rule:
                opposite = "deny" if rule.endswith("-allow") else "allow"
                opposite_rule = f"{base}-{opposite}"
                if opposite_rule in rule_list:
                    if rule not in conflicts:
                        conflicts.append(rule)
                    if opposite_rule not in conflicts:
                        conflicts.append(opposite_rule)
        return conflicts

    # ── Internal helpers ─────────────────────────────────────────────

    def _load_template(self, project_type: str) -> Dict[str, Any]:
        """Load template dict for a project type.

        Args:
            project_type: Profile key.

        Returns:
            Template dict.
        """
        return self.get_template(project_type)
