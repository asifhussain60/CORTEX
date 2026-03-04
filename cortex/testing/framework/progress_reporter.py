"""
CORTEX Batch Progress Reporter — Real-time terminal feedback for parallel test runs.

Renders per-batch headers, live progress bars, worker status lines, and
a final aggregated summary — all to stderr so pytest output is unaffected.

Terminal output format::

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🧪 Batch 2 / 4  |  Tests 501–1000 of 1800  |  4 workers
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      Worker 0  ✅ tests/unit/core/test_factory.py        0.3s
      Worker 1  🔵 tests/unit/governance/test_rules.py ...
      Worker 2  ✅ tests/unit/mcp/test_tools.py           0.1s
    [████████████████████░░░░░░░░░░░░░░░░]  53% | ✅ 942  🔴 3  ⏭️ 5

Authority: CORE-008 | CORE-011 | CORE-012
AC-ID: AC-TEST-PARALLEL-001
"""

from __future__ import annotations

import math
import sys
import time
from typing import Dict, List, Tuple


# ── Terminal width guard ───────────────────────────────────────────────────
try:
    import shutil
    _TERM_WIDTH: int = shutil.get_terminal_size((80, 24)).columns
except Exception:
    _TERM_WIDTH = 80

# Use the real stderr (bypasses pytest-sugar / capsys capture so output
# always appears in the terminal even during parallel xdist runs).
_STDERR = sys.__stderr__ if hasattr(sys, "__stderr__") and sys.__stderr__ else sys.stderr

_SEP = "━" * min(_TERM_WIDTH, 72)


def _write(msg: str) -> None:
    """Write to real stderr, bypassing pytest-sugar/capsys capture."""
    try:
        _STDERR.write(msg)
        _STDERR.flush()
    except Exception:
        pass  # never crash the test run due to output failure


