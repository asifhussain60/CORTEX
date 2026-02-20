"""
Registry Sync Service - Event-driven automatic registry updates.
Authority: WAVE-1 Foundation - Event Infrastructure
Purpose: Subscribe to orchestrator events and update registry YAML automatically.
"""

import pytest
from pathlib import Path
import yaml
from datetime import datetime
from cortex.core.registry.sync.registry_sync_service import RegistrySyncService
from cortex.core.event_bus import EventBus, Event


class TestRegistrySyncService:
    """Test automatic registry synchronization via events."""
    
    def test_service_initialization(self, tmp_path):
        """Test RegistrySyncService initializes with event bus and registry path."""
        # AC_START: AC-WAVE1-TEST-011
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        assert service.event_bus is bus
        assert service.registry_path == str(registry_path)
        # AC_COMPLETE: AC-WAVE1-TEST-011 ✅
    
    def test_service_subscribes_to_events(self, tmp_path):
        """Test service subscribes to completion events on initialization."""
        # AC_START: AC-WAVE1-TEST-012
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Verify subscriptions
        assert "PhaseCompleted" in bus.subscribers
        assert "StageCompleted" in bus.subscribers
        assert "OperationCompleted" in bus.subscribers
        # AC_COMPLETE: AC-WAVE1-TEST-012 ✅
    
    def test_phase_completed_updates_status(self, tmp_path):
        """Test PhaseCompleted event updates phase status in registry."""
        # AC_START: AC-WAVE1-TEST-013
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        # Create test phase file
        phase_file = registry_path / "phase-test.yaml"
        phase_file.write_text(yaml.dump({
            "id": "PHASE-TEST",
            "status": "IN_PROGRESS",
            "stages": []
        }))
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Emit PhaseCompleted event
        event = Event(
            type="PhaseCompleted",
            payload={
                "phase_id": "PHASE-TEST",
                "test_results": {"passed": 10, "failed": 0},
                "duration_ms": 5000
            }
        )
        bus.publish(event)
        
        # Verify status updated
        updated = yaml.safe_load(phase_file.read_text())
        assert updated["status"] == "COMPLETE"
        assert "completion_date" in updated
        assert updated["test_results"]["passed"] == 10
        # AC_COMPLETE: AC-WAVE1-TEST-013 ✅
    
    def test_stage_completed_updates_stage_status(self, tmp_path):
        """Test StageCompleted event updates stage status within phase."""
        # AC_START: AC-WAVE1-TEST-014
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        phase_file = registry_path / "phase-test.yaml"
        phase_file.write_text(yaml.dump({
            "id": "PHASE-TEST",
            "status": "IN_PROGRESS",
            "stages": [
                {"id": "S1", "status": "IN_PROGRESS"},
                {"id": "S2", "status": "PENDING"}
            ]
        }))
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Emit StageCompleted event
        event = Event(
            type="StageCompleted",
            payload={
                "phase_id": "PHASE-TEST",
                "stage_id": "S1",
                "test_count": 5
            }
        )
        bus.publish(event)
        
        # Verify stage status updated
        updated = yaml.safe_load(phase_file.read_text())
        assert updated["stages"][0]["status"] == "COMPLETE"
        assert updated["stages"][1]["status"] == "PENDING"  # Unchanged
        # AC_COMPLETE: AC-WAVE1-TEST-014 ✅
    
    def test_operation_completed_updates_enhancement(self, tmp_path):
        """Test OperationCompleted event updates enhancement status."""
        # AC_START: AC-WAVE1-TEST-015
        registry_path = tmp_path / "registry"
        enhancements_dir = registry_path / "enhancements" / "active"
        enhancements_dir.mkdir(parents=True)
        
        enh_file = enhancements_dir / "enh-001.yaml"
        enh_file.write_text(yaml.dump({
            "id": "ENH-001",
            "status": "IN_PROGRESS"
        }))
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Emit OperationCompleted event
        event = Event(
            type="OperationCompleted",
            payload={
                "enhancement_id": "ENH-001",
                "operation": "implement",
                "success": True
            }
        )
        bus.publish(event)
        
        # Verify enhancement status updated
        updated = yaml.safe_load(enh_file.read_text())
        assert updated["status"] == "COMPLETE"
        # AC_COMPLETE: AC-WAVE1-TEST-015 ✅
    
    def test_event_processing_under_100ms(self, tmp_path):
        """Test event processing completes within 100ms SLA."""
        # AC_START: AC-WAVE1-TEST-016
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        phase_file = registry_path / "phase-test.yaml"
        phase_file.write_text(yaml.dump({
            "id": "PHASE-TEST",
            "status": "IN_PROGRESS"
        }))
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Measure processing time
        import time
        start = time.time()
        
        event = Event(
            type="PhaseCompleted",
            payload={"phase_id": "PHASE-TEST"}
        )
        bus.publish(event)
        
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 100, f"Processing took {elapsed_ms}ms (>100ms SLA)"
        # AC_COMPLETE: AC-WAVE1-TEST-016 ✅
    
    def test_missing_file_handling(self, tmp_path):
        """Test service handles missing registry files gracefully."""
        # AC_START: AC-WAVE1-TEST-017
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Emit event for non-existent phase (should not raise)
        event = Event(
            type="PhaseCompleted",
            payload={"phase_id": "NONEXISTENT"}
        )
        bus.publish(event)  # Should not raise
        # AC_COMPLETE: AC-WAVE1-TEST-017 ✅
    
    def test_concurrent_updates_handled(self, tmp_path):
        """Test service handles concurrent event updates safely."""
        # AC_START: AC-WAVE1-TEST-018
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        phase_file = registry_path / "phase-test.yaml"
        phase_file.write_text(yaml.dump({
            "id": "PHASE-TEST",
            "status": "IN_PROGRESS",
            "stages": [
                {"id": "S1", "status": "IN_PROGRESS"},
                {"id": "S2", "status": "IN_PROGRESS"}
            ]
        }))
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Emit multiple stage completions rapidly
        bus.publish(Event(type="StageCompleted", payload={"phase_id": "PHASE-TEST", "stage_id": "S1"}))
        bus.publish(Event(type="StageCompleted", payload={"phase_id": "PHASE-TEST", "stage_id": "S2"}))
        
        # Verify both updates applied
        updated = yaml.safe_load(phase_file.read_text())
        assert updated["stages"][0]["status"] == "COMPLETE"
        assert updated["stages"][1]["status"] == "COMPLETE"
        # AC_COMPLETE: AC-WAVE1-TEST-018 ✅
    
    def test_backup_created_before_update(self, tmp_path):
        """Test service creates backup before modifying registry files."""
        # AC_START: AC-WAVE1-TEST-019
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        phase_file = registry_path / "phase-test.yaml"
        original_content = yaml.dump({"id": "PHASE-TEST", "status": "IN_PROGRESS"})
        phase_file.write_text(original_content)
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Emit update event
        event = Event(type="PhaseCompleted", payload={"phase_id": "PHASE-TEST"})
        bus.publish(event)
        
        # Verify backup exists
        backup_files = list(registry_path.glob("*.backup"))
        assert len(backup_files) > 0
        # AC_COMPLETE: AC-WAVE1-TEST-019 ✅
    
    def test_multiple_registry_files_updated(self, tmp_path):
        """Test service can update multiple registry files in sequence."""
        # AC_START: AC-WAVE1-TEST-020
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        # Create multiple phase files
        for i in range(3):
            phase_file = registry_path / f"phase-{i}.yaml"
            phase_file.write_text(yaml.dump({
                "id": f"PHASE-{i}",
                "status": "IN_PROGRESS"
            }))
        
        bus = EventBus()
        service = RegistrySyncService(event_bus=bus, registry_path=str(registry_path))
        
        # Complete all phases
        for i in range(3):
            event = Event(type="PhaseCompleted", payload={"phase_id": f"PHASE-{i}"})
            bus.publish(event)
        
        # Verify all updated
        for i in range(3):
            phase_file = registry_path / f"phase-{i}.yaml"
            updated = yaml.safe_load(phase_file.read_text())
            assert updated["status"] == "COMPLETE"
        # AC_COMPLETE: AC-WAVE1-TEST-020 ✅
