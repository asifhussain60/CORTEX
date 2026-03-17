"""Detection and Recovery - Detect and recover from hallucination events.

Provides detection of hallucination patterns and recovery mechanisms.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum

class ConfidenceLevel(Enum):
    """Confidence score buckets."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ConfidenceScore:
    """Confidence score with rationale and evidence."""

    value: float
    reasoning: str
    fact_checks: List[str] = field(default_factory=list)
    evidence_sources: List[str] = field(default_factory=list)

    def get_level(self) -> ConfidenceLevel:
        """Classify confidence level from numeric value."""
        if self.value < 0.2:
            return ConfidenceLevel.VERY_LOW
        if self.value < 0.5:
            return ConfidenceLevel.LOW
        if self.value < 0.7:
            return ConfidenceLevel.MEDIUM
        if self.value < 0.9:
            return ConfidenceLevel.HIGH
        return ConfidenceLevel.VERY_HIGH


class HallucinationRisk(Enum):
    """Risk severity for hallucination detection results."""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HallucinationAssessment:
    """Assessment payload returned by detect_hallucinations."""

    is_safe: bool
    confidence_score: ConfidenceScore
    hallucination_risk: HallucinationRisk
    detected_hallucinations: List[str] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    evidence_sources: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DetectionResult:
    """Simple result wrapper for hallucination detection compatibility."""

    success: bool
    value: Optional[HallucinationAssessment] = None
    error: Optional[str] = None


class HallucinationPattern(Enum):
    """Types of hallucination patterns."""

    FACTUAL_ERROR = "factual_error"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    CONTEXT_DRIFT = "context_drift"
    CONFABULATION = "confabulation"
    INCONSISTENCY = "inconsistency"


class CorruptionType(Enum):
    """Types of corruption detected."""

    STATE_MISMATCH = "state_mismatch"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    CONSENSUS_VIOLATION = "consensus_violation"


class RecoveryStrategy(Enum):
    """Recovery strategies."""

    RESTORE_FROM_SSOT = "restore_from_ssot"
    ROLLBACK_TO_CHECKPOINT = "rollback_to_checkpoint"
    MANUAL_INTERVENTION = "manual_intervention"
    IGNORE = "ignore"
    FULL_REBUILD = "full_rebuild"
    REBUILD_RELATIONSHIPS = "rebuild_relationships"
    CONSENSUS_RESOLUTION = "consensus_resolution"


@dataclass
class RecoveryResult:
    """Result of a recovery operation.

    Attributes:
        recovery_status: Status of recovery (INITIATED, COMPLETED, FAILED).
        strategy: Recovery strategy used.
        detection_result: Original detection result.
        recovered_state: State after recovery (if successful).
        error: Error message if failed.
    """
    recovery_status: str
    strategy: Optional[RecoveryStrategy] = None
    detection_result: Optional["CorruptionDetectionResult"] = None
    recovered_state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Incident:
    """Corruption incident for logging and analysis.

    Attributes:
        incident_id: Unique incident identifier.
        corruption_type: Type of corruption detected.
        timestamp: When incident was created.
        detection_timestamp: When corruption was detected.
        mismatches: List of detected mismatches.
        recovery_status: Recovery status if recovery was attempted.
        details: Additional incident details.
    """
    incident_id: str
    corruption_type: Optional[CorruptionType] = None
    timestamp: Optional[str] = None
    detection_timestamp: Optional[str] = None
    mismatches: List[Dict[str, Any]] = field(default_factory=list)
    recovery_status: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CorruptionDetectionResult:
    """Result of corruption detection.

    Attributes:
        corruption_detected: Whether corruption was found.
        corruption_type: Type of corruption.
        mismatches: List of detected mismatches.
        details: Additional details.
    """
    corruption_detected: bool
    corruption_type: Optional[CorruptionType] = None
    mismatches: List[Dict[str, Any]] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentReport:
    """Incident report for corruption events.

    Attributes:
        incident_id: Unique incident identifier.
        timestamp: When incident was detected.
        corruption_type: Type of corruption.
        severity: Severity level.
        details: Incident details.
        recovery_action: Applied recovery action.
    """
    incident_id: str
    timestamp: str
    corruption_type: CorruptionType
    severity: int
    details: Dict[str, Any] = field(default_factory=dict)
    recovery_action: Optional[RecoveryStrategy] = None


