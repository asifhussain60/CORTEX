"""
Phase 111 TDD Tests — CORE-035 Duplicate Class Sweep
Audit Check #26: assert DUPLICATES=0 across all cortex/ source files.

Authority: CORE-035 (Single canonical implementation — no duplicates)
AC-IDs: AC-P111-001, AC-P111-002, AC-P111-003
Sweep ID: SWEEP-111-DUPLICATE-CLASS-SWEEP
"""
# ruff: noqa: S101
from __future__ import annotations

import ast
import pathlib
from collections import defaultdict

import pytest

ROOT = pathlib.Path(__file__).parents[2]
CORTEX = ROOT / "cortex"

# Classes that are INTENTIONALLY duplicated in separate domain-scoped modules.
# These are NOT violations — each copy serves a distinct domain boundary.
# Key: class name  Value: reason / canonical location
INTENTIONAL_DUPLICATES: dict[str, str] = {
    # Proxy pattern — support/vacuum_orchestrator.py is a thin re-export
    "VacuumOrchestrator": "support/ is a proxy re-export of health/ canonical",
    # Persona domain has its own MasterOrchestrator variant intentionally
    "MasterOrchestrator": "persona/ variant is a distinct persona-scoped orchestrator",
    # OpenTelemetry Span/SpanKind/SpanStatus — stdlib shim + otel are intentionally parallel
    "Span": "opentelemetry_tracing.py is a stdlib shim alongside infrastructure/tracing.py",
    "SpanKind": "opentelemetry_tracing.py is a stdlib shim alongside infrastructure/tracing.py",
    "SpanStatus": "opentelemetry_tracing.py is a stdlib shim alongside infrastructure/tracing.py",
    # Pydantic Config inner class is top-level in some files by design
    # (excluded by top-level-only scan, but listing here for reference)
    # Phase 129-130 domain-isolation boundaries — distinct result types for different pipelines
    "OptimizationResult": (
        "content_optimization_orchestrator defines file-level OptimizationResult; "
        "response_optimizer defines LLM response-level OptimizationResult — distinct domains"
    ),
    "DistillationResult": (
        "distillation_orchestrator (Phase 129) and token_distillation_engine are "
        "independent pipelines with domain-isolated result types"
    ),
    "EpochShuffler": (
        "content_library_facade and content_library_engine co-define EpochShuffler "
        "via facade+engine pattern — intentional co-ownership"
    ),
}

# Classes exempt due to annotated files (CORE-035 governance comment)
NOQA_ANNOTATION = "# CORE-035"


def _scan_top_level_classes() -> dict[str, list[str]]:
    """Scan cortex/ for TOP-LEVEL class names (direct Module children only).

    - Excludes __pycache__
    - Excludes files annotated with 'CORE-035'
    - Only counts top-level class definitions (not inner Pydantic Config etc.)
    """
    class_locs: dict[str, list[str]] = defaultdict(list)
    for py_file in CORTEX.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            src = py_file.read_text(encoding="utf-8", errors="ignore")
            if NOQA_ANNOTATION in src:
                continue
            tree = ast.parse(src)
        except Exception:
            continue
        # Only top-level classes — excludes inner Pydantic Config classes
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_locs[node.name].append(str(py_file))
    return class_locs


def _get_violations() -> dict[str, list[str]]:
    """Return classes with >1 top-level definition, excluding intentional duplicates."""
    all_classes = _scan_top_level_classes()
    violations = {}
    for name, files in all_classes.items():
        if len(files) <= 1:
            continue
        if name in INTENTIONAL_DUPLICATES:
            continue
        violations[name] = files
    return violations


