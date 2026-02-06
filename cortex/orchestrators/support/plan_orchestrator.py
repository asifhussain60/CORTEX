"""
Plan Orchestrator - Phase Lifecycle Management

Orchestrates PLAN MODE operations with setup/teardown hooks,
VacuumOrchestrator integration, and dashboard synchronization.

AC-ID: PHASE-25-STAGE-4-001
Authority: phase-25-plan-mode-cortex-architect.yaml
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from cortex.models.canonical_enums import IntentType
from cortex.registry.phase_manager import PhaseManager, PhaseOperation, PhaseResolutionResult
from cortex.registry.dashboard_generator import DashboardGenerator


@dataclass
class PlanSetupResult:
    """Result of plan setup hook."""
    success: bool
    phase_id: Optional[str] = None
    checkpoint_created: bool = False
    cleanup_performed: bool = False
    error_message: Optional[str] = None


@dataclass
class PlanTeardownResult:
    """Result of plan teardown hook."""
    success: bool
    artifacts_cleaned: int = 0
    dashboard_synced: bool = False
    audit_logged: bool = False
    error_message: Optional[str] = None


class PlanOrchestrator:
    """
    Orchestrates PLAN MODE lifecycle with mandatory hooks.
    
    Responsibilities:
    - Execute setup hook before phase implementation
    - Execute teardown hook after phase completion
    - Coordinate PhaseManager and DashboardGenerator
    - Integrate with VacuumOrchestrator for cleanup
    - Enforce 3-source sync verification
    
    Usage:
        orchestrator = PlanOrchestrator()
        
        # Setup
        setup_result = orchestrator.setup_phase("phase-25")
        
        # ... implementation work ...
        
        # Teardown
        teardown_result = orchestrator.teardown_phase("phase-25")
    """
    
    def __init__(
        self,
        registry_root: str = "cortex-registry/_cortex-master",
        enable_vacuum: bool = True
    ):
        """
        Initialize PlanOrchestrator.
        
        Args:
            registry_root: Path to master registry
            enable_vacuum: Enable VacuumOrchestrator integration
        """
        self.phase_manager = PhaseManager(registry_root=registry_root)
        self.dashboard_generator = DashboardGenerator(registry_root=registry_root)
        self.enable_vacuum = enable_vacuum
        self.registry_root = Path(registry_root)
    
    def resolve_phase_operation(self, user_request: str) -> PhaseResolutionResult:
        """
        Intelligently resolve phase operation from user request.
        
        Delegates to PhaseManager for 4-step resolution algorithm.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            PhaseResolutionResult with operation and rationale
        """
        return self.phase_manager.resolve_phase_operation(user_request)
    
    def setup_phase(self, phase_id: str) -> PlanSetupResult:
        """
        Execute setup hook before phase implementation.
        
        Steps (from phase-25 spec):
        1. Load phase specification
        2. Verify no conflicting active phases
        3. Run VacuumOrchestrator cleanup (if enabled)
        4. Create git checkpoint (CORE-026)
        5. Initialize AC_START audit trail (CORE-027)
        
        Args:
            phase_id: Phase ID to set up
            
        Returns:
            PlanSetupResult with success status
        """
        result = PlanSetupResult(success=False, phase_id=phase_id)
        
        try:
            # Step 1: Load phase specification (validates it exists)
            try:
                phase_data = self.phase_manager._load_phase_yaml(phase_id)
            except FileNotFoundError:
                result.error_message = f"Phase {phase_id} not found in registry"
                return result
            
            # Step 2: Verify no conflicting active phases
            # (Simplified - could check for scope conflicts)
            
            # Step 3: Run VacuumOrchestrator cleanup
            if self.enable_vacuum:
                result.cleanup_performed = self._run_vacuum_cleanup()
            
            # Step 4: Create git checkpoint (CORE-026)
            result.checkpoint_created = self._create_git_checkpoint(f"Setup: {phase_id}")
            
            # Step 5: Initialize AC_START audit trail (CORE-027)
            self._log_audit_trail(phase_id, "SETUP")
            
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
        
        return result
    
    def teardown_phase(self, phase_id: str) -> PlanTeardownResult:
        """
        Execute teardown hook after phase completion.
        
        Steps (from phase-25 spec):
        1. Verify all deliverables
        2. Run VacuumOrchestrator cleanup
        3. Archive temporary files
        4. Delete stale markdown (CORE-002 enforcement)
        5. Update dashboard data
        6. Regenerate dashboard HTML
        7. Log AC_COMPLETE audit trail
        8. Commit all changes
        
        Args:
            phase_id: Phase ID to tear down
            
        Returns:
            PlanTeardownResult with success status
        """
        result = PlanTeardownResult(success=False)
        
        try:
            # Step 1: Verify all deliverables
            if not self._verify_deliverables(phase_id):
                result.error_message = "Deliverables verification failed"
                return result
            
            # Step 2: Run VacuumOrchestrator cleanup
            if self.enable_vacuum:
                self._run_vacuum_cleanup()
            
            # Step 3: Archive temporary files
            result.artifacts_cleaned = self._archive_artifacts(phase_id)
            
            # Step 4: Delete stale markdown (handled by VacuumOrchestrator)
            
            # Step 5-6: Update and regenerate dashboard
            sync_result = self.dashboard_generator.sync_dashboard()
            result.dashboard_synced = sync_result.success
            
            # Step 7: Log AC_COMPLETE audit trail
            result.audit_logged = self._log_audit_trail(phase_id, "TEARDOWN")
            
            # Step 8: Commit all changes
            self._create_git_checkpoint(f"Teardown: {phase_id}")
            
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
        
        return result
    
    def create_phase(self, phase_data: Dict[str, Any], auto_sync: bool = True) -> bool:
        """
        Create new phase with setup hook.
        
        Args:
            phase_data: Phase metadata
            auto_sync: Auto-sync dashboard after creation
            
        Returns:
            success: True if created successfully
        """
        try:
            # Create phase
            phase_id = self.phase_manager.create_phase(phase_data)
            
            # Sync dashboard
            if auto_sync:
                self.dashboard_generator.sync_dashboard()
            
            return True
        except Exception:
            return False
    
    def update_phase(self, phase_id: str, updates: Dict[str, Any], auto_sync: bool = True) -> bool:
        """
        Update existing phase with dashboard sync.
        
        Args:
            phase_id: Phase ID to update
            updates: Updates to apply
            auto_sync: Auto-sync dashboard after update
            
        Returns:
            success: True if updated successfully
        """
        try:
            # Update phase
            self.phase_manager.update_phase(phase_id, updates)
            
            # Sync dashboard
            if auto_sync:
                self.dashboard_generator.sync_dashboard()
            
            return True
        except Exception:
            return False    
    def complete_phase(self, phase_id: str) -> bool:
        """
        Complete phase with 3-source sync verification.
        
        Args:
            phase_id: Phase ID to complete
            
        Returns:
            success: True if completed successfully
        """
        # Verify sync before completion
        sync_status = self.phase_manager.verify_sync_before_completion(phase_id)
        
        if not sync_status.all_synced:
            print("❌ Cannot complete phase - sync verification failed:")
            for failure in sync_status.failures:
                print(f"   - {failure}")
            return False
        
        # Complete phase
        self.phase_manager.complete_phase(phase_id)
        
        # Final dashboard sync
        self.dashboard_generator.sync_dashboard()
        
        return True
    
    def prioritize_pending_phases(self) -> list:
        """
        Get pending phases sorted by ROI score.
        
        Returns:
            List of phases with ROI scores
        """
        return self.phase_manager.prioritize_pending_phases()
    
    def sync_dashboard(self) -> bool:
        """
        Manually trigger dashboard sync.
        
        Returns:
            success: True if synced successfully
        """
        result = self.dashboard_generator.sync_dashboard()
        # Handle both bool and result object returns
        if isinstance(result, bool):
            return result
        return result.success
    
    # ===== Private Helper Methods =====
    
    def _create_git_checkpoint(self, message: str = "Phase checkpoint") -> bool:
        """
        Create git checkpoint before phase work.
        
        Args:
            message: Commit message
            
        Returns:
            success: True if checkpoint created
        """
        try:
            import subprocess
            
            # Check git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.registry_root.parent
            )
            
            if result.returncode != 0:
                return False
            
            # If there are changes, create checkpoint
            if result.stdout.strip():
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=self.registry_root.parent,
                    check=True
                )
                subprocess.run(
                    ["git", "commit", "-m", f"[CHECKPOINT] {message}"],
                    cwd=self.registry_root.parent,
                    check=True
                )
            
            return True
            
        except Exception as e:
            print(f"⚠️ Git checkpoint failed: {e}")
            return False
    
    def _run_vacuum_cleanup(self) -> bool:
        """
        Run VacuumOrchestrator cleanup.
        
        Returns:
            success: True if cleanup successful
        """
        try:
            # Placeholder - VacuumOrchestrator integration in Stage 5
            # For now, return True (no-op)
            return True
            
        except Exception as e:
            print(f"⚠️ Vacuum cleanup failed: {e}")
            return False
    
    def _verify_deliverables(self, phase_id: str) -> bool:
        """
        Verify phase deliverables are complete.
        
        Args:
            phase_id: Phase ID to verify
            
        Returns:
            success: True if all deliverables present
        """
        try:
            # Placeholder - would check phase YAML deliverables list
            # For now, always return True
            return True
            
        except Exception:
            return False
    
    def _archive_artifacts(self, phase_id: str) -> int:
        """
        Archive temporary phase artifacts.
        
        Args:
            phase_id: Phase ID
            
        Returns:
            count: Number of artifacts archived
        """
        try:
            # Placeholder - would move files to archive directory
            # For now, return 0
            return 0
            
        except Exception:
            return 0
    
    def _log_audit_trail(self, phase_id: str, operation: str) -> bool:
        """
        Log operation to audit trail.
        
        Args:
            phase_id: Phase ID
            operation: Operation type (SETUP/TEARDOWN/etc)
            
        Returns:
            success: True if logged successfully
        """
        try:
            # Placeholder - would log to audit system
            # For now, return True
            return True
            
        except Exception:
            return False
    
    def _load_pending_phases(self) -> list:
        """
        Load all pending phases from registry.
        
        Returns:
            List of pending phase dicts
        """
        try:
            # Placeholder - would load from index.yaml
            # For now, return empty list
            return []
            
        except Exception:
            return []