@dataclass
class HallucinationEvent:
    """A detected hallucination event.

    Attributes:
        pattern: Type of hallucination.
        severity: Severity level (0-100).
        description: Event description.
        context: Related context.
        recovery_applied: Whether recovery was applied.
    """

    pattern: HallucinationPattern
    severity: int
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_applied: bool = False


class HallucinationDetector:
    """Detects hallucination patterns."""

    def __init__(self) -> None:
        """Initialize detector."""
        self.events: List[HallucinationEvent] = []
        self.confidence_threshold: float = 0.75
        self.knowledge_base: Set[str] = set()
        self.detection_history: List[HallucinationAssessment] = []
        self.thresholds = {
            HallucinationPattern.FACTUAL_ERROR: 70,
            HallucinationPattern.LOGICAL_CONTRADICTION: 80,
            HallucinationPattern.CONTEXT_DRIFT: 60,
            HallucinationPattern.CONFABULATION: 75,
            HallucinationPattern.INCONSISTENCY: 65,
        }

    def add_to_knowledge_base(self, facts: List[str]) -> None:
        """Add trusted facts to the verification knowledge base."""
        for fact in facts:
            if fact:
                self.knowledge_base.add(fact)

    def score_confidence(
        self,
        output: str,
        reasoning: str,
        fact_checks: Optional[List[str]] = None,
    ) -> ConfidenceScore:
        """Compute confidence score from output, reasoning quality, and fact verification."""
        if not output or not reasoning:
            return ConfidenceScore(value=0.0, reasoning=reasoning, fact_checks=fact_checks or [])

        fact_checks = fact_checks or []
        base = 0.25
        reasoning_bonus = min(len(reasoning) / 200.0, 0.35)

        verified = 0
        if fact_checks:
            verified = sum(1 for fact in fact_checks if fact in self.knowledge_base)
            fact_bonus = 0.4 * (verified / max(len(fact_checks), 1))
        else:
            fact_bonus = 0.0

        value = max(0.0, min(1.0, base + reasoning_bonus + fact_bonus))
        return ConfidenceScore(
            value=value,
            reasoning=reasoning,
            fact_checks=fact_checks,
            evidence_sources=self._extract_sources(reasoning),
        )

    def _assess_risk(self, confidence: float, hallucinations: List[str]) -> HallucinationRisk:
        """Map confidence + hallucination count to risk class."""
        if confidence >= 0.9 and not hallucinations:
            return HallucinationRisk.SAFE
        if confidence >= 0.75 and len(hallucinations) == 0:
            return HallucinationRisk.LOW
        if confidence >= 0.55 and len(hallucinations) <= 1:
            return HallucinationRisk.MEDIUM
        if confidence >= 0.35 and len(hallucinations) <= 2:
            return HallucinationRisk.HIGH
        return HallucinationRisk.CRITICAL

    def _extract_reasoning_steps(self, reasoning: str) -> List[str]:
        """Extract coarse reasoning steps from prose."""
        if not reasoning:
            return []
        return [step.strip() for step in reasoning.split('.') if step.strip()]

    def _extract_sources(self, reasoning: str) -> List[str]:
        """Extract evidence source hints from reasoning text."""
        if not reasoning:
            return []
        lower = reasoning.lower()
        sources: List[str] = []
        if "knowledge base" in lower:
            sources.append("knowledge_base")
        if "verified" in lower:
            sources.append("verified_sources")
        if "source" in lower and "verified_sources" not in sources:
            sources.append("textual_source")
        return sources

    def _generate_recommendations(
        self,
        is_safe: bool,
        risk_level: HallucinationRisk,
    ) -> List[str]:
        """Generate risk-driven remediation guidance."""
        if is_safe:
            return []
        if risk_level == HallucinationRisk.CRITICAL:
            return ["Retry generation with stricter grounding and verified sources"]
        if risk_level == HallucinationRisk.HIGH:
            return ["Review claims manually before accepting output"]
        if risk_level == HallucinationRisk.MEDIUM:
            return ["Validate key facts against trusted references"]
        return ["Monitor output quality"]

    def detect_hallucinations(
        self,
        output: str,
        reasoning: str,
        fact_checks: Optional[List[str]] = None,
    ) -> DetectionResult:
        """Run hallucination assessment and return wrapped Result."""
        if not output:
            return DetectionResult(success=False, error="Output cannot be empty")

        fact_checks = fact_checks or []
        score = self.score_confidence(output=output, reasoning=reasoning, fact_checks=fact_checks)
        unverified = [fact for fact in fact_checks if fact not in self.knowledge_base]
        risk = self._assess_risk(score.value, unverified)
        is_safe = risk in (HallucinationRisk.SAFE, HallucinationRisk.LOW)

        assessment = HallucinationAssessment(
            is_safe=is_safe,
            confidence_score=score,
            hallucination_risk=risk,
            detected_hallucinations=unverified,
            reasoning_steps=self._extract_reasoning_steps(reasoning),
            evidence_sources=self._extract_sources(reasoning),
            recommendations=self._generate_recommendations(is_safe, risk),
        )
        self.detection_history.append(assessment)
        return DetectionResult(success=True, value=assessment)

    def get_detection_summary(self) -> Dict[str, Any]:
        """Return aggregate statistics for detection history."""
        total = len(self.detection_history)
        if total == 0:
            return {"total_detections": 0, "safe_outputs": 0, "average_confidence": 0.0}

        safe = sum(1 for entry in self.detection_history if entry.is_safe)
        avg_conf = sum(entry.confidence_score.value for entry in self.detection_history) / total
        return {
            "total_detections": total,
            "safe_outputs": safe,
            "average_confidence": avg_conf,
        }

    def detect(
        self,
        pattern: HallucinationPattern,
        severity: int,
        description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> HallucinationEvent:
        """Detect a hallucination event.

        Args:
            pattern: Type of hallucination.
            severity: Severity level.
            description: Description.
            context: Related context.

        Returns:
            HallucinationEvent.
        """
        event = HallucinationEvent(
            pattern=pattern,
            severity=severity,
            description=description,
            context=context or {},
        )
        self.events.append(event)
        return event

    def is_critical(self, event: HallucinationEvent) -> bool:
        """Check if event is critical.

        Args:
            event: Event to check.

        Returns:
            True if critical, False otherwise.
        """
        threshold = self.thresholds.get(event.pattern, 50)
        return event.severity >= threshold

    def get_events(self, pattern: Optional[HallucinationPattern] = None) -> List[HallucinationEvent]:
        """Get detected events.

        Args:
            pattern: Optional filter by pattern.

        Returns:
            List of events.
        """
        if pattern:
            return [e for e in self.events if e.pattern == pattern]
        return self.events.copy()

    def clear_events(self) -> None:
        """Clear event history."""
        self.events.clear()

    def detect_corruption(
        self,
        authoritative_state: Dict[str, Any] = None,
        current_state: Dict[str, Any] = None,
        state: Dict[str, Any] = None,
        check_type: str = "all",
    ) -> CorruptionDetectionResult:
        """Detect corruption between authoritative and current state.

        Args:
            authoritative_state: The trusted source of truth state.
            current_state: The state to validate.
            state: Alternative single state to check (legacy).
            check_type: Type of check to perform.

        Returns:
            CorruptionDetectionResult with detection details.
        """
        # Handle legacy single-state API
        if state is not None and authoritative_state is None:
            authoritative_state = state
            current_state = state

        # Validate inputs - raise if authoritative_state is None but current_state provided
        if authoritative_state is None and current_state is not None:
            raise ValueError("authoritative_state cannot be None when current_state is provided")

        if authoritative_state is None or current_state is None:
            return CorruptionDetectionResult(corruption_detected=False)

        mismatches = []
        corruption_type = None

        # Compare states field by field
        for key in authoritative_state:
            if key == "checksum":
                continue
            if key in current_state:
                if authoritative_state[key] != current_state[key]:
                    mismatches.append({
                        "field": key,
                        "expected": authoritative_state[key],
                        "actual": current_state[key],
                    })

        # Check for checksum mismatch
        auth_checksum = authoritative_state.get("checksum")
        curr_checksum = current_state.get("checksum")
        if auth_checksum and curr_checksum and auth_checksum != curr_checksum:
            return CorruptionDetectionResult(
                corruption_detected=True,
                corruption_type=CorruptionType.CHECKSUM_MISMATCH,
                mismatches=mismatches,
                details={"auth_checksum": auth_checksum, "curr_checksum": curr_checksum},
            )

        # Check for temporal anomalies
        auth_updates = authoritative_state.get("ac_updates", [])
        curr_updates = current_state.get("ac_updates", [])
        if auth_updates and curr_updates:
            for i, (auth, curr) in enumerate(zip(auth_updates, curr_updates)):
                if auth.get("timestamp") and curr.get("timestamp"):
                    if auth["timestamp"] != curr["timestamp"]:
                        return CorruptionDetectionResult(
                            corruption_detected=True,
                            corruption_type=CorruptionType.TEMPORAL_ANOMALY,
                            mismatches=mismatches,
                            details={"index": i},
                        )

        # Check for referential integrity
        auth_ac_ids = set(authoritative_state.get("ac_ids", []))
        curr_ac_ids = set(current_state.get("ac_ids", []))
        curr_deps = current_state.get("dependencies", {})
        for dep_id in curr_deps:
            if dep_id not in curr_ac_ids:
                return CorruptionDetectionResult(
                    corruption_detected=True,
                    corruption_type=CorruptionType.REFERENTIAL_INTEGRITY,
                    mismatches=mismatches,
                    details={"missing_dependency": dep_id},
                )

        # Check for state mismatch
        if mismatches:
            return CorruptionDetectionResult(
                corruption_detected=True,
                corruption_type=CorruptionType.STATE_MISMATCH,
                mismatches=mismatches,
            )

        return CorruptionDetectionResult(corruption_detected=False)

    def calculate_checksum(self, state: Dict[str, Any]) -> str:
        """Calculate checksum for state data.

        Args:
            state: State data.

        Returns:
            SHA256 checksum string.
        """
        import hashlib
        import json

        # Exclude checksum field from calculation
        state_copy = {k: v for k, v in state.items() if k != "checksum"}
        state_json = json.dumps(state_copy, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()[:16]

    def detect_consensus_violation(
        self,
        authoritative_state: Dict[str, Any] = None,
        replicas: List[Dict[str, Any]] = None,
        states: List[Dict[str, Any]] = None,
        field: str = None,
    ) -> Optional[CorruptionDetectionResult]:
        """Detect consensus violations across multiple states/replicas.

        Args:
            authoritative_state: The trusted source of truth state.
            replicas: List of replica states to check.
            states: Alternative list of states (legacy).
            field: Field to check for consensus (legacy).

        Returns:
            CorruptionDetectionResult if violation found, None otherwise.
        """
        # Handle legacy API
        if states is not None and replicas is None:
            replicas = states

        if not replicas:
            return None

        if authoritative_state:
            # Compare each replica against authoritative
            disagreements = []
            for i, replica in enumerate(replicas):
                mismatches = []
                for key in authoritative_state:
                    if key in replica and authoritative_state[key] != replica[key]:
                        mismatches.append({"field": key, "expected": authoritative_state[key], "actual": replica[key]})
                if mismatches:
                    disagreements.append({"replica_index": i, "mismatches": mismatches})

            if disagreements:
                return CorruptionDetectionResult(
                    corruption_detected=True,
                    corruption_type=CorruptionType.CONSENSUS_VIOLATION,
                    mismatches=disagreements,
                )

        # Field-based consensus check (legacy)
        if field:
            values = [s.get(field) for s in replicas]
            unique_values = set(str(v) for v in values)
            if len(unique_values) > 1:
                return CorruptionDetectionResult(
                    corruption_detected=True,
                    corruption_type=CorruptionType.CONSENSUS_VIOLATION,
                    details={"field": field, "values": values},
                )

        return None

    def trigger_recovery(
        self,
        detection: CorruptionDetectionResult,
        authoritative_state: Dict[str, Any] = None,
        checkpoint: Dict[str, Any] = None,
    ) -> RecoveryResult:
        """Trigger recovery based on detection result.

        Args:
            detection: The corruption detection result.
            authoritative_state: The authoritative state to restore to.
            checkpoint: Checkpoint to rollback to (for temporal anomalies).

        Returns:
            RecoveryResult with recovery status and strategy.
        """
        if not detection or not detection.corruption_detected:
            return RecoveryResult(
                recovery_status="SKIPPED",
                detection_result=detection,
            )

        # Select strategy based on corruption type
        strategy = self._select_strategy(detection.corruption_type)

        # Attempt recovery
        try:
            recovered_state = None

            if strategy == RecoveryStrategy.ROLLBACK_TO_CHECKPOINT:
                if checkpoint:
                    recovered_state = checkpoint.copy()
                    return RecoveryResult(
                        recovery_status="COMPLETED",
                        strategy=strategy,
                        detection_result=detection,
                        recovered_state=recovered_state,
                    )
            elif strategy == RecoveryStrategy.FULL_REBUILD:
                if authoritative_state:
                    recovered_state = authoritative_state.copy()
                    return RecoveryResult(
                        recovery_status="COMPLETED",
                        strategy=strategy,
                        detection_result=detection,
                        recovered_state=recovered_state,
                    )
            elif strategy == RecoveryStrategy.REBUILD_RELATIONSHIPS:
                if authoritative_state:
                    recovered_state = authoritative_state.copy()
                    return RecoveryResult(
                        recovery_status="COMPLETED",
                        strategy=strategy,
                        detection_result=detection,
                        recovered_state=recovered_state,
                    )
            elif strategy == RecoveryStrategy.CONSENSUS_RESOLUTION:
                if authoritative_state:
                    recovered_state = authoritative_state.copy()
                    return RecoveryResult(
                        recovery_status="COMPLETED",
                        strategy=strategy,
                        detection_result=detection,
                        recovered_state=recovered_state,
                    )

            # No authoritative state or checkpoint provided
            return RecoveryResult(
                recovery_status="INITIATED",
                strategy=strategy,
                detection_result=detection,
            )

        except Exception as e:
            return RecoveryResult(
                recovery_status="FAILED",
                strategy=strategy,
                detection_result=detection,
                error=str(e),
            )

    def _select_strategy(self, corruption_type: Optional[CorruptionType]) -> RecoveryStrategy:
        """Select recovery strategy based on corruption type.

        Args:
            corruption_type: The type of corruption detected.

        Returns:
            Appropriate RecoveryStrategy.
        """
        if corruption_type is None:
            return RecoveryStrategy.FULL_REBUILD

        strategy_map = {
            CorruptionType.STATE_MISMATCH: RecoveryStrategy.FULL_REBUILD,
            CorruptionType.CHECKSUM_MISMATCH: RecoveryStrategy.FULL_REBUILD,
            CorruptionType.TEMPORAL_ANOMALY: RecoveryStrategy.ROLLBACK_TO_CHECKPOINT,
            CorruptionType.REFERENTIAL_INTEGRITY: RecoveryStrategy.REBUILD_RELATIONSHIPS,
            CorruptionType.CONSENSUS_VIOLATION: RecoveryStrategy.CONSENSUS_RESOLUTION,
        }

        return strategy_map.get(corruption_type, RecoveryStrategy.FULL_REBUILD)

    def create_incident(
        self,
        detection: CorruptionDetectionResult,
        recovery: Optional[RecoveryResult] = None,
    ) -> Incident:
        """Create an incident record from detection result.

        Args:
            detection: The corruption detection result.
            recovery: Optional recovery result to include.

        Returns:
            Incident record for logging.
        """
        import uuid
        from datetime import datetime

        timestamp = datetime.utcnow().isoformat()

        incident = Incident(
            incident_id=str(uuid.uuid4()),
            corruption_type=detection.corruption_type,
            timestamp=timestamp,
            detection_timestamp=timestamp,
            mismatches=detection.mismatches,
            recovery_status=recovery.recovery_status if recovery else None,
            details=detection.details,
        )

        return incident

    def store_incident(self, incident: Incident) -> None:
        """Store an incident in the incident store.

        Args:
            incident: Incident to store.
        """
        if not hasattr(self, '_incidents'):
            self._incidents: Dict[str, Incident] = {}
        self._incidents[incident.incident_id] = incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Retrieve an incident by ID.

        Args:
            incident_id: The incident ID to retrieve.

        Returns:
            Incident if found, None otherwise.
        """
        if not hasattr(self, '_incidents'):
            return None
        return self._incidents.get(incident_id)

    def query_incidents(
        self,
        corruption_type: Optional[CorruptionType] = None,
        limit: int = 100,
    ) -> List[Incident]:
        """Query incidents with optional filtering.

        Args:
            corruption_type: Filter by corruption type.
            limit: Maximum number of results.

        Returns:
            List of matching incidents.
        """
        if not hasattr(self, '_incidents'):
            return []

        incidents = list(self._incidents.values())

        if corruption_type:
            incidents = [i for i in incidents if i.corruption_type == corruption_type]

        return incidents[:limit]


@dataclass
class CorruptionResult:
    """Result of corruption detection."""
    corrupted: bool
    corruption_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusResult:
    """Result of consensus check."""
    violated: bool
    field: str
    values: List[Any] = field(default_factory=list)
    majority_value: Any = None


class HallucinationRecovery:
    """Recovers from hallucination events."""

    def __init__(self) -> None:
        """Initialize recovery."""
        self.recovery_actions: Dict[HallucinationPattern, list] = {}

    def register_recovery(self, pattern: HallucinationPattern, action: callable) -> None:
        """Register recovery action.

        Args:
            pattern: Hallucination pattern.
            action: Recovery action callable.
        """
        if pattern not in self.recovery_actions:
            self.recovery_actions[pattern] = []
        self.recovery_actions[pattern].append(action)

    def recover(self, event: HallucinationEvent) -> bool:
        """Apply recovery for an event.

        Args:
            event: Event to recover from.

        Returns:
            True if recovery successful, False otherwise.
        """
        actions = self.recovery_actions.get(event.pattern, [])

        for action in actions:
            try:
                result = action(event)
                if result:
                    event.recovery_applied = True
                    return True
            except Exception:
                pass

        return False

    def get_recovery_status(self, pattern: HallucinationPattern) -> int:
        """Get number of recovery actions for pattern.

        Args:
            pattern: Hallucination pattern.

        Returns:
            Number of registered actions.
        """
        return len(self.recovery_actions.get(pattern, []))


# Note: CorruptionDetectionResult is defined at top of file (line ~45)
# with fields: corruption_detected, corruption_type, confidence, details, affected_components

# Aliases and stubs for test compatibility
class CorruptionIndicator(Enum):
    """Types of corruption indicators."""
    INVALID_STATE = "invalid_state"
    INCONSISTENT_DATA = "inconsistent_data"
    MISSING_REFERENCE = "missing_reference"


# Note: CorruptionType is defined at top of file with values:
# STATE_MISMATCH, CHECKSUM_MISMATCH, TEMPORAL_ANOMALY,
# REFERENTIAL_INTEGRITY, CONSENSUS_VIOLATION


# Note: RecoveryStrategy is defined at top of file with values:
# RESTORE_FROM_SSOT, ROLLBACK_TO_CHECKPOINT, MANUAL_INTERVENTION, IGNORE


# Note: IncidentReport is defined at top of file


__all__ = [
    "HallucinationDetector",
    "HallucinationRecovery",
    "HallucinationEvent",
    "HallucinationPattern",
    "CorruptionIndicator",
    "CorruptionDetectionResult",
    "CorruptionType",
    "RecoveryStrategy",
    "IncidentReport",
]
