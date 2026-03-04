"""
HistoryTracker — hash-based change tracking for registry snapshots.

Stores timestamped JSON snapshots of parsed model state.
Supports:
- snapshot(): persist current model hashes
- list_snapshots(): list available snapshot files
- diff(): compare last two snapshots (added / removed / changed)
- max_snapshots cap (default 50) to avoid unbounded growth
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


class HistoryTracker:
    """Persist model snapshots and detect changes between them."""

    def __init__(self, storage_dir: str, max_snapshots: int = 50) -> None:
        self._storage_dir = storage_dir
        self._max_snapshots = max_snapshots
        os.makedirs(self._storage_dir, exist_ok=True)

    # ── public API ──────────────────────────────────────────────────────

    def snapshot(self, models: List[BaseRegistryModel]) -> str:
        """Write a timestamped snapshot and return its file path."""
        ts = time.time()
        filename = f"snapshot_{ts:.6f}.json"
        path = os.path.join(self._storage_dir, filename)

        data: Dict[str, Any] = {
            "timestamp": ts,
            "artifact_count": len(models),
            "artifacts": {},
        }
        for m in models:
            data["artifacts"][m.id] = {
                "type": m.type,
                "title": m.title,
                "source_file": m.source_file,
                "hash": m.stable_hash(),
            }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)

        self._enforce_cap()
        return path

    def list_snapshots(self) -> List[str]:
        """Return sorted list of snapshot file paths (oldest first)."""
        files = [
            os.path.join(self._storage_dir, fn)
            for fn in os.listdir(self._storage_dir)
            if fn.startswith("snapshot_") and fn.endswith(".json")
        ]
        files.sort()
        return files

    def diff(self) -> Dict[str, List[Dict[str, Any]]]:
        """Compare the two most recent snapshots.

        Returns dict with keys: added, removed, changed.
        If fewer than 2 snapshots exist, returns empty lists.
        """
        snaps = self.list_snapshots()
        empty: Dict[str, List[Dict[str, Any]]] = {"added": [], "removed": [], "changed": []}
        if len(snaps) < 2:
            return empty

        old = self._load(snaps[-2])
        new = self._load(snaps[-1])

        old_arts = old.get("artifacts", {})
        new_arts = new.get("artifacts", {})

        old_ids = set(old_arts.keys())
        new_ids = set(new_arts.keys())

        added = [{"id": aid, **new_arts[aid]} for aid in sorted(new_ids - old_ids)]
        removed = [{"id": rid, **old_arts[rid]} for rid in sorted(old_ids - new_ids)]
        changed: List[Dict[str, Any]] = []
        for cid in sorted(old_ids & new_ids):
            if old_arts[cid].get("hash") != new_arts[cid].get("hash"):
                changed.append({
                    "id": cid,
                    "old_hash": old_arts[cid].get("hash", ""),
                    "new_hash": new_arts[cid].get("hash", ""),
                })

        return {"added": added, "removed": removed, "changed": changed}

    # ── private helpers ─────────────────────────────────────────────────

    def _load(self, path: str) -> Dict[str, Any]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]

    def _enforce_cap(self) -> None:
        """Delete oldest snapshots beyond max_snapshots."""
        snaps = self.list_snapshots()
        while len(snaps) > self._max_snapshots:
            os.remove(snaps.pop(0))
