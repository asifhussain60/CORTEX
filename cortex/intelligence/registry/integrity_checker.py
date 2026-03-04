"""
IntegrityChecker — validates registry model health.

Checks:
- Broken references (integrity.all_refs_resolved == False)
- Duplicate IDs across all models
- Schema validity flags
- Type-level breakdown

Produces a structured report dict suitable for JSON serialisation
and rendering in the integrity dashboard (Phase 125-g).
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


class IntegrityChecker:
    """Analyse a list of parsed registry models for integrity issues."""

    # ── public API ──────────────────────────────────────────────────────

    def check(self, models: List[BaseRegistryModel]) -> Dict[str, Any]:
        """Return a structured integrity report for *models*."""
        broken: List[Dict[str, Any]] = []
        warnings: List[str] = []
        type_counter: Counter[str] = Counter()
        seen_ids: Dict[str, List[str]] = {}  # id -> list of source_files

        for m in models:
            type_counter[m.type] += 1
            # track duplicates
            seen_ids.setdefault(m.id, []).append(m.source_file)

            integrity = m.integrity or {}
            if not integrity.get("all_refs_resolved", True):
                broken.append({
                    "id": m.id,
                    "type": m.type,
                    "source_file": m.source_file,
                    "warnings": integrity.get("warnings", []),
                })
                for w in integrity.get("warnings", []):
                    warnings.append(f"[{m.id}] {w}")

        # duplicate detection
        duplicate_ids: List[Dict[str, Any]] = []
        for mid, files in seen_ids.items():
            if len(files) > 1:
                duplicate_ids.append({"id": mid, "source_files": files})
                warnings.append(f"Duplicate ID '{mid}' found in {len(files)} files")

        return {
            "total_artifacts": len(models),
            "healthy_count": len(models) - len(broken),
            "broken_count": len(broken),
            "broken_artifacts": broken,
            "duplicate_ids": duplicate_ids,
            "warnings": warnings,
            "types": dict(type_counter),
        }

    def to_json(self, report: Dict[str, Any]) -> str:
        """Serialise *report* to deterministic JSON."""
        return json.dumps(report, indent=2, sort_keys=True)
