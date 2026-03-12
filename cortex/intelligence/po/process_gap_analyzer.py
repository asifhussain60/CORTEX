"""Process Gap Analyzer — detects process anti-patterns from work item history (GAP-129-01)."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List


class ProcessGapAnalyzer:
    """Identifies recurring process anti-patterns from ADO/Jira work item history.

    Detects three categories:
        scope_creep — stories added after sprint start
        cycle_time_spike — stories taking significantly longer than baseline
        recurring_blocked — items blocked (or with "blocked" tags) in multiple sprints
    """

    BLOCKED_KEYWORDS = frozenset({"blocked", "impediment", "waiting", "on hold", "dependency"})
    CYCLE_TIME_SPIKE_MULTIPLIER: float = 2.0  # spike if > 2× baseline

    def analyze(self, work_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyse a list of work items and return detected anti-patterns.

        Args:
            work_items: list of canonical work item dicts (see WorkItemClient).
                Additional optional keys used here:
                    sprint_added_at (str) — ISO timestamp when added to sprint
                    sprint_started_at (str) — ISO sprint start timestamp
                    cycle_time_days (float) — actual cycle time
                    sprint_id (str) — sprint identifier for recurrence detection

        Returns:
            dict with keys: scope_creep, cycle_time_spikes, recurring_blocked
            Each value is a list of work item dicts that exhibit the anti-pattern.
        """
        scope_creep = self._detect_scope_creep(work_items)
        cycle_time_spikes = self._detect_cycle_time_spikes(work_items)
        recurring_blocked = self._detect_recurring_blocked(work_items)

        return {
            "scope_creep": scope_creep,
            "cycle_time_spikes": cycle_time_spikes,
            "recurring_blocked": recurring_blocked,
        }

    def summary(self, work_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Return anti-pattern counts for quick reporting."""
        result = self.analyze(work_items)
        return {category: len(items) for category, items in result.items()}

    # ── Private helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _detect_scope_creep(work_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stories where sprint_added_at > sprint_started_at = scope creep."""
        out = []
        for item in work_items:
            added = item.get("sprint_added_at", "")
            started = item.get("sprint_started_at", "")
            if added and started and added > started:
                out.append(item)
        return out

    def _detect_cycle_time_spikes(
        self, work_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Items with cycle_time_days > CYCLE_TIME_SPIKE_MULTIPLIER × baseline."""
        times = [
            float(item["cycle_time_days"])
            for item in work_items
            if item.get("cycle_time_days") is not None
        ]
        if not times:
            return []
        baseline = sum(times) / len(times)
        threshold = baseline * self.CYCLE_TIME_SPIKE_MULTIPLIER
        return [
            item
            for item in work_items
            if (item.get("cycle_time_days") or 0) > threshold
        ]

    def _detect_recurring_blocked(
        self, work_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Items with blocked keywords that appear across multiple sprints."""
        blocked_per_sprint: Dict[str, list] = defaultdict(list)
        for item in work_items:
            text = (
                f"{item.get('title', '')} {item.get('description', '')} {item.get('tags', '')}"
            ).lower()
            is_blocked = any(kw in text for kw in self.BLOCKED_KEYWORDS)
            if is_blocked:
                sprint_id = item.get("sprint_id", "unknown")
                blocked_per_sprint[sprint_id].append(item)

        # Return items that appear blocked in more than one sprint
        multi_sprint_blocked = [
            item
            for items in blocked_per_sprint.values()
            if len(blocked_per_sprint) > 1
            for item in items
        ]
        return multi_sprint_blocked
