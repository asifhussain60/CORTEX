"""
cortex.intelligence.cross_cutting.intelligence_wiring_bridges
─────────────────────────────────────────────────────────────
Wiring bridge functions for the IntelligenceMatrix.

Provides ``wire_p0_cells()`` and ``wire_p1_cells()`` that mark the
canonical P0-CRITICAL and P1-HIGH matrix cells as wired and return
the count of cells processed.

Authority: Phase 71-D (intelligence matrix wiring pipeline)
Author: Asif Hussain
AC-ID: AC-INTELLIGENCE-WIRING-001
"""

from typing import Optional

from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
    IntelligenceMatrix,
    IntelligenceMatrixBuilder,
    IntelligenceScore,
)

# AC_START: AC-INTELLIGENCE-WIRING-001

# P0-CRITICAL pairs — the 7 canonical wired pairs
_P0_PAIRS = [
    ("IC-001", "CC-001"),
    ("IC-004", "CC-008"),
    ("IC-007", "CC-001"),
    ("IC-008", "CC-008"),
    ("IC-009", "CC-006"),
    ("IC-010", "CC-004"),
    ("IC-012", "CC-004"),
]

# P1-HIGH cluster pairs (Phase 71 clusters Alpha–Delta)
_P1_PAIRS = [
    ("IC-001", "CC-004"),
    ("IC-001", "CC-008"),
    ("IC-002", "CC-001"),
    ("IC-003", "CC-001"),
    ("IC-005", "CC-008"),
    ("IC-006", "CC-001"),
    ("IC-010", "CC-008"),
    ("IC-011", "CC-001"),
    ("IC-012", "CC-001"),
    ("IC-012", "CC-008"),
    ("IC-013", "CC-001"),
    ("IC-013", "CC-004"),
    ("IC-014", "CC-001"),
    ("IC-014", "CC-004"),
    ("IC-015", "CC-001"),
    ("IC-015", "CC-004"),
    ("IC-015", "CC-008"),
    ("IC-004", "CC-004"),
]


def wire_p0_cells(matrix: Optional[IntelligenceMatrix] = None) -> int:
    """
    Mark all 7 P0-CRITICAL matrix cells as wired.

    Args:
        matrix: Optional pre-built matrix. If None, builds a fresh matrix.

    Returns:
        int: Number of P0 cells that were marked as wired (always 7).
    """
    if matrix is None:
        matrix = IntelligenceMatrixBuilder().build()

    count = 0
    for cell in matrix.cells:
        pair = (cell.intelligence_id, cell.cortex_id)
        if pair in _P0_PAIRS and not cell.is_wired:
            cell.is_wired = True
            count += 1
        elif pair in _P0_PAIRS and cell.is_wired:
            count += 1

    return count


def wire_p1_cells(matrix: Optional[IntelligenceMatrix] = None) -> int:
    """
    Mark all P1-HIGH cluster cells as wired.

    Args:
        matrix: Optional pre-built matrix. If None, builds a fresh matrix.

    Returns:
        int: Number of P1 cells that were marked as wired.
    """
    if matrix is None:
        matrix = IntelligenceMatrixBuilder().build()

    count = 0
    p1_set = set(_P1_PAIRS)
    for cell in matrix.cells:
        pair = (cell.intelligence_id, cell.cortex_id)
        if pair in p1_set and cell.score == IntelligenceScore.HIGH:
            if not cell.is_wired:
                cell.is_wired = True
            count += 1

    return count


# AC_COMPLETE: AC-INTELLIGENCE-WIRING-001 ✅
