"""
CORTEX Pytest Quality Plugin (Phase 07b)

Registers a pytest_collect_file hook that scores each test file at collection
time using TestQualityGate. Operates in two modes:

  warn   (default) — scores files, emits warnings for REVIEW/DELETE tier.
                     No tests are deselected.
  strict            — BLOCK (deselect) DELETE-tier files at collection.
                     Activated via CORTEX_QUALITY_GATE=strict env var or
                     --quality-gate=strict CLI flag.

Golden tests (tests/golden/* or auto-detected) are NEVER deselected regardless
of mode.

Integration:
  Registered alongside CortexXdistPlugin in conftest.py.
  Parallel-safe — stateless, no shared state between workers.

Authority: test-quality.txt | CORE-008 | CORE-011 | CORE-012
AC-ID: AC-PHASE-07B-TEST-QUALITY-GATE-001
Author: Asif Hussain
Date: 2026-02-20
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Optional

from cortex.testing.quality_gate import DELETE, TestQualityGate


class CortexQualityPlugin:
    """Pytest plugin that gates test collection on quality score.

    Attributes:
        mode: "warn" (default) or "strict" (deselects DELETE-tier files).
        gate: TestQualityGate instance for scoring.
    """

    def __init__(self, mode: str = "warn") -> None:
        """Initialise plugin.

        Args:
            mode: "warn" emits warnings only. "strict" deselects DELETE-tier files.
        """
        self.mode = mode
        self.gate = TestQualityGate()

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

        # Golden tests are always kept
        if result.is_golden:
            return False

        if self.mode == "strict" and result.category == DELETE:
            return True

        return False

    def pytest_collect_file(self, parent: object, file_path: Path) -> None:
        """Hook: called for each candidate test file during collection.

        Scores the file and emits a warning for REVIEW/DELETE tier files.
        In strict mode, raises pytest.skip equivalent via deselection.

        Args:
            parent: pytest collector parent node.
            file_path: Path to the candidate test file.
        """
        if not str(file_path).endswith(".py"):
            return
        if not file_path.name.startswith("test_"):
            return

        result = self.gate.score_file(file_path)

        if result.category == DELETE and not result.is_golden:
            msg = (
                f"[CORTEX Quality Gate] DELETE-tier file "
                f"(score={result.score}/9): {file_path.name} — "
                f"Impact:{result.breakdown.get('impact', 0)} "
                f"Likelihood:{result.breakdown.get('likelihood', 0)} "
                f"Detection:{result.breakdown.get('detection', 0)} "
                f"Efficiency:{result.breakdown.get('efficiency', 0)} "
                f"Penalty:{result.breakdown.get('maintenance_penalty', 0)}"
            )
            if self.mode == "strict":
                warnings.warn(msg + " [BLOCKED]", stacklevel=2)
            else:
                warnings.warn(msg + " [consider archiving]", stacklevel=2)

        elif result.category == "REVIEW":
            warnings.warn(
                f"[CORTEX Quality Gate] REVIEW-tier file "
                f"(score={result.score}/9): {file_path.name}",
                stacklevel=2,
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
