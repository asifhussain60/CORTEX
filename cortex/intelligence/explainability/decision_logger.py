"""
ENH-068 Stage 4: Decision Traceability Logger
Decision logging with audit trail generation
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class DecisionType(Enum):
    """Types of decisions tracked"""
    RESOLUTION = "resolution"
    VALIDATION = "validation"
    APPROVAL = "approval"
    REJECTION = "rejection"


class DecisionOutcome(Enum):
    """Decision outcome types"""
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class DecisionLog:
    """
    Log entry for a decision

    Attributes:
        decision_id: Unique decision identifier
        decision_type: Type of decision
        context: Decision context data
        outcome: Decision outcome
        rationale: Human-readable rationale
        confidence: Confidence score (0.0-1.0)
        timestamp: When decision was made
        metadata: Additional metadata
    """
    decision_type: DecisionType
    context: Dict[str, Any]
    outcome: DecisionOutcome
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rationale: str = ""
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DecisionTraceabilityLogger:
    """
    Decision Traceability Logger

    Features:
    - Decision logging with context
    - History retrieval with filtering
    - Audit trail generation
    - Decision outcome tracking
    """

    def __init__(self) -> None:
        """Initialize decision logger"""
        self._history: List[DecisionLog] = []

    def log_decision(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        outcome: DecisionOutcome,
        rationale: str = "",
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DecisionLog:
        """
        Log a decision

        Args:
            decision_type: Type of decision
            context: Decision context data
            outcome: Decision outcome
            rationale: Human-readable rationale
            confidence: Confidence score
            metadata: Additional metadata

        Returns:
            Decision log entry
        """
        decision = DecisionLog(
            decision_type=decision_type,
            context=context,
            outcome=outcome,
            rationale=rationale,
            confidence=confidence,
            metadata=metadata or {}
        )

        self._history.append(decision)

        return decision

    def get_history(
        self,
        decision_type: Optional[DecisionType] = None,
        outcome: Optional[DecisionOutcome] = None,
        since: Optional[datetime] = None
    ) -> List[DecisionLog]:
        """
        Retrieve decision history with optional filtering

        Args:
            decision_type: Filter by decision type
            outcome: Filter by outcome
            since: Filter decisions since timestamp

        Returns:
            Filtered decision history
        """
        filtered = self._history

        if decision_type:
            filtered = [d for d in filtered if d.decision_type == decision_type]

        if outcome:
            filtered = [d for d in filtered if d.outcome == outcome]

        if since:
            filtered = [d for d in filtered if d.timestamp >= since]

        return filtered

    def generate_audit_trail(
        self,
        decision_type: Optional[DecisionType] = None
    ) -> str:
        """
        Generate human-readable audit trail

        Args:
            decision_type: Filter by decision type

        Returns:
            Formatted audit trail string
        """
        decisions = self.get_history(decision_type=decision_type)

        if not decisions:
            return "No decisions logged"

        lines = ["=" * 60, "Decision Audit Trail", "=" * 60, ""]

        for decision in decisions:
            lines.append(f"Decision ID: {decision.decision_id}")
            lines.append(f"Type: {decision.decision_type.value.upper()}")
            lines.append(f"Outcome: {decision.outcome.value.upper()}")
            lines.append(f"Timestamp: {decision.timestamp.isoformat()}")
            lines.append(f"Confidence: {decision.confidence:.2%}")

            if decision.rationale:
                lines.append(f"Rationale: {decision.rationale}")

            if decision.context:
                lines.append("Context:")
                for key, value in decision.context.items():
                    lines.append(f"  - {key}: {value}")

            lines.append("-" * 60)

        lines.append(f"\nTotal Decisions: {len(decisions)}")

        return "\n".join(lines)
