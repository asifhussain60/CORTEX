"""
Status update hook for orchestrator completion events.

Automatically updates the cortex-registry when orchestrators complete phases,
maintaining registry synchronization without manual intervention.

AC_START: AC-WAVE-3-AUTOMATION-HOOKS-001
Description: StatusUpdateHook implementation for phase completion registry sync
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import yaml


logger = logging.getLogger(__name__)


class StatusUpdateHook:
    """
    Hook triggered on orchestrator phase completion.

    Updates registry with completion status, timestamps, and metrics
    within 5-minute SLA requirement.

    Attributes:
        registry_path: Path to cortex-registry root
        sla_seconds: Maximum update latency (default: 300s = 5 min)
    """

    def __init__(self, registry_path: Optional[Path] = None, sla_seconds: int = 300) -> None:
        """
        Initialize status update hook.

        Args:
            registry_path: Path to registry root (defaults to cortex-registry/)
            sla_seconds: Maximum update latency in seconds (default: 300)
        """
        self.registry_path = registry_path or Path("cortex-registry")
        self.sla_seconds = sla_seconds
        self._update_count = 0

    def on_phase_complete(
        self,
        phase_id: str,
        status: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Handle phase completion event.

        Args:
            phase_id: Phase identifier (e.g., "phase-51")
            status: Completion status ("COMPLETE", "PARTIAL", "FAILED")
            metrics: Optional metrics dictionary (tests, coverage, duration)

        Returns:
            True if registry updated successfully within SLA

        Raises:
            ValueError: If phase_id invalid or status not recognized
        """
        if not phase_id:
            raise ValueError("phase_id cannot be empty")

        valid_statuses = {"COMPLETE", "PARTIAL", "FAILED"}
        if status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}, got: {status}")

        start_time = datetime.now()

        try:
            # Locate phase file in registry
            phase_file = self._find_phase_file(phase_id)
            if not phase_file:
                logger.warning(f"Phase file not found for {phase_id}, skipping update")
                return False

            # Update phase YAML
            updated = self._update_phase_yaml(phase_file, status, metrics)

            # Check SLA compliance
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > self.sla_seconds:
                logger.warning(
                    f"SLA violation: Update took {elapsed:.2f}s (limit: {self.sla_seconds}s)"
                )
                return False

            self._update_count += 1
            logger.info(f"Phase {phase_id} updated to {status} in {elapsed:.2f}s")
            return updated

        except Exception as e:
            logger.error(f"Failed to update phase {phase_id}: {e}")
            return False

    def _find_phase_file(self, phase_id: str) -> Optional[Path]:
        """
        Locate phase YAML file in registry.

        Args:
            phase_id: Phase identifier

        Returns:
            Path to phase file or None if not found
        """
        # Check active phases first
        active_dir = self.registry_path / "_cortex-master" / "phases" / "active"
        if active_dir.exists():
            phase_file = active_dir / f"{phase_id}.yaml"
            if phase_file.exists():
                return phase_file

        # Check completed phases
        completed_dir = self.registry_path / "_cortex-master" / "phases" / "completed"
        if completed_dir.exists():
            phase_file = completed_dir / f"{phase_id}.yaml"
            if phase_file.exists():
                return phase_file

        return None

    def _update_phase_yaml(
        self,
        phase_file: Path,
        status: str,
        metrics: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Update phase YAML file with completion data.

        Args:
            phase_file: Path to phase YAML file
            status: Completion status
            metrics: Optional metrics dictionary

        Returns:
            True if update successful
        """
        try:
            # Load existing YAML
            with open(phase_file, "r") as f:
                data = yaml.safe_load(f) or {}

            # Update status and timestamp
            data["status"] = status
            data["updated_at"] = datetime.now().isoformat()

            # Add metrics if provided
            if metrics:
                data["metrics"] = metrics

            # Write back to file
            with open(phase_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            return True

        except Exception as e:
            logger.error(f"Failed to update YAML {phase_file}: {e}")
            return False

    def get_update_count(self) -> int:
        """
        Get total number of successful updates.

        Returns:
            Update count since initialization
        """
        return self._update_count
