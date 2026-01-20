"""Tests for AC-DEPLOY-002-02: Emergency Rollback with Point-in-Time Recovery"""
import pytest
from src.deployment.recovery import RecoveryManager, Snapshot, SnapshotStatus
from datetime import datetime


class TestRecoveryManager:
    def test_create_snapshot(self):
        manager = RecoveryManager()
        snap = manager.create_snapshot("1.0.0")
        assert snap.version == "1.0.0"
        assert snap.status == SnapshotStatus.ACTIVE
    
    def test_list_snapshots(self):
        manager = RecoveryManager()
        manager.create_snapshot("1.0.0")
        manager.create_snapshot("2.0.0")
        snaps = manager.list_snapshots()
        assert len(snaps) == 2
    
    def test_recover_to_snapshot(self):
        manager = RecoveryManager()
        snap1 = manager.create_snapshot("1.0.0")
        snap2 = manager.create_snapshot("2.0.0")
        result = manager.recover_to_snapshot(snap1.id)
        assert result is True
        assert manager.current_version == "1.0.0"
    
    def test_recover_nonexistent(self):
        manager = RecoveryManager()
        result = manager.recover_to_snapshot("nonexistent")
        assert result is False
    
    def test_snapshot_recovery_status(self):
        manager = RecoveryManager()
        snap = manager.create_snapshot("1.0.0")
        manager.recover_to_snapshot(snap.id)
        retrieved = manager.get_snapshot(snap.id)
        assert retrieved.status == SnapshotStatus.ACTIVE
    
    def test_point_in_time_recovery(self):
        manager = RecoveryManager()
        v1 = manager.create_snapshot("1.0.0")
        v2 = manager.create_snapshot("2.0.0")
        v3 = manager.create_snapshot("3.0.0")
        manager.recover_to_snapshot(v2.id)
        assert manager.current_version == "2.0.0"
    
    def test_rollback_from_failed(self):
        manager = RecoveryManager()
        good = manager.create_snapshot("stable")
        bad = manager.create_snapshot("broken")
        result = manager.recover_to_snapshot(good.id)
        assert result is True
    
    def test_snapshot_immutability(self):
        manager = RecoveryManager()
        snap = manager.create_snapshot("1.0.0")
        original_data = snap.data.copy()
        manager.recover_to_snapshot(snap.id)
        assert snap.data == original_data
    
    def test_recovery_speed(self):
        manager = RecoveryManager()
        snap = manager.create_snapshot("1.0.0")
        start = datetime.now()
        manager.recover_to_snapshot(snap.id)
        end = datetime.now()
        duration = (end - start).total_seconds()
        assert duration < 5  # Should be quick
    
    def test_multiple_recovery_cycles(self):
        manager = RecoveryManager()
        s1 = manager.create_snapshot("v1")
        s2 = manager.create_snapshot("v2")
        manager.recover_to_snapshot(s1.id)
        assert manager.current_version == "v1"
        manager.recover_to_snapshot(s2.id)
        assert manager.current_version == "v2"
        manager.recover_to_snapshot(s1.id)
        assert manager.current_version == "v1"
    
    def test_snapshot_count(self):
        manager = RecoveryManager()
        for i in range(5):
            manager.create_snapshot(f"{i}.0.0")
        assert len(manager.list_snapshots()) == 5
    
    def test_recovery_with_data_consistency(self):
        manager = RecoveryManager()
        snap = manager.create_snapshot("consistent")
        assert snap.data["version"] == "consistent"
        manager.recover_to_snapshot(snap.id)
        recovered = manager.get_snapshot(snap.id)
        assert recovered.data["version"] == "consistent"
    
    def test_concurrent_snapshots(self):
        manager = RecoveryManager()
        versions = ["v1", "v2", "v3"]
        snaps = [manager.create_snapshot(v) for v in versions]
        assert len(manager.list_snapshots()) == 3
        for i, snap in enumerate(snaps):
            manager.recover_to_snapshot(snap.id)
            assert manager.current_version == versions[i]
    
    def test_recovery_status_tracking(self):
        manager = RecoveryManager()
        snap = manager.create_snapshot("test")
        assert snap.status == SnapshotStatus.ACTIVE
        manager.recover_to_snapshot(snap.id)
        assert manager.get_snapshot(snap.id).status == SnapshotStatus.ACTIVE
    
    def test_empty_recovery_list(self):
        manager = RecoveryManager()
        snaps = manager.list_snapshots()
        assert len(snaps) == 0
