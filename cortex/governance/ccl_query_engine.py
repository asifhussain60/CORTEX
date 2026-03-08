"""CCLQueryEngine — Convergence Crystal Language governance query engine.

Translates CORE rule IDs (e.g. "CORE-008") into business-language impact
statements by querying ccl-governance-crystal.yaml. Supports audience-specific
translations and multi-violation markdown rendering.

Authority: CORE-061 (CCL Integration), CORE-011 (type hints), CORE-012 (docstrings)
Phase: 137 (GAP-137-01)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

__all__ = ["CCLQueryEngine"]

# ── Module-level crystal cache (singleton pattern — CORE-035) ─────────────────
_CRYSTAL_CACHE: Optional[Dict[str, Any]] = None
_CRYSTAL_PATH = (
    Path(__file__).resolve().parents[2]
    / "cortex-registry"
    / "core"
    / "ccl-governance-crystal.yaml"
)

_DEFAULT_TRANSLATION: Dict[str, Any] = {
    "business_term": "governance_compliance",
    "principle": "Governance Rule",
    "business_statement": (
        "This rule enforces a governance standard that maintains system quality and consistency."
    ),
    "business_audience": [],
    "alignment": "Reduces risk and improves maintainability",
}


def _load_crystal() -> Dict[str, Any]:
    """Load and cache ccl-governance-crystal.yaml (CORE-035: load once).

    Returns:
        Parsed YAML dict — the full crystal document.
    """
    global _CRYSTAL_CACHE
    if _CRYSTAL_CACHE is None:
        try:
            _CRYSTAL_CACHE = yaml.safe_load(_CRYSTAL_PATH.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.warning("CCLQueryEngine: failed to load crystal YAML — %s", exc)
            _CRYSTAL_CACHE = {}
    return _CRYSTAL_CACHE


def _get_governance_rules(crystal: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the governance rules section from the crystal document.

    The CCL crystal uses ``rule_mappings`` as the top-level key for CORE rules.

    Args:
        crystal: Full parsed crystal YAML dict.

    Returns:
        Dict of {rule_id: rule_dict} entries.
    """
    return crystal.get("rule_mappings", crystal.get("governance_rules", {}))


class CCLQueryEngine:
    """Query engine for CCL (Convergence Crystal Language) governance crystal.

    Provides business-language translations of CORE governance rule IDs.
    Reads from ``ccl-governance-crystal.yaml`` (cached after first load).

    Usage::

        engine = CCLQueryEngine()
        translation = engine.translate_violation("CORE-008")
        md = engine.render_business_impact(["CORE-008", "CORE-035"])
        all_rules = engine.get_all_rules()
    """

    def translate_violation(self, rule_id: str) -> Dict[str, Any]:
        """Translate a CORE rule ID to a business-language dict.

        Args:
            rule_id: Governance rule identifier (e.g. ``"CORE-008"``).

        Returns:
            Dict with keys:
              - ``rule_id`` — the input rule ID
              - ``business_term`` — short CCL term
              - ``business_statement`` — plain-language business statement
              - ``business_audience`` — list of audience strings
              - ``alignment`` — strategic alignment note (may be empty)
        """
        crystal = _load_crystal()
        rules = _get_governance_rules(crystal)
        rule_data = rules.get(rule_id, {})

        if not rule_data:
            # Graceful default — no KeyError (CORE-035: null-object pattern)
            return {
                "rule_id": rule_id,
                "business_term": _DEFAULT_TRANSLATION["business_term"],
                "business_statement": _DEFAULT_TRANSLATION["business_statement"],
                "business_audience": _DEFAULT_TRANSLATION["business_audience"],
                "alignment": _DEFAULT_TRANSLATION["alignment"],
            }

        return {
            "rule_id": rule_id,
            "business_term": rule_data.get(
                "business_term", _DEFAULT_TRANSLATION["business_term"]
            ),
            "business_statement": rule_data.get(
                "business_statement", _DEFAULT_TRANSLATION["business_statement"]
            ),
            "business_audience": rule_data.get("business_audience", []),
            "alignment": rule_data.get("alignment", ""),
        }

    def get_audience_for_rule(self, rule_id: str) -> List[str]:
        """Return the list of target business audiences for a CORE rule.

        Args:
            rule_id: Governance rule identifier (e.g. ``"CORE-008"``).

        Returns:
            List of audience strings. Empty list for unknown rule IDs.
        """
        translation = self.translate_violation(rule_id)
        return translation.get("business_audience", [])

    def render_business_impact(self, rule_ids: List[str]) -> str:
        """Render a markdown-formatted business impact report for multiple violations.

        Args:
            rule_ids: List of CORE rule IDs to render (e.g. ``["CORE-008", "CORE-035"]``).

        Returns:
            Markdown string with one section per violation.
        """
        if not rule_ids:
            return ""

        lines: List[str] = ["## Business Impact Assessment\n"]
        for rule_id in rule_ids:
            trans = self.translate_violation(rule_id)
            lines.append(f"### {rule_id} — {trans['business_term']}")
            lines.append(f"{trans['business_statement']}")
            audience = trans.get("business_audience", [])
            if audience:
                lines.append(f"**Audience:** {', '.join(audience)}")
            alignment = trans.get("alignment", "")
            if alignment:
                lines.append(f"**Strategic Alignment:** {alignment}")
            lines.append("")  # blank line between sections

        return "\n".join(lines)

    def get_all_rules(self) -> List[str]:
        """Return a sorted list of all CORE rule IDs in the crystal.

        Returns:
            Sorted list of rule ID strings (e.g. ``["CORE-008", "CORE-011", ...]``).
        """
        crystal = _load_crystal()
        rules = _get_governance_rules(crystal)
        return sorted(rules.keys())
