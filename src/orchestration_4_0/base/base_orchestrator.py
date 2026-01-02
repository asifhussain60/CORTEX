"""
Base Orchestrator for CORTEX 4.0

Provides template method pattern for all orchestrators with:
- Phase management
- Error handling
- Lifecycle hooks
- Dependency injection integration
- Progress tracking
- Session management and continuation prompts
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import logging
import subprocess
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .phase_manager import PhaseManager, PhaseStatus
from .error_handler import ErrorHandler, ErrorSeverity, RecoveryStrategy, OrchestratorError


class BaseOrchestrator(ABC):
    """
    Abstract base class for all CORTEX 4.0 orchestrators.
    
    Template Method Pattern:
    1. _setup() - Initialize orchestrator-specific resources
    2. _register_phases() - Define phases for this orchestrator
    3. _execute_phase(phase_name) - Execute a single phase
    4. _teardown() - Cleanup resources
    
    Subclasses must implement these methods.
    """
    
    def __init__(
        self,
        name: str,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base orchestrator.
        
        Args:
            name: Orchestrator name (e.g., "execution", "planning")
            logger: Optional logger instance (created if not provided)
            config: Optional configuration dictionary
        """
        self.name = name
        self.logger = logger or logging.getLogger(f"cortex.orchestration.{name}")
        self.config = config or {}
        
        # Core components
        self.phase_manager = PhaseManager(orchestrator_name=name)
        self.error_handler = ErrorHandler(
            orchestrator_name=name,
            max_retries=self.config.get("max_retries", 3)
        )
        
        # State tracking
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.is_running: bool = False
        self.is_complete: bool = False
        self.result: Optional[Dict[str, Any]] = None
        
        # Session management
        self.token_warning_threshold = self.config.get("token_warning_threshold", 80000)
        self.continuation_prompt_enabled = self.config.get("continuation_prompt_enabled", True)
        self.template_env = None
        if self.continuation_prompt_enabled:
            template_dir = Path(__file__).parent.parent.parent.parent / "templates"
            if template_dir.exists():
                self.template_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        self.logger.info(f"🎭 Orchestrator initialized: {name}")
    
    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution entry point (Template Method).
        
        Orchestrates the full workflow:
        1. Setup
        2. Register phases
        3. Execute phases in order
        4. Handle errors
        5. Teardown
        
        Args:
            context: Execution context data
            
        Returns:
            Execution result dictionary
            
        Raises:
            RuntimeError: If orchestrator already running or critical error occurs
        """
        if self.is_running:
            raise RuntimeError(f"Orchestrator {self.name} already running")
        
        self.is_running = True
        self.started_at = datetime.now()
        self.logger.info(f"🎭 Orchestrator engaged: {self.name}")
        
        try:
            # Step 1: Setup
            self.logger.debug("Running setup...")
            setup_result = self._setup(context or {})
            
            # Step 2: Register phases
            self.logger.debug("Registering phases...")
            self._register_phases()
            
            # Step 3: Execute phases
            self.logger.debug(f"Executing {len(self.phase_manager.phases)} phases...")
            for phase in self.phase_manager.phases:
                self._execute_phase_with_error_handling(phase.name, context or {})
                
                # Stop if critical error occurred
                if self.error_handler.has_critical_errors():
                    self.logger.error("❌ Critical error occurred, stopping execution")
                    break
            
            # Step 4: Collect results
            self.result = self._collect_results()
            
            # Step 5: Determine completion status
            self.is_complete = self._is_workflow_complete()
            
            if self.is_complete:
                self.logger.info(f"🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            return self.result
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator failed: {e}")
            self.error_handler.handle_error(
                phase="orchestrator",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
            raise
        
        finally:
            # Always run teardown
            try:
                self.logger.debug("Running teardown...")
                self._teardown(context or {})
            except Exception as e:
                self.logger.error(f"⚠️  Teardown failed: {e}")
            
            self.is_running = False
            self.completed_at = datetime.now()
            
            # Log summary
            duration = (self.completed_at - self.started_at).total_seconds()
            progress = self.phase_manager.get_progress()
            self.logger.info(
                f"🎭 Orchestrator finished: {self.name} "
                f"({duration:.2f}s, {progress['completed']}/{progress['total_phases']} phases complete)"
            )
    
    def _execute_phase_with_error_handling(
        self,
        phase_name: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Execute a phase with error handling and retry logic.
        
        Args:
            phase_name: Name of phase to execute
            context: Execution context
        """
        while True:
            try:
                # Start phase
                self.phase_manager.start_phase(phase_name)
                
                # Execute phase-specific logic
                result = self._execute_phase(phase_name, context)
                
                # Complete phase
                self.phase_manager.complete_phase(phase_name, result)
                
                # Reset retry counter on success
                self.error_handler.reset_retries(phase_name)
                break
                
            except Exception as e:
                # Handle error
                error = self.error_handler.handle_error(
                    phase=phase_name,
                    exception=e,
                    context={"attempt": self.error_handler.retry_counts.get(phase_name, 0)}
                )
                
                # Fail phase
                self.phase_manager.fail_phase(phase_name, str(e))
                
                # Determine action based on recovery strategy
                if error.recovery_strategy == RecoveryStrategy.RETRY and self.error_handler.can_retry(phase_name):
                    self.error_handler.record_retry(phase_name)
                    self.logger.info(f"🔄 Retrying phase: {phase_name}")
                    self.phase_manager.phases[self.phase_manager.phases.index(
                        self.phase_manager._get_phase(phase_name)
                    )].status = PhaseStatus.PENDING
                    continue
                
                elif error.recovery_strategy == RecoveryStrategy.SKIP:
                    self.phase_manager.skip_phase(phase_name, f"Skipped due to error: {str(e)}")
                    self.logger.warning(f"⏭️  Skipping phase: {phase_name}")
                    break
                
                elif error.recovery_strategy == RecoveryStrategy.FAIL_FAST:
                    self.logger.error(f"❌ Failing fast due to error in phase: {phase_name}")
                    raise
                
                else:
                    # For other strategies, just log and continue
                    self.logger.warning(f"⚠️  Continuing after error in phase: {phase_name}")
                    break
    
    def _collect_results(self) -> Dict[str, Any]:
        """
        Collect results from all phases.
        
        Returns:
            Dictionary with orchestrator results
        """
        phase_results = {}
        for phase in self.phase_manager.phases:
            if phase.result:
                phase_results[phase.name] = phase.result
        
        progress = self.phase_manager.get_progress()
        error_summary = self.error_handler.get_error_summary()
        
        return {
            "orchestrator": self.name,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.started_at).total_seconds() if self.started_at else 0,
            "progress": progress,
            "errors": error_summary,
            "phase_results": phase_results,
            "is_complete": self._is_workflow_complete()
        }
    
    def _is_workflow_complete(self) -> bool:
        """
        Determine if workflow is fully complete.
        
        Returns:
            True if all required phases completed successfully
        """
        # Check if any critical errors
        if self.error_handler.has_critical_errors():
            return False
        
        # Check if all required phases completed
        for phase in self.phase_manager.phases:
            if phase.required and phase.status != PhaseStatus.COMPLETED:
                return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current orchestrator status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "name": self.name,
            "is_running": self.is_running,
            "is_complete": self.is_complete,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "progress": self.phase_manager.get_progress(),
            "errors": self.error_handler.get_error_summary()
        }
    
    # Public wrapper methods for testing and external access
    
    def setup(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Public wrapper for setup.
        
        Args:
            context: Optional execution context
            
        Returns:
            Setup result
        """
        return self._setup(context or {})
    
    def teardown(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Public wrapper for teardown.
        
        Args:
            context: Optional teardown context
            
        Returns:
            Teardown result
        """
        return self._teardown(context or {})
    
    def execute_phase(self, phase_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Public wrapper for phase execution.
        
        Args:
            phase_name: Name of phase to execute
            context: Optional execution context
            
        Returns:
            Phase execution result
        """
        return self._execute_phase(phase_name, context or {})
    
    # Session Management Methods
    
    def update_continuation_prompt(
        self, 
        plan_name: str,
        plan_id: str,
        plan_dir: Path,
        current_phase: Dict[str, Any],
        next_phase: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Generate or update continuation prompt for session handoff.
        
        Args:
            plan_name: Name of the plan being executed
            plan_id: Database plan ID
            plan_dir: Path to plan directory
            current_phase: Current phase information dict
            next_phase: Next phase information dict (if available)
            
        Returns:
            True if prompt generated successfully, False otherwise
        """
        if not self.continuation_prompt_enabled or not self.template_env:
            self.logger.debug("Continuation prompt disabled or template environment unavailable")
            return False
        
        try:
            # Get template
            template = self.template_env.get_template("continuation-prompt.jinja2")
            
            # Get git checkpoints
            checkpoints = self._get_git_checkpoints(limit=5)
            
            # Get completed phases
            completed_phases = self.phase_manager.get_completed_phases()
            total_phases = len(self.phase_manager.phases)
            
            # Calculate progress
            progress_percentage = int((len(completed_phases) / total_phases * 100)) if total_phases > 0 else 0
            
            # Prepare template context
            context = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "plan_name": plan_name,
                "plan_id": plan_id,
                "completed_phases": completed_phases,
                "completed_phases_list": [
                    {
                        "number": i + 1,
                        "name": phase.name,
                        "duration": getattr(phase, "duration", "N/A")
                    }
                    for i, phase in enumerate(completed_phases)
                ],
                "total_phases": total_phases,
                "progress_percentage": progress_percentage,
                "current_phase": current_phase,
                "next_phase": next_phase or {"number": "N/A", "name": "Plan Complete"},
                "checkpoints": checkpoints,
                "plan_status": "IN_PROGRESS" if next_phase else "COMPLETE",
                "artifact_count": len(list(plan_dir.glob("artifacts/*"))) if (plan_dir / "artifacts").exists() else 0
            }
            
            # Render template
            content = template.render(**context)
            
            # Write to tracking directory
            tracking_dir = plan_dir / "tracking"
            tracking_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = tracking_dir / "CONTINUATION-PROMPT.md"
            output_path.write_text(content, encoding="utf-8")
            
            self.logger.info(f"✅ Continuation prompt updated: {output_path}")
            return True
            
        except TemplateNotFound:
            self.logger.warning("⚠️ Continuation prompt template not found: continuation-prompt.jinja2")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error generating continuation prompt: {e}")
            return False
    
    def check_token_usage(self) -> Dict[str, Any]:
        """
        Estimate token usage and check if approaching limit.
        
        Returns:
            Dict with keys:
                - estimated_tokens: Heuristic token count
                - threshold: Warning threshold
                - should_warn: Boolean indicating if warning needed
                - percentage: Current usage as percentage of threshold
        """
        completed_count = len(self.phase_manager.get_completed_phases())
        
        # Heuristic: ~1000 tokens per phase interaction
        estimated_tokens = completed_count * 1000
        
        percentage = (estimated_tokens / self.token_warning_threshold * 100) if self.token_warning_threshold > 0 else 0
        should_warn = estimated_tokens >= self.token_warning_threshold
        
        result = {
            "estimated_tokens": estimated_tokens,
            "threshold": self.token_warning_threshold,
            "should_warn": should_warn,
            "percentage": round(percentage, 1)
        }
        
        if should_warn:
            self.logger.warning(
                f"⚠️ TOKEN WARNING: Estimated {estimated_tokens} tokens "
                f"({percentage:.1f}% of {self.token_warning_threshold} threshold). "
                f"Consider copying continuation prompt for session handoff."
            )
        
        return result
    
    def _estimate_tokens(self, text: str = "") -> int:
        """
        Estimate token count for given text.
        
        Simple heuristic: ~4 characters per token.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return len(self.phase_manager.get_completed_phases()) * 1000
        
        return len(text) // 4
    
    def _get_git_checkpoints(self, limit: int = 5) -> List[Dict[str, str]]:
        """
        Get recent git commits as checkpoints.
        
        Args:
            limit: Maximum number of checkpoints to retrieve
            
        Returns:
            List of checkpoint dicts with keys: hash, message, date
        """
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%h|%s|%ci"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode != 0:
                return []
            
            checkpoints = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        checkpoints.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "date": parts[2][:10]  # Just the date part
                        })
            
            return checkpoints
            
        except Exception as e:
            self.logger.debug(f"Could not retrieve git checkpoints: {e}")
            return []
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    def _setup(self, context: Dict[str, Any]) -> None:
        """
        Setup orchestrator-specific resources.
        
        Called before phases are registered.
        
        Args:
            context: Execution context
        """
        pass
    
    @abstractmethod
    def _register_phases(self) -> None:
        """
        Register all phases for this orchestrator.
        
        Use self.phase_manager.register_phase() to add phases.
        """
        pass
    
    @abstractmethod
    def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a specific phase.
        
        Args:
            phase_name: Name of phase to execute
            context: Execution context
            
        Returns:
            Optional phase result data
        """
        pass
    
    @abstractmethod
    def _teardown(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleanup orchestrator-specific resources.
        
        Called after all phases complete (even if errors occurred).
        
        Args:
            context: Teardown context
            
        Returns:
            Teardown result
        """
        pass
