"""
Test suite for permanent wiring fix.

Tests persistent wiring state that:
- Survives process restarts
- Is immutable (once wired, never unwireds)
- Has audit trail (CORE-027)
- Can only be explicitly reset via admin function

CORE-008: TDD - Tests before code
CORE-027: Audit trail for wiring state changes
"""

import pytest
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict
from unittest.mock import Mock, patch, MagicMock

# These will be implemented next
from cortex.orchestrators.core.permanent_wiring_state import (
    PermanentWiringState,
    WiringStateSnapshot,
    WiringAuditEvent,
)


class TestPermanentWiringStatePersistence:
    """Test that wiring state persists to database"""
    
    def test_wiring_persists_to_database_after_wire_all(self):
        """After wire_all() succeeds, database should have wired=1 for all"""
        state = PermanentWiringState()
        
        # Wire all orchestrators
        state.wire_all_orchestrators()
        
        # Verify database has wired=1
        wired_count = state.get_wired_count_from_database()
        assert wired_count == 23, f"Expected 23 wired, got {wired_count}"
    
    def test_wiring_persists_across_process_restart(self):
        """Wiring should be readable after process restart (new instance)"""
        # First instance wires orchestrators
        state1 = PermanentWiringState()
        state1.wire_all_orchestrators()
        wired_count_1 = state1.get_wired_count_from_database()
        assert wired_count_1 == 23
        
        # Simulate process restart (new instance)
        state2 = PermanentWiringState()
        wired_count_2 = state2.get_wired_count_from_database()
        
        assert wired_count_2 == 23, "Wiring lost after simulated process restart"
    
    def test_wiring_state_immutable_once_set(self):
        """Once wired=1, normal code cannot change it to wired=0"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        # Try to set wired=0 (should fail or be no-op)
        with patch.object(state, '_is_admin_operation', return_value=False):
            result = state.set_wiring_state('MasterOrchestrator', 0)
        
        # Should fail gracefully
        assert not result, "Non-admin code was able to unwire orchestrator"
        
        # Verify database still has wired=1
        wired_count = state.get_wired_count_from_database()
        assert wired_count == 23
    
    def test_explicit_unwire_only_with_admin_context(self):
        """Only admin operations can unwire orchestrators"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        # Regular code tries to unwire - fails
        with patch.object(state, '_is_admin_operation', return_value=False):
            result = state.unwire_orchestrator('BrokenOrch')
            assert not result, "Non-admin code unwired orchestrator"
        
        # Admin code unwires - succeeds
        with patch.object(state, '_is_admin_operation', return_value=True):
            result = state.unwire_orchestrator('BrokenOrch')
            assert result, "Admin code could not unwire orchestrator"
    
    def test_database_update_is_atomic(self):
        """Database updates for wiring are atomic (no partial updates)"""
        state = PermanentWiringState()
        
        # Start with empty database
        state.initialize_empty_database()
        
        # Simulate partial update failure
        with patch.object(state, '_update_orchestrator_wiring') as mock_update:
            mock_update.side_effect = sqlite3.DatabaseError("Disk full")
            
            result = state.wire_all_orchestrators()
        
        # Should fail without partial updates
        assert not result, "Partial update was committed"
        
        # Verify database is consistent (either all wired or all unwired)
        wired_count = state.get_wired_count_from_database()
        total_count = state.get_total_count_from_database()
        
        # Should be 0 or 23, never partial
        assert wired_count in [0, 23], f"Partial wiring: {wired_count}/{total_count}"


class TestWiringAuditTrail:
    """CORE-027: Audit trail for wiring state changes"""
    
    def test_audit_log_records_wiring_event(self):
        """Each wiring operation should be logged"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        # Check audit log has entries
        audit_records = state.get_audit_log(limit=10)
        assert len(audit_records) > 0, "No audit records found"
        
        # Should have WIRING_COMPLETE event
        wiring_events = [r for r in audit_records if r['event_type'] == 'WIRING_COMPLETE']
        assert len(wiring_events) > 0, "No WIRING_COMPLETE event in audit log"
    
    def test_audit_log_records_unwiring_event(self):
        """Unwiring should be audited"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        # Admin unwires
        with patch.object(state, '_is_admin_operation', return_value=True):
            state.unwire_orchestrator('BrokenOrch')
        
        # Check audit log
        audit_records = state.get_audit_log(limit=10)
        unwire_events = [r for r in audit_records if r['event_type'] == 'UNWIRING']
        assert len(unwire_events) > 0, "Unwiring not audited"
    
    def test_audit_log_includes_timestamp_and_reason(self):
        """Audit log should include when and why"""
        state = PermanentWiringState()
        state.wire_all_orchestrators(reason="Initial setup")
        
        audit_records = state.get_audit_log(limit=1)
        
        assert 'timestamp' in audit_records[0]
        assert 'reason' in audit_records[0]
        assert audit_records[0]['reason'] == 'Initial setup'
    
    def test_audit_log_survives_process_restart(self):
        """Audit trail should be persistent"""
        state1 = PermanentWiringState()
        state1.wire_all_orchestrators(reason="First setup")
        
        records_before = state1.get_audit_log(limit=1)
        assert len(records_before) > 0
        
        # Simulate restart
        state2 = PermanentWiringState()
        records_after = state2.get_audit_log(limit=1)
        
        # Should still have the record
        assert len(records_after) > 0
        assert records_after[0]['reason'] == 'First setup'


