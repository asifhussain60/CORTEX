"""
tests/preflight/test_noqa_budget.py — Phase 114-c RED→GREEN

Enforces noqa:CORE-035 suppression budget.
Acceptance criteria from GAP-114-04:
  - Bare noqa:CORE-035 (without -scoped or justification suffix) count ≤ 50
  - noqa:CORE-035-scoped is the approved form for domain-specific variants
  - All bare suppressions must have justification after the noqa tag

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Phase: 114-c
"""
import pathlib
import re
import pytest


NOQA_BUDGET = 50

# Match bare CORE-035 (not -scoped, not justified)
# noqa: CORE-035-scoped ...          → APPROVED (domain-specific with dash-qualifier)
# noqa: CORE-035 # justification     → APPROVED (explicit # comment)
# noqa: CORE-035 — justification     → APPROVED (em-dash justification)
# noqa: CORE-035-domain ...          → APPROVED (any dash-qualifier)
BARE_NOQA_PATTERN = re.compile(r"noqa:\s*CORE-035(?!-)")
JUSTIFIED_HASH = re.compile(r"noqa:\s*CORE-035\s*#\s*\S")
JUSTIFIED_EMDASH = re.compile(r"noqa:\s*CORE-035\s*[—–]\s*\S")


def _scan_bare_suppressions() -> list[tuple[str, int, str]]:
    """Return (filepath, lineno, line) for bare noqa:CORE-035 without justification."""
    results = []
    for f in pathlib.Path("cortex").rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if BARE_NOQA_PATTERN.search(line):
                    # Any dash-qualified form (-scoped, -domain, etc.) is approved
                    # Already excluded by BARE_NOQA_PATTERN (uses negative lookahead for -)
                    # noqa: CORE-035 # <reason> is acceptable
                    if JUSTIFIED_HASH.search(line):
                        continue
                    # noqa: CORE-035 — <reason> or – <reason> is acceptable
                    if JUSTIFIED_EMDASH.search(line):
                        continue
                    results.append((str(f), i, line.strip()))
        except Exception:
            pass
    return results


def test_core035_bare_suppression_count_under_budget():
    """Bare noqa:CORE-035 (no -scoped, no justification) count must be ≤ 50.

    Approved alternatives:
    - noqa: CORE-035-scoped — <domain reason>     (domain-specific variant)
    - noqa: CORE-035  # <justification>            (explicit justification)
    """
    suppressions = _scan_bare_suppressions()
    count = len(suppressions)
    assert count <= NOQA_BUDGET, (
        f"Bare noqa:CORE-035 suppression count is {count} (budget ≤ {NOQA_BUDGET}). "
        f"Use 'noqa: CORE-035-scoped — <reason>' or 'noqa: CORE-035  # <reason>' instead.\n"
        f"First 10:\n" + "\n".join(f"  {f}:{l}" for f, l, _ in suppressions[:10])
    )


def test_all_bare_suppressions_use_approved_form():
    """Every noqa:CORE-035 must either be -scoped or have justification comment.

    This test ensures no bare, unjustified suppressions creep back in.
    """
    suppressions = _scan_bare_suppressions()
    if suppressions:
        pytest.fail(
            f"Found {len(suppressions)} bare noqa:CORE-035 without -scoped or justification:\n"
            + "\n".join(f"  {f}:{l}: {line[:80]}" for f, l, line in suppressions[:10])
        )
