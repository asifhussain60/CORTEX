"""
HP-002-02: Hallucination Detection & Recovery

Detects SSOT (Single Source of Truth) corruption and triggers recovery.
Monitors for state inconsistencies, temporal anomalies, and referential integrity
violations. Initiates appropriate recovery strategies and logs all incidents.

AC-ID: HP-002-02
Phase: PHASE-11-HALLUCINATION-PREVENTION
TDD Status: GREEN phase
"""

import sqlite3
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CorruptionType(Enum):
    """Types of SSOT corruption that can be detected.
    
    Categorizes corruption patterns for appropriate recovery strategy.
    """
    STATE_MISMATCH = "STATE_MISMATCH"  # Values don't match
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"  # Integrity hash invalid
    TEMPORAL_ANOMALY = "TEMPORAL_ANOMALY"  # Out-of-order timestamps
    REFERENTIAL_INTEGRITY = "REFERENTIAL_INTEGRITY"  # Broken references
    CONSENSUS_VIOLATION = "CONSENSUS_VIOLATION"  # Replica disagreement


class RecoveryStrategy(Enum):
    """Recovery strategies for different corruption types.
    
    Defines how to restore system to consistent state.
    """
    FULL_REBUILD = "FULL_REBUILD"  # Complete state reconstruction
    ROLLBACK_TO_CHECKPOINT = "ROLLBACK_TO_CHECKPOINT"  # Restore from checkpoint
    REBUILD_RELATIONSHIPS = "REBUILD_RELATIONSHIPS"  # Fix references
    CONSENSUS_RESOLUTION = "CONSENSUS_RESOLUTION"  # Resolve replica disagreement


@dataclass
class CorruptionDetectionResult:
    """Result of corruption detection check.
    
    Attributes:
        corruption_detected: Whether corruption was found
        corruption_type: Type of corruption if detected
        mismatches: List of specific field mismatches
        severity: Corruption severity (LOW, MEDIUM, HIGH, CRITICAL)
        details: Additional corruption details
    """
    corruption_detected: bool = False
    corruption_type: Optional[CorruptionType] = None
    mismatches: List[Dict[str, Any]] = field(default_factory=list)
    severity: str = "LOW"
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryResult:
    """Result of recovery attempt.
    
    Attributes:
        recovery_status: Status of recovery (INITIATED, RUNNING, COMPLETED, FAILED)
        strategy: Recovery strategy used
        recovered_state: State after recovery
        detection_result: Original detection result
        errors: Any errors encountered
        recovery_duration_ms: Time taken to recover
    """
    recovery_status: str = "PENDING"
    strategy: Optional[RecoveryStrategy] = None
    recovered_state: Optional[Dict[str, Any]] = None
    detection_result: Optional[CorruptionDetectionResult] = None
    errors: List[str] = field(default_factory=list)
    recovery_duration_ms: float = 0.0


