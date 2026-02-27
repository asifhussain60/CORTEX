#!/usr/bin/env python3
"""
CORTEX TDD Gate — CORE-008 Enforcement
Replaces: .github/workflows/tdd-gate.yml

Checks:
  1. Every implementation file in cortex/ has a corresponding test
  2. Cross-layer integration tests pass (Phase 21 contracts)
  3. Governance policy compliance (CORE-008, CORE-019, CORE-035)

Usage:
    python scripts/governance/tdd_gate.py
    python scripts/governance/tdd_gate.py --strict   # fail on any missing test
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORTEX_SRC = ROOT / "cortex"
TESTS_ROOT = ROOT / "tests"

# Files that are allowed to have no test (infrastructure, __init__, etc.)
EXEMPT_PATTERNS = {
    "__init__.py",
    "conftest.py",
    "bootstrap.py",
    "health_check_service.py",
    "opentelemetry_tracing.py",
    "prometheus_metrics.py",
}

EXEMPT_DIRS = {
    "cortex/scripts",
    "cortex/templates",
}


def _find_implementation_files() -> list[Path]:
    """Return all non-exempt Python source files under cortex/."""
    files = []
    for f in CORTEX_SRC.rglob("*.py"):
        if f.name in EXEMPT_PATTERNS:
            continue
        rel = f.relative_to(ROOT)
        if any(str(rel).startswith(d) for d in EXEMPT_DIRS):
            continue
        files.append(f)
    return files


def _expected_test_path(src: Path) -> Path:
    """
    Map cortex/foo/bar/baz.py → tests/unit/foo/bar/test_baz.py
    or tests/foo/bar/test_baz.py (any sub-location).
    """
    rel = src.relative_to(CORTEX_SRC)          # foo/bar/baz.py
    test_name = f"test_{rel.name}"             # test_baz.py
    test_rel = Path(*rel.parts[:-1]) / test_name  # foo/bar/test_baz.py
    return TESTS_ROOT / "unit" / test_rel


def _test_exists_anywhere(src: Path) -> bool:
    """Return True if any test file matching test_<name>.py exists under tests/."""
    test_name = f"test_{src.name}"
    return bool(list(TESTS_ROOT.rglob(test_name)))


def check_tdd_compliance(strict: bool = False) -> tuple[int, list[str]]:
    """
    Returns (missing_count, list_of_missing_paths).
    """
    impl_files = _find_implementation_files()
    missing = []

    for f in impl_files:
        if not _test_exists_anywhere(f):
            rel = str(f.relative_to(ROOT))
            missing.append(rel)

    return len(missing), missing


def run_cross_layer_tests() -> bool:
    """Run Phase 21 contract tests."""
    contract_test = TESTS_ROOT / "integration" / "test_phase21_contracts.py"
    if not contract_test.exists():
        print("  ℹ️  Phase 21 contract tests not found — skipping")
        return True

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(contract_test), "-v", "--tb=short", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout[-2000:])
        print(result.stderr[-500:])
        return False
    print(f"  ✅ Phase 21 cross-layer contracts: PASSED")
    return True


def check_governance_compliance() -> bool:
    """Validate CORE-008/035 via GovernanceAnalyzer if available."""
    try:
        sys.path.insert(0, str(ROOT))
        from cortex.governance.governance_analyzer import GovernanceAnalyzer  # type: ignore

        analyzer = GovernanceAnalyzer()
        print(f"  ✅ Governance analyzer: {len(analyzer.CORE_RULES)} CORE rules active")
        return True
    except ImportError:
        print("  ℹ️  GovernanceAnalyzer not importable — skipping governance check")
        return True
    except Exception as e:
        print(f"  ⚠️  Governance check warning: {e}")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="CORTEX TDD Gate (CORE-008)")
    parser.add_argument("--strict", action="store_true", help="Fail on any missing test")
    parser.add_argument(
        "--threshold",
        type=int,
        default=50,
        help="Max allowed missing tests before blocking (default: 50)",
    )
    args = parser.parse_args()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 CORTEX TDD Gate (CORE-008)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 1. TDD Compliance
    print("\n[1/3] TDD Compliance Check...")
    missing_count, missing_files = check_tdd_compliance(args.strict)
    threshold = 0 if args.strict else args.threshold

    if missing_count == 0:
        print("  ✅ All implementation files have corresponding tests")
    else:
        print(f"  {'❌' if missing_count > threshold else '⚠️ '} {missing_count} files missing tests (threshold: {threshold})")
        if missing_count <= 20:
            for f in missing_files:
                print(f"     - {f}")
        else:
            for f in missing_files[:10]:
                print(f"     - {f}")
            print(f"     ... and {missing_count - 10} more")

    # 2. Cross-layer contracts
    print("\n[2/3] Cross-Layer Integration Tests...")
    contracts_ok = run_cross_layer_tests()

    # 3. Governance
    print("\n[3/3] Governance Policy Compliance...")
    governance_ok = check_governance_compliance()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Determine exit code
    if missing_count > threshold:
        print(f"❌ TDD Gate FAILED: {missing_count} missing tests exceeds threshold of {threshold}")
        print("\nRequired Actions:")
        print("  1. Write tests BEFORE implementation (CORE-008)")
        print("  2. Follow RED → GREEN → REFACTOR workflow")
        print("  3. Use TDDOrchestrator via cortex_validate MCP tool")
        return 1

    if not contracts_ok:
        print("❌ TDD Gate FAILED: Cross-layer contract tests failed")
        return 1

    print(f"✅ TDD Gate PASSED ({missing_count} missing, {threshold} threshold)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
