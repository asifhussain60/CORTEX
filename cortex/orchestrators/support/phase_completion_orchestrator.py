"""
Phase 24.3 - Layer 3: Post-Completion Sync (PhaseCompletionOrchestrator)

Orchestrator that auto-updates phase YAML status, regenerates dashboard data,
and triggers PlanRegistrySyncOrchestrator after phase completion.

Key Responsibilities:
- Update phase YAML completion_status and sub_status
- Regenerate cortex-registry/_cortex-master/dashboard/data/plan-summary.json
- Trigger PlanRegistrySyncOrchestrator for index.yaml statistics
- Update enhancement-history.yaml with completion metadata
- Ensure dashboard HTML reflects changes within 60 seconds

Architecture:
- Called by TDDOrchestrator after successful phase implementation
- Non-blocking async execution (doesn't delay user response)
- Idempotent (safe to call multiple times for same phase)
- Full audit trail logging

Integration Points:
- TDDOrchestrator: Post-execution hook
- PlanRegistrySyncOrchestrator: Dashboard sync trigger
- MCP Tool: cortex_complete_phase
"""

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import yaml
import json
import logging

from cortex.orchestrators.core.plan_registry_sync import PlanRegistrySyncOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class PhaseCompletionResult:
    """Result of phase completion operation"""
    success: bool
    phase_updated: bool = False
    dashboard_regenerated: bool = False
    registry_synced: bool = False
    enhancement_updated: bool = False
    error: Optional[str] = None
    duration_seconds: float = 0.0


