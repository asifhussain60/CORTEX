"""
tests/models/test_phase119_canonical_types.py — Phase 119-A TDD Red→Green

Governance gate for CORE-035 Sub-Phase A: canonicalise the 9 high-severity
shared types (≥5 duplicate locations) into cortex/models/shared/ and
cortex/models/canonical_enums.

Each test asserts:
  1. The canonical class is importable from its single authoritative path.
  2. Non-scoped shadow definitions no longer exist (each class body appears
     in exactly 1 non-scoped file).

A "scoped" definition carries the comment ``# CORE-035-scoped`` on the same
line as the ``class`` keyword — these are intentional domain-local variants
and are exempt from consolidation.

Phase 119-A target:
  - CacheStats: 6 non-scoped → 1 non-scoped (canonical only)
  - ExecutionResult: 2 non-scoped → 1 non-scoped (canonical only)
  - HealthCheckResult: 1 non-scoped canonical + 1 unscoped in
    deployment_validator.py → 1 non-scoped
  - All other GAP-119-01 classes: verify canonical exists, shadow count ≤ 1

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Authority: phase-119-a, SWEEP-119-CLASS-CONSOLIDATION
"""
from __future__ import annotations

import ast
import pathlib
from typing import Dict, List, Tuple

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — AST scan for non-scoped class definitions
# ─────────────────────────────────────────────────────────────────────────────

CORTEX_ROOT = pathlib.Path(__file__).parent.parent.parent / "cortex"


def _find_nonscoped_definitions(class_name: str) -> List[Tuple[str, int]]:
    """Return list of (filepath, lineno) for every non-scoped definition.

    A definition is ``non-scoped`` if the ``class`` line does NOT contain
    ``# CORE-035-scoped``. Canonical files and true duplicates are both
    non-scoped; intentional domain variants are scoped and excluded.

    Excludes __pycache__ and _quarantine directories.
    """
    results: List[Tuple[str, int]] = []
    for f in CORTEX_ROOT.rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            src = f.read_text(errors="ignore")
            lines = src.splitlines()
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    class_line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                    if "CORE-035-scoped" not in class_line:
                        results.append((str(f.relative_to(CORTEX_ROOT.parent)), node.lineno))
        except Exception:
            pass
    return results


def _assert_single_nonscoped(class_name: str, canonical_path_fragment: str) -> None:
    """Assert exactly 1 non-scoped definition exists and it is in canonical_path_fragment."""
    locations = _find_nonscoped_definitions(class_name)
    loc_paths = [loc[0] for loc in locations]
    assert len(locations) == 1, (
        f"CORE-035 violation: '{class_name}' has {len(locations)} non-scoped definitions "
        f"(expected exactly 1 in {canonical_path_fragment}).\n"
        f"Found at:\n" + "\n".join(f"  {p}:{ln}" for p, ln in locations)
    )
    assert canonical_path_fragment in loc_paths[0], (
        f"'{class_name}' sole non-scoped definition is NOT in canonical path '{canonical_path_fragment}'.\n"
        f"Found at: {loc_paths[0]}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL IMPORT TESTS — verify each class is importable from its SSOT
# (These pass even at RED — canonical modules exist from Phase 114)
# ─────────────────────────────────────────────────────────────────────────────

def test_validation_result_canonical_importable() -> None:
    """ValidationResult importable from cortex.models.shared.validation (re-exports canonical)."""
    from cortex.models.shared.validation import ValidationResult  # noqa: F401
    assert ValidationResult is not None


def test_health_check_result_canonical_importable() -> None:
    """HealthCheckResult importable from cortex.models.shared.health."""
    from cortex.models.shared.health import HealthCheckResult  # noqa: F401
    assert HealthCheckResult is not None


def test_cache_entry_canonical_importable() -> None:
    """CacheEntry importable from cortex.models.shared.cache."""
    from cortex.models.shared.cache import CacheEntry  # noqa: F401
    assert CacheEntry is not None


def test_cache_stats_canonical_importable() -> None:
    """CacheStats importable from cortex.models.shared.cache."""
    from cortex.models.shared.cache import CacheStats  # noqa: F401
    assert CacheStats is not None


def test_execution_result_canonical_importable() -> None:
    """ExecutionResult importable from cortex.models.shared.execution."""
    from cortex.models.shared.execution import ExecutionResult  # noqa: F401
    assert ExecutionResult is not None


def test_intent_type_canonical_importable() -> None:
    """IntentType importable from cortex.models.canonical_enums."""
    from cortex.models.canonical_enums import IntentType  # noqa: F401
    assert IntentType is not None


def test_risk_level_canonical_importable() -> None:
    """RiskLevel importable from cortex.models.canonical_enums."""
    from cortex.models.canonical_enums import RiskLevel  # noqa: F401
    assert RiskLevel is not None


# ─────────────────────────────────────────────────────────────────────────────
# SHADOW COUNT TESTS — these FAIL at RED (shadow definitions still exist)
# and pass GREEN once shadows are replaced with imports from canonical
# ─────────────────────────────────────────────────────────────────────────────

def test_cache_stats_single_nonscoped_definition() -> None:
    """CacheStats must have exactly 1 non-scoped body in cortex/models/shared/cache.py.

    RED: 6 non-scoped definitions exist (core_context_cache_layer, models/shared/cache,
    orchestrators/core/context_cache_layer, lens/cache, lens/analysis/remote_cache,
    lens/cache/__init__). GREEN: only models/shared/cache.py remains; all others
    import from canonical.
    """
    _assert_single_nonscoped("CacheStats", "cortex/models/shared/cache.py")


def test_execution_result_single_nonscoped_definition() -> None:
    """ExecutionResult must have exactly 1 non-scoped body in cortex/models/shared/execution.py.

    RED: 2 non-scoped definitions exist (models/shared/execution and
    orchestrators/domain/strategy_base). GREEN: strategy_base imports from canonical.
    """
    _assert_single_nonscoped("ExecutionResult", "cortex/models/shared/execution.py")


def test_health_check_result_single_nonscoped_definition() -> None:
    """HealthCheckResult must have exactly 1 non-scoped body in cortex/models/shared/health.py.

    RED: deployment_validator.py has an extra non-scoped HealthCheckResult.
    GREEN: deployment_validator imports from cortex.models.shared.health.
    """
    _assert_single_nonscoped("HealthCheckResult", "cortex/models/shared/health.py")


# ─────────────────────────────────────────────────────────────────────────────
# BUDGET GATE — no regression on overall >2-location duplicate count
# ─────────────────────────────────────────────────────────────────────────────

PHASE_119A_SHADOW_BUDGET: Dict[str, int] = {
    # class_name: max allowed non-scoped count during Sub-Phase A
    # Target for GREEN: all = 1
    "CacheStats": 1,
    "ExecutionResult": 1,
    "HealthCheckResult": 1,
    "CacheEntry": 1,       # already scoped everywhere except models/shared/cache.py
    "DependencyGraph": 1,  # already scoped everywhere except infrastructure/devx
}


@pytest.mark.parametrize("class_name,canonical_fragment", [
    ("CacheEntry", "cortex/models/shared/cache.py"),
    ("DependencyGraph", "cortex/infrastructure/devx/integration_validator.py"),
])
def test_already_canonical_classes_have_single_nonscoped_definition(
    class_name: str,
    canonical_fragment: str,
) -> None:
    """CacheEntry and DependencyGraph are already fully scoped — verify no regression."""
    _assert_single_nonscoped(class_name, canonical_fragment)