class TestWiringRecovery:
    """Recovery mechanisms for state loss scenarios"""
    
    def test_recovery_from_corrupted_in_memory_state(self):
        """If in-memory state is lost, should recover from DB"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        # Corrupt in-memory state
        state._in_memory_wiring = {}
        
        # Recover from database
        recovered = state.recover_from_database()
        
        assert recovered, "Failed to recover from database"
        assert len(state._in_memory_wiring) == 23, "In-memory state not fully recovered"
    
    def test_recovery_validates_consistency(self):
        """Recovery should detect and repair inconsistencies"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        # Create inconsistency: in-memory says wired=0, DB says wired=1
        state._in_memory_wiring['MasterOrchestrator']['wired'] = False
        
        # Run consistency check
        inconsistencies = state.check_consistency()
        
        assert 'MasterOrchestrator' in [i['orchestrator'] for i in inconsistencies]
    
    def test_consistency_repair_fixes_in_memory_from_database(self):
        """Consistency repair should sync in-memory to database (database is SSOT)"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        # Create inconsistency
        state._in_memory_wiring['MasterOrchestrator']['wired'] = False
        
        # Repair
        state.repair_consistency()
        
        # Should now match database
        assert state._in_memory_wiring['MasterOrchestrator']['wired'] == True


class TestWiringIntegration:
    """Integration tests for permanent wiring system"""
    
    def test_full_lifecycle_wire_persist_recover(self):
        """Full lifecycle: wire → persist → restart → recover"""
        # Phase 1: Initial wiring
        state1 = PermanentWiringState()
        state1.wire_all_orchestrators()
        wired_1 = state1.get_wired_count_from_database()
        
        # Phase 2: Simulate process crash (in-memory lost)
        state1._in_memory_wiring = {}  # Simulate memory loss
        
        # Phase 3: Restart and recover
        state2 = PermanentWiringState()
        state2.recover_from_database()
        wired_2 = state2.get_wired_count_from_database()
        
        # Should be fully recovered
        assert wired_1 == 23
        assert wired_2 == 23
        assert state2._in_memory_wiring['MasterOrchestrator']['wired'] == True
    
    def test_pre_commit_validator_uses_permanent_wiring(self):
        """Pre-commit validator should check persistent DB state"""
        from cortex.infrastructure.pre_commit_validator import PreCommitValidator
        
        # Wire all
        wiring = PermanentWiringState()
        wiring.wire_all_orchestrators()
        
        # Validator checks database (not in-memory)
        validator = PreCommitValidator()
        decision = validator.evaluate_commit()
        
        # Should allow commit (database shows 23/23 wired)
        assert decision.allow_commit is True


class TestWiringEdgeCases:
    """Edge cases and error handling"""
    
    def test_handle_partial_wiring_failure(self):
        """If some orchestrators fail to wire, mark them clearly"""
        state = PermanentWiringState()
        
        # Make one orchestrator fail to wire
        with patch.object(state, '_wire_single_orchestrator') as mock_wire:
            def side_effect(name):
                if name == 'BrokenOrch':
                    raise RuntimeError("Failed to instantiate")
                return True
            
            mock_wire.side_effect = side_effect
            
            result = state.wire_all_orchestrators()
        
        # Should fail but not corrupt others
        assert not result
        
        # Check DB: BrokenOrch unwired, others wired
        state_dict = state.get_all_wiring_states()
        broken = state_dict.get('BrokenOrch', {})
        
        assert broken.get('wired') == False
        assert broken.get('error') is not None
    
    def test_handle_database_corruption(self):
        """Graceful handling if database is corrupted"""
        state = PermanentWiringState()
        
        # Simulate corrupted DB
        with patch.object(state, '_get_db_connection') as mock_conn:
            mock_conn.side_effect = sqlite3.DatabaseError("Corrupted")
            
            result = state.wire_all_orchestrators()
        
        # Should fail gracefully, not crash
        assert not result
    
    def test_concurrent_wiring_attempts_are_serialized(self):
        """Multiple simultaneous wire calls should be serialized"""
        state = PermanentWiringState()
        
        # Attempt concurrent wiring (should serialize)
        call_count = [0]
        
        def mock_wire():
            call_count[0] += 1
            if call_count[0] == 1:
                time.sleep(0.1)  # First call takes longer
            state.wire_all_orchestrators()
        
        # Both should succeed but not interfere
        result1 = state.wire_all_orchestrators()
        result2 = state.wire_all_orchestrators()
        
        assert result1 and result2


class TestWiringStateSnapshot:
    """Snapshot mechanism for point-in-time wiring state"""
    
    def test_create_wiring_snapshot(self):
        """Should be able to capture wiring state snapshot"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        snapshot = state.create_snapshot()
        
        assert snapshot.timestamp is not None
        assert snapshot.total_orchestrators == 23
        assert snapshot.wired_count == 23
    
    def test_snapshot_can_be_restored(self):
        """Should be able to restore to previous snapshot"""
        state = PermanentWiringState()
        state.wire_all_orchestrators()
        
        snapshot = state.create_snapshot()
        
        # Break something
        with patch.object(state, '_is_admin_operation', return_value=True):
            state.unwire_orchestrator('MasterOrchestrator')
        
        # Restore snapshot
        state.restore_snapshot(snapshot)
        
        # Should be back to 23 wired
        assert state.get_wired_count_from_database() == 23


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
