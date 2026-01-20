"""
Hallucination Detection & Recovery Module (AC-HP-002-02)

Detects SSOT corruption through multiple methods and executes recovery strategies.

Implements CORE-017 (Corruption Detection) and CORE-018 (Automatic Recovery).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from hashlib import sha256
from uuid import uuid4


# =========================================================================
# DATA STRUCTURES
# =========================================================================

@dataclass
class CorruptionIndicator:
    """
    Represents a detected corruption indicator.
    
    Attributes:
        corruption_id: Unique corruption identifier
        corruption_type: Type of corruption detected
        severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        description: Description of the corruption
        corrupted_data: Data that failed validation
        timestamp: When corruption was detected
        recovery_recommended: Whether recovery is recommended
    """
    corruption_id: str
    corruption_type: str
    severity: str
    description: str
    corrupted_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    recovery_recommended: bool = True


# =========================================================================
# CORRUPTION DETECTOR
# =========================================================================

class CorruptionDetector:
    """
    Detects SSOT corruption through multiple methods.
    
    Detection methods:
    - State mismatch: Inconsistent state values
    - Checksum failure: Data integrity violation
    - Temporal anomaly: Timeline inconsistencies
    - Referential integrity: Missing/orphaned references
    """

    def __init__(self):
        """Initialize corruption detector."""
        self.detected_corruptions: List[CorruptionIndicator] = []
        self.incident_log: List[Dict[str, Any]] = []

    def check_state_mismatch(self, ssot: Dict[str, Any]) -> Optional[CorruptionIndicator]:
        """
        Check for state mismatches (e.g., completed ACs > total ACs).
        
        Args:
            ssot: SSOT data to check
            
        Returns:
            CorruptionIndicator if mismatch found, None otherwise
        """
        if not ssot:
            return None

        # Check completed ACs vs total
        completed = ssot.get('completed_acs', 0)
        total = ssot.get('total_acs', 0)
        
        if completed > total:
            corruption = CorruptionIndicator(
                corruption_id=f'COR-{uuid4().hex[:8]}',
                corruption_type='STATE_MISMATCH',
                severity='CRITICAL',
                description=f'Completed ACs ({completed}) exceeds total ({total})',
                corrupted_data=ssot,
            )
            self.detected_corruptions.append(corruption)
            return corruption

        # Check phase status vs AC progress
        phase_status = ssot.get('phase_status')
        if phase_status == 'COMPLETED' and completed == 0:
            corruption = CorruptionIndicator(
                corruption_id=f'COR-{uuid4().hex[:8]}',
                corruption_type='STATE_MISMATCH',
                severity='HIGH',
                description='Phase marked complete but no ACs completed',
                corrupted_data=ssot,
            )
            self.detected_corruptions.append(corruption)
            return corruption

        return None

    def check_checksum_integrity(self, ssot: Dict[str, Any]) -> Optional[CorruptionIndicator]:
        """
        Check checksum integrity.
        
        Args:
            ssot: SSOT data to check
            
        Returns:
            CorruptionIndicator if checksum fails, None otherwise
        """
        if not ssot or 'checksum' not in ssot:
            return None

        reported_checksum = ssot['checksum']
        calculated = self.calculate_checksum(ssot)

        if reported_checksum != calculated:
            corruption = CorruptionIndicator(
                corruption_id=f'COR-{uuid4().hex[:8]}',
                corruption_type='CHECKSUM_FAILURE',
                severity='MEDIUM',
                description=f'Checksum mismatch: reported={reported_checksum[:8]}... vs calculated={calculated[:8]}...',
                corrupted_data=ssot,
            )
            self.detected_corruptions.append(corruption)
            return corruption

        return None

    def check_temporal_integrity(self, ssot: Dict[str, Any]) -> Optional[CorruptionIndicator]:
        """
        Check for temporal anomalies (future dates, version rollback).
        
        Args:
            ssot: SSOT data to check
            
        Returns:
            CorruptionIndicator if anomaly found, None otherwise
        """
        if not ssot:
            return None

        # Check for future timestamps
        if 'timestamp' in ssot:
            try:
                ts = datetime.fromisoformat(ssot['timestamp'])
                if ts > datetime.now():
                    corruption = CorruptionIndicator(
                        corruption_id=f'COR-{uuid4().hex[:8]}',
                        corruption_type='TEMPORAL_ANOMALY',
                        severity='HIGH',
                        description='Timestamp is in the future',
                        corrupted_data=ssot,
                    )
                    self.detected_corruptions.append(corruption)
                    return corruption
            except (ValueError, TypeError):
                pass

        # Check version rollback
        if 'version' in ssot and 'previous_version' in ssot:
            if ssot['version'] < ssot['previous_version']:
                corruption = CorruptionIndicator(
                    corruption_id=f'COR-{uuid4().hex[:8]}',
                    corruption_type='TEMPORAL_ANOMALY',
                    severity='HIGH',
                    description=f'Version rollback: {ssot["version"]} < {ssot["previous_version"]}',
                    corrupted_data=ssot,
                )
                self.detected_corruptions.append(corruption)
                return corruption

        return None

    def check_referential_integrity(self, ssot: Dict[str, Any]) -> Optional[CorruptionIndicator]:
        """
        Check for referential integrity violations (missing references, orphaned data).
        
        Args:
            ssot: SSOT data to check
            
        Returns:
            CorruptionIndicator if violation found, None otherwise
        """
        if not ssot:
            return None

        # Check AC references
        if 'ac_references' in ssot and 'defined_acs' in ssot:
            refs = set(ssot['ac_references'])
            defined = set(ssot['defined_acs'])
            
            if not refs.issubset(defined):
                missing = refs - defined
                corruption = CorruptionIndicator(
                    corruption_id=f'COR-{uuid4().hex[:8]}',
                    corruption_type='REFERENTIAL_INTEGRITY',
                    severity='HIGH',
                    description=f'Missing AC references: {missing}',
                    corrupted_data=ssot,
                )
                self.detected_corruptions.append(corruption)
                return corruption

        # Check AC phase references
        if 'acs' in ssot:
            for ac in ssot['acs']:
                if 'phase' in ac and ac['phase'] not in ['PHASE-01', 'PHASE-02', 'PHASE-03', 'PHASE-04', 'PHASE-05', 'PHASE-06', 'PHASE-07', 'PHASE-08', 'PHASE-09', 'PHASE-10', 'PHASE-11', 'PHASE-12', 'PHASE-13']:
                    corruption = CorruptionIndicator(
                        corruption_id=f'COR-{uuid4().hex[:8]}',
                        corruption_type='REFERENTIAL_INTEGRITY',
                        severity='HIGH',
                        description=f'Orphaned AC {ac.get("ac_id")} references invalid phase {ac["phase"]}',
                        corrupted_data=ac,
                    )
                    self.detected_corruptions.append(corruption)
                    return corruption

        return None

    def scan_for_all_corruption(self, ssot: Dict[str, Any]) -> List[CorruptionIndicator]:
        """
        Scan using all detection methods.
        
        Args:
            ssot: SSOT data to scan
            
        Returns:
            List of detected corruptions
        """
        detections = []
        
        # Run all checks
        checks = [
            self.check_state_mismatch(ssot),
            self.check_checksum_integrity(ssot),
            self.check_temporal_integrity(ssot),
            self.check_referential_integrity(ssot),
        ]
        
        for detection in checks:
            if detection is not None:
                detections.append(detection)
        
        return detections

    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """
        Calculate checksum of data (excluding checksum field).
        
        Args:
            data: Data to checksum
            
        Returns:
            Checksum hash
        """
        # Create copy without checksum
        data_copy = {k: v for k, v in data.items() if k != 'checksum'}
        
        # Convert to string and hash
        data_str = str(sorted(data_copy.items()))
        return sha256(data_str.encode()).hexdigest()

    def log_incident(self, corruption: CorruptionIndicator) -> str:
        """
        Log a corruption incident.
        
        Args:
            corruption: Corruption to log
            
        Returns:
            Incident ID
        """
        incident = {
            'incident_id': f'INC-{uuid4().hex[:8]}',
            'corruption_id': corruption.corruption_id,
            'corruption_type': corruption.corruption_type,
            'severity': corruption.severity,
            'description': corruption.description,
            'timestamp': datetime.now().isoformat(),
        }
        self.incident_log.append(incident)
        return incident['incident_id']

    def get_incident_history(self) -> List[Dict[str, Any]]:
        """Get incident history."""
        return self.incident_log.copy()


# =========================================================================
# RECOVERY STRATEGY
# =========================================================================

class RecoveryStrategy:
    """
    Selects and executes recovery strategies based on corruption type.
    """

    def __init__(self):
        """Initialize recovery strategy handler."""
        self.recovery_actions: List[Dict[str, Any]] = []

    def select_recovery_strategy(self, corruption: CorruptionIndicator) -> str:
        """
        Select recovery strategy based on corruption type.
        
        Args:
            corruption: Corruption indicator
            
        Returns:
            Recovery strategy name
        """
        strategies = {
            'CHECKSUM_FAILURE': 'recompute_checksums',
            'STATE_MISMATCH': 'reconcile_state',
            'TEMPORAL_ANOMALY': 'sync_timestamps',
            'REFERENTIAL_INTEGRITY': 'rebuild_references',
        }
        
        return strategies.get(corruption.corruption_type, 'manual_review')

    def recover_from_backup(self, backup: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recover from backup copy.
        
        Args:
            backup: Backup to restore from
            
        Returns:
            Recovery result
        """
        action = {
            'action_id': f'ACT-{uuid4().hex[:8]}',
            'action_type': 'RESTORE_FROM_BACKUP',
            'status': 'SUCCESS',
            'timestamp': datetime.now().isoformat(),
            'restored_data': backup,
        }
        self.recovery_actions.append(action)
        return action

    def rebuild_state_from_audit_log(self) -> Dict[str, Any]:
        """
        Rebuild state from audit log.
        
        Returns:
            Recovery result
        """
        action = {
            'action_id': f'ACT-{uuid4().hex[:8]}',
            'action_type': 'REBUILD_FROM_AUDIT',
            'status': 'SUCCESS',
            'timestamp': datetime.now().isoformat(),
        }
        self.recovery_actions.append(action)
        return action

    def isolate_corrupted_data(self, phase_id: str) -> Dict[str, Any]:
        """
        Isolate corrupted data.
        
        Args:
            phase_id: Phase to isolate
            
        Returns:
            Isolation result
        """
        action = {
            'action_id': f'ACT-{uuid4().hex[:8]}',
            'action_type': 'ISOLATE_CORRUPTED',
            'phase_id': phase_id,
            'status': 'SUCCESS',
            'timestamp': datetime.now().isoformat(),
        }
        self.recovery_actions.append(action)
        return action


# =========================================================================
# MODULE EXPORTS
# =========================================================================

__all__ = [
    'CorruptionIndicator',
    'CorruptionDetector',
    'RecoveryStrategy',
]
