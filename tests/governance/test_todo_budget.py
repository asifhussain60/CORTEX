"""
GAP-128-H-01: TODO/FIXME/HACK/XXX count exceeds threshold.

The production codebase must keep technical-debt markers below a strict
budget. This test enforces the budget and prevents silent accumulation.

Drift lock: check-47-production-purity-lock.yaml
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = REPO_ROOT / "cortex"

# ── Budget thresholds ──────────────────────────────────────────────────────
# Measured 2026-03-05: 41 instances in production code (excluding test files).
# Budget set to current count + 5 grace. Must DECREASE over time, never grow.
TODO_BUDGET = 50  # Must not exceed
FIXME_BUDGET = 20
HACK_BUDGET = 10
XXX_BUDGET = 10


def _count_marker(marker: str) -> list[str]:
    """Return lines matching `marker` in cortex/ production Python files.

    Uses pure-Python scanning for Windows portability (no grep dependency).
    """
    pattern = re.compile(marker)
    hits: list[str] = []
    for py_file in SRC_ROOT.rglob("*.py"):
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                if pattern.search(line):
                    hits.append(f"{py_file}:{i}: {line.strip()[:120]}")
        except OSError:
            continue
    return hits


class TestTodoBudget:
    """Technical-debt markers must stay within defined budgets."""

    def test_todo_count_within_budget(self):
        """TODO markers in cortex/ must not exceed budget."""
        hits = _count_marker("TODO")
        assert len(hits) <= TODO_BUDGET, (
            f"TODO count {len(hits)} exceeds budget {TODO_BUDGET}. "
            f"Reduce TODOs before adding new ones.\n"
            + "\n".join(hits[:20])
        )

    def test_fixme_count_within_budget(self):
        """FIXME markers in cortex/ must not exceed budget."""
        hits = _count_marker("FIXME")
        assert len(hits) <= FIXME_BUDGET, (
            f"FIXME count {len(hits)} exceeds budget {FIXME_BUDGET}.\n"
            + "\n".join(hits[:20])
        )

    def test_hack_count_within_budget(self):
        """HACK markers in cortex/ must not exceed budget."""
        hits = _count_marker(r"\bHACK\b")
        assert len(hits) <= HACK_BUDGET, (
            f"HACK count {len(hits)} exceeds budget {HACK_BUDGET}.\n"
            + "\n".join(hits[:10])
        )

    def test_xxx_count_within_budget(self):
        """XXX markers in cortex/ must not exceed budget."""
        hits = _count_marker(r"\bXXX\b")
        assert len(hits) <= XXX_BUDGET, (
            f"XXX count {len(hits)} exceeds budget {XXX_BUDGET}.\n"
            + "\n".join(hits[:10])
        )

    def test_total_debt_markers_stable(self):
        """Combined total of all debt markers must be ≤ 100."""
        total = sum(
            len(_count_marker(m)) for m in ["TODO", "FIXME", r"\bHACK\b", r"\bXXX\b"]
        )
        assert total <= 100, (
            f"Total debt markers ({total}) exceeds combined budget of 100."
        )
