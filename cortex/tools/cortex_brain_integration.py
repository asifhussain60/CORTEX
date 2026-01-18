"""
Governance Brain Integration Module.

Provides access to governance rules from tier0, tier1, tier2, tier3 brain layers,
with caching and efficient query interfaces.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class GovernanceRuleLoader:
    """
    Load and query governance rules from tier0/governance files.

    Rules are cached in memory for sub-100ms query performance.
    """

    def __init__(self, governance_dir: Optional[Path] = None):
        """
        Initialize rule loader.

        Args:
            governance_dir: Path to cortex-brain/tier0/governance.
                          Defaults to standard location.
        """
        if governance_dir is None:
            # Standard location relative to project root
            governance_dir = (
                Path(__file__).parent.parent.parent /
                "cortex-brain/tier0/governance"
            )

        self.governance_dir = governance_dir
        self._rules_cache: Dict[str, Dict[str, Any]] = {}
        self._domain_index: Dict[str, List[str]] = {}
        self._phase_index: Dict[str, List[str]] = {}
        self._loaded = False

    def _load_rules(self) -> None:
        """Load all governance rules from YAML files."""
        if self._loaded:
            return

        # Load core rules
        core_rules_file = self.governance_dir / "core-rules.yaml"
        if core_rules_file.exists():
            with open(core_rules_file) as f:
                data = yaml.safe_load(f)
                if data and "rules" in data:
                    for rule in data["rules"]:
                        rule_id = rule.get("rule_id")
                        if rule_id:
                            self._rules_cache[rule_id] = rule
                            self._index_rule_by_domain(rule_id, rule)

        # Load other governance files
        for yaml_file in self.governance_dir.glob("*.yaml"):
            if yaml_file.name in ("core-rules.yaml", ".gitkeep"):
                continue

            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                if not data:
                    continue

                # Load phase-specific rules
                if "phases" in data or "phase_enforcement" in yaml_file.name:
                    self._load_phase_enforcement(data)
                # Load other rules
                elif "rules" in data:
                    for rule in data["rules"]:
                        rule_id = rule.get("rule_id")
                        if rule_id:
                            self._rules_cache[rule_id] = rule
                            self._index_rule_by_domain(rule_id, rule)

        self._loaded = True

    def _index_rule_by_domain(self, rule_id: str, rule: Dict[str, Any]) -> None:
        """Index rule by domain."""
        domain = rule.get("category")
        if domain:
            if domain not in self._domain_index:
                self._domain_index[domain] = []
            self._domain_index[domain].append(rule_id)

    def _load_phase_enforcement(self, data: Dict[str, Any]) -> None:
        """Load phase enforcement mappings."""
        # This could be expanded to parse phase-enforcement-map.yaml
        # For now, populate with basic structure
        pass

    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single rule by ID.

        Args:
            rule_id: Rule identifier (e.g., 'CORE-008', 'FR-001-02')

        Returns:
            Rule dict or None if not found
        """
        self._load_rules()
        return self._rules_cache.get(rule_id)

    def get_rules_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get all rules in a domain.

        Args:
            domain: Domain name (e.g., 'tdd', 'orchestration_lifecycle')

        Returns:
            List of rule dicts
        """
        self._load_rules()
        rule_ids = self._domain_index.get(domain, [])
        return [
            self._rules_cache[rid]
            for rid in rule_ids
            if rid in self._rules_cache
        ]

    def get_rules_for_phase(self, phase: str) -> List[Dict[str, Any]]:
        """
        Get all rules enforced in a phase.

        Args:
            phase: Phase ID (e.g., 'PHASE-01')

        Returns:
            List of rule dicts
        """
        self._load_rules()

        # Load phase enforcement map
        enforcement_file = (
            self.governance_dir / "phase-enforcement-map.yaml"
        )
        if not enforcement_file.exists():
            return []

        with open(enforcement_file) as f:
            enforcement_data = yaml.safe_load(f)

        if not enforcement_data:
            return []

        # Collect all rules for this phase
        rule_ids: set[str] = set()

        # Global rules apply to all phases
        if "global_rules" in enforcement_data:
            global_rules = enforcement_data["global_rules"]
            if "mandatory" in global_rules:
                for rule in global_rules["mandatory"]:
                    rule_ids.add(rule.get("rule_id"))
            if "warning" in global_rules:
                for rule in global_rules["warning"]:
                    rule_ids.add(rule.get("rule_id"))

        # Phase-specific rules
        if "phases" in enforcement_data:
            phase_data = enforcement_data["phases"].get(phase, {})
            if "mandatory" in phase_data:
                for rule in phase_data["mandatory"]:
                    rule_ids.add(rule.get("rule_id"))
            if "warning" in phase_data:
                for rule in phase_data["warning"]:
                    rule_ids.add(rule.get("rule_id"))

        return [
            self._rules_cache[rid]
            for rid in rule_ids
            if rid in self._rules_cache
        ]

    def get_all_domains(self) -> List[str]:
        """Get all available domains."""
        self._load_rules()
        return sorted(self._domain_index.keys())

    def get_all_phases(self) -> List[str]:
        """Get all available phases."""
        self._load_rules()
        return sorted(self._phase_index.keys())


class ValidationEngine:
    """
    Validate code/projects against governance rules.

    Checks for compliance with type hints, docstrings, naming conventions,
    exception handling, and other CORE rules.
    """

    def __init__(
        self,
        phase: Optional[str] = None,
        ac_id: Optional[str] = None,
        strict: bool = False,
    ):
        """
        Initialize validation engine.

        Args:
            phase: Phase context (e.g., 'PHASE-09')
            ac_id: Specific AC-ID to validate (e.g., 'GV-001-01')
            strict: If True, treat warnings as violations
        """
        self.phase = phase
        self.ac_id = ac_id
        self.strict = strict
        self.loader = GovernanceRuleLoader()

    def validate_path(self, path: Path) -> List[Dict[str, Any]]:
        """
        Validate a file or directory.

        Args:
            path: Path to validate

        Returns:
            List of violation dicts
        """
        violations: List[Dict[str, Any]] = []

        if path.is_file():
            if path.suffix == ".py":
                violations.extend(self._validate_python_file(path))
        else:
            # Directory - validate all Python files
            for py_file in path.rglob("*.py"):
                if ".venv" not in py_file.parts and "__pycache__" not in py_file.parts:
                    violations.extend(self._validate_python_file(py_file))

        return violations

    def _validate_python_file(
        self, file_path: Path
    ) -> List[Dict[str, Any]]:
        """
        Validate a single Python file.

        Args:
            file_path: Path to Python file

        Returns:
            List of violation dicts
        """
        violations: List[Dict[str, Any]] = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Check for CORE-011: Type hints
            if "def " in content and ": " not in content:
                violations.append({
                    "rule_id": "CORE-011",
                    "message": "Function missing type hints",
                    "file": str(file_path),
                    "severity": "warning",
                })

            # Check for CORE-012: Docstrings on public functions
            if 'def ' in content and '"""' not in content:
                violations.append({
                    "rule_id": "CORE-012",
                    "message": "Function missing docstring",
                    "file": str(file_path),
                    "severity": "warning",
                })

            # Check for CORE-013: Bare except
            if "except:" in content:
                violations.append({
                    "rule_id": "CORE-013",
                    "message": "Bare 'except:' clause found (use specific exceptions)",
                    "file": str(file_path),
                    "severity": "blocked",
                    "fix_suggestion": "Replace 'except:' with specific exception types",
                })

            # Check for CORE-028: Kebab-case filenames
            if not self._is_kebab_case(file_path.stem):
                violations.append({
                    "rule_id": "CORE-028",
                    "message": f"Filename '{file_path.name}' should use kebab-case",
                    "file": str(file_path),
                    "severity": "warning",
                    "fix_suggestion": (
                        f"Rename to '{self._to_kebab_case(file_path.stem)}.py'"
                    ),
                })

        except Exception as e:
            violations.append({
                "rule_id": "VALIDATION_ERROR",
                "message": f"Failed to validate file: {e}",
                "file": str(file_path),
                "severity": "warning",
            })

        return violations

    @staticmethod
    def _is_kebab_case(name: str) -> bool:
        """Check if name is in kebab-case."""
        # Allow underscores and digits, but should prefer dashes
        return not any(c.isupper() for c in name) and len(name) <= 25

    @staticmethod
    def _to_kebab_case(name: str) -> str:
        """Convert name to kebab-case."""
        # Simple conversion: CamelCase or snake_case -> kebab-case
        import re
        # Insert dash before uppercase letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
        # Replace underscores and spaces with dashes
        return re.sub("_| ", "-", s1).lower()[:25]
