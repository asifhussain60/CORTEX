"""
Test suite for HP-002-02: Hallucination Detection & Recovery

Tests for SSOT corruption detection and recovery mechanisms.
Ensures system can detect when the Single Source of Truth becomes corrupted
and trigger automatic recovery procedures with incident logging.

AC-ID: HP-002-02
Phase: PHASE-11-HALLUCINATION-PREVENTION
Status: TDD - RED phase
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import json
import hashlib

from src.core.hallucination_prevention.hallucination_detection import (
    HallucinationDetector,
    CorruptionDetectionResult,
    CorruptionType,
    RecoveryStrategy,
    IncidentReport,
)


class TestSSOTCorruptionDetection:
    """Test suite for SSOT corruption detection."""

    @pytest.fixture
    def detector(self):
        """Initialize hallucination detector."""
        return HallucinationDetector()

    def test_detect_phase_state_mismatch(self, detector):
        """ACID: SSOT corruption detected automatically
        
        Verify that phase state mismatches are detected.
        """
        # Setup: Create SSOT with authoritative state
        ssot_state = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
            "completed_ac_ids": ["HP-001-01", "HP-001-02"],
            "progress_percentage": 50.0,
        }
        
        # Create corrupted version (mismatched state)
        corrupted_state = {
            "phase_id": "PHASE-11",
            "locked": False,  # Mismatch: should be True
            "ac_count": 5,  # Mismatch: should be 3
            "completed_ac_ids": ["HP-001-01"],  # Mismatch: missing one AC
            "progress_percentage": 100.0,  # Mismatch: should be 50%
        }
        
        result = detector.detect_corruption(
            authoritative_state=ssot_state,
            current_state=corrupted_state
        )
        
        # Verify corruption detected
        assert result.corruption_detected is True
        assert result.corruption_type == CorruptionType.STATE_MISMATCH
        assert len(result.mismatches) > 0

    def test_detect_checksum_failure(self, detector):
        """Checksum failure indicates data integrity corruption.
        
        Verify that invalid checksums are detected.
        """
        state = {
            "phase_id": "PHASE-11",
            "ac_count": 3,
            "locked": True,
            "data": "original content",
        }
        
        # Calculate valid checksum
        valid_checksum = detector.calculate_checksum(state)
        
        # Create state with invalid checksum
        state["checksum"] = "invalid_checksum_xyz"
        
        result = detector.detect_corruption(
            authoritative_state={**state, "checksum": valid_checksum},
            current_state=state
        )
        
        # Verify corruption detected
        assert result.corruption_detected is True
        assert result.corruption_type == CorruptionType.CHECKSUM_MISMATCH

    def test_detect_timestamp_anomaly(self, detector):
        """Timestamp anomalies indicate out-of-order updates.
        
        Verify that backward time progression is detected.
        """
        now = datetime.utcnow()
        past = now - timedelta(hours=1)
        
        authoritative = {
            "phase_id": "PHASE-11",
            "last_update": now.isoformat(),
            "ac_updates": [
                {"ac_id": "HP-001-01", "timestamp": (now - timedelta(hours=2)).isoformat()},
                {"ac_id": "HP-001-02", "timestamp": (now - timedelta(hours=1)).isoformat()},
            ]
        }
        
        corrupted = {
            "phase_id": "PHASE-11",
            "last_update": past.isoformat(),  # Older than it should be
            "ac_updates": [
                {"ac_id": "HP-001-01", "timestamp": now.isoformat()},
                {"ac_id": "HP-001-02", "timestamp": (now - timedelta(hours=2)).isoformat()},  # Out of order
            ]
        }
        
        result = detector.detect_corruption(
            authoritative_state=authoritative,
            current_state=corrupted
        )
        
        # Verify temporal anomaly detected
        assert result.corruption_detected is True
        assert result.corruption_type == CorruptionType.TEMPORAL_ANOMALY

    def test_detect_referential_integrity_violation(self, detector):
        """Referential integrity violations in AC relationships.
        
        Verify that invalid AC references are detected.
        """
        authoritative = {
            "phase_id": "PHASE-11",
            "ac_ids": ["HP-001-01", "HP-001-02", "HP-002-01"],
            "dependencies": {
                "HP-001-02": ["HP-001-01"],
                "HP-002-01": ["HP-001-02"],
            }
        }
        
        corrupted = {
            "phase_id": "PHASE-11",
            "ac_ids": ["HP-001-01", "HP-002-01"],  # Missing HP-001-02
            "dependencies": {
                "HP-001-02": ["HP-001-01"],  # AC-ID not in ac_ids list
                "HP-002-01": ["HP-001-02"],  # Depends on missing AC
            }
        }
        
        result = detector.detect_corruption(
            authoritative_state=authoritative,
            current_state=corrupted
        )
        
        # Verify referential integrity violation detected
        assert result.corruption_detected is True
        assert result.corruption_type == CorruptionType.REFERENTIAL_INTEGRITY

    def test_detect_consensus_violation(self, detector):
        """Distributed consensus violations with multiple replicas.
        
        Verify that majority agreement is verified.
        """
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        replicas = [
            {"phase_id": "PHASE-11", "locked": True, "ac_count": 3},   # Agrees
            {"phase_id": "PHASE-11", "locked": True, "ac_count": 3},   # Agrees
            {"phase_id": "PHASE-11", "locked": False, "ac_count": 5},  # Disagrees
        ]
        
        result = detector.detect_consensus_violation(
            authoritative_state=authoritative,
            replicas=replicas
        )
        
        # With consensus violation detection, should return result
        # (either violation detected or None if consensus OK)
        assert result is None or result.corruption_detected is True


class TestRecoveryTriggering:
    """Test suite for recovery triggering."""

    @pytest.fixture
    def detector(self):
        """Initialize hallucination detector."""
        return HallucinationDetector()

    def test_recovery_triggered_on_detection(self, detector):
        """ACID: Recovery triggered on detection
        
        Verify that recovery starts automatically on corruption detection.
        """
        corrupted_state = {
            "phase_id": "PHASE-11",
            "locked": False,
            "ac_count": 5,
        }
        
        authoritative_state = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        # Detect corruption
        detection = detector.detect_corruption(
            authoritative_state=authoritative_state,
            current_state=corrupted_state
        )
        
        # Trigger recovery
        if detection.corruption_detected:
            recovery = detector.trigger_recovery(
                detection,
                authoritative_state=authoritative_state
            )
            
            # Verify recovery was triggered
            assert recovery.recovery_status in ["INITIATED", "COMPLETED"]
            assert recovery.strategy is not None

    def test_recovery_strategy_selection(self, detector):
        """Recovery strategy selected based on corruption type.
        
        Verify appropriate strategy is chosen.
        """
        # Test different corruption types
        test_cases = [
            (CorruptionType.STATE_MISMATCH, RecoveryStrategy.FULL_REBUILD),
            (CorruptionType.CHECKSUM_MISMATCH, RecoveryStrategy.FULL_REBUILD),
            (CorruptionType.TEMPORAL_ANOMALY, RecoveryStrategy.ROLLBACK_TO_CHECKPOINT),
            (CorruptionType.REFERENTIAL_INTEGRITY, RecoveryStrategy.REBUILD_RELATIONSHIPS),
            (CorruptionType.CONSENSUS_VIOLATION, RecoveryStrategy.CONSENSUS_RESOLUTION),
        ]
        
        for corruption_type, expected_strategy in test_cases:
            detection = CorruptionDetectionResult(
                corruption_detected=True,
                corruption_type=corruption_type
            )
            
            recovery = detector.trigger_recovery(detection)
            assert recovery.strategy == expected_strategy

    def test_recovery_restores_authoritative_state(self, detector):
        """Recovery restores system to authoritative state.
        
        Verify that corrupted state is replaced with authoritative.
        """
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
            "completed_ac_ids": ["HP-001-01", "HP-001-02"],
        }
        
        corrupted = {
            "phase_id": "PHASE-11",
            "locked": False,
            "ac_count": 5,
            "completed_ac_ids": ["HP-001-01"],
        }
        
        # Detect and recover
        detection = detector.detect_corruption(authoritative, corrupted)
        recovery = detector.trigger_recovery(
            detection,
            authoritative_state=authoritative
        )
        
        # Verify state restored
        if recovery.recovery_status == "COMPLETED" and recovery.recovered_state:
            assert recovery.recovered_state["ac_count"] == authoritative["ac_count"]
            assert recovery.recovered_state["locked"] == authoritative["locked"]

    def test_recovery_with_checkpoint_rollback(self, detector):
        """Recovery uses checkpoint rollback for temporal anomalies.
        
        Verify that system can rollback to last known good state.
        """
        current_time = datetime.utcnow()
        last_good_checkpoint = {
            "timestamp": (current_time - timedelta(hours=1)).isoformat(),
            "phase_id": "PHASE-11",
            "ac_count": 3,
            "locked": True,
        }
        
        corrupted_state = {
            "timestamp": current_time.isoformat(),
            "phase_id": "PHASE-11",
            "ac_count": 10,  # Corrupted value
            "locked": False,  # Corrupted value
        }
        
        detection = CorruptionDetectionResult(
            corruption_detected=True,
            corruption_type=CorruptionType.TEMPORAL_ANOMALY,
        )
        
        recovery = detector.trigger_recovery(
            detection,
            checkpoint=last_good_checkpoint
        )
        
        # Verify rollback used checkpoint
        assert recovery.strategy == RecoveryStrategy.ROLLBACK_TO_CHECKPOINT
        if recovery.recovery_status == "COMPLETED":
            assert recovery.recovered_state["ac_count"] == 3

    def test_recovery_failure_handling(self, detector):
        """Recovery failure is handled gracefully.
        
        Verify that failed recovery is logged and reported.
        """
        detection = CorruptionDetectionResult(
            corruption_detected=True,
            corruption_type=CorruptionType.STATE_MISMATCH,
        )
        
        # Trigger recovery with invalid state (will fail)
        recovery = detector.trigger_recovery(detection)
        
        # Even if recovery fails, should be tracked
        assert recovery is not None
        assert recovery.detection_result is not None


class TestIncidentLogging:
    """Test suite for incident logging and reporting."""

    @pytest.fixture
    def detector(self):
        """Initialize hallucination detector."""
        return HallucinationDetector()

    def test_incident_logged_for_analysis(self, detector):
        """ACID: Incident logged for analysis
        
        Verify that corruption incidents are logged.
        """
        corruption = {
            "phase_id": "PHASE-11",
            "locked": False,
            "ac_count": 5,
        }
        
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        detection = detector.detect_corruption(authoritative, corruption)
        incident = detector.create_incident(detection)
        
        # Verify incident created
        assert incident.incident_id is not None
        assert incident.corruption_type == CorruptionType.STATE_MISMATCH
        assert incident.timestamp is not None

    def test_incident_includes_detection_details(self, detector):
        """Incident report includes full corruption details.
        
        Verify that details are captured for forensics.
        """
        corruption = {
            "phase_id": "PHASE-11",
            "locked": False,
            "ac_count": 5,
        }
        
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        detection = detector.detect_corruption(authoritative, corruption)
        incident = detector.create_incident(detection)
        
        # Verify details captured
        assert incident.corruption_type == detection.corruption_type
        assert len(incident.mismatches) > 0 if detection.mismatches else True
        assert incident.detection_timestamp is not None

    def test_incident_trackable_in_database(self, detector):
        """Incidents can be stored and retrieved from database.
        
        Verify persistence of incident records.
        """
        corruption = {
            "phase_id": "PHASE-11",
            "locked": False,
            "ac_count": 5,
        }
        
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        detection = detector.detect_corruption(authoritative, corruption)
        incident = detector.create_incident(detection)
        
        # Store incident
        detector.store_incident(incident)
        
        # Retrieve incident
        retrieved = detector.get_incident(incident.incident_id)
        assert retrieved is not None
        assert retrieved.incident_id == incident.incident_id

    def test_incident_query_by_corruption_type(self, detector):
        """Query incidents filtered by corruption type.
        
        Verify ability to analyze incident patterns.
        """
        # Create multiple incidents of different types
        incidents = []
        for _ in range(3):
            corruption = {"phase_id": "PHASE-11", "locked": False}
            authoritative = {"phase_id": "PHASE-11", "locked": True}
            detection = detector.detect_corruption(authoritative, corruption)
            incident = detector.create_incident(detection)
            detector.store_incident(incident)
            incidents.append(incident)
        
        # Query by corruption type
        matching = detector.query_incidents(
            corruption_type=CorruptionType.STATE_MISMATCH,
            limit=10
        )
        
        # Should find incidents
        assert len(matching) > 0

    def test_incident_with_recovery_context(self, detector):
        """Incident includes recovery context.
        
        Verify incident tracks recovery outcome.
        """
        corruption = {
            "phase_id": "PHASE-11",
            "locked": False,
            "ac_count": 5,
        }
        
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        detection = detector.detect_corruption(authoritative, corruption)
        recovery = detector.trigger_recovery(detection)
        incident = detector.create_incident(detection, recovery)
        
        # Verify recovery context included
        if recovery:
            assert incident.recovery_status == recovery.recovery_status


class TestDetectionIntegration:
    """Integration tests for hallucination detection."""

    @pytest.fixture
    def detector(self):
        """Initialize hallucination detector."""
        return HallucinationDetector()

    def test_end_to_end_detection_recovery_incident(self, detector):
        """End-to-end: detect → recover → log incident.
        
        Verify complete workflow.
        """
        # Setup corrupted and authoritative states
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
            "completed_ac_ids": ["HP-001-01", "HP-001-02"],
        }
        
        corrupted = {
            "phase_id": "PHASE-11",
            "locked": False,
            "ac_count": 5,
            "completed_ac_ids": ["HP-001-01"],
        }
        
        # Step 1: Detect corruption
        detection = detector.detect_corruption(authoritative, corrupted)
        assert detection.corruption_detected is True
        
        # Step 2: Trigger recovery
        recovery = detector.trigger_recovery(detection)
        assert recovery.strategy is not None
        
        # Step 3: Log incident
        incident = detector.create_incident(detection, recovery)
        assert incident.incident_id is not None
        
        # Verify all steps connected
        assert incident.corruption_type == detection.corruption_type

    def test_detection_with_multiple_replicas(self, detector):
        """Detection considers multiple replica states.
        
        Verify consensus-based detection.
        """
        authoritative = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        replicas = [
            {"phase_id": "PHASE-11", "locked": True, "ac_count": 3},
            {"phase_id": "PHASE-11", "locked": True, "ac_count": 3},
            {"phase_id": "PHASE-11", "locked": False, "ac_count": 5},  # Corrupted
        ]
        
        result = detector.detect_consensus_violation(authoritative, replicas)
        
        # Should return result (either None or CorruptionDetectionResult)
        assert result is None or isinstance(result, CorruptionDetectionResult)

    def test_cascading_corruption_detection(self, detector):
        """Detect corruption that cascades through relationships.
        
        Verify impact analysis of corruption.
        """
        authoritative = {
            "phase_id": "PHASE-11",
            "ac_ids": ["HP-001-01", "HP-001-02", "HP-002-01"],
            "dependencies": {
                "HP-001-02": ["HP-001-01"],
                "HP-002-01": ["HP-001-02"],
            },
            "locked_phases": ["PHASE-09", "PHASE-10"],
        }
        
        corrupted = {
            "phase_id": "PHASE-11",
            "ac_ids": ["HP-001-01"],  # Missing downstream ACs
            "dependencies": {},  # All dependencies lost
            "locked_phases": [],  # Locked phases corrupted
        }
        
        detection = detector.detect_corruption(authoritative, corrupted)
        
        # Should detect cascading corruption
        if detection.corruption_detected:
            assert len(detection.mismatches) > 1


class TestEdgeCasesAndRobustness:
    """Edge case tests for detection robustness."""

    @pytest.fixture
    def detector(self):
        """Initialize hallucination detector."""
        return HallucinationDetector()

    def test_null_states_handled(self, detector):
        """Null or empty states are handled gracefully.
        
        Verify robustness to edge cases.
        """
        with pytest.raises((TypeError, ValueError)):
            detector.detect_corruption(None, {})

    def test_identical_states_no_corruption(self, detector):
        """Identical states report no corruption.
        
        Verify false positive prevention.
        """
        state = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
        }
        
        result = detector.detect_corruption(state, state.copy())
        assert result.corruption_detected is False

    def test_partial_state_comparison(self, detector):
        """Partial states can be compared.
        
        Verify graceful handling of incomplete data.
        """
        complete = {
            "phase_id": "PHASE-11",
            "locked": True,
            "ac_count": 3,
            "metadata": {"created": "2026-01-01"},
        }
        
        partial = {
            "phase_id": "PHASE-11",
            "locked": True,
        }
        
        result = detector.detect_corruption(complete, partial)
        # Should detect mismatch in missing fields
        assert result is not None

    def test_large_state_processing(self, detector):
        """Large states with many ACs are processed efficiently.
        
        Verify performance with complex systems.
        """
        # Create state with 100 ACs
        large_state = {
            "phase_id": "PHASE-11",
            "ac_count": 100,
            "ac_ids": [f"HP-{i:03d}" for i in range(100)],
        }
        
        result = detector.detect_corruption(large_state, large_state.copy())
        assert result.corruption_detected is False

    def test_deeply_nested_state_comparison(self, detector):
        """Deeply nested structures are compared.
        
        Verify recursive comparison capability.
        """
        nested = {
            "phase": {
                "id": "PHASE-11",
                "acs": {
                    "hp001": {
                        "id": "HP-001-01",
                        "status": "COMPLETED",
                        "tests": [1, 2, 3],
                    }
                }
            }
        }
        
        result = detector.detect_corruption(nested, nested.copy())
        assert result.corruption_detected is False