class TestNoDuplicateClasses:
    """Audit Check #26 — assert DUPLICATES=0 for all cortex/ source files."""

    def test_no_duplicate_class_definitions(self) -> None:
        """CORE-035: Each class name must have exactly ONE top-level definition in cortex/.

        Exclusions:
          - Files annotated with 'CORE-035'
          - Known intentional proxies listed in INTENTIONAL_DUPLICATES
          - Inner/nested classes (only top-level module children are checked)

        Phase 111 target: DUPLICATES=0
        Current entry state: ~270 violations
        """
        violations = _get_violations()
        if violations:
            top = sorted(violations.items(), key=lambda x: -len(x[1]))[:20]
            detail = "\n".join(
                f"  {name} ({len(files)}x definitions):\n"
                + "\n".join(f"    {f}" for f in sorted(files))
                for name, files in top
            )
            count = len(violations)
            pytest.fail(
                f"CORE-035 VIOLATED: {count} class names have multiple top-level definitions.\n"
                f"Top violations (showing ≤20 of {count}):\n{detail}\n\n"
                f"Fix: consolidate each to one canonical file, then delete shadow copies.\n"
                f"Exempt intentional proxies by adding to INTENTIONAL_DUPLICATES or "
                f"'# CORE-035' in the file."
            )

    def test_validation_result_canonical_import(self) -> None:
        """ValidationResult (24 defs) must resolve from cortex.models.validation_result."""
        try:
            from cortex.models.validation_result import ValidationResult  # noqa: F401
        except ImportError:
            pytest.fail(
                "cortex.models.validation_result.ValidationResult not importable. "
                "Ensure cortex/models/validation_result.py defines the canonical ValidationResult."
            )

    def test_intent_type_single_canonical_import(self) -> None:
        """IntentType must be importable from cortex.models.canonical_enums (SSOT)."""
        try:
            from cortex.models.canonical_enums import IntentType  # noqa: F401
        except ImportError:
            pytest.fail(
                "IntentType not in cortex.models.canonical_enums. "
                "It must be defined there and imported everywhere else."
            )

    def test_health_status_canonical_import(self) -> None:
        """HealthStatus must be importable from cortex.models.canonical_enums (SSOT)."""
        try:
            from cortex.models.canonical_enums import HealthStatus  # noqa: F401
        except ImportError:
            pytest.fail(
                "HealthStatus not in cortex.models.canonical_enums — add it."
            )

    def test_risk_level_canonical_import(self) -> None:
        """RiskLevel must be importable from cortex.models.canonical_enums (SSOT)."""
        try:
            from cortex.models.canonical_enums import RiskLevel  # noqa: F401
        except ImportError:
            pytest.fail(
                "RiskLevel not in cortex.models.canonical_enums — add it."
            )

    def test_severity_level_canonical_import(self) -> None:
        """SeverityLevel must be importable from cortex.models.canonical_enums (SSOT)."""
        try:
            from cortex.models.canonical_enums import SeverityLevel  # noqa: F401
        except ImportError:
            pytest.fail(
                "SeverityLevel not in cortex.models.canonical_enums — add it."
            )


class TestDuplicateClassAuditMetrics:
    """Metrics tests — track progress toward DUPLICATES=0 with numeric gates."""

    def test_duplicate_count_below_threshold(self) -> None:
        """Track total duplicate class count — gates at progressive thresholds.

        Thresholds tighten as Phase 111 sub-phases complete:
          Phase 111-a complete: ≤ 240
          Phase 111-b complete: ≤ 180
          Phase 111-c complete: 0
        """
        violations = _get_violations()
        count = len(violations)
        # Current threshold — update after each sub-phase completes
        CURRENT_THRESHOLD = 0  # Phase 111 COMPLETE: 0 violations (all consolidated or annotated)
        assert count <= CURRENT_THRESHOLD, (
            f"Duplicate class count {count} exceeds threshold {CURRENT_THRESHOLD}. "
            f"Run Phase 111 consolidation steps."
        )

    def test_no_class_with_10_or_more_definitions(self) -> None:
        """No single class may have 10+ definitions — P0 violation requiring immediate fix."""
        violations = _get_violations()
        critical = {k: v for k, v in violations.items() if len(v) >= 10}
        if critical:
            detail = "\n".join(
                f"  {k} ({len(v)} defs): {', '.join(sorted(v)[:3])} ..."
                for k, v in sorted(critical.items(), key=lambda x: -len(x[1]))
            )
            pytest.fail(
                f"CRITICAL (P0): {len(critical)} class(es) with 10+ definitions:\n{detail}"
            )
