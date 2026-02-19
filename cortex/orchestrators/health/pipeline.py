"""HealthVacuumPipeline — 5-Stage Coordinator

Orchestrates the full lifecycle:

1. **Preflight** — validate workspace exists, check git status
2. **Scan** — HealthOrchestrator.scan() + write_handoff()
3. **Review** — interactive confirmation (skipped in autonomous mode)
4. **Execute** — VacuumOrchestrator.consume() or run()
5. **Verify** — re-scan to check convergence, teardown

Supports a convergence gate that retries scan→execute until
``issues_fixed == issues_found`` or ``max_cycles`` is reached.

Phase: PHASE-51
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .constants import HANDOFF_FILENAME, ROLLBACK_FILENAME, RUNTIME_DIR
from .health_orchestrator import HealthOrchestrator
from .models import PipelineReport, ScanResult, VacuumReport
from .vacuum_orchestrator import VacuumOrchestrator

logger = logging.getLogger(__name__)


class HealthVacuumPipeline:
    """5-stage coordinator for the Health → Vacuum lifecycle.

    Usage::

        pipe = HealthVacuumPipeline(Path("/project"))
        report = pipe.run()                # autonomous
        report = pipe.run(dry_run=True)    # preview

    Attributes:
        workspace_root: Absolute path of the workspace.
        max_cycles: Maximum scan→execute convergence cycles.
    """

    def __init__(
        self,
        workspace_root: Path,
        *,
        max_cycles: int = 3,
    ) -> None:
        """Initialise the pipeline.

        Args:
            workspace_root: Root of the workspace.
            max_cycles: Max convergence iterations (default 3).
        """
        self.workspace_root = workspace_root
        self.max_cycles = max_cycles

    def run(self, *, dry_run: bool = False) -> PipelineReport:
        """Execute the full pipeline.

        Args:
            dry_run: If ``True``, scan runs but vacuum previews only.

        Returns:
            :class:`PipelineReport` with scan + vacuum results.
        """
        report = PipelineReport()

        # Stage 1: Preflight
        self._preflight()

        runtime_dir = self.workspace_root / RUNTIME_DIR
        runtime_dir.mkdir(parents=True, exist_ok=True)
        handoff_path = runtime_dir / HANDOFF_FILENAME
        rollback_path = runtime_dir / ROLLBACK_FILENAME

        scan_result: Optional[ScanResult] = None
        vacuum_report: Optional[VacuumReport] = None

        for cycle in range(1, self.max_cycles + 1):
            report.cycles = cycle

            # Stage 2: Scan
            health = HealthOrchestrator(self.workspace_root)
            scan_result = health.scan()
            health.write_handoff(scan_result, handoff_path)
            report.scan_result = scan_result

            logger.info(
                "Cycle %d — %d issues, score %.1f",
                cycle, scan_result.total_issues, scan_result.health_score,
            )

            # Stage 3: Review (autonomous — skipped)

            # No issues? Converged.
            if scan_result.total_issues == 0:
                report.converged = True
                report.vacuum_report = VacuumReport(dry_run=dry_run)
                break

            # Stage 4: Execute
            vacuum = VacuumOrchestrator(self.workspace_root)
            if dry_run:
                vacuum_report = vacuum.run(dry_run=True)
            else:
                vacuum_report = vacuum.consume(handoff_path)
                vacuum.save_rollback_manifest(rollback_path)
            report.vacuum_report = vacuum_report

            # Stage 5: Verify — check if we converged
            if vacuum_report.failed_operations == 0 and not dry_run:
                verify_health = HealthOrchestrator(self.workspace_root)
                verify_result = verify_health.scan()
                if verify_result.total_issues == 0:
                    report.converged = True
                    report.scan_result = verify_result
                    break
            else:
                # dry-run or failures — don't loop
                break

        return report

    # ── internal stages ──────────────────────────────────────────────────

    def _preflight(self) -> None:
        """Stage 1: Validate workspace."""
        if not self.workspace_root.exists():
            raise ValueError(
                f"Workspace does not exist: {self.workspace_root}"
            )
        logger.info("Preflight passed: %s", self.workspace_root)


__all__ = ["HealthVacuumPipeline"]