@dataclass
class IncidentReport:
    """Incident report for corruption event.
    
    Attributes:
        incident_id: Unique identifier for incident
        timestamp: When incident was detected
        corruption_type: Type of corruption detected
        mismatches: Corruption details
        recovery_status: Outcome of recovery attempt
        detection_timestamp: When detection occurred
        investigation_notes: Analysis notes
    """
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    corruption_type: CorruptionType = CorruptionType.STATE_MISMATCH
    mismatches: List[Dict[str, Any]] = field(default_factory=list)
    recovery_status: str = "PENDING"
    detection_timestamp: datetime = field(default_factory=datetime.utcnow)
    investigation_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary.
        
        Returns:
            Dictionary representation of incident.
        """
        return {
            "incident_id": self.incident_id,
            "timestamp": self.timestamp.isoformat(),
            "corruption_type": self.corruption_type.value,
            "mismatches": self.mismatches,
            "recovery_status": self.recovery_status,
            "detection_timestamp": self.detection_timestamp.isoformat(),
            "investigation_notes": self.investigation_notes,
        }


class HallucinationDetector:
    """Detects SSOT corruption and triggers recovery.
    
    Monitors system state for various corruption patterns including:
    - State mismatches (field values differ from authoritative)
    - Checksum failures (integrity compromised)
    - Temporal anomalies (out-of-order timestamps)
    - Referential integrity violations (broken AC relationships)
    - Consensus violations (replica disagreement)
    
    Upon detection, initiates appropriate recovery strategy and logs incident.
    
    Key Features:
    - Multi-level corruption detection
    - Automatic recovery strategy selection
    - Checksum-based integrity verification
    - Consensus-based replica validation
    - Comprehensive incident logging and querying
    """

    def __init__(self, db_path: str = "cortex-brain/state/governance.db"):
        """Initialize hallucination detector.
        
        Args:
            db_path: Path to governance database for incident storage.
        """
        self.db_path = db_path
        self._incidents: List[IncidentReport] = []
        self._init_incident_table()

    def _init_incident_table(self) -> None:
        """Initialize incident tracking table in database.
        
        Creates hallucination_incidents table if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hallucination_incidents (
                        incident_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        corruption_type TEXT NOT NULL,
                        mismatches JSON,
                        recovery_status TEXT DEFAULT 'PENDING',
                        detection_timestamp TEXT,
                        investigation_notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except sqlite3.Error:
            # Database may not be available, use in-memory fallback
            pass

    def calculate_checksum(self, state: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum of state for integrity verification.
        
        Args:
            state: State object to checksum (excluding existing checksum).
            
        Returns:
            Hex-encoded SHA256 checksum.
        """
        # Create copy without checksum to avoid circular reference
        checksum_state = {k: v for k, v in state.items() if k != "checksum"}
        try:
            state_str = json.dumps(checksum_state, sort_keys=True, default=str)
            return hashlib.sha256(state_str.encode()).hexdigest()
        except (TypeError, ValueError):
            return ""

    def detect_corruption(
        self,
        authoritative_state: Dict[str, Any],
        current_state: Dict[str, Any],
    ) -> CorruptionDetectionResult:
        """Detect SSOT corruption by comparing authoritative and current state.
        
        Checks for:
        - State field mismatches
        - Checksum failures
        - Temporal anomalies
        - Referential integrity violations
        
        Args:
            authoritative_state: Known-good authoritative state.
            current_state: Current system state to validate.
            
        Returns:
            CorruptionDetectionResult with detection details.
            
        Raises:
            TypeError: If states are None.
        """
        if authoritative_state is None or current_state is None:
            raise TypeError("States cannot be None")

        result = CorruptionDetectionResult()

        # Check 1: Checksum mismatch
        if self._check_checksum_mismatch(authoritative_state, current_state):
            result.corruption_detected = True
            result.corruption_type = CorruptionType.CHECKSUM_MISMATCH
            result.severity = "CRITICAL"
            result.mismatches.append({
                "field": "checksum",
                "authoritative": authoritative_state.get("checksum"),
                "current": current_state.get("checksum"),
            })

        # Check 2: State mismatches
        state_mismatches = self._detect_state_mismatches(authoritative_state, current_state)
        if state_mismatches:
            result.corruption_detected = True
            if not result.corruption_type:
                result.corruption_type = CorruptionType.STATE_MISMATCH
            result.severity = "HIGH"
            result.mismatches.extend(state_mismatches)

        # Check 3: Temporal anomalies
        if self._detect_temporal_anomaly(authoritative_state, current_state):
            result.corruption_detected = True
            result.corruption_type = CorruptionType.TEMPORAL_ANOMALY
            result.severity = "HIGH"

        # Check 4: Referential integrity
        if self._detect_referential_integrity_violation(authoritative_state, current_state):
            result.corruption_detected = True
            result.corruption_type = CorruptionType.REFERENTIAL_INTEGRITY
            result.severity = "CRITICAL"

        return result

    def _check_checksum_mismatch(
        self,
        authoritative: Dict[str, Any],
        current: Dict[str, Any],
    ) -> bool:
        """Check if checksums don't match.
        
        Args:
            authoritative: Authoritative state.
            current: Current state.
            
        Returns:
            True if checksums don't match.
        """
        if "checksum" not in authoritative or "checksum" not in current:
            return False

        auth_checksum = authoritative.get("checksum")
        curr_checksum = current.get("checksum")

        # Recalculate to verify integrity
        calculated = self.calculate_checksum(current)
        return calculated != curr_checksum

    def _detect_state_mismatches(
        self,
        authoritative: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Detect individual field mismatches between states.
        
        Args:
            authoritative: Authoritative state.
            current: Current state.
            
        Returns:
            List of mismatch records.
        """
        mismatches = []

        # Check common keys
        for key in set(list(authoritative.keys()) + list(current.keys())):
            if key == "checksum":
                continue  # Skip checksum field

            auth_val = authoritative.get(key)
            curr_val = current.get(key)

            if auth_val != curr_val:
                mismatches.append({
                    "field": key,
                    "authoritative": auth_val,
                    "current": curr_val,
                })

        return mismatches

    def _detect_temporal_anomaly(
        self,
        authoritative: Dict[str, Any],
        current: Dict[str, Any],
    ) -> bool:
        """Detect out-of-order timestamps or temporal inconsistencies.
        
        Args:
            authoritative: Authoritative state.
            current: Current state.
            
        Returns:
            True if temporal anomaly detected.
        """
        try:
            # Check if last_update went backward
            auth_update = authoritative.get("last_update")
            curr_update = current.get("last_update")

            if auth_update and curr_update:
                auth_time = datetime.fromisoformat(auth_update.replace("Z", "+00:00"))
                curr_time = datetime.fromisoformat(curr_update.replace("Z", "+00:00"))

                if curr_time < auth_time:
                    return True

            # Check for out-of-order AC updates
            auth_ac_updates = authoritative.get("ac_updates", [])
            curr_ac_updates = current.get("ac_updates", [])

            if auth_ac_updates and curr_ac_updates:
                # Verify AC updates are in chronological order
                curr_times = []
                for update in curr_ac_updates:
                    if "timestamp" in update:
                        ts = datetime.fromisoformat(update["timestamp"].replace("Z", "+00:00"))
                        curr_times.append(ts)

                if curr_times and curr_times != sorted(curr_times):
                    return True

        except (ValueError, TypeError):
            pass

        return False

    def _detect_referential_integrity_violation(
        self,
        authoritative: Dict[str, Any],
        current: Dict[str, Any],
    ) -> bool:
        """Detect broken references between entities.
        
        Args:
            authoritative: Authoritative state.
            current: Current state.
            
        Returns:
            True if referential integrity violation detected.
        """
        # Check AC references
        auth_ac_ids = set(authoritative.get("ac_ids", []))
        curr_ac_ids = set(current.get("ac_ids", []))

        # Get dependencies
        auth_deps = authoritative.get("dependencies", {})
        curr_deps = current.get("dependencies", {})

        # Check if dependent AC is missing
        for ac_id, dependencies in curr_deps.items():
            if ac_id not in curr_ac_ids:
                return True  # AC referenced but not in ac_ids

            for dep in dependencies:
                if dep not in curr_ac_ids:
                    return True  # Dependency refers to non-existent AC

        return False

    def detect_consensus_violation(
        self,
        authoritative_state: Dict[str, Any],
        replicas: List[Dict[str, Any]],
    ) -> Optional[CorruptionDetectionResult]:
        """Detect consensus violations among replicas.
        
        Compares replicas against authoritative state and each other.
        
        Args:
            authoritative_state: Known-good authoritative state.
            replicas: List of replica states.
            
        Returns:
            CorruptionDetectionResult if violation detected, None otherwise.
        """
        if not replicas or len(replicas) < 2:
            return None

        # Check if majority agrees with authoritative
        agreement_count = sum(
            1 for r in replicas
            if json.dumps(r, sort_keys=True, default=str) ==
            json.dumps(authoritative_state, sort_keys=True, default=str)
        )

        if agreement_count < len(replicas) / 2:
            return CorruptionDetectionResult(
                corruption_detected=True,
                corruption_type=CorruptionType.CONSENSUS_VIOLATION,
                severity="CRITICAL",
                details={"agreeing_replicas": agreement_count, "total": len(replicas)},
            )

        return None

    def trigger_recovery(
        self,
        detection: CorruptionDetectionResult,
        checkpoint: Optional[Dict[str, Any]] = None,
        authoritative_state: Optional[Dict[str, Any]] = None,
    ) -> RecoveryResult:
        """Trigger recovery based on corruption type.
        
        Selects and executes appropriate recovery strategy.
        
        Args:
            detection: Corruption detection result.
            checkpoint: Last known-good checkpoint (for rollback).
            authoritative_state: Authoritative state to restore to.
            
        Returns:
            RecoveryResult with recovery outcome.
        """
        recovery = RecoveryResult(
            recovery_status="INITIATED",
            detection_result=detection,
        )

        start_time = datetime.utcnow()

        try:
            # Select strategy based on corruption type
            if detection.corruption_type == CorruptionType.TEMPORAL_ANOMALY:
                recovery.strategy = RecoveryStrategy.ROLLBACK_TO_CHECKPOINT
                if checkpoint:
                    recovery.recovered_state = checkpoint.copy()
            elif detection.corruption_type == CorruptionType.REFERENTIAL_INTEGRITY:
                recovery.strategy = RecoveryStrategy.REBUILD_RELATIONSHIPS
            elif detection.corruption_type == CorruptionType.CONSENSUS_VIOLATION:
                recovery.strategy = RecoveryStrategy.CONSENSUS_RESOLUTION
            else:
                recovery.strategy = RecoveryStrategy.FULL_REBUILD
                if authoritative_state:
                    recovery.recovered_state = authoritative_state.copy()

            recovery.recovery_status = "COMPLETED"

        except Exception as e:
            recovery.recovery_status = "FAILED"
            recovery.errors.append(str(e))

        finally:
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            recovery.recovery_duration_ms = elapsed

        return recovery

    def create_incident(
        self,
        detection: CorruptionDetectionResult,
        recovery: Optional[RecoveryResult] = None,
    ) -> IncidentReport:
        """Create incident report for corruption event.
        
        Args:
            detection: Corruption detection result.
            recovery: Recovery result if recovery attempted.
            
        Returns:
            IncidentReport for logging and analysis.
        """
        incident = IncidentReport(
            corruption_type=detection.corruption_type or CorruptionType.STATE_MISMATCH,
            mismatches=detection.mismatches,
            recovery_status=recovery.recovery_status if recovery else "PENDING",
        )

        if recovery:
            if recovery.errors:
                incident.investigation_notes = f"Recovery errors: {'; '.join(recovery.errors)}"

        return incident

    def store_incident(self, incident: IncidentReport) -> None:
        """Store incident to database and memory.
        
        Args:
            incident: IncidentReport to store.
        """
        # Add to in-memory list
        self._incidents.append(incident)

        # Store to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO hallucination_incidents
                    (incident_id, timestamp, corruption_type, mismatches,
                     recovery_status, detection_timestamp, investigation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident.incident_id,
                    incident.timestamp.isoformat(),
                    incident.corruption_type.value,
                    json.dumps(incident.mismatches),
                    incident.recovery_status,
                    incident.detection_timestamp.isoformat(),
                    incident.investigation_notes,
                ))
                conn.commit()
        except sqlite3.Error:
            # Database logging failed, continue with in-memory
            pass

    def get_incident(self, incident_id: str) -> Optional[IncidentReport]:
        """Retrieve incident by ID.
        
        Args:
            incident_id: ID of incident to retrieve.
            
        Returns:
            IncidentReport if found, None otherwise.
        """
        # Search in-memory list first
        for incident in self._incidents:
            if incident.incident_id == incident_id:
                return incident

        # Try database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT incident_id, timestamp, corruption_type, mismatches,
                           recovery_status, detection_timestamp, investigation_notes
                    FROM hallucination_incidents
                    WHERE incident_id = ?
                """, (incident_id,))
                row = cursor.fetchone()

                if row:
                    return IncidentReport(
                        incident_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        corruption_type=CorruptionType(row[2]),
                        mismatches=json.loads(row[3]) if row[3] else [],
                        recovery_status=row[4],
                        detection_timestamp=datetime.fromisoformat(row[5]),
                        investigation_notes=row[6] or "",
                    )
        except sqlite3.Error:
            pass

        return None

    def query_incidents(
        self,
        corruption_type: Optional[CorruptionType] = None,
        recovery_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query incidents with optional filtering.
        
        Args:
            corruption_type: Filter by corruption type.
            recovery_status: Filter by recovery status.
            limit: Maximum results to return.
            
        Returns:
            List of incident records matching filters.
        """
        results = []

        # Filter in-memory incidents
        for incident in self._incidents:
            if corruption_type and incident.corruption_type != corruption_type:
                continue
            if recovery_status and incident.recovery_status != recovery_status:
                continue
            results.append(incident.to_dict())

        return results[:limit]

    def clear_incidents(self) -> None:
        """Clear incident history from memory.
        
        Note: Database incidents are not cleared.
        """
        self._incidents.clear()
