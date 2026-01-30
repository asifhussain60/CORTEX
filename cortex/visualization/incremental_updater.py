"""Incremental Knowledge Updates (STATIC-VIZ-007)."""
from typing import List, Dict, Any

class IncrementalUpdater:
    def detect_changes(self, old_repos: List[Dict[str, Any]], new_repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        changed = []
        for new in new_repos:
            old = next((r for r in old_repos if r["repo"] == new["repo"]), None)
            if not old or old.get("ts") != new.get("ts"):
                changed.append(new)
        return changed
