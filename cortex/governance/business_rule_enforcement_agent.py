"""
cortex/governance/business_rule_enforcement_agent.py

BusinessRuleEnforcementAgent — Enforcement agent for extracted business rules (Phase 84-b, GAP-84-04).

Loads business rules from YAML and validates proposed changes against them.
Integrated into EnforcementOrchestrator as agent #10.

Authority: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (no duplicates)
AC_START: AC-84-B-BUSINESS-RULE-ENFORCEMENT-2026-02-26
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_RULES_PATH = Path("cortex-registry/company/domains/shared/business-rules.yaml")


class BusinessRuleEnforcementAgent:
    """
    Enforcement agent that validates changes against extracted business rules.

    Loads rules from business-rules.yaml and checks proposed changes for violations.
    Integrates into EnforcementOrchestrator as an additional enforcement agent (GAP-84-04).

    Example::

        agent = BusinessRuleEnforcementAgent()
        result = agent.enforce_change("Set price to -5")
        if not result['allowed']:
            print(result['violations'])
    """

    def __init__(
        self,
        rules_path: Optional[Path] = None,
    ) -> None:
        """
        Initialise the enforcement agent.

        Args:
            rules_path: Path to business-rules.yaml. Falls back to default location.
        """
        self._rules_path: Path = rules_path or _DEFAULT_RULES_PATH
        self._rules: List[Dict[str, Any]] = []
        self.load_rules()

    def load_rules(self) -> None:
        """
        Load business rules from the YAML backing file.

        Silently returns empty rule set if file does not exist.
        """
        if not self._rules_path.exists():
            self._rules = []
            return
        try:
            data = yaml.safe_load(self._rules_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._rules = data.get("rules", [])
            elif isinstance(data, list):
                self._rules = data
            else:
                self._rules = []
        except Exception as exc:
            logger.warning("BusinessRuleEnforcementAgent: failed to load rules — %s", exc)
            self._rules = []

    def enforce_change(self, change_description: str) -> Dict[str, Any]:
        """
        Validate a proposed change against all loaded business rules.

        Args:
            change_description: Human-readable description of the proposed change.

        Returns:
            Dict with:
                allowed (bool): True if no violations detected.
                violations (list): List of violated rule descriptions.
                rules_checked (int): Number of rules evaluated.
        """
        if not self._rules:
            return {"allowed": True, "violations": [], "rules_checked": 0}

        violations: List[str] = []
        change_lower = change_description.lower()

        for rule in self._rules:
            description = rule.get("description", "").lower()
            field = rule.get("field", "").lower()
            # Simple heuristic: if a change mentions a field and appears to violate it
            if field and field in change_lower:
                if self._appears_to_violate(change_lower, description):
                    violations.append(
                        f"Rule violation on '{rule.get('field')}': {rule.get('description')}"
                    )

        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "rules_checked": len(self._rules),
        }

    # ── Private helpers ──────────────────────────────────────────────────────

    def _appears_to_violate(self, change: str, rule_description: str) -> bool:
        """
        Heuristic check: does the change appear to violate the rule?

        Looks for numeric negation patterns (negative values, zero) when the rule
        says "positive", "must be > 0", etc.

        Args:
            change: Lower-cased change description.
            rule_description: Lower-cased rule description.

        Returns:
            True if the change likely violates the rule.
        """
        if "positive" in rule_description or "> 0" in rule_description:
            # Flag changes that explicitly set a negative value
            if re.search(r"to\s*-\d+", change) or re.search(r"=\s*-\d+", change):
                return True
        if "must contain @" in rule_description or "email" in rule_description:
            if "remove @" in change or "no @" in change:
                return True
        if "minimum" in rule_description:
            match = re.search(r"to\s*(\d+(?:\.\d+)?)", change)
            if match:
                minimum_match = re.search(r"\$?(\d+(?:\.\d+)?)", rule_description)
                if minimum_match:
                    try:
                        if float(match.group(1)) < float(minimum_match.group(1)):
                            return True
                    except ValueError:
                        pass
        return False
