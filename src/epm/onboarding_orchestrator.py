"""
Onboarding Orchestrator

Coordinates onboarding flow execution with progress tracking and error handling.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from pathlib import Path

from .step_registry import StepRegistry
from .onboarding_step import OnboardingStep, StepStatus, StepResult

logger = logging.getLogger(__name__)


class OnboardingProfile(Enum):
    """Onboarding flow profiles"""
    QUICK = "quick"  # 5-7 minutes
    STANDARD = "standard"  # 10-15 minutes
    COMPREHENSIVE = "comprehensive"  # 20-30 minutes


@dataclass
class OnboardingSession:
    """Tracks onboarding session state"""
    session_id: str
    profile: OnboardingProfile
    start_time: datetime
    end_time: Optional[datetime] = None
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    current_step: Optional[str] = None
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OnboardingOrchestrator:
    """
    Orchestrates onboarding flow execution.
    
    Responsibilities:
    - Execute steps in proper order
    - Handle dependencies and prerequisites
    - Track progress and state
    - Enable pause/resume capability
    - Graceful error handling
    - Generate execution reports
    
    Example:
    ```python
    orchestrator = OnboardingOrchestrator()
    
    # Register steps
    orchestrator.registry.register(EnvironmentDetectionStep())
    orchestrator.registry.register(DependencyInstallationStep())
    
    # Start onboarding
    session = orchestrator.start_onboarding(
        profile=OnboardingProfile.STANDARD,
        context={"project_root": Path(".")}
    )
    
    # Steps execute automatically
    # Access results
    print(f"Completed: {session.completed_steps}/{session.total_steps}")
    ```
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize orchestrator.
        
        Args:
            project_root: Project root path (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.registry = StepRegistry()
        self.current_session: Optional[OnboardingSession] = None
        self.logger = logging.getLogger("epm.orchestrator")
    
    def start_onboarding(
        self,
        profile: OnboardingProfile = OnboardingProfile.STANDARD,
        context: Optional[Dict[str, Any]] = None,
        resume_session_id: Optional[str] = None
    ) -> OnboardingSession:
        """
        Start onboarding flow.
        
        Args:
            profile: Onboarding profile to use
            context: Additional execution context
            resume_session_id: Optional session ID to resume
        
        Returns:
            OnboardingSession tracking execution state
        """
        # Create or resume session
        if resume_session_id:
            session = self._resume_session(resume_session_id)
            if not session:
                self.logger.error(f"Failed to resume session {resume_session_id}")
                return self._create_new_session(profile, context)
        else:
            session = self._create_new_session(profile, context)
        
        self.current_session = session
        
        # Execute steps
        self._execute_steps(session)
        
        return session
    
    def _create_new_session(
        self,
        profile: OnboardingProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> OnboardingSession:
        """Create new onboarding session"""
        import uuid
        
        session_id = str(uuid.uuid4())
        session_context = {
            "profile": profile.value,
            "project_root": self.project_root,
            "previous_results": {},
            **(context or {})
        }
        
        steps = self.registry.get_execution_order(profile=profile.value)
        
        session = OnboardingSession(
            session_id=session_id,
            profile=profile,
            start_time=datetime.now(),
            total_steps=len(steps),
            context=session_context
        )
        
        self.logger.info(
            f"Created onboarding session {session_id} "
            f"(profile: {profile.value}, steps: {len(steps)})"
        )
        
        return session
    
    def _resume_session(self, session_id: str) -> Optional[OnboardingSession]:
        """Resume existing session (load from persistence)"""
        # TODO: Implement session persistence and loading
        self.logger.warning("Session resume not yet implemented")
        return None
    
    def _execute_steps(self, session: OnboardingSession) -> None:
        """
        Execute all steps for session.
        
        Args:
            session: Session to execute
        """
        steps = self.registry.get_execution_order(
            profile=session.profile.value,
            skip_completed=True  # Skip if resuming
        )
        
        for step in steps:
            # Update session state
            session.current_step = step.step_id
            
            # Check if step should be skipped
            if step.can_skip(session.context):
                self._skip_step(step, session, "Prerequisites not met or not required for profile")
                continue
            
            # Execute step
            self._execute_step(step, session)
            
            # Check for failures
            if step.status == StepStatus.FAILED and not step.skippable:
                self.logger.error(f"Critical step {step.step_id} failed, aborting onboarding")
                break
        
        # Finalize session
        session.end_time = datetime.now()
        session.current_step = None
        
        self.logger.info(
            f"Onboarding session {session.session_id} completed: "
            f"{session.completed_steps} completed, "
            f"{session.failed_steps} failed, "
            f"{session.skipped_steps} skipped"
        )
    
    def _execute_step(
        self,
        step: OnboardingStep,
        session: OnboardingSession
    ) -> None:
        """
        Execute a single step.
        
        Args:
            step: Step to execute
            session: Current session
        """
        try:
            self.logger.info(f"Executing step: {step.step_id} ({step.name})")
            
            # Update step status
            step.status = StepStatus.RUNNING
            step.start_time = datetime.now()
            
            # Execute step
            result = step.execute(session.context)
            
            # Update step status
            step.end_time = datetime.now()
            step.result = result
            step.status = StepStatus.COMPLETED if result.success else StepStatus.FAILED
            
            # Calculate duration
            duration = (step.end_time - step.start_time).total_seconds()
            result.duration_seconds = duration
            
            # Store result in session
            session.step_results[step.step_id] = result
            session.context["previous_results"][step.step_id] = result.data
            
            # Update session counters
            if result.success:
                session.completed_steps += 1
                self.logger.info(
                    f"✓ Step {step.step_id} completed in {duration:.1f}s: {result.message}"
                )
            else:
                session.failed_steps += 1
                self.logger.error(
                    f"✗ Step {step.step_id} failed after {duration:.1f}s: {result.message}"
                )
                
                # Log errors
                for error in result.errors:
                    self.logger.error(f"  Error: {error}")
            
            # Log warnings
            for warning in result.warnings:
                self.logger.warning(f"  Warning: {warning}")
        
        except Exception as e:
            self.logger.error(f"Exception in step {step.step_id}: {e}", exc_info=True)
            step.status = StepStatus.FAILED
            step.end_time = datetime.now()
            session.failed_steps += 1
    
    def _skip_step(
        self,
        step: OnboardingStep,
        session: OnboardingSession,
        reason: str
    ) -> None:
        """Skip a step with reason"""
        step.status = StepStatus.SKIPPED
        session.skipped_steps += 1
        
        result = StepResult(
            success=True,
            status=StepStatus.SKIPPED,
            message=reason
        )
        
        session.step_results[step.step_id] = result
        
        self.logger.info(f"⊘ Step {step.step_id} skipped: {reason}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        if not self.current_session:
            return {"status": "No active session"}
        
        session = self.current_session
        total = session.total_steps
        completed = session.completed_steps
        progress_pct = (completed / total * 100) if total > 0 else 0
        
        return {
            "session_id": session.session_id,
            "profile": session.profile.value,
            "progress_percent": round(progress_pct, 1),
            "total_steps": total,
            "completed_steps": completed,
            "failed_steps": session.failed_steps,
            "skipped_steps": session.skipped_steps,
            "current_step": session.current_step,
            "elapsed_time_seconds": (
                (datetime.now() - session.start_time).total_seconds()
                if not session.end_time else
                (session.end_time - session.start_time).total_seconds()
            )
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate execution report"""
        if not self.current_session:
            return {"error": "No active session"}
        
        session = self.current_session
        
        return {
            "session_id": session.session_id,
            "profile": session.profile.value,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "total_steps": session.total_steps,
            "completed_steps": session.completed_steps,
            "failed_steps": session.failed_steps,
            "skipped_steps": session.skipped_steps,
            "step_results": {
                step_id: {
                    "success": result.success,
                    "status": result.status.value,
                    "message": result.message,
                    "duration_seconds": result.duration_seconds,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
                for step_id, result in session.step_results.items()
            },
            "registry_stats": self.registry.get_stats()
        }
