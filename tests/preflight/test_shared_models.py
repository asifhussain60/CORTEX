"""
tests/preflight/test_shared_models.py — Phase 114-a RED→GREEN

Enforces shared model extraction from cortex/models/shared/.
Acceptance criteria from GAP-114-01:
  - Top models consolidated into cortex/models/shared/
  - ValidationResult importable from cortex.models.shared.validation
  - HealthCheckResult importable from cortex.models.shared.health
  - CacheEntry importable from cortex.models.shared.cache
  - Duplicate class count ≤ 80 across the codebase

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep completeness)
Phase: 114-a
"""
import ast
import pathlib
import collections
import importlib
import pytest


# ─────────────────────────────────────────────────────────────────
# GAP-114-01: Shared model extraction
# ─────────────────────────────────────────────────────────────────

def test_shared_models_package_exists():
    """cortex/models/shared/ must exist as a Python package."""
    pkg = pathlib.Path("cortex/models/shared")
    assert pkg.is_dir(), "cortex/models/shared/ directory missing"
    assert (pkg / "__init__.py").exists(), "cortex/models/shared/__init__.py missing"


def test_validation_result_single_canonical_import():
    """ValidationResult must be importable from cortex.models.shared.validation."""
    try:
        from cortex.models.shared.validation import ValidationResult  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Cannot import ValidationResult from cortex.models.shared.validation: {e}")


def test_health_check_result_single_canonical_import():
    """HealthCheckResult must be importable from cortex.models.shared.health."""
    try:
        from cortex.models.shared.health import HealthCheckResult  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Cannot import HealthCheckResult from cortex.models.shared.health: {e}")


def test_cache_entry_single_canonical_import():
    """CacheEntry must be importable from cortex.models.shared.cache."""
    try:
        from cortex.models.shared.cache import CacheEntry  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Cannot import CacheEntry from cortex.models.shared.cache: {e}")


def test_execution_result_single_canonical_import():
    """ExecutionResult must be importable from cortex.models.shared.execution."""
    try:
        from cortex.models.shared.execution import ExecutionResult  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Cannot import ExecutionResult from cortex.models.shared.execution: {e}")


def _count_duplicate_classes() -> dict:
    """Return dict of class names with count > 1, scanning cortex/ source."""
    counts: collections.Counter = collections.Counter()
    for f in pathlib.Path("cortex").rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            tree = ast.parse(f.read_text(errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    counts[node.name] += 1
        except Exception:
            pass
    return {n: c for n, c in counts.items() if c > 2}


def test_no_duplicate_class_over_threshold():
    """Duplicate class count (names appearing in >2 files) must be ≤ 80.

    Baseline: 75 at Phase 114 start. Target: ≤ 80 maintained.
    """
    duplicates = _count_duplicate_classes()
    count = len(duplicates)
    assert count <= 80, (
        f"Duplicate class count is {count} (budget ≤ 80). "
        f"Top offenders: {sorted(duplicates.items(), key=lambda x: -x[1])[:10]}"
    )
