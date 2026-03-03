"""
tests/preflight/test_noqa_budget.py — Phase 114-c RED→GREEN

Enforces CORE-035 suppression budget.
Acceptance criteria from GAP-114-04:
  - Bare CORE-035 (without -scoped or justification suffix) count ≤ 50
  - CORE-035-scoped is the approved form for domain-specific variants
  - All bare suppressions must have justification after the governance tag

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Phase: 114-c
"""
import pathlib
import re
import pytest


NOQA_BUDGET = 50

# Match bare CORE-035 governance annotations in comments (not docstrings or code references)
# # CORE-035-scoped ...          → APPROVED (domain-specific with dash-qualifier)
# # CORE-035 — justification     → APPROVED (em-dash justification)
# # CORE-035 <any text>          → APPROVED (any following text counts as justification)
# # CORE-035                     → BARE (no justification — needs review)
BARE_NOQA_PATTERN = re.compile(r"#\s*CORE-035(?![-\w])\s*$")


def _scan_bare_suppressions() -> list[tuple[str, int, str]]:
    """Return (filepath, lineno, line) for bare # CORE-035 with no justification text."""
    results = []
    for f in pathlib.Path("cortex").rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if BARE_NOQA_PATTERN.search(line):
                    results.append((str(f), i, line.strip()))
        except Exception:
            pass
    return results


def test_core035_bare_suppression_count_under_budget():
    """Bare CORE-035 (no -scoped, no justification) count must be ≤ 50.

    Approved alternatives:
    - CORE-035-scoped — <domain reason>     (domain-specific variant)
    - CORE-035  # <justification>            (explicit justification)
    """
    suppressions = _scan_bare_suppressions()
    count = len(suppressions)
    assert count <= NOQA_BUDGET, (
        f"Bare CORE-035 suppression count is {count} (budget ≤ {NOQA_BUDGET}). "
        f"Use 'CORE-035-scoped — <reason>' or 'CORE-035  # <reason>' instead.\n"
        f"First 10:\n" + "\n".join(f"  {f}:{l}" for f, l, _ in suppressions[:10])
    )


def test_all_bare_suppressions_use_approved_form():
    """Every CORE-035 must either be -scoped or have justification comment.

    This test ensures no bare, unjustified suppressions creep back in.
    """
    suppressions = _scan_bare_suppressions()
    if suppressions:
        pytest.fail(
            f"Found {len(suppressions)} bare CORE-035 without -scoped or justification:\n"
            + "\n".join(f"  {f}:{l}: {line[:80]}" for f, l, line in suppressions[:10])
        )

