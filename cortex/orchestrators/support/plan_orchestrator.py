"""
Plan Orchestrator - Phase Lifecycle Management

Orchestrates PLAN MODE operations with setup/teardown hooks,
VacuumOrchestrator integration, dashboard synchronization,
and EventBus-driven state transitions (Phase 45 § Stage 2).

AC-ID: PHASE-25-STAGE-4-001
Authority: phase-25-plan-mode-cortex-architect.yaml
Enhanced: phase-45-enhanced-planning-system.yaml § Stage 2
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from cortex.models.canonical_enums import IntentType
from cortex.models.event_models import (
    EventType,
    OrchestratorEvent,
    PlanCreatedPayload,
    PlanStateChangedPayload,
    PlanArchivedPayload,
)
from cortex.registry.phase_manager import PhaseManager, PhaseOperation, PhaseResolutionResult
from cortex.registry.dashboard_generator import DashboardGenerator
from cortex.registry.plan_registry import PlanRegistry, PlanSpec
from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus



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
        enable_vacuum: bool = True,
        event_bus: Optional[OrchestratorEventBus] = None,
    ):
        """
        Initialize PlanOrchestrator.
        
        Args:
            registry_root: Path to master registry
            enable_vacuum: Enable VacuumOrchestrator integration
            event_bus: OrchestratorEventBus instance for event publishing
        """
        self.phase_manager = PhaseManager(registry_root=registry_root)
        self.dashboard_generator = DashboardGenerator(registry_root=registry_root)
        self.plan_registry = PlanRegistry(registry_path="cortex-registry/planning")
        self.event_bus = event_bus or OrchestratorEventBus()
        self.enable_vacuum = enable_vacuum
        self.registry_root = Path(registry_root)
        self.correlation_id = str(uuid4())
        
        # Subscribe to relevant events (Phase 45 § Stage 2)
        self.event_bus.subscribe(
            EventType.PLAN_INTENT_DETECTED,
            self._handle_plan_intent_detected,
        )
    
    def _handle_plan_intent_detected(self, event: OrchestratorEvent) -> None:
        """Handle PLAN_INTENT_DETECTED events from InteractionOrchestrator.
        
        Triggered when user intent contains plan-related operations.
        Initiates plan creation or enrichment workflow.
        
        Args:
            event: The PLAN_INTENT_DETECTED event
        """
        try:
            payload = event.payload
            plan_id = payload.get("plan_id")
            user_context = payload.get("user_context", "")
            detected_type = payload.get("detected_type", "")
            
            # If creating new plan, initialize it
            if not plan_id:
                plan_id = self._generate_plan_id(detected_type)
            
            # Log event processing
            self._log_audit_trail(plan_id, f"INTENT_DETECTED: {detected_type}")
            
        except Exception as e:
            self._publish_error_event(f"PLAN_INTENT_DETECTED handler failed: {e}")
    
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
            # Handle both bool and result object returns
            if isinstance(sync_result, bool):
                result.dashboard_synced = sync_result
            else:
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

    # ===== Phase 45 Stage 2: Event-Driven Methods =====

    def _generate_plan_id(self, plan_type: str) -> str:
        """
        Generate unique plan ID based on type.
        
        Args:
            plan_type: Type of plan (IMPLEMENT, FIX, REFACTOR, etc.)
            
        Returns:
            Unique plan identifier
        """
        prefix = plan_type.lower()[:3] if plan_type else "plan"
        suffix = str(uuid4())[:8]
        return f"plan-{prefix}-{suffix}"

    def _publish_error_event(self, error_message: str) -> None:
        """
        Publish error event to EventBus.
        
        Args:
            error_message: Error description
        """
        try:
            event = OrchestratorEvent(
                event_type=EventType.ERROR_OCCURRED,
                source_orchestrator="PlanOrchestrator",
                payload={"error": error_message},
                correlation_id=self.correlation_id,
            )
            self.event_bus.publish_event(event)
        except Exception as e:
            # Fallback: log locally if EventBus fails
            print(f"⚠️ Error publishing error event: {e}")

    def create_plan_from_spec(
        self,
        plan_spec: PlanSpec,
        plan_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create new plan with EventBus integration.
        
        Publishes PLAN_CREATED event after successful creation.
        Triggers EnhancedPlanningOrchestrator enrichment via event.
        
        Args:
            plan_spec: Full plan specification
            plan_id: Optional custom plan ID
            
        Returns:
            plan_id if successful, None otherwise
        """
        try:
            # Create plan via registry
            plan_id = self.plan_registry.create_plan(plan_spec, plan_id)
            
            # Publish PLAN_CREATED event
            payload = PlanCreatedPayload(
                plan_id=plan_id,
                title=plan_spec.metadata.title,
                status=plan_spec.metadata.status,
                created_at=plan_spec.metadata.created_date,
            )
            event = OrchestratorEvent(
                event_type=EventType.PLAN_CREATED,
                source_orchestrator="PlanOrchestrator",
                payload=payload.__dict__,
                correlation_id=self.correlation_id,
            )
            self.event_bus.publish_event(event)
            
            # Log audit trail
            self._log_audit_trail(plan_id, "PLAN_CREATED")
            
            return plan_id
            
        except Exception as e:
            self._publish_error_event(f"Plan creation failed: {e}")
            return None

    def update_plan_status(
        self,
        plan_id: str,
        new_status: str,
        reason: str = "",
    ) -> bool:
        """
        Update plan status with PLAN_STATE_CHANGED event.
        
        Args:
            plan_id: Plan identifier
            new_status: New status value
            reason: Reason for state change
            
        Returns:
            True if update successful
        """
        try:
            # Get current plan
            plan_spec = self.plan_registry.get_plan(plan_id)
            old_status = plan_spec.metadata.status
            
            # Update status via registry
            self.plan_registry.update_plan_status(plan_id, new_status)
            
            # Publish PLAN_STATE_CHANGED event
            payload = PlanStateChangedPayload(
                plan_id=plan_id,
                old_status=old_status,
                new_status=new_status,
                reason=reason,
                changed_at=None,
            )
            event = OrchestratorEvent(
                event_type=EventType.PLAN_STATE_CHANGED,
                source_orchestrator="PlanOrchestrator",
                payload=payload.__dict__,
                correlation_id=self.correlation_id,
            )
            self.event_bus.publish_event(event)
            
            # Trigger dashboard sync on state change
            self.dashboard_generator.sync_dashboard()
            
            # Log audit trail
            self._log_audit_trail(plan_id, f"STATUS_CHANGED: {old_status} → {new_status}")
            
            return True
            
        except Exception as e:
            self._publish_error_event(f"Plan status update failed: {e}")
            return False

    def archive_plan(
        self,
        plan_id: str,
        completion_status: str = "completed",
    ) -> bool:
        """
        Archive plan with PLAN_ARCHIVED event.
        
        Moves plan from active/ to completed/YYYY/ directory.
        
        Args:
            plan_id: Plan identifier
            completion_status: Final status (completed/cancelled/deferred)
            
        Returns:
            True if archive successful
        """
        try:
            # Archive via registry
            archive_path = self.plan_registry.archive_plan(plan_id)
            
            # Publish PLAN_ARCHIVED event
            payload = PlanArchivedPayload(
                plan_id=plan_id,
                archive_path=str(archive_path),
                completion_status=completion_status,
                archived_at=None,
            )
            event = OrchestratorEvent(
                event_type=EventType.PLAN_ARCHIVED,
                source_orchestrator="PlanOrchestrator",
                payload=payload.__dict__,
                correlation_id=self.correlation_id,
            )
            self.event_bus.publish_event(event)
            
            # Update dashboard
            self.dashboard_generator.sync_dashboard()
            
            # Log audit trail
            self._log_audit_trail(plan_id, f"PLAN_ARCHIVED: {completion_status}")
            
            return True
            
        except Exception as e:
            self._publish_error_event(f"Plan archival failed: {e}")
            return False

    def subscribe_to_events(
        self,
        event_types: list,
        handler_func,
    ) -> None:
        """
        Register event subscription (convenience method).
        
        Args:
            event_types: List of EventType enums to subscribe to
            handler_func: Callback function for events
        """
        for event_type in event_types:
            self.event_bus.subscribe(event_type, handler_func)
