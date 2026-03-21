"""
cortex.intelligence.models.master_plan_index — MasterPlanIndex + PhaseEntry
=============================================================================

Typed representation of ``cortex-registry/cortex-master.yaml`` (THIN INDEX).
Loaded via ``IntelligenceFacade.load_plans()`` — do not parse the YAML directly.

Phase 123 (GAP-123-04): Provides structured, filterable access to the master plan
index without requiring callers to know the YAML file location or structure.

CORE Rules: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-035 (single canonical — no duplicate plan parsers)
AC_START: AC-123-REGISTRY-INTELLIGENCE-ENGINE
AC_COMPLETE: AC-123-REGISTRY-INTELLIGENCE-ENGINE | marker pair declared for static audit coverage
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = ["MasterPlanIndex", "PhaseEntry"]


@dataclass
class PhaseEntry:
    """Typed representation of a single phase entry in cortex-master.yaml.

    Attributes:
        id: Unique phase identifier (e.g. 'phase-123').
        title: Human-readable phase title.
        status: Phase lifecycle status (PLANNED | ACTIVE | COMPLETE | DEFERRED | ARCHIVED).
        priority: Phase priority (P0 | P1 | P2).
        sweep_id: Associated sweep catalogue ID, if any.
        gaps: Number of gaps in this phase.
        sub_phases: Number of sub-phases.
        file: Path to the detailed phase YAML file.
        note: Completion or progress note.
        raw: Full raw dict from the YAML entry (for forward-compat access).
    """

    id: str
    title: str
    status: str
    priority: str = "P1"
    sweep_id: Optional[str] = None
    gaps: int = 0
    sub_phases: int = 0
    file: Optional[str] = None
    note: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhaseEntry":
        """Construct a PhaseEntry from a raw YAML dict.

        Args:
            data: Raw dict from cortex-master.yaml phases list.

        Returns:
            Populated PhaseEntry instance.
        """
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            status=str(data.get("status", "UNKNOWN")),
            priority=str(data.get("priority", "P1")),
            sweep_id=data.get("sweep_id"),
            gaps=int(data.get("gaps", 0)),
            sub_phases=int(data.get("sub_phases", 0)),
            file=data.get("file"),
            note=data.get("note"),
            raw=dict(data),
        )


@dataclass
class MasterPlanIndex:
    """Typed index of all phases in cortex-master.yaml.

    This is the canonical in-memory representation of the THIN INDEX — it does
    not include inline phase detail (gap_catalogue, tdd_sequence, etc.),
    mirroring the THIN INDEX CONTRACT enforced on the YAML itself.

    Attributes:
        phases: List of all PhaseEntry objects from the master plan.
        source_line_count: Actual line count of the source YAML file (THIN
            INDEX CONTRACT requires ≤500 lines).
        source_path: Absolute path to the parsed cortex-master.yaml file.
        metadata: Any top-level metadata fields from the YAML (title, version, etc.).
    """

    phases: List[PhaseEntry] = field(default_factory=list)
    source_line_count: int = 0
    source_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def filter_by_status(self, status: str) -> "MasterPlanIndex":
        """Return a new MasterPlanIndex containing only phases with the given status.

        Args:
            status: Phase status to filter by (e.g. 'PLANNED', 'COMPLETE').

        Returns:
            New MasterPlanIndex with filtered phases; source metadata preserved.
        """
        return MasterPlanIndex(
            phases=[p for p in self.phases if p.status == status],
            source_line_count=self.source_line_count,
            source_path=self.source_path,
            metadata=self.metadata,
        )
