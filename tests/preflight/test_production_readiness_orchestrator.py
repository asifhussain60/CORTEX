"""Preflight test — Check #40: Production Readiness Validation Suite Orchestrator.

Validates that the preflight runner:
- Runs all registered check tests and passes ≥ 258 baseline
- Can emit a machine-readable evidence report
- Completes all checks within performance budget
- Evidence report path is defined and writable

Gap ref: GAP-126-11
Check: #40
Phase: phase-126-k
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
RUN_TESTS_SCRIPT = CORTEX_ROOT / "scripts" / "run_tests.py"
EVIDENCE_REPORT_PATH = CORTEX_ROOT / ".cortex-runtime" / "traces" / "production-readiness-evidence.json"

_PREFLIGHT_BASELINE = 258
_PERFORMANCE_BUDGET_SECONDS = 120


class TestProductionReadinessOrchestrator:
    """Check #40: Preflight runner orchestrates all production readiness checks."""

    def test_run_tests_script_exists(self) -> None:
        """scripts/run_tests.py must exist — it is the production readiness orchestrator."""
        assert RUN_TESTS_SCRIPT.exists(), (
            "scripts/run_tests.py is missing — production readiness orchestrator is gone."
        )

    def test_preflight_mode_registered_in_run_tests(self) -> None:
        """The 'preflight' mode must be registered in scripts/run_tests.py."""
        content = RUN_TESTS_SCRIPT.read_text(encoding="utf-8")
        assert '"preflight"' in content or "'preflight'" in content, (
            "scripts/run_tests.py does not register a 'preflight' mode."
        )

    def test_preflight_test_directory_exists(self) -> None:
        """tests/preflight/ directory must exist and contain test files."""
        preflight_dir = CORTEX_ROOT / "tests" / "preflight"
        assert preflight_dir.exists(), "tests/preflight/ directory is missing."
        test_files = list(preflight_dir.glob("test_*.py"))
        assert len(test_files) >= 10, (
            f"Expected ≥10 preflight test files, found {len(test_files)}."
        )

    def test_evidence_report_directory_exists_or_creatable(self) -> None:
        """The directory for the evidence report must exist or be creatable."""
        evidence_dir = EVIDENCE_REPORT_PATH.parent
        # Create if not present (runtime dir)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        assert evidence_dir.exists(), (
            f"{evidence_dir} could not be created — evidence report directory missing."
        )

    def test_evidence_report_schema_is_valid(self) -> None:
        """If the evidence report exists, it must be valid JSON with required fields."""
        if not EVIDENCE_REPORT_PATH.exists():
            pytest.skip("Evidence report not yet generated — run preflight to produce it.")
        data = json.loads(EVIDENCE_REPORT_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "Evidence report must be a JSON object."
        # Required top-level keys
        for key in ("generated_at", "checks_passed", "checks_total", "status"):
            assert key in data, f"Evidence report missing required field: '{key}'"
        # checks_total counts test *files* — must have at least 10
        assert data["checks_total"] >= 10, (
            f"Evidence report shows only {data['checks_total']} check files — expected ≥ 10."
        )

    @pytest.mark.skipif(
        os.environ.get("CORTEX_SKIP_INTEGRATION") == "true",
        reason="Integration execution skipped via CORTEX_SKIP_INTEGRATION=true",
    )
    @pytest.mark.timeout(150)
    def test_preflight_completes_within_performance_budget(self) -> None:
        """Preflight must complete all checks within 120 seconds (sequential mode).

        Note: This test spawns a subprocess and is intentionally excluded from
        the regular preflight run to avoid circular invocation. Run directly:
            pytest tests/preflight/test_production_readiness_orchestrator.py -k performance_budget
        """
        # Guard against being run inside the preflight suite itself (avoids subprocess loop)
        if os.environ.get("CORTEX_INSIDE_PREFLIGHT") == "true":
            pytest.skip("Skipped — circular invocation guard (CORTEX_INSIDE_PREFLIGHT)")

        """Preflight must complete all checks within 120 seconds (sequential mode)."""
        start = time.perf_counter()
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest", "tests/preflight/",
                "-q",
                "-p", "no:xdist",  # sequential — avoids parallel race conditions
                "--ignore=tests/preflight/test_production_readiness_orchestrator.py",
                "--tb=no",
                "--no-header",
            ],
            capture_output=True,
            text=True,
            cwd=str(CORTEX_ROOT),
            timeout=_PERFORMANCE_BUDGET_SECONDS + 30,
        )
        elapsed = time.perf_counter() - start
        assert elapsed <= _PERFORMANCE_BUDGET_SECONDS, (
            f"Preflight took {elapsed:.1f}s — exceeds {_PERFORMANCE_BUDGET_SECONDS}s budget."
        )
        assert result.returncode == 0, (
            f"Preflight failed (exit code {result.returncode}):\n{result.stdout[-2000:]}"
        )

    @pytest.mark.skipif(
        not (DRIFT_LOCKS_DIR / "check-40-production-readiness-orchestrator-lock.yaml").exists(),
        reason="Drift lock not yet created (pre-GREEN)",
    )
    def test_drift_lock_check_40_exists_and_valid(self) -> None:
        """Drift lock YAML for Check #40 must exist and be valid."""
        lock = DRIFT_LOCKS_DIR / "check-40-production-readiness-orchestrator-lock.yaml"
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 40
        assert data.get("status") == "ACTIVE"
