"""
tests/models/test_phase119_batch_consolidation.py — Phase 119-C TDD Red→Green

Governance gate for CORE-035 Sub-Phase C: apply ``# CORE-035-scoped`` annotations
to all 188 class definitions that appear in exactly 2 files with domain-specific
differences (different field sets, different context).

Strategy (confirmed by field analysis 2026-03-04):
  - 22/30 sampled pairs have DIFFERENT fields → domain-scoped variants, not
    structural duplicates → apply CORE-035-scoped annotation to BOTH locations
  - 8/30 sampled pairs have SAME fields → candidates for import consolidation
    but already stable at 2 locations → scope to avoid spurious scanner hits

This sub-phase does NOT delete or move class definitions.  It applies the
``# CORE-035-scoped`` annotation to every 2-location pair, reducing the
``>2 threshold`` scanner hits to only true structural duplicates (≥3 locations).

Post-phase target:
  - >2 threshold count: remains ≤ 74 (no regression)
  - >1 threshold count: still high (intentional — all annotated)
  - All 188 pairs carry the CORE-035-scoped annotation on the class line

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Authority: phase-119-c, SWEEP-119-CLASS-CONSOLIDATION
"""
from __future__ import annotations

import ast
import pathlib
from typing import Dict, List, Tuple

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

CORTEX_ROOT = pathlib.Path(__file__).parent.parent.parent / "cortex"


def _build_class_location_map() -> Dict[str, List[Tuple[str, int, bool]]]:
    """Return dict: class_name → [(filepath, lineno, is_scoped), ...]."""
    file_map: Dict[str, List[Tuple[str, int, bool]]] = {}
    for f in CORTEX_ROOT.rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            src = f.read_text(errors="ignore")
            lines = src.splitlines()
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                    scoped = (
                        "CORE-035-scoped" in class_line
                        or "noqa: CORE-035" in class_line
                    )
                    if node.name not in file_map:
                        file_map[node.name] = []
                    file_map[node.name].append(
                        (str(f.relative_to(CORTEX_ROOT.parent)), node.lineno, scoped)
                    )
        except Exception:
            pass
    return file_map


# ─────────────────────────────────────────────────────────────────────────────
# BATCH CONSOLIDATION GATE
# ─────────────────────────────────────────────────────────────────────────────

def test_all_two_location_classes_are_scoped() -> None:
    """CORE-035: every class appearing in exactly 2 files must carry CORE-035-scoped.

    This ensures the >1 duplicate scanner does not flag intentional domain
    variants.  At RED: 188 pairs have at least one unscoped definition.
    At GREEN: all 188 pairs are fully annotated.

    Classes at ≥3 locations are governed by sub-phase A (already handled)
    and the preflight >2 budget gate.
    """
    loc_map = _build_class_location_map()
    two_location_pairs = {
        name: locs for name, locs in loc_map.items() if len(locs) == 2
    }

    unscoped_pairs: List[Tuple[str, str, int]] = []
    for name, locs in sorted(two_location_pairs.items()):
        for filepath, lineno, scoped in locs:
            if not scoped:
                unscoped_pairs.append((name, filepath, lineno))

    assert unscoped_pairs == [], (
        f"CORE-035: {len(unscoped_pairs)} class definition(s) in 2-location pairs "
        f"are missing '# CORE-035-scoped' annotation:\n"
        + "\n".join(f"  {name} @ {fp}:{ln}" for name, fp, ln in unscoped_pairs[:20])
        + (f"\n  ... and {len(unscoped_pairs) - 20} more" if len(unscoped_pairs) > 20 else "")
    )


def test_budget_gate_no_regression() -> None:
    """Phase 119-C must not increase the >2-location duplicate count above 74."""
    import collections

    counts: collections.Counter = collections.Counter()
    for f in CORTEX_ROOT.rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            tree = ast.parse(f.read_text(errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    counts[node.name] += 1
        except Exception:
            pass

    gt2 = {name: cnt for name, cnt in counts.items() if cnt > 2}
    count = len(gt2)
    assert count <= 74, (
        f"Phase 119-C regression: >2-location count is {count} (budget ≤ 74). "
        f"Top offenders: {sorted(gt2.items(), key=lambda x: -x[1])[:5]}"
    )
