"""
DecisionJournal — Architecture decision recording and retrieval.

Phase 24.4: Layer 4 Architecture Evolution Tracking
"""
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class DecisionJournal:
    """Records and retrieves architecture decisions as YAML files."""

    def __init__(self, journal_dir: "str | Path") -> None:
        """Initialize instance."""
        self._dir = Path(journal_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    # ── Write ──────────────────────────────────────────────────────────────

    def record_decision(
        self,
        decision: str,
        rationale: str,
        alternatives: List[str],
        impact: str,
        challenge_verdict: Optional[str] = None,
        dor_approved: Optional[bool] = None,
        execution_outcome: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Record a new decision to the journal.

        Args:
            decision: The decision text.
            rationale: Why this decision was made.
            alternatives: Alternative approaches considered.
            impact: Expected impact of the decision.
            challenge_verdict: Optional challenge gate result.
            dor_approved: Optional Definition of Ready approval flag.
            execution_outcome: Optional outcome after execution.
            **kwargs: Additional metadata fields.

        Returns:
            The generated decision ID.
        """
        if not decision:
            raise ValueError("'decision' field is required and cannot be empty")

        timestamp = datetime.utcnow()
        decision_id = f"decision-{timestamp.strftime('%Y%m%d-%H%M%S')}"

        data: Dict[str, Any] = {
            "id": decision_id,
            "timestamp": timestamp.isoformat(),
            "decision": decision,
            "rationale": rationale,
            "alternatives": alternatives,
            "impact": impact,
        }
        if challenge_verdict is not None:
            data["challenge_verdict"] = challenge_verdict
        if dor_approved is not None:
            data["dor_approved"] = dor_approved
        if execution_outcome is not None:
            data["execution_outcome"] = execution_outcome
        data.update(kwargs)

        file_path = self._dir / f"{decision_id}.yaml"
        file_path.write_text(yaml.dump(data, allow_unicode=True))
        return decision_id

    def update_decision(self, decision_id: str, **updates: Any) -> bool:
        """Update an existing decision with new fields.

        Args:
            decision_id: The ID of the decision to update.
            **updates: Key-value pairs to merge into the decision.

        Returns:
            True if the decision was found and updated, False otherwise.
        """
        file_path = self._dir / f"{decision_id}.yaml"
        if not file_path.exists():
            return False
        data = yaml.safe_load(file_path.read_text()) or {}
        data.update(updates)
        file_path.write_text(yaml.dump(data, allow_unicode=True))
        return True

    # ── Read ───────────────────────────────────────────────────────────────

    def load_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Load a single decision by its ID.

        Args:
            decision_id: The ID of the decision to load.

        Returns:
            The decision data dict, or None if not found.
        """
        file_path = self._dir / f"{decision_id}.yaml"
        if not file_path.exists():
            return None
        return yaml.safe_load(file_path.read_text())

    def load_all_decisions(self) -> List[Dict[str, Any]]:
        """Load all decisions from the journal directory.

        Returns:
            List of decision data dicts, sorted by filename.
        """
        decisions = []
        for f in sorted(self._dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(f.read_text())
                if data:
                    decisions.append(data)
            except Exception:
                pass
        return decisions

    def search_decisions(self, **criteria: Any) -> List[Dict[str, Any]]:
        """Search decisions matching all given criteria.

        Args:
            **criteria: Key-value pairs to match against decision fields.

        Returns:
            List of decisions where all criteria match.
        """
        results = []
        for decision in self.load_all_decisions():
            if all(decision.get(k) == v for k, v in criteria.items()):
                results.append(decision)
        return results