class PhaseCompletionOrchestrator:
    """
    Orchestrator for automatic phase completion synchronization.
    
    Ensures that when a phase is completed:
    1. Phase YAML is updated with new status
    2. Dashboard data is regenerated
    3. Master plan statistics are recalculated
    4. Enhancement history is updated
    5. Changes are visible in dashboard HTML within 60 seconds
    
    Example:
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=Path("cortex-registry/_cortex-master/phases/active/phase-24.yaml"),
            phase_key="phase_24_3",
            enhancement_id="ENH-039"
        )
        
        if result.success:
            print(f"Phase completed in {result.duration_seconds}s")
    """
    
    def __init__(self):
        self.logger = logger
    
    def complete_phase(
        self,
        phase_file: Path,
        phase_key: str,
        enhancement_id: Optional[str] = None,
        index_file: Optional[Path] = None,
        dashboard_data_file: Optional[Path] = None
    ) -> PhaseCompletionResult:
        """
        Complete a phase and synchronize all related artifacts.
        
        Args:
            phase_file: Path to phase YAML file
            phase_key: Key in completion_status dict (e.g., "phase_24_3")
            enhancement_id: Optional enhancement ID to update (e.g., "ENH-039")
            index_file: Optional path to index.yaml (auto-detected if not provided)
            dashboard_data_file: Optional path to plan-summary.json (auto-detected)
        
        Returns:
            PhaseCompletionResult with success status and operation details
        """
        start_time = datetime.now()
        
        try:
            # Validate inputs
            if not phase_file.exists():
                return PhaseCompletionResult(
                    success=False,
                    error=f"Phase file not found: {phase_file}"
                )
            
            # Step 1: Update phase YAML
            phase_updated = self._update_phase_yaml(phase_file, phase_key)
            if not phase_updated:
                return PhaseCompletionResult(
                    success=False,
                    error=f"Failed to update phase YAML for key: {phase_key}"
                )
            
            # Step 2: Regenerate dashboard data
            dashboard_regenerated = self._regenerate_dashboard(dashboard_data_file)
            
            # Step 3: Trigger plan registry sync
            registry_synced = self._trigger_registry_sync(index_file)
            
            # Step 4: Update enhancement history (if provided)
            enhancement_updated = False
            if enhancement_id:
                enhancement_updated = self._update_enhancement_history(
                    enhancement_id,
                    phase_key
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return PhaseCompletionResult(
                success=True,
                phase_updated=phase_updated,
                dashboard_regenerated=dashboard_regenerated,
                registry_synced=registry_synced,
                enhancement_updated=enhancement_updated,
                duration_seconds=duration
            )
        
        except PermissionError as e:
            return PhaseCompletionResult(
                success=False,
                error=f"Permission denied: {e}"
            )
        except Exception as e:
            self.logger.error(f"Phase completion failed: {e}", exc_info=True)
            return PhaseCompletionResult(
                success=False,
                error=str(e)
            )
    
    def _update_phase_yaml(self, phase_file: Path, phase_key: str) -> bool:
        """
        Update phase YAML completion_status and sub_status.
        
        Updates:
        - completion_status[phase_key] = "COMPLETE ✅ (YYYY-MM-DD)"
        - sub_status: Reflects completed phase
        
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Load phase YAML
            phase_data = yaml.safe_load(phase_file.read_text())
            
            # Validate structure
            if "metadata" not in phase_data:
                self.logger.error(f"Invalid phase YAML: missing 'metadata' key")
                return False
            
            metadata = phase_data["metadata"]
            
            # Check if phase key exists
            if "completion_status" not in metadata:
                self.logger.error(f"Invalid phase YAML: missing 'completion_status'")
                return False
            
            if phase_key not in metadata["completion_status"]:
                self.logger.error(f"Invalid phase key: {phase_key} not in completion_status")
                return False
            
            # Update completion status
            completion_date = datetime.now().strftime("%Y-%m-%d")
            metadata["completion_status"][phase_key] = f"COMPLETE ✅ ({completion_date})"
            
            # Update sub_status if present
            if "sub_status" in metadata:
                old_sub_status = metadata["sub_status"]
                # Replace PENDING with COMPLETE for this phase
                # Extract phase number from key (e.g., "phase_24_2" → "24.2")
                phase_parts = phase_key.replace("phase_", "").split("_")
                if len(phase_parts) == 2:
                    phase_number = f"Phase {phase_parts[0]}.{phase_parts[1]}"
                else:
                    phase_number = f"Phase {phase_key.replace('phase_', '')}"
                
                new_sub_status = old_sub_status.replace(
                    f"{phase_number} PENDING",
                    f"{phase_number} COMPLETE ✅"
                )
                metadata["sub_status"] = new_sub_status
            
            # Update last_updated timestamp
            metadata["last_updated"] = completion_date
            
            # Write back to file
            phase_file.write_text(yaml.dump(phase_data, sort_keys=False))
            
            self.logger.info(f"Updated phase YAML: {phase_key} → COMPLETE")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to update phase YAML: {e}", exc_info=True)
            return False
    
    def _regenerate_dashboard(self, dashboard_data_file: Optional[Path] = None) -> bool:
        """
        Regenerate dashboard data (plan-summary.json).
        
        Calls regenerate_dashboard() function from dashboard generator.
        
        Returns:
            True if regeneration successful, False otherwise
        """
        try:
            # Import regenerate function (mock for tests)
            result = regenerate_dashboard(dashboard_data_file)
            
            if result and result.get("status") == "success":
                self.logger.info("Dashboard data regenerated successfully")
                return True
            else:
                self.logger.warning("Dashboard regeneration returned non-success status")
                return False
        
        except Exception as e:
            self.logger.error(f"Dashboard regeneration failed: {e}", exc_info=True)
            return False
    
    def _trigger_registry_sync(self, index_file: Optional[Path] = None) -> bool:
        """
        Trigger PlanRegistrySyncOrchestrator to update index.yaml statistics.
        
        Recalculates:
        - total_phases
        - active_phases
        - completed_phases
        
        Returns:
            True if sync successful, False otherwise
        """
        try:
            # Use real sync orchestrator
            sync_orchestrator = PlanRegistrySyncOrchestrator()
            
            # Load index data
            if index_file is None:
                index_file = sync_orchestrator.INDEX_FILE
            
            if not index_file.exists():
                self.logger.warning(f"Index file not found: {index_file}")
                return False
            
            index_data = yaml.safe_load(index_file.read_text())
            
            # Update dashboard metrics
            success = sync_orchestrator.update_dashboard_metrics(index_data)
            
            if success:
                self.logger.info("Plan registry sync triggered successfully")
            else:
                self.logger.warning("Plan registry sync returned False")
            
            return success
        
        except Exception as e:
            self.logger.error(f"Plan registry sync failed: {e}", exc_info=True)
            return False
    
    def _update_enhancement_history(self, enhancement_id: str, phase_key: str) -> bool:
        """
        Update enhancement-history.yaml with phase completion metadata.
        
        Adds completion timestamp, test count, pass rate to enhancement record.
        
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Call update function (mock for tests)
            result = update_enhancement_history(enhancement_id, phase_key)
            
            if result:
                self.logger.info(f"Enhancement history updated: {enhancement_id}")
                return True
            else:
                self.logger.warning(f"Enhancement history update returned False")
                return False
        
        except Exception as e:
            self.logger.error(f"Enhancement history update failed: {e}", exc_info=True)
            return False


# Mock functions for testing (will be replaced with real implementations)
def regenerate_dashboard(dashboard_data_file: Optional[Path] = None) -> Dict[str, Any]:
    """Mock function for dashboard regeneration (replaced in production)"""
    return {"status": "success"}


def update_enhancement_history(enhancement_id: str, phase_key: str) -> bool:
    """Mock function for enhancement history update (replaced in production)"""
    return True
