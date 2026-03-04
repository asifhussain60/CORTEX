"""
Registry Sync Service - Event-driven automatic registry updates.

Authority: WAVE-1 Foundation - Event Infrastructure
Purpose: Subscribe to orchestrator completion events and automatically update
         registry YAML files with status, timestamps, and test results.

Architecture:
- Subscribes to: PhaseCompleted, StageCompleted, OperationCompleted
- Updates: Phase YAML files, enhancement YAML files
- SLA: <100ms event processing time
- Safety: Backup before update, error handling, concurrent update support
"""

from pathlib import Path
from typing import Optional
import yaml
from datetime import datetime
import shutil
from threading import Lock

from cortex.core.event_bus import EventBus, Event


class RegistrySyncService:
    """
    Event subscriber that automatically updates registry YAML files.

    Listens for orchestrator completion events and updates corresponding
    registry files with completion status, timestamps, and metadata.
    """

    def __init__(self, event_bus: EventBus, registry_path: str) -> None:
        """
        Initialize registry sync service.

        Args:
            event_bus: EventBus instance to subscribe to
            registry_path: Root path to registry directory
        """
        self.event_bus = event_bus
        self.registry_path = registry_path
        self._lock = Lock()  # For thread-safe file updates

        # Subscribe to completion events
        self.event_bus.subscribe("PhaseCompleted", self._handle_phase_completed)
        self.event_bus.subscribe("StageCompleted", self._handle_stage_completed)
        self.event_bus.subscribe("OperationCompleted", self._handle_operation_completed)

    def _handle_phase_completed(self, event: Event) -> None:
        """
        Handle PhaseCompleted event - update phase status to COMPLETE.

        Args:
            event: Event with payload containing phase_id, test_results, duration_ms
        """
        payload = event.payload if isinstance(event, Event) else event
        phase_id = payload.get("phase_id")

        if not phase_id:
            return

        # Find phase file
        phase_file = self._find_phase_file(phase_id)
        if not phase_file:
            return  # Phase file not found, skip silently

        # Update phase file with thread safety
        with self._lock:
            try:
                # Backup before update
                self._create_backup(phase_file)

                # Load current content
                with open(phase_file, 'r') as f:
                    phase_data = yaml.safe_load(f)

                # Update status and metadata
                phase_data["status"] = "COMPLETE"
                phase_data["completion_date"] = datetime.now().isoformat()

                if "test_results" in payload:
                    phase_data["test_results"] = payload["test_results"]

                if "duration_ms" in payload:
                    phase_data["duration_ms"] = payload["duration_ms"]

                # Write updated content
                with open(phase_file, 'w') as f:
                    yaml.dump(phase_data, f, default_flow_style=False)

            except Exception as e:
                print(f"Warning: Failed to update phase {phase_id}: {e}")

    def _handle_stage_completed(self, event: Event) -> None:
        """
        Handle StageCompleted event - update stage status within phase.

        Args:
            event: Event with payload containing phase_id, stage_id, test_count
        """
        payload = event.payload if isinstance(event, Event) else event
        phase_id = payload.get("phase_id")
        stage_id = payload.get("stage_id")

        if not phase_id or not stage_id:
            return

        # Find phase file
        phase_file = self._find_phase_file(phase_id)
        if not phase_file:
            return

        # Update stage within phase file
        with self._lock:
            try:
                # Backup before update
                self._create_backup(phase_file)

                # Load current content
                with open(phase_file, 'r') as f:
                    phase_data = yaml.safe_load(f)

                # Update stage status
                if "stages" in phase_data:
                    for stage in phase_data["stages"]:
                        if stage.get("id") == stage_id:
                            stage["status"] = "COMPLETE"
                            if "test_count" in payload:
                                stage["test_count"] = payload["test_count"]
                            break

                # Write updated content
                with open(phase_file, 'w') as f:
                    yaml.dump(phase_data, f, default_flow_style=False)

            except Exception as e:
                print(f"Warning: Failed to update stage {stage_id}: {e}")

    def _handle_operation_completed(self, event: Event) -> None:
        """
        Handle OperationCompleted event - update enhancement status.

        Args:
            event: Event with payload containing enhancement_id, operation, success
        """
        payload = event.payload if isinstance(event, Event) else event
        enhancement_id = payload.get("enhancement_id")

        if not enhancement_id:
            return

        # Find enhancement file
        enh_file = self._find_enhancement_file(enhancement_id)
        if not enh_file:
            return

        # Update enhancement file
        with self._lock:
            try:
                # Backup before update
                self._create_backup(enh_file)

                # Load current content
                with open(enh_file, 'r') as f:
                    enh_data = yaml.safe_load(f)

                # Update status
                if payload.get("success", True):
                    enh_data["status"] = "COMPLETE"
                    enh_data["completion_date"] = datetime.now().isoformat()

                # Write updated content
                with open(enh_file, 'w') as f:
                    yaml.dump(enh_data, f, default_flow_style=False)

            except Exception as e:
                print(f"Warning: Failed to update enhancement {enhancement_id}: {e}")

    def _find_phase_file(self, phase_id: str) -> Optional[Path]:
        """
        Find phase YAML file by phase ID.

        Args:
            phase_id: Phase identifier (e.g., "PHASE-TEST")

        Returns:
            Path to phase file or None if not found
        """
        registry_path = Path(self.registry_path)

        # Try direct match
        phase_file = registry_path / f"{phase_id.lower()}.yaml"
        if phase_file.exists():
            return phase_file

        # Try searching all YAML files
        for yaml_file in registry_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and data.get("id") == phase_id:
                        return yaml_file
            except Exception:
                continue

        return None

    def _find_enhancement_file(self, enhancement_id: str) -> Optional[Path]:
        """
        Find enhancement YAML file by enhancement ID.

        Args:
            enhancement_id: Enhancement identifier (e.g., "ENH-001")

        Returns:
            Path to enhancement file or None if not found
        """
        registry_path = Path(self.registry_path)

        # Check active enhancements
        active_dir = registry_path / "enhancements" / "active"
        if active_dir.exists():
            enh_file = active_dir / f"{enhancement_id.lower()}.yaml"
            if enh_file.exists():
                return enh_file

        return None

    def _create_backup(self, file_path: Path) -> None:
        """
        Create backup of file before modification.

        Args:
            file_path: Path to file to backup
        """
        try:
            backup_path = file_path.with_suffix(".backup")
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            print(f"Warning: Failed to create backup: {e}")
