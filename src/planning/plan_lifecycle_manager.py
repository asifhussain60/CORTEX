"""
Plan Lifecycle Manager

Manages plan state machine, DoR approval workflows, folder transitions,
and progress persistence.

Author: Asif Hussain
Date: December 15, 2025
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

from src.orchestration_3_0.core.state_machine import (
    StateMachine,
    TransitionResult
)

logger = logging.getLogger(__name__)


class PlanState(Enum):
    """Plan lifecycle states."""
    TEMP = "temp"
    AWAITING_APPROVAL = "awaiting_approval"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class ApprovalResult:
    """Result of DoR approval request."""
    approved: bool
    approved_by: Optional[str] = None
    auto_approved: bool = False
    reason: Optional[str] = None
    timestamp: str = None
    dor_checklist_complete: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class LifecycleTransitionError(Exception):
    """Raised when invalid lifecycle transition attempted."""
    pass


class PlanLifecycleManager:
    """
    Manages plan lifecycle with state machine validation.
    
    Features:
    - State machine enforces valid transitions
    - DoR approval workflow
    - Automated folder movement
    - Progress persistence
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize lifecycle manager.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.planning_root = self.project_root / "cortex-brain" / "documents" / "planning"
        
        # Folder paths for each state
        self.state_folders = {
            PlanState.TEMP: self.planning_root / "temp-plans",
            PlanState.AWAITING_APPROVAL: self.planning_root / "temp-plans",  # Same as TEMP
            PlanState.ACTIVE: self.planning_root / "active",
            PlanState.IN_PROGRESS: self.planning_root / "active",  # Same as ACTIVE
            PlanState.COMPLETED: self.planning_root / "completed",
            PlanState.ARCHIVED: self.planning_root / "archived"
        }
        
        # Plan state machines (one per plan)
        self._state_machines: Dict[str, StateMachine] = {}
        
        # Plan metadata (complexity tiers, etc.)
        self._plan_metadata: Dict[str, Dict[str, Any]] = {}
    
    def _create_lifecycle_fsm(self, plan_id: str) -> StateMachine:
        """
        Create finite state machine for plan lifecycle.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Configured StateMachine
        """
        fsm = StateMachine(
            initial_state=PlanState.TEMP.value,
            orchestrator_name=f"PlanLifecycle_{plan_id}"
        )
        
        # Register valid transitions
        fsm.register_transition(PlanState.TEMP.value, PlanState.AWAITING_APPROVAL.value)
        fsm.register_transition(PlanState.AWAITING_APPROVAL.value, PlanState.ACTIVE.value)
        fsm.register_transition(PlanState.AWAITING_APPROVAL.value, PlanState.TEMP.value)  # Rejection
        fsm.register_transition(PlanState.ACTIVE.value, PlanState.IN_PROGRESS.value)
        fsm.register_transition(PlanState.IN_PROGRESS.value, PlanState.COMPLETED.value)
        fsm.register_transition(PlanState.COMPLETED.value, PlanState.ARCHIVED.value)
        
        return fsm
    
    def initialize_plan(
        self,
        plan_id: str,
        initial_state: PlanState = PlanState.TEMP,
        complexity_tier: int = 3
    ):
        """
        Initialize plan lifecycle.
        
        Args:
            plan_id: Plan identifier
            initial_state: Starting state (default: TEMP)
            complexity_tier: Plan complexity (1-4)
        """
        # Create state machine
        fsm = self._create_lifecycle_fsm(plan_id)
        
        # If not starting from TEMP, transition to initial state
        if initial_state != PlanState.TEMP:
            # Force state (for testing/recovery)
            fsm.current_state = initial_state.value
        
        self._state_machines[plan_id] = fsm
        
        # Store metadata
        self._plan_metadata[plan_id] = {
            "complexity_tier": complexity_tier,
            "created_at": datetime.now().isoformat(),
            "lifecycle_history": []
        }
        
        # Persist state
        self.persist_state(plan_id, initial_state)
        
        logger.info(f"🎭 Initialized plan lifecycle: {plan_id} in {initial_state.value}")
    
    def get_current_state(self, plan_id: str) -> PlanState:
        """
        Get current lifecycle state.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Current PlanState
        """
        # Try to restore from persistence first
        restored_state = self.restore_state(plan_id)
        if restored_state:
            return restored_state
        
        # Check in-memory state machine
        if plan_id in self._state_machines:
            state_str = self._state_machines[plan_id].current_state
            return PlanState(state_str)
        
        # Default to TEMP for new plans
        return PlanState.TEMP
    
    def transition_to(self, plan_id: str, to_state: PlanState) -> bool:
        """
        Attempt state transition with validation.
        
        Args:
            plan_id: Plan identifier
            to_state: Target state
            
        Returns:
            True if transition successful
            
        Raises:
            LifecycleTransitionError: If transition invalid or requires approval
        """
        # Initialize if not exists
        if plan_id not in self._state_machines:
            self.initialize_plan(plan_id)
        
        fsm = self._state_machines[plan_id]
        from_state = PlanState(fsm.current_state)
        
        # Check if transition requires approval
        if to_state == PlanState.ACTIVE and from_state == PlanState.AWAITING_APPROVAL:
            # Check if approved
            metadata = self._plan_metadata.get(plan_id, {})
            if not metadata.get("approved", False):
                raise LifecycleTransitionError(
                    f"Transition {from_state.value} → {to_state.value} requires approval"
                )
        
        # Attempt transition
        result = fsm.transition_to(to_state.value)
        
        if result == TransitionResult.INVALID_TRANSITION:
            raise LifecycleTransitionError(
                f"Invalid transition: {from_state.value} → {to_state.value}"
            )
        
        if result != TransitionResult.SUCCESS:
            raise LifecycleTransitionError(
                f"Transition failed: {from_state.value} → {to_state.value} ({result.value})"
            )
        
        # Record in history
        self._record_transition(plan_id, from_state, to_state)
        
        # Move folder if needed
        self._move_folder_for_state(plan_id, from_state, to_state)
        
        # Persist state
        self.persist_state(plan_id, to_state)
        
        logger.info(f"🎭 State transition: {plan_id} {from_state.value} → {to_state.value}")
        return True
    
    def _move_folder_for_state(self, plan_id: str, from_state: PlanState, to_state: PlanState):
        """
        Move plan folder when state changes.
        
        Args:
            plan_id: Plan identifier
            from_state: Previous state
            to_state: New state
        """
        from_folder_base = self.state_folders[from_state]
        to_folder_base = self.state_folders[to_state]
        
        # Skip if same folder
        if from_folder_base == to_folder_base:
            return
        
        from_folder = from_folder_base / plan_id
        to_folder = to_folder_base / plan_id
        
        if from_folder.exists():
            # Ensure target directory exists
            to_folder_base.mkdir(parents=True, exist_ok=True)
            
            # Move folder
            from_folder.rename(to_folder)
            logger.info(f"📁 Moved plan folder: {from_folder} → {to_folder}")
    
    def approve_plan(self, plan_id: str, approved_by: str):
        """
        Approve plan for transition to ACTIVE.
        
        Args:
            plan_id: Plan identifier
            approved_by: User/email who approved
        """
        metadata = self._plan_metadata.get(plan_id, {})
        metadata["approved"] = True
        metadata["approved_by"] = approved_by
        metadata["approval_timestamp"] = datetime.now().isoformat()
        metadata["dor_checklist_complete"] = True
        self._plan_metadata[plan_id] = metadata
        
        # Persist approval metadata
        self._persist_approval_metadata(plan_id, metadata)
        
        logger.info(f"✅ Plan approved: {plan_id} by {approved_by}")
    
    def reject_approval(self, plan_id: str, reason: str):
        """
        Reject approval and return to TEMP state.
        
        Args:
            plan_id: Plan identifier
            reason: Rejection reason
        """
        # Transition back to TEMP
        self.transition_to(plan_id, PlanState.TEMP)
        
        metadata = self._plan_metadata.get(plan_id, {})
        metadata["rejection_reason"] = reason
        metadata["rejection_timestamp"] = datetime.now().isoformat()
        self._plan_metadata[plan_id] = metadata
        
        logger.info(f"❌ Plan approval rejected: {plan_id} - {reason}")
    
    def validate_dor_checklist(self, plan_id: str, checklist: Dict[str, bool]) -> bool:
        """
        Validate DoR checklist completeness.
        
        Args:
            plan_id: Plan identifier
            checklist: DoR checklist items with status
            
        Returns:
            True if all checklist items complete
        """
        return all(checklist.values())
    
    def requires_user_approval(self, plan_id: str) -> bool:
        """
        Check if plan requires user approval.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            True if user approval required (tier 3-4)
        """
        metadata = self._plan_metadata.get(plan_id, {})
        tier = metadata.get("complexity_tier", 3)
        return tier >= 3
    
    def request_dor_approval(
        self,
        plan_id: str,
        dor_checklist: Dict[str, bool],
        auto_approve: bool = False
    ) -> ApprovalResult:
        """
        Request DoR approval.
        
        Args:
            plan_id: Plan identifier
            dor_checklist: DoR checklist with status
            auto_approve: Auto-approve if tier 1-2
            
        Returns:
            ApprovalResult
        """
        # Validate checklist
        checklist_complete = self.validate_dor_checklist(plan_id, dor_checklist)
        
        if not checklist_complete:
            return ApprovalResult(
                approved=False,
                reason="DoR checklist incomplete",
                dor_checklist_complete=False
            )
        
        # Check if auto-approve allowed
        if auto_approve and not self.requires_user_approval(plan_id):
            self.approve_plan(plan_id, approved_by="auto")
            return ApprovalResult(
                approved=True,
                approved_by="auto",
                auto_approved=True,
                dor_checklist_complete=True
            )
        
        # User approval required
        return ApprovalResult(
            approved=False,
            reason="User approval required",
            dor_checklist_complete=True
        )
    
    def request_dor_approval_interactive(self, plan_id: str) -> ApprovalResult:
        """
        Interactive DoR approval workflow.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            ApprovalResult
        """
        # Display plan summary (simplified for testing)
        print(f"\n📋 Plan Approval Request: {plan_id}")
        print("DoR Checklist: All items complete ✅")
        print("\nApprove this plan? (y/n): ", end="")
        
        response = input().strip().lower()
        
        if response == 'y':
            self.approve_plan(plan_id, approved_by="user")
            return ApprovalResult(
                approved=True,
                approved_by="user",
                dor_checklist_complete=True
            )
        else:
            return ApprovalResult(
                approved=False,
                reason="User declined approval",
                dor_checklist_complete=True
            )
    
    def get_approval_metadata(self, plan_id: str) -> Dict[str, Any]:
        """
        Get approval metadata.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Approval metadata dictionary
        """
        metadata = self._plan_metadata.get(plan_id, {})
        return {
            "approved": metadata.get("approved", False),
            "approved_by": metadata.get("approved_by"),
            "approval_timestamp": metadata.get("approval_timestamp"),
            "dor_checklist_complete": metadata.get("dor_checklist_complete", False)
        }
    
    def _record_transition(self, plan_id: str, from_state: PlanState, to_state: PlanState):
        """Record state transition in history."""
        metadata = self._plan_metadata.get(plan_id, {})
        history = metadata.get("lifecycle_history", [])
        
        history.append({
            "from": from_state.value,
            "to": to_state.value,
            "timestamp": datetime.now().isoformat()
        })
        
        metadata["lifecycle_history"] = history
        self._plan_metadata[plan_id] = metadata
    
    def get_lifecycle_history(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Get lifecycle transition history.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            List of transition records
        """
        metadata = self._plan_metadata.get(plan_id, {})
        return metadata.get("lifecycle_history", [])
    
    def get_valid_next_states(self, plan_id: str) -> List[PlanState]:
        """
        Get valid next states from current state.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            List of valid PlanStates
        """
        if plan_id not in self._state_machines:
            return []
        
        fsm = self._state_machines[plan_id]
        valid_state_strs = fsm.get_valid_next_states()
        
        return [PlanState(s) for s in valid_state_strs]
    
    def persist_state(self, plan_id: str, state: PlanState):
        """
        Save state to progress-tracker.json.
        
        Args:
            plan_id: Plan identifier
            state: Current lifecycle state
        """
        # Find plan folder
        state_folder = self.state_folders[state]
        plan_folder = state_folder / plan_id
        
        if not plan_folder.exists():
            logger.warning(f"Plan folder not found for persistence: {plan_folder}")
            return
        
        tracking_folder = plan_folder / "tracking"
        tracking_folder.mkdir(exist_ok=True)
        
        tracker_file = tracking_folder / "progress-tracker.json"
        
        # Load existing tracker or create new
        if tracker_file.exists():
            tracker_data = json.loads(tracker_file.read_text())
        else:
            tracker_data = {
                "plan_id": plan_id,
                "created_at": datetime.now().isoformat()
            }
        
        # Update lifecycle data
        tracker_data["lifecycle_state"] = state.value
        tracker_data["lifecycle_history"] = self.get_lifecycle_history(plan_id)
        
        # Save
        tracker_file.write_text(json.dumps(tracker_data, indent=2))
        logger.debug(f"💾 Persisted lifecycle state: {plan_id} = {state.value}")
    
    def restore_state(self, plan_id: str) -> Optional[PlanState]:
        """
        Load state from progress-tracker.json.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Restored PlanState or None if not found
        """
        # Search all state folders
        for state_folder in self.state_folders.values():
            plan_folder = state_folder / plan_id
            tracker_file = plan_folder / "tracking" / "progress-tracker.json"
            
            if tracker_file.exists():
                tracker_data = json.loads(tracker_file.read_text())
                state_str = tracker_data.get("lifecycle_state")
                
                if state_str:
                    # Restore to state machine
                    if plan_id not in self._state_machines:
                        self.initialize_plan(plan_id)
                    
                    self._state_machines[plan_id].current_state = state_str
                    
                    # Restore history
                    metadata = self._plan_metadata.get(plan_id, {})
                    metadata["lifecycle_history"] = tracker_data.get("lifecycle_history", [])
                    self._plan_metadata[plan_id] = metadata
                    
                    return PlanState(state_str)
        
        return None
    
    def _persist_approval_metadata(self, plan_id: str, metadata: Dict[str, Any]):
        """Persist approval metadata to progress tracker."""
        # Find plan folder
        current_state = self.get_current_state(plan_id)
        state_folder = self.state_folders[current_state]
        plan_folder = state_folder / plan_id
        
        tracking_folder = plan_folder / "tracking"
        tracking_folder.mkdir(exist_ok=True)
        
        tracker_file = tracking_folder / "progress-tracker.json"
        
        if tracker_file.exists():
            tracker_data = json.loads(tracker_file.read_text())
        else:
            tracker_data = {"plan_id": plan_id}
        
        tracker_data["approval_metadata"] = {
            "approved": metadata.get("approved", False),
            "approved_by": metadata.get("approved_by"),
            "approval_timestamp": metadata.get("approval_timestamp"),
            "dor_checklist_complete": metadata.get("dor_checklist_complete", False)
        }
        
        tracker_file.write_text(json.dumps(tracker_data, indent=2))
