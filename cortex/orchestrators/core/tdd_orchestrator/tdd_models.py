"""
TDD data models: enums, dataclasses, and TDDKnowledgeLoader.

Extracted from tdd_orchestrator.py (Phase 103-c).
Contains all public data types used across TDD mixin modules.

Governance:
- CORE-011: Type hints on all functions
- CORE-012: Docstrings on all public APIs
- CORE-035: Single canonical definition — no duplicates
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# TDD Phase Enum
# =============================================================================


class TDDPhase(Enum):
    """TDD phase enumeration: RED → GREEN → REFACTOR."""

    RED = "red"          # Write failing test
    GREEN = "green"      # Minimal code to pass
    REFACTOR = "refactor"  # Improve design


# =============================================================================
# TDD Dataclasses
# =============================================================================


@dataclass
class TDDDisciplineRule:
    """A single TDD discipline rule loaded from YAML knowledge base."""

    rule_id: str
    description: str
    phase: TDDPhase
    enforcement: str = "recommended"
    examples: List[str] = field(default_factory=list)


@dataclass
class SuccessCriteria:
    """Exit criteria for multi-cycle TDD execution (ENH-088).

    Attributes:
        min_coverage: Minimum acceptable test coverage (0.0–1.0).
        max_latency_ms: Maximum acceptable test execution latency in ms.
        all_tests_pass: Whether all tests must pass (default: True).
        max_complexity: Maximum cyclomatic complexity (default: 10).
        extensibility_required: Whether extensibility gate must pass.
        custom_checks: Optional list of callables returning bool given CycleMetrics.
        goal_predicate: Optional callable returning bool for convergence gate.
    """

    min_coverage: float = 0.8
    max_latency_ms: float = 100.0
    all_tests_pass: bool = True
    max_complexity: int = 10
    extensibility_required: bool = False
    custom_checks: List[Callable[..., bool]] = field(default_factory=list)
    goal_predicate: Optional[Callable[..., bool]] = None


@dataclass
class CycleMetrics:
    """Metrics captured during a single TDD cycle (ENH-088).

    Attributes:
        cycle_number: 1-based cycle counter.
        tests_passed: Number of tests that passed.
        tests_failed: Number of tests that failed.
        coverage_percent: Measured code coverage (0.0–1.0).
        avg_latency_ms: Average test execution time in ms.
        extensibility_score: Extensibility score (0.0–1.0).
    """

    cycle_number: int
    tests_passed: int
    tests_failed: int
    coverage_percent: float
    avg_latency_ms: float
    extensibility_score: float = 0.0


@dataclass
class GateResult:
    """Result from the holistic refactor gate (ENH-088).

    Attributes:
        passed: Whether the gate passed (all criteria met).
        gaps: List of human-readable gap descriptions.
        recommendations: List of human-readable improvement suggestions.
    """

    passed: bool
    gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TDDImplementationGuidance:
    """Guidance produced by the TDD orchestrator for a RED→GREEN→REFACTOR cycle.

    Attributes:
        module_path: Target module path.
        domain: Domain classification string.
        tdd_phase: Current TDD phase.
        rules: Phase-specific discipline rules.
        best_practices: Ordered best-practice strings.
        test_patterns: Suggested test patterns for the phase.
        coverage_targets: Coverage thresholds (line, branch, overall).
        governance_rules: Applicable CORE governance rule IDs.
    """

    module_path: str
    domain: str
    tdd_phase: TDDPhase
    rules: List[TDDDisciplineRule] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    test_patterns: List[str] = field(default_factory=list)
    coverage_targets: Dict[str, float] = field(default_factory=dict)
    governance_rules: List[str] = field(default_factory=list)


# =============================================================================
# TDD Knowledge Loader
# =============================================================================


class TDDKnowledgeLoader:
    """Load TDD best practices and discipline rules from YAML knowledge files.

    Reads up to 4 YAML files from ``cortex-registry/workflows/templates/tdd/``:
    - ``tdd-best-practices.yaml``
    - ``tdd-discipline-rules.yaml``
    - ``tdd-workflow.yaml``
    - ``tdd-anti-patterns.yaml``

    Attributes:
        knowledge_root: Root path used for YAML discovery.
        tdd_yamls: Mapping of filename → parsed YAML content.
        tdd_rules: Extracted list of :class:`TDDDisciplineRule` objects.
    """

    def __init__(self, knowledge_root: Optional[Path] = None) -> None:
        """Initialise loader and immediately parse all YAML files.

        Args:
            knowledge_root: Override root path for YAML discovery.
                            Defaults to ``cortex-registry/workflows/templates/tdd/``.
        """
        self.knowledge_root = knowledge_root or Path("cortex-registry/workflows/templates/tdd")
        self.tdd_yamls: Dict[str, Any] = self._load_tdd_yamls()
        self.tdd_rules: List[TDDDisciplineRule] = self._extract_tdd_rules()

    def _load_tdd_yamls(self) -> Dict[str, Any]:
        """Load all TDD YAML files from *knowledge_root*.

        Returns:
            Mapping of filename → parsed YAML dict (silently skips missing files).
        """
        yaml_files = [
            "tdd-best-practices.yaml",
            "tdd-discipline-rules.yaml",
            "tdd-workflow.yaml",
            "tdd-anti-patterns.yaml",
        ]

        loaded: Dict[str, Any] = {}
        for yaml_file in yaml_files:
            yaml_path = self.knowledge_root / yaml_file
            if yaml_path.exists():
                try:
                    with open(yaml_path) as f:
                        loaded[yaml_file] = yaml.safe_load(f) or {}
                    logger.debug(f"Loaded TDD YAML: {yaml_file}")
                except Exception as e:
                    logger.warning(f"Failed to load {yaml_file}: {e}")

        return loaded

    def _extract_tdd_rules(self) -> List[TDDDisciplineRule]:
        """Extract :class:`TDDDisciplineRule` objects from loaded YAML data.

        Returns:
            List of discipline rules extracted from ``tdd-discipline-rules.yaml``.
        """
        rules: List[TDDDisciplineRule] = []

        rules_yaml = self.tdd_yamls.get("tdd-discipline-rules.yaml", {})
        if not rules_yaml:
            return rules

        for rule_data in rules_yaml.get("rules", []):
            try:
                phase_str = rule_data.get("phase", "GREEN")
                phase = (
                    TDDPhase[phase_str.upper()]
                    if phase_str.upper() in TDDPhase.__members__
                    else TDDPhase.GREEN
                )

                rule = TDDDisciplineRule(
                    rule_id=rule_data.get("id", "UNKNOWN"),
                    description=rule_data.get("description", ""),
                    phase=phase,
                    enforcement=rule_data.get("enforcement", "recommended"),
                    examples=rule_data.get("examples", []),
                )
                rules.append(rule)
            except Exception as e:
                logger.warning(f"Failed to extract rule: {e}")

        return rules

    def get_best_practices(self) -> List[str]:
        """Return ordered list of TDD best-practice strings.

        Returns:
            List of best-practice description strings (may be empty if YAML absent).
        """
        practices_yaml = self.tdd_yamls.get("tdd-best-practices.yaml", {})
        if not practices_yaml:
            return []

        practices = []
        for practice in practices_yaml.get("best_practices", []):
            if isinstance(practice, dict):
                practices.append(practice.get("description", str(practice)))
            elif isinstance(practice, str):
                practices.append(practice)

        return practices


__all__ = [
    "TDDPhase",
    "TDDDisciplineRule",
    "SuccessCriteria",
    "CycleMetrics",
    "GateResult",
    "TDDImplementationGuidance",
    "TDDKnowledgeLoader",
]
