"""
CORTEX Pytest Quality Plugin (Phase 07b)

Registers a pytest_collect_file hook that scores each test file at collection
time using TestQualityGate. Operates in two modes:

  warn   (default) — scores files, collects REVIEW/DELETE findings and emits
                     a single compact summary via pytest_terminal_summary.
                     No tests are deselected. No per-file UserWarnings emitted.
  strict            — BLOCK (deselect) DELETE-tier files at collection.
                     Activated via CORTEX_QUALITY_GATE=strict env var or
                     --quality-gate=strict CLI flag.

Golden tests (tests/golden/* or auto-detected) are NEVER deselected regardless
of mode.

Integration:
  Registered alongside CortexXdistPlugin in conftest.py.
  Parallel-safe — findings list is populated sequentially during collection.

Authority: test-quality.txt | CORE-008 | CORE-011 | CORE-012
AC-ID: AC-PHASE-07B-TEST-QUALITY-GATE-001
Author: Asif Hussain
Date: 2026-02-20
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Tuple

from cortex.testing.quality_gate import DELETE, REVIEW, ScoreResult, TestQualityGate


# Findings: (category, filename, score, breakdown_str, blocked)
_Finding = Tuple[str, str, float, str, bool]


class CortexQualityPlugin:
    """Pytest plugin that gates test collection on quality score.

    Findings (REVIEW/DELETE) are collected during pytest_collect_file and
    emitted as a single compact table via pytest_terminal_summary.  This
    eliminates the per-file UserWarning flood (previously 900+ warnings).

    Attributes:
        mode: "warn" (default) or "strict" (deselects DELETE-tier files).
        gate: TestQualityGate instance for scoring.
        _findings: Accumulated REVIEW/DELETE findings for the summary report.
    """

    def __init__(self, mode: str = "warn") -> None:
        """Initialise plugin.

        Args:
            mode: "warn" collects findings for summary. "strict" also deselects
                  DELETE-tier files at collection time.
        """
        self.mode = mode
        self.gate = TestQualityGate()
        self._findings: List[_Finding] = []

    def should_deselect(self, filepath: Path) -> bool:
        """Determine if a test file should be deselected at collection.

        Golden tests (tests/golden/ path) are NEVER deselected.
        In warn mode, nothing is deselected.
        In strict mode, DELETE-tier files are deselected.

        Args:
            filepath: Path to the test file.

        Returns:
            True if the file should be excluded from collection.
        """
        result = self.gate.score_file(filepath)

        if result.is_golden:
            return False

        if self.mode == "strict" and result.category == DELETE:
            return True

        return False

    def pytest_collect_file(self, parent: object, file_path: Path) -> None:
        """Hook: called for each candidate test file during collection.

        Scores the file and records REVIEW/DELETE findings for the terminal
        summary.  Does NOT call warnings.warn() — previously caused 900+
        UserWarning lines that cluttered pytest output.

        Args:
            parent: pytest collector parent node.
            file_path: Path to the candidate test file.
        """
        if not str(file_path).endswith(".py"):
            return
        if not file_path.name.startswith("test_"):
            return

        result = self.gate.score_file(file_path)

        if result.is_golden or result.category not in (DELETE, REVIEW):
            return

        blocked = self.mode == "strict" and result.category == DELETE
        breakdown_str = ""
        if result.category == DELETE:
            bd = result.breakdown
            breakdown_str = (
                f"Impact:{bd.get('impact', 0)} "
                f"Likelihood:{bd.get('likelihood', 0)} "
                f"Detection:{bd.get('detection', 0)} "
                f"Efficiency:{bd.get('efficiency', 0)} "
                f"Penalty:{bd.get('maintenance_penalty', 0)}"
            )

        self._findings.append(
            (result.category, file_path.name, result.score, breakdown_str, blocked)
        )

    def pytest_terminal_summary(self, terminalreporter: object, exitstatus: int) -> None:
        """Emit a compact quality gate summary after all tests complete.

        Replaces the previous per-file warnings.warn() approach.
        Only printed when there are REVIEW or DELETE findings.

        Args:
            terminalreporter: pytest's terminal reporter.
            exitstatus: Exit status of the test run.
        """
        if not self._findings:
            return

        tr = terminalreporter
        delete_findings = [f for f in self._findings if f[0] == DELETE]
        review_findings = [f for f in self._findings if f[0] == REVIEW]

        tr.write_sep("-", "CORTEX Quality Gate Summary", yellow=True)
        tr.write_line(
            f"  {len(delete_findings)} DELETE-tier  |  "
            f"{len(review_findings)} REVIEW-tier  |  "
            f"{len(self._findings)} total files below KEEP threshold (score < 7/9)",
            yellow=True,
        )

        if delete_findings:
            tr.write_line("  DELETE-tier files [consider archiving]:", red=True)
            for _cat, fname, score, bd, blocked in sorted(delete_findings, key=lambda x: x[2]):
                suffix = " [BLOCKED]" if blocked else ""
                tr.write_line(f"    score={score}/9  {fname}{suffix}  {bd}", red=True)

        if review_findings:
            tr.write_line("  REVIEW-tier files [human review required]:", yellow=True)
            for _cat, fname, score, _bd, _blocked in sorted(review_findings, key=lambda x: x[2]):
                tr.write_line(f"    score={score}/9  {fname}", yellow=True)

        tr.write_line(
            "  Run with CORTEX_QUALITY_GATE=strict to block DELETE-tier files.",
            bold=True,
        )


def make_plugin(mode: Optional[str] = None) -> CortexQualityPlugin:
    """Factory: create plugin with mode resolved from env var or argument.

    Priority: explicit arg > CORTEX_QUALITY_GATE env var > "warn" default.

    Args:
        mode: Explicit mode override ("warn" or "strict").

    Returns:
        Configured CortexQualityPlugin instance.
    """
    resolved_mode = mode or os.environ.get("CORTEX_QUALITY_GATE", "warn")
    return CortexQualityPlugin(mode=resolved_mode)


__all__ = ["CortexQualityPlugin", "make_plugin"]
