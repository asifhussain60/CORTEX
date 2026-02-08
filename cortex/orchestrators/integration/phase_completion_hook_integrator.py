"""
Phase Completion Hook Integrator - Auto-complete phases after successful execution.

AC_START: AC-INTEGRATION-003
Description: Auto-call PhaseCompletionOrchestrator after session completion
Authority: ROOT-CAUSE-ANALYSIS-2026-02-08 (Handoff gaps, Phase continuation)
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PhaseCompletionHookIntegrator:
    """
    Integrates phase completion into the chat execution loop.
    
    When a session successfully completes:
    1. Detects if phase context exists
    2. Calls PhaseCompletionOrchestrator to update registry
    3. Syncs dashboard data
    4. Generates continuation prompt if needed
    """
    
    def __init__(self) -> None:
        """Initialize phase completion hook integrator."""
        self.logger = logger
    
    def detect_phase_context(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect if current session is working on a phase.
        
        Looks for phase identifiers in context:
        - phase_file: Path to phase YAML
        - phase_key: Completion status key
        - phase_id: Phase identifier (e.g., "phase-44")
        
        Args:
            context: Execution context
            
        Returns:
            Phase context dict, or None if not phase-based
        """
        phase_file = context.get("phase_file")
        phase_key = context.get("phase_key")
        phase_id = context.get("phase_id")
        
        if not (phase_file or phase_id):
            return None
        
        # Generate phase_key from phase_id if not provided
        if phase_key is None and phase_id:
            parts = phase_id.split('-')
            phase_num = parts[1] if len(parts) > 1 else "unknown"
            phase_key = f"phase_{phase_num}_completion"
        
        return {
            "phase_file": phase_file,
            "phase_key": phase_key,
            "phase_id": phase_id,
            "execution_context": context,
        }
    
    def on_session_complete(
        self,
        success: bool,
        execution_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle session completion event.
        
        Args:
            success: Whether execution was successful
            execution_result: Result of execution
            context: Execution context
            
        Returns:
            Completion result with phase sync status
        """
        result = {
            "session_complete": True,
            "success": success,
            "phase_synced": False,
            "continuation_prompt": None,
            "errors": [],
        }
        
        if not success:
            return result
        
        # Detect phase context
        phase_context = self.detect_phase_context(context)
        if not phase_context:
            self.logger.debug("No phase context detected, skipping phase completion")
            return result
        
        # Import here to avoid circular imports
        try:
            from cortex.orchestrators.support.phase_completion_orchestrator import (
                PhaseCompletionOrchestrator
            )
            
            orchestrator = PhaseCompletionOrchestrator()
            
            # Call completion orchestrator
            phase_file = Path(phase_context["phase_file"]) if phase_context["phase_file"] else None
            phase_key = phase_context["phase_key"]
            
            if phase_file and phase_file.exists():
                completion_result = orchestrator.complete_phase(
                    phase_file=phase_file,
                    phase_key=phase_key,
                    enhancement_id=context.get("enhancement_id"),
                )
                
                result["phase_synced"] = completion_result.success
                
                if not completion_result.success:
                    result["errors"].append(
                        f"Phase sync failed: {completion_result.error}"
                    )
                    self.logger.warning(
                        f"Phase completion failed for {phase_key}: {completion_result.error}"
                    )
                else:
                    self.logger.info(
                        f"✅ Phase {phase_key} synced to registry (status updated)"
                    )
            
        except Exception as e:
            result["errors"].append(f"Phase completion error: {str(e)}")
            self.logger.error(
                f"Phase completion orchestrator error: {e}",
                exc_info=True
            )
        
        return result
    
    def should_generate_continuation_prompt(
        self,
        token_usage: float,
        token_budget: float = 200000
    ) -> bool:
        """
        Check if continuation prompt should be generated.
        
        Triggers when token usage >= 75% of budget.
        
        Args:
            token_usage: Current token usage
            token_budget: Total token budget
            
        Returns:
            True if continuation prompt should be generated
        """
        threshold = token_budget * 0.75
        return token_usage >= threshold
    
    def generate_continuation_prompt(
        self,
        phase_context: Optional[Dict[str, Any]],
        completed_stages: int,
        total_stages: int,
        test_status: Dict[str, int],
        next_stage_effort: str
    ) -> str:
        """
        Generate structured continuation prompt for next session.
        
        Args:
            phase_context: Current phase context
            completed_stages: Stages completed
            total_stages: Total stages in phase
            test_status: Test pass/fail counts
            next_stage_effort: Estimated effort for next stage
            
        Returns:
            Continuation prompt (200-400 tokens)
        """
        if phase_context is None:
            phase_context = {}
        
        phase_id = phase_context.get('phase_id', 'Unknown')
        phase_num = 'unknown'
        if isinstance(phase_id, str) and '-' in phase_id:
            parts = phase_id.split('-')
            phase_num = parts[1] if len(parts) > 1 else 'unknown'
        
        lines = [
            "## 📋 Continuation Prompt (Copy to New Copilot Session)",
            "",
            "```",
            "Follow instructions in .github/prompts/cortex-architect.prompt.md",
            "",
            f"Phase: {phase_id}",
            f"Progress: {completed_stages}/{total_stages} stages complete",
            f"Tests: {test_status.get('passing', 0)}/{test_status.get('total', 0)} passing",
            "",
            "Status:",
            f"- ✅ Completed: Stages 1-{completed_stages}",
            f"- ⚪ Remaining: Stages {completed_stages + 1}-{total_stages}",
            f"- 📊 Effort: {next_stage_effort}",
            "",
            "Command:",
            f"/implement phase-{phase_num} --continue",
            "```",
        ]
        
        return "\n".join(lines)


# AC_COMPLETE: AC-INTEGRATION-003 ✅
