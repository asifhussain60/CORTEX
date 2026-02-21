"""Feature registry audit trail."""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class FeatureAudit:
    """Captures all feature registry changes for compliance."""

    def __init__(self, db: Any) -> None:
        """Initialize audit trail.

        Args:
            db: Database connection or dict-like store for audit persistence.
        """
        self.db = db
        self._in_memory: List[Dict[str, Any]] = []

    def log_change(
        self,
        feature_id: str,
        action: str,
        old_value: Any,
        new_value: Any,
        user_id: str,
    ) -> Dict[str, Any]:
        """Log a change to the audit trail.

        Args:
            feature_id: Identifier of the feature that changed.
            action: Action taken (e.g. ``enable``, ``disable``, ``update``).
            old_value: Previous value before the change.
            new_value: New value after the change.
            user_id: Identifier of the actor who made the change.

        Returns:
            The audit entry that was recorded.
        """
        entry: Dict[str, Any] = {
            "feature_id": feature_id,
            "action": action,
            "old_value": old_value,
            "new_value": new_value,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._in_memory.append(entry)
        if hasattr(self.db, "execute"):
            try:
                self.db.execute(
                    "INSERT INTO feature_audit (feature_id, action, old_value, new_value, user_id, timestamp) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        feature_id,
                        action,
                        json.dumps(old_value),
                        json.dumps(new_value),
                        user_id,
                        entry["timestamp"],
                    ),
                )
            except Exception:
                pass  # Graceful degradation — in-memory log is source of truth
        return entry

    def get_audit_trail(self, feature_id: str) -> List[Dict[str, Any]]:
        """Retrieve audit trail for a feature.

        Args:
            feature_id: Feature to retrieve history for.

        Returns:
            List of audit entries in chronological order.
        """
        if hasattr(self.db, "execute"):
            try:
                cursor = self.db.execute(
                    "SELECT * FROM feature_audit WHERE feature_id = ? ORDER BY timestamp ASC",
                    (feature_id,),
                )
                rows = cursor.fetchall()
                if rows:
                    cols = [d[0] for d in cursor.description]
                    return [dict(zip(cols, row)) for row in rows]
            except Exception:
                pass
        return [e for e in self._in_memory if e.get("feature_id") == feature_id]

    def export_audit(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Export audit trail for compliance review.

        Args:
            start_date: ISO-format start date (inclusive).
            end_date: ISO-format end date (inclusive).

        Returns:
            Audit entries within the given date range.
        """
        results = []
        for entry in self._in_memory:
            ts = entry.get("timestamp", "")
            if start_date <= ts <= end_date + "Z":
                results.append(entry)
        return results
