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
    
    def _regenerate_dashboard(self, dashboard_data_file: Optional[Path] = None) -> bool:
        """
        Regenerate dashboard data from phase registry.
        
        Reads all phase data and generates plan-summary.json with statistics.
        
        AC_PHASE1-STUB-001: Replace stub with real implementation using PlanRegistry.list_plans()
        """
        try:
            from cortex.registry.plan_registry import PlanRegistry
            
            registry = PlanRegistry()
            
            # Get all plans/phases from registry
            plans = registry.list_plans() or []
            
            # Generate dashboard data
            dashboard_data = {
                'generated_at': datetime.now().isoformat(),
                'total_phases': len(plans),
                'completed_phases': sum(1 for p in plans if p.status in ['COMPLETED', 'COMPLETE']),
                'phases': [
                    {
                        'id': p.plan_id,
                        'title': p.title,
                        'status': p.status,
                        'priority': p.priority,
                        'roi_score': p.roi_score,
                        'created': p.created
                    }
                    for p in plans
                ]
            }
            
            # Save JSON data file
            if not dashboard_data_file:
                dashboard_data_file = Path('_workspaces/dashboard/data/plan-summary.json')
            
            dashboard_data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(dashboard_data_file, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
            
            self.logger.info(f"✅ Dashboard regenerated at {dashboard_data_file}")
            # AC_PHASE1-STUB-001-COMPLETE
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Dashboard regeneration failed: {e}", exc_info=True)
            return False

    def _trigger_registry_sync(self, index_file: Optional[Path] = None) -> bool:
        """
        Trigger plan registry sync to update master statistics.
        
        AC_PHASE1-STUB-002: Replace stub with real synchronization logic
        """
        try:
            from cortex.registry.plan_registry import PlanRegistry
            
            registry = PlanRegistry()
            plans = registry.list_plans()
            
            # Update index with phase counts
            index = registry._load_index()
            index['active_phases_count'] = len([p for p in plans if p.status != 'COMPLETED'])
            index['completed_phases_count'] = len([p for p in plans if p.status == 'COMPLETED'])
            index['total_phases'] = len(plans)
            index['last_sync'] = datetime.now().isoformat()
            
            registry._save_index()
            
            self.logger.info(f"✅ Registry sync completed")
            # AC_PHASE1-STUB-002-COMPLETE
            return True
        except Exception as e:
            self.logger.error(f"❌ Registry sync failed: {e}", exc_info=True)
            return False

    def _update_enhancement_history(self, enhancement_id: str, phase_key: str) -> bool:
        """
        Update enhancement history tracking with completion metadata.
        
        AC_PHASE1-STUB-003: Replace stub with real history tracking
        """
        try:
            history_file = Path('docs/meta/enhancement_history.yaml')
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load or create history
            if history_file.exists():
                history = yaml.safe_load(history_file.read_text()) or []
            else:
                history = []
            
            # Update or create entry
            found = False
            for entry in history:
                if entry.get('enhancement_id') == enhancement_id:
                    entry['phase_key'] = phase_key
                    entry['completed_at'] = datetime.now().isoformat()
                    entry['status'] = 'COMPLETED'
                    found = True
                    break
            
            if not found:
                history.append({
                    'enhancement_id': enhancement_id,
                    'phase_key': phase_key,
                    'completed_at': datetime.now().isoformat(),
                    'status': 'COMPLETED'
                })
            
            # Save updated history
            with open(history_file, 'w') as f:
                yaml.dump(history, f, default_flow_style=False)
            
            self.logger.info(f"✅ Enhancement history updated: {enhancement_id}")
            # AC_PHASE1-STUB-003-COMPLETE
            return True
        except Exception as e:
            self.logger.error(f"❌ History update failed: {e}", exc_info=True)
            return False

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

        return False
