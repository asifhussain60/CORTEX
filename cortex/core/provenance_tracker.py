"""COMPAT shim — cortex.core.provenance_tracker → cortex.core.core.provenance_tracker.

Phase 58: Canonical implementation lives in cortex/core/core/provenance_tracker.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.provenance_tracker import ProvenanceType, EvidenceType, ProvenanceEntry, EvidenceBundle, ProvenanceTracker

__all__ = ["ProvenanceType", "EvidenceType", "ProvenanceEntry", "EvidenceBundle", "ProvenanceTracker"]