class BatchProgressReporter:
    """Real-time batch progress display for CORTEX parallel test runs.

    Writes exclusively to stderr so pytest's captured stdout remains clean.
    Tracks per-batch pass/fail counts and prints aggregated final summary.

    Args:
        total: Total number of test items in the run.
        batch_size: Number of tests per batch.
    """

    def __init__(self, total: int, batch_size: int) -> None:
        """Initialise reporter with total test count and batch size."""
        self.total = total
        self.batch_size = batch_size
        self.batch_count: int = math.ceil(total / batch_size) if batch_size else 1
        self._batches: List[Tuple[int, int, float]] = []   # (passed, failed, duration)
        self._start: float = time.monotonic()

    # ------------------------------------------------------------------ #
    # Lifecycle hooks called by plugin
    # ------------------------------------------------------------------ #

    def on_batch_start(self, batch_num: int, count: int) -> None:
        """Print batch header to stderr.

        Args:
            batch_num: 1-based batch index.
            count: Number of tests in this batch.
        """
        offset = (batch_num - 1) * self.batch_size + 1
        end_offset = min(offset + count - 1, self.total)
        msg = (
            f"\n{_SEP}\n"
            f"🧪 Batch {batch_num} / {self.batch_count}"
            f"  |  Tests {offset}–{end_offset} of {self.total}"
            f"  |  {count} tests\n"
            f"{_SEP}"
        )
        _write(msg + "\n")

    def on_batch_complete(
        self,
        batch_num: int,
        passed: int,
        failed: int,
        duration: float,
    ) -> None:
        """Print batch completion summary to stderr.

        Args:
            batch_num: 1-based batch index.
            passed: Number of tests that passed in this batch.
            failed: Number of tests that failed in this batch.
            duration: Wall-clock seconds for this batch.
        """
        self._batches.append((passed, failed, duration))
        total_done = sum(p + f for p, f, _ in self._batches)
        bar = self.render_progress_bar(done=total_done, total=self.total)
        status = "✅" if failed == 0 else "🔴"
        msg = (
            f"  {status} Batch {batch_num} done — "
            f"✅ {passed} passed  🔴 {failed} failed  ⏱ {duration:.1f}s\n"
            f"  {bar}\n"
        )
        _write(msg)

    def print_final_summary(self) -> None:
        """Print aggregated pass/fail/duration summary across all batches."""
        total_passed = sum(p for p, _, _ in self._batches)
        total_failed = sum(f for _, f, _ in self._batches)
        total_time = time.monotonic() - self._start
        overall = "✅ PASS" if total_failed == 0 else "🔴 FAIL"
        msg = (
            f"\n{_SEP}\n"
            f"🏁 CORTEX Test Run Complete — {overall}\n"
            f"   ✅ {total_passed} passed   🔴 {total_failed} failed"
            f"   ⏱ {total_time:.1f}s total\n"
            f"   📦 {len(self._batches)} batches × {self.batch_size} tests/batch\n"
            f"{_SEP}\n"
        )
        _write(msg)

    # ------------------------------------------------------------------ #
    # Rendering helpers
    # ------------------------------------------------------------------ #

    def render_progress_bar(self, done: int, total: int, width: int = 36) -> str:
        """Render an ASCII progress bar string.

        Args:
            done: Number of completed tests.
            total: Total test count.
            width: Bar width in characters.

        Returns:
            String like: [████████░░░░░░░░]  47% | ✅ 470  🔴 3
        """
        pct = done / total if total > 0 else 0
        filled = int(width * pct)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        pct_str = f"{pct * 100:.0f}%"
        return f"[{bar}] {pct_str:>4} | {done}/{total} completed"

    def render_worker_status(self, workers: Dict[str, str]) -> str:
        """Render a multi-line worker status block.

        Args:
            workers: Mapping of worker id → status string.

        Returns:
            Multi-line string, one line per worker.
        """
        lines: List[str] = []
        for wid, status in workers.items():
            icon = "✅" if status == "done" else "🔵" if status == "running" else "⚪"
            lines.append(f"  {icon} {wid}: {status}")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Chat-output builders — return strings for VS Code Copilot Chat
    # ------------------------------------------------------------------ #

    def build_chat_output(
        self,
        batch_num: int,
        passed: int,
        failed: int,
        duration: float,
    ) -> str:
        """Build an inline ASCII progress string for VS Code Copilot Chat.

        Unlike :meth:`on_batch_complete` (which writes to stderr/terminal),
        this method returns a formatted string that MCP tools can embed
        directly in their response body, making it visible in Chat.

        Args:
            batch_num: 1-based batch index.
            passed: Number of tests that passed in this batch.
            failed: Number of tests that failed in this batch.
            duration: Wall-clock seconds for this batch.

        Returns:
            Single-line ASCII string, e.g.:
            ``[████████░░░░]  67% · Batch 2/4 ✅ 450 passed  🔴 0 failed  ⏱ 3.1s``
        """
        self._batches.append((passed, failed, duration))
        total_done = sum(p + f for p, f, _ in self._batches)
        bar = self.render_progress_bar(done=total_done, total=self.total, width=20)
        status_icon = "✅" if failed == 0 else "🔴"
        return (
            f"{bar} · Batch {batch_num}/{self.batch_count} "
            f"{status_icon} {passed} passed  🔴 {failed} failed  ⏱ {duration:.1f}s"
        )

    def build_final_summary(self) -> str:
        """Build an inline final summary string for VS Code Copilot Chat.

        Returns:
            Multi-line string summarising the entire run across all batches,
            suitable for embedding in an MCP tool response.
        """
        total_passed = sum(p for p, _, _ in self._batches)
        total_failed = sum(f for _, f, _ in self._batches)
        total_time = time.monotonic() - self._start
        overall = "✅ PASS" if total_failed == 0 else "🔴 FAIL"
        bar = self.render_progress_bar(done=total_passed + total_failed, total=self.total, width=20)
        return (
            f"{bar}\n"
            f"🏁 CORTEX Batch Run — {overall}\n"
            f"   ✅ {total_passed} passed   🔴 {total_failed} failed   ⏱ {total_time:.1f}s total\n"
            f"   📦 {len(self._batches)} batches"
        )
