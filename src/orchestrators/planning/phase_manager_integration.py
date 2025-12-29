"""
CORTEX 4.0 PhaseManager Integration - Orchestrator Lifecycle Management

Purpose: Integrates PlanningOrchestrator with BaseOrchestrator's PhaseManager
         for standardized phase transitions, progress tracking, and validation.
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19 (Week 8 Day 3)

Key Features:
- PhaseManager lifecycle integration
- Phase transition coordination
- Progress tracking and metrics
- Validation checkpoint enforcement
- Error handling and recovery
- Phase state persistence

Architecture:
- PhaseManagerIntegration: Main integration coordinator
- PhaseTransitionHandler: Phase-specific transition logic
- PhaseValidationGate: DoR/DoD validation at boundaries
- PhaseProgressTracker: Progress monitoring and metrics

Integration Points:
- BaseOrchestrator: Core orchestrator framework
- PlanExecutor: Execution engine
- ValidationFramework: Multi-layer validation (Week 9)
- SessionManager: State persistence
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import json

from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorStatus
)

logger = logging.getLogger(__name__)


# ============================================================================
# Domain Models
# ============================================================================

class PhaseValidationType(Enum):
    """Phase validation types."""
    DOR = "definition_of_ready"       # Pre-phase validation
    DOD = "definition_of_done"        # Post-phase validation
    QUALITY_GATE = "quality_gate"     # Quality metrics validation


@dataclass
class PhaseTransition:
    """Phase transition metadata."""
    from_phase: str
    to_phase: str
    timestamp: datetime = field(default_factory=datetime.now)
    validation_result: Optional[Dict[str, Any]] = None
    duration_seconds: float = 0.0
    success: bool = True
    errors: List[str] = field(default_factory=list)


@dataclass
class PhaseProgress:
    """Phase execution progress."""
    phase_name: str
    status: OrchestratorStatus
    progress_percent: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# PhaseManager Integration
# ============================================================================

class PhaseManagerIntegration:
    """
    Integrates PlanningOrchestrator with BaseOrchestrator's PhaseManager.
    
    Responsibilities:
    - Coordinate phase transitions
    - Validate phase boundaries (DoR/DoD)
    - Track progress and metrics
    - Handle errors and recovery
    - Persist phase state
    """
    
    def __init__(
        self,
        orchestrator: BaseOrchestrator,
        workspace_root: Path,
        logger_instance: Optional[logging.Logger] = None
    ):
        """
        Initialize PhaseManager integration.
        
        Args:
            orchestrator: BaseOrchestrator instance (PlanningOrchestrator)
            workspace_root: User workspace root directory
            logger_instance: Optional logger instance
        """
        self.orchestrator = orchestrator
        self.workspace_root = Path(workspace_root)
        self.logger = logger_instance or logger
        
        # Phase tracking
        self.phase_history: List[PhaseTransition] = []
        self.current_progress: Dict[str, PhaseProgress] = {}
        
        # State persistence
        self.state_file = self.workspace_root / ".cortex" / "phase_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def begin_phase(
        self,
        phase_name: str,
        validation_handler: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> bool:
        """
        Begin a new phase with DoR validation.
        
        Workflow:
        1. Validate DoR (Definition of Ready) if handler provided
        2. Create phase progress tracker
        3. Update orchestrator status
        4. Log phase transition
        5. Persist state
        
        Args:
            phase_name: Name of phase to begin
            validation_handler: Optional DoR validation handler
        
        Returns:
            True if phase began successfully, False otherwise
        """
        self.logger.info(f"🎭 Phase transition: {self.orchestrator.current_phase} → {phase_name}")
        
        try:
            # Validate DoR
            if validation_handler:
                dor_valid = validation_handler({
                    "phase_name": phase_name,
                    "orchestrator_status": self.orchestrator.status
                })
                
                if not dor_valid:
                    self.logger.error(f"❌ DoR validation failed for phase: {phase_name}")
                    return False
            
            # Create phase progress tracker
            progress = PhaseProgress(
                phase_name=phase_name,
                status=OrchestratorStatus.RUNNING,
                start_time=datetime.now()
            )
            self.current_progress[phase_name] = progress
            
            # Update orchestrator
            previous_phase = self.orchestrator.current_phase
            self.orchestrator.current_phase = phase_name
            self.orchestrator.status = OrchestratorStatus.RUNNING
            
            # Record transition
            transition = PhaseTransition(
                from_phase=previous_phase,
                to_phase=phase_name,
                success=True
            )
            self.phase_history.append(transition)
            
            # Persist state
            self._persist_state()
            
            self.logger.info(f"✅ Phase {phase_name} began successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Failed to begin phase {phase_name}: {e}", exc_info=True)
            return False
    
    def complete_phase(
        self,
        phase_name: str,
        validation_handler: Optional[Callable[[Dict[str, Any]], bool]] = None,
        phase_metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Complete a phase with DoD validation.
        
        Workflow:
        1. Validate DoD (Definition of Done) if handler provided
        2. Update phase progress
        3. Calculate phase duration
        4. Store phase metrics
        5. Persist state
        
        Args:
            phase_name: Name of phase to complete
            validation_handler: Optional DoD validation handler
            phase_metrics: Optional phase execution metrics
        
        Returns:
            True if phase completed successfully, False otherwise
        """
        self.logger.info(f"✅ Completing phase: {phase_name}")
        
        try:
            # Validate DoD
            if validation_handler:
                dod_valid = validation_handler({
                    "phase_name": phase_name,
                    "phase_metrics": phase_metrics or {}
                })
                
                if not dod_valid:
                    self.logger.error(f"❌ DoD validation failed for phase: {phase_name}")
                    return False
            
            # Update phase progress
            if phase_name in self.current_progress:
                progress = self.current_progress[phase_name]
                progress.status = OrchestratorStatus.COMPLETED
                progress.end_time = datetime.now()
                progress.progress_percent = 100.0
                
                # Calculate duration
                if progress.start_time:
                    duration = (progress.end_time - progress.start_time).total_seconds()
                    progress.metrics["duration_seconds"] = duration
                
                # Store phase metrics
                if phase_metrics:
                    progress.metrics.update(phase_metrics)
            
            # Persist state
            self._persist_state()
            
            self.logger.info(f"✅ Phase {phase_name} completed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Failed to complete phase {phase_name}: {e}", exc_info=True)
            return False
    
    def fail_phase(
        self,
        phase_name: str,
        error_message: str,
        errors: Optional[List[str]] = None
    ) -> None:
        """
        Mark phase as failed.
        
        Args:
            phase_name: Name of failed phase
            error_message: Error message
            errors: Optional list of detailed errors
        """
        self.logger.error(f"❌ Phase {phase_name} failed: {error_message}")
        
        # Update phase progress
        if phase_name in self.current_progress:
            progress = self.current_progress[phase_name]
            progress.status = OrchestratorStatus.FAILED
            progress.end_time = datetime.now()
            progress.metrics["errors"] = errors or [error_message]
        
        # Update orchestrator status
        self.orchestrator.status = OrchestratorStatus.FAILED
        
        # Persist state
        self._persist_state()
    
    def update_progress(
        self,
        phase_name: str,
        progress_percent: float,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update phase progress.
        
        Args:
            phase_name: Name of phase to update
            progress_percent: Progress percentage (0-100)
            metrics: Optional progress metrics
        """
        if phase_name not in self.current_progress:
            self.logger.warning(f"⚠️  Phase {phase_name} not found in progress tracker")
            return
        
        progress = self.current_progress[phase_name]
        progress.progress_percent = min(100.0, max(0.0, progress_percent))
        
        if metrics:
            progress.metrics.update(metrics)
        
        # Persist state
        self._persist_state()
    
    def get_phase_progress(self, phase_name: str) -> Optional[PhaseProgress]:
        """
        Get progress for specific phase.
        
        Args:
            phase_name: Phase name
        
        Returns:
            PhaseProgress or None if phase not found
        """
        return self.current_progress.get(phase_name)
    
    def get_all_progress(self) -> Dict[str, PhaseProgress]:
        """
        Get progress for all phases.
        
        Returns:
            Dictionary of phase_name -> PhaseProgress
        """
        return self.current_progress.copy()
    
    def get_phase_history(self) -> List[PhaseTransition]:
        """
        Get phase transition history.
        
        Returns:
            List of PhaseTransition objects
        """
        return self.phase_history.copy()
    
    def _persist_state(self) -> None:
        """
        Persist phase state to disk for recovery.
        
        Week 8 Day 3: Basic JSON persistence
        Week 9: Enhanced with SessionManager integration
        """
        try:
            state_data = {
                "current_phase": self.orchestrator.current_phase,
                "orchestrator_status": self.orchestrator.status.value,
                "phase_history": [
                    {
                        "from_phase": t.from_phase,
                        "to_phase": t.to_phase,
                        "timestamp": t.timestamp.isoformat(),
                        "success": t.success,
                        "errors": t.errors
                    }
                    for t in self.phase_history
                ],
                "current_progress": {
                    phase_name: {
                        "phase_name": p.phase_name,
                        "status": p.status.value,
                        "progress_percent": p.progress_percent,
                        "start_time": p.start_time.isoformat() if p.start_time else None,
                        "end_time": p.end_time.isoformat() if p.end_time else None,
                        "metrics": p.metrics
                    }
                    for phase_name, p in self.current_progress.items()
                }
            }
            
            self.state_file.write_text(json.dumps(state_data, indent=2))
            self.logger.debug(f"💾 Phase state persisted: {self.state_file}")
        
        except Exception as e:
            self.logger.error(f"❌ Failed to persist phase state: {e}", exc_info=True)
    
    def restore_state(self) -> bool:
        """
        Restore phase state from disk.
        
        Returns:
            True if state restored successfully, False otherwise
        """
        if not self.state_file.exists():
            self.logger.info("ℹ️  No phase state file found")
            return False
        
        try:
            state_data = json.loads(self.state_file.read_text())
            
            # Restore orchestrator state
            self.orchestrator.current_phase = state_data["current_phase"]
            self.orchestrator.status = OrchestratorStatus(state_data["orchestrator_status"])
            
            # Restore phase history
            self.phase_history = [
                PhaseTransition(
                    from_phase=t["from_phase"],
                    to_phase=t["to_phase"],
                    timestamp=datetime.fromisoformat(t["timestamp"]),
                    success=t["success"],
                    errors=t["errors"]
                )
                for t in state_data["phase_history"]
            ]
            
            # Restore current progress
            self.current_progress = {
                phase_name: PhaseProgress(
                    phase_name=p["phase_name"],
                    status=OrchestratorStatus(p["status"]),
                    progress_percent=p["progress_percent"],
                    start_time=datetime.fromisoformat(p["start_time"]) if p["start_time"] else None,
                    end_time=datetime.fromisoformat(p["end_time"]) if p["end_time"] else None,
                    metrics=p["metrics"]
                )
                for phase_name, p in state_data["current_progress"].items()
            }
            
            self.logger.info(f"✅ Phase state restored: {len(self.phase_history)} transitions, {len(self.current_progress)} phases")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Failed to restore phase state: {e}", exc_info=True)
            return False
    
    def clear_state(self) -> None:
        """Clear phase state (after successful completion)."""
        self.phase_history.clear()
        self.current_progress.clear()
        
        if self.state_file.exists():
            self.state_file.unlink()
            self.logger.info("🗑️  Phase state cleared")
