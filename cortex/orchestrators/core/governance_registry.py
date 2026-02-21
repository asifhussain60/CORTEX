"""
Governance Registry - Manages governance gates and rules.

AC-BUGFIX-001: Missing governance_registry module
AC-P1-FIX-001: Real gate checking with rule evaluation

Provides:
- Singleton governance gate registry
- Rule registration and lookup by tier
- Gate checking against registered rules
- Tier 0 CORE rule pre-loading from YAML
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.core.core.interfaces import GovernanceRule
from cortex.core.core.result import Err, Ok, Result

logger = logging.getLogger(__name__)

# Intent types that require strict gate enforcement
_STRICT_INTENTS = {"IMPLEMENT", "FIX", "REFACTOR"}

# Default CORE rules loaded when YAML is unavailable
_FALLBACK_CORE_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "CORE-008",
        "name": "TDD Mandatory",
        "severity": "blocked",
        "tier": 0,
        "description": "Tests must be written BEFORE implementation code.",
        "category": "quality_gates",
    },
    {
        "rule_id": "CORE-011",
        "name": "Type Hints Mandatory",
        "severity": "blocked",
        "tier": 0,
        "description": "All parameters and return values must have type hints.",
        "category": "quality_gates",
    },
    {
        "rule_id": "CORE-012",
        "name": "Google-style Docstrings",
        "severity": "warning",
        "tier": 0,
        "description": "Google-style docstrings on all public functions/classes.",
        "category": "quality_gates",
    },
    {
        "rule_id": "CORE-013",
        "name": "No Bare Except",
        "severity": "blocked",
        "tier": 0,
        "description": "Specific exception handling only — no bare except.",
        "category": "quality_gates",
    },
]


class GovernanceRegistry:
    """
    Singleton registry for governance gates and rules.

    Manages gate registration, rule loading (tier 0 from YAML, tier 1/2
    registered at runtime), and gate checking that evaluates registered
    rules against an operation specification.
    """

    _instance: Optional["GovernanceRegistry"] = None

    def __init__(self) -> None:
        """Initialize governance registry with empty collections and load rules."""
        self.gates: Dict[str, Dict[str, Any]] = {}
        self.rules: List[Dict[str, Any]] = []
        self._tier0_rules: Dict[str, GovernanceRule] = {}
        self._initialized: bool = False
        # Auto-initialize on construction so rules are always available
        self.initialize()

    @classmethod
    def instance(cls: object) -> "GovernanceRegistry":
        """Get singleton instance.

        Returns:
            The singleton GovernanceRegistry instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls: object) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize(self) -> Result:
        """
        Initialize registry by loading tier 0 rules from YAML.

        Loads CORE rules from ``cortex_intelligence/tier0/governance/core-rules.yaml``.
        Falls back to a minimal built-in set if the file is missing.

        Returns:
            Ok(None) on success, Err on failure.
        """
        if self._initialized:
            return Ok(None)

        try:
            self._load_tier0_from_yaml()
            self._initialized = True
            return Ok(None)
        except Exception as exc:
            logger.warning("Tier 0 YAML load failed, using fallback rules: %s", exc)
            self._load_fallback_rules()
            self._initialized = True
            return Ok(None)

    def _load_tier0_from_yaml(self) -> None:
        """Load tier 0 rules from the governance YAML file."""
        yaml_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "cortex_intelligence"
            / "tier0"
            / "governance"
            / "core-rules.yaml"
        )
        if not yaml_path.exists():
            raise FileNotFoundError(f"Tier 0 YAML not found: {yaml_path}")

        with open(yaml_path, "r") as fh:
            content = yaml.safe_load(fh) or {}

        raw_rules = content.get("rules", [])
        if isinstance(raw_rules, list):
            for entry in raw_rules:
                rule_id = entry.get("rule_id", "")
                rule = GovernanceRule(
                    rule_id=rule_id,
                    name=entry.get("name", rule_id),
                    severity=entry.get("severity", "warning"),
                    tier=0,
                    description=entry.get("description", ""),
                )
                self._tier0_rules[rule_id] = rule
                # Also keep in the flat list for get_rules()
                self.rules.append({
                    "rule_id": rule_id,
                    "name": rule.name,
                    "severity": rule.severity,
                    "tier": 0,
                    "description": rule.description,
                    "category": entry.get("category", "general"),
                })

            logger.info(
                "Loaded %d tier 0 rules from YAML", len(self._tier0_rules)
            )
        elif isinstance(raw_rules, dict):
            for rule_id, entry in raw_rules.items():
                desc = entry if isinstance(entry, str) else str(entry)
                rule = GovernanceRule(
                    rule_id=rule_id,
                    name=rule_id,
                    severity="blocked",
                    tier=0,
                    description=desc,
                )
                self._tier0_rules[rule_id] = rule
                self.rules.append({
                    "rule_id": rule_id,
                    "name": rule_id,
                    "severity": "blocked",
                    "tier": 0,
                    "description": desc,
                    "category": "general",
                })

    def _load_fallback_rules(self) -> None:
        """Load minimal built-in CORE rules as fallback."""
        for entry in _FALLBACK_CORE_RULES:
            rule_id = entry["rule_id"]
            self._tier0_rules[rule_id] = GovernanceRule(
                rule_id=rule_id,
                name=entry["name"],
                severity=entry["severity"],
                tier=0,
                description=entry["description"],
            )
            self.rules.append(dict(entry))

    # ------------------------------------------------------------------
    # Gate checking
    # ------------------------------------------------------------------

    def check_gate(
        self,
        gate_name: str,
        operation_spec: Dict[str, Any],
        intent_type: str,
    ) -> Dict[str, Any]:
        """
        Check if an operation passes a governance gate.

        Evaluates registered rules that apply to *gate_name* against the
        operation specification.  For strict intents (IMPLEMENT/FIX/REFACTOR)
        a "blocked"-severity rule failure will reject the gate.

        Args:
            gate_name: Name of governance gate to check.
            operation_spec: Operation specification dict.
            intent_type: Intent type (IMPLEMENT, FIX, REFACTOR, ANALYZE …).

        Returns:
            Dict with keys ``passed``, ``error_code``, ``message``, ``severity``.
        """
        # Ensure initialised
        if not self._initialized:
            self.initialize()

        gate_config = self.gates.get(gate_name)

        # Gate not registered — warn but allow
        if gate_config is None:
            return {
                "passed": True,
                "error_code": None,
                "message": f"Governance gate '{gate_name}' not registered — allowed by default",
                "severity": "WARNING",
            }

        # Determine which intents the gate applies to
        applies_to = gate_config.get("applies_to", list(_STRICT_INTENTS))
        if intent_type not in applies_to:
            return {
                "passed": True,
                "error_code": None,
                "message": (
                    f"Gate '{gate_name}' does not apply to intent '{intent_type}'"
                ),
                "severity": "INFO",
            }

        # Evaluate matching rules
        gate_severity = gate_config.get("severity", "WARNING")
        violations: List[str] = []

        for rule_dict in self.rules:
            rule_id = rule_dict.get("rule_id", "")
            rule_severity = rule_dict.get("severity", "warning")

            # Match rules whose category or explicit gate list includes this gate
            rule_gates = rule_dict.get("gates", [])
            rule_category = rule_dict.get("category", "")

            applies = (
                gate_name in rule_gates
                or gate_name == rule_category
                or gate_config.get("category") == rule_category
            )
            if not applies:
                continue

            # For strict intents, blocked-severity rules are violations
            if (
                intent_type in _STRICT_INTENTS
                and rule_severity == "blocked"
            ):
                # Check if operation_spec satisfies the rule
                if not self._operation_satisfies_rule(operation_spec, rule_dict):
                    violations.append(
                        f"[{rule_id}] {rule_dict.get('name', rule_id)}: "
                        f"{rule_dict.get('description', 'violation')}"
                    )

        if violations:
            return {
                "passed": False,
                "error_code": "GOVERNANCE_VIOLATION",
                "message": (
                    f"Gate '{gate_name}' FAILED — {len(violations)} violation(s): "
                    + "; ".join(violations)
                ),
                "severity": gate_severity,
            }

        return {
            "passed": True,
            "error_code": None,
            "message": f"Governance gate '{gate_name}' passed ({len(self.rules)} rules evaluated)",
            "severity": "INFO",
        }

    @staticmethod
    def _operation_satisfies_rule(
        operation_spec: Dict[str, Any],
        rule_dict: Dict[str, Any],
    ) -> bool:
        """
        Check whether an operation satisfies a governance rule.

        Args:
            operation_spec: The operation being evaluated.
            rule_dict: The rule definition dict.

        Returns:
            True if the operation satisfies (passes) the rule.
        """
        rule_id = rule_dict.get("rule_id", "")

        # CORE-008 — TDD: operation must declare test_written=True
        if rule_id == "CORE-008":
            return bool(operation_spec.get("test_written", False))

        # CORE-011 — Type hints: operation must not flag missing hints
        if rule_id == "CORE-011":
            return not bool(operation_spec.get("missing_type_hints", False))

        # CORE-013 — No bare except
        if rule_id == "CORE-013":
            return operation_spec.get("bare_except_count", 0) == 0

        # Default: assume satisfied unless explicitly flagged
        violation_key = f"violates_{rule_id.lower().replace('-', '_')}"
        return not bool(operation_spec.get(violation_key, False))

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def register_gate(self, gate_name: str, gate_config: Dict[str, Any]) -> None:
        """
        Register a governance gate.

        Args:
            gate_name: Unique gate identifier.
            gate_config: Configuration dict (severity, description, applies_to …).
        """
        gate_config.setdefault("name", gate_name)
        gate_config.setdefault("applies_to", list(_STRICT_INTENTS))
        self.gates[gate_name] = gate_config

    def register_rule(self, rule: Dict[str, Any]) -> None:
        """
        Register a governance rule.

        Args:
            rule: Rule definition dict with at least ``rule_id``.
        """
        self.rules.append(rule)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_gates(self) -> Dict[str, Dict[str, Any]]:
        """Get a copy of all registered gates.

        Returns:
            Dict mapping gate name → config.
        """
        return self.gates.copy()

    def get_rules(self) -> List[Dict[str, Any]]:
        """Get a copy of all registered rules.

        Returns:
            List of rule definition dicts.
        """
        return self.rules.copy()

    def get_rule(self, rule_id: str) -> Result[Optional[GovernanceRule]]:
        """
        Get a single rule by ID, applying tier precedence.
        
        When multiple versions of the same rule exist across tiers, returns
        the highest precedence version (tier 0 > tier 1 > tier 2).
        
        Args:
            rule_id: Rule identifier (e.g., "CORE-008").
        
        Returns:
            Result containing the GovernanceRule if found (applying tier precedence),
            Ok(None) if rule doesn't exist, or Err on failure.
        """
        if not self._initialized:
            init_result = self.initialize()
            if init_result.is_err():
                return Err(f"Failed to initialize registry: {init_result.unwrap_err()}")
        
        # Check tier 0 first (highest precedence)
        if rule_id in self._tier0_rules:
            return Ok(self._tier0_rules[rule_id])
        
        # Check tier 1 and tier 2 from rules list
        # Sort by tier (0 first, then 1, then 2) to respect precedence
        matching_rules = [r for r in self.rules if r.get("rule_id") == rule_id]
        
        if not matching_rules:
            return Ok(None)
        
        # Sort by tier (ascending: 0, 1, 2) and take first (highest precedence)
        matching_rules.sort(key=lambda r: r.get("tier", 999))
        best_match = matching_rules[0]
        
        # Convert dict to GovernanceRule
        rule = GovernanceRule(
            rule_id=best_match.get("rule_id", rule_id),
            name=best_match.get("name", rule_id),
            severity=best_match.get("severity", "warning"),
            tier=best_match.get("tier", 0),
            description=best_match.get("description", ""),
        )
        
        return Ok(rule)

    def get_all_rules(self) -> Dict[str, List[GovernanceRule]]:
        """
        Get rules grouped by tier for the rule evaluator.

        Returns:
            Dict with keys ``tier0``, ``tier1``, ``tier2`` mapping to
            lists of :class:`GovernanceRule` objects.
        """
        if not self._initialized:
            self.initialize()

        grouped: Dict[str, List[GovernanceRule]] = {
            "tier0": list(self._tier0_rules.values()),
            "tier1": [],
            "tier2": [],
        }

        # Tier 1/2 rules come from runtime registration
        for rule_dict in self.rules:
            tier = rule_dict.get("tier", 0)
            rule_id = rule_dict.get("rule_id", "")
            if tier == 1 and rule_id not in self._tier0_rules:
                grouped["tier1"].append(
                    GovernanceRule(
                        rule_id=rule_id,
                        name=rule_dict.get("name", rule_id),
                        severity=rule_dict.get("severity", "warning"),
                        tier=1,
                        description=rule_dict.get("description", ""),
                    )
                )
            elif tier == 2 and rule_id not in self._tier0_rules:
                grouped["tier2"].append(
                    GovernanceRule(
                        rule_id=rule_id,
                        name=rule_dict.get("name", rule_id),
                        severity=rule_dict.get("severity", "warning"),
                        tier=2,
                        description=rule_dict.get("description", ""),
                    )
                )

        return grouped
