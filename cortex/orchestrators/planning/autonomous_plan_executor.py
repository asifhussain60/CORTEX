"""Autonomous Plan Executor for seamless plan continuation.

This orchestrator enables CORTEX to autonomously continue multi-phase plans
when user intent is clearly "continue implementation" - bypassing verbose
challenge/approval cycles.

Author: Asif Hussain
Version: 1.0
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import yaml


@dataclass
class PhaseStatus:
    """Phase execution status."""
    phase_id: str
    name: str
    status: str  # "planned" | "in-progress" | "completed"
    file_path: str
    priority: str
    started: Optional[str] = None
    completed: Optional[str] = None


@dataclass
class ContinuationContext:
    """Context for autonomous continuation."""
    last_completed_phase: Optional[str]
    next_phase: Optional[str]
    active_phases: List[PhaseStatus]
    registry_path: Path
    should_continue: bool
    continuation_reason: str


class AutonomousPlanExecutor:
    """Orchestrator for seamless multi-phase plan execution.
    
    Detects continuation intent and enables autonomous execution without
    verbose challenge/approval cycles. Integrates with _cortex-master registry.
    
    Usage:
        >>> executor = AutonomousPlanExecutor(registry_path)
        >>> context = executor.analyze_continuation_intent(user_request)
        >>> if context.should_continue:
        ...     executor.execute_next_phase(context)
    """
    
    # Intent patterns that signal continuation (not exploratory)
    CONTINUATION_PATTERNS = [
        "continue",
        "proceed",
        "next phase",
        "phase ",  # e.g., "phase 2", "phase 3"
        "implement phase",
        "autonomously",
        "bypass challenge",
        "immediately",
        "skip approval",
    ]
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize executor with registry path.
        
        Args:
            registry_path: Path to _cortex-master registry (defaults to standard location)
        """
        if registry_path is None:
            registry_path = Path(__file__).parents[3] / "cortex-registry" / "_cortex-master"
        
        self.registry_path = registry_path
        self.index_path = registry_path / "index.yaml"
    
    def load_registry(self) -> Dict[str, Any]:
        """Load registry index.yaml.
        
        Returns:
            Registry data dictionary
            
        Raises:
            FileNotFoundError: If registry index not found
        """
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Registry index not found: {self.index_path}\n"
                f"Expected at: cortex-registry/_cortex-master/index.yaml"
            )
        
        with open(self.index_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def detect_continuation_intent(self, user_request: str) -> bool:
        """Detect if user intent is to continue plan implementation.
        
        Args:
            user_request: User's request string
            
        Returns:
            True if continuation intent detected (skip challenge), False otherwise
        """
        request_lower = user_request.lower()
        
        # Check for continuation patterns
        for pattern in self.CONTINUATION_PATTERNS:
            if pattern in request_lower:
                return True
        
        return False
    
    def analyze_continuation_context(
        self,
        user_request: str,
        registry_data: Optional[Dict[str, Any]] = None
    ) -> ContinuationContext:
        """Analyze request and determine continuation context.
        
        Args:
            user_request: User's request string
            registry_data: Pre-loaded registry (optional, will load if None)
            
        Returns:
            ContinuationContext with next phase and continuation decision
        """
        if registry_data is None:
            registry_data = self.load_registry()
        
        # Extract phase statuses
        active_phases = []
        for phase_data in registry_data.get("active_phases", []):
            active_phases.append(PhaseStatus(
                phase_id=phase_data["id"],
                name=phase_data["name"],
                status=phase_data.get("status", "planned"),
                file_path=phase_data["file"],
                priority=phase_data.get("priority", "P2"),
                started=phase_data.get("started"),
                completed=phase_data.get("completed")
            ))
        
        # Find last completed phase
        completed_2026 = registry_data.get("completed_phases_2026", {}).get("phases", [])
        completed_2025 = registry_data.get("completed_phases_2025", {}).get("phases", [])
        
        last_completed = None
        if completed_2026:
            # Extract phase number from filename (e.g., "phase-20-xxx.yaml" -> "phase-20")
            last_file = completed_2026[-1]  # Most recent
            phase_id = last_file.split('.')[0]  # Remove .yaml
            last_completed = phase_id
        
        # Find next phase to execute
        next_phase = None
        in_progress_phases = [p for p in active_phases if p.status == "in-progress"]
        planned_phases = [p for p in active_phases if p.status == "planned"]
        
        if in_progress_phases:
            # Continue the in-progress phase
            next_phase = in_progress_phases[0].phase_id
        elif planned_phases:
            # Start the first planned phase
            next_phase = planned_phases[0].phase_id
        
        # Detect continuation intent
        should_continue = self.detect_continuation_intent(user_request)
        
        # Build continuation reason
        if should_continue and next_phase:
            reason = f"Continuation intent detected. Next phase: {next_phase}"
        elif not should_continue:
            reason = "No continuation intent detected (exploratory request)"
        else:
            reason = "No next phase available (all phases complete)"
        
        return ContinuationContext(
            last_completed_phase=last_completed,
            next_phase=next_phase,
            active_phases=active_phases,
            registry_path=self.registry_path,
            should_continue=should_continue and next_phase is not None,
            continuation_reason=reason
        )
    
    def get_phase_plan(self, phase_id: str) -> Dict[str, Any]:
        """Load full phase plan YAML.
        
        Args:
            phase_id: Phase identifier (e.g., "phase-21")
            
        Returns:
            Phase plan data
            
        Raises:
            FileNotFoundError: If phase file not found
        """
        # Try active phases first
        phase_file = self.registry_path / "phases" / "active" / f"{phase_id}.yaml"
        
        if not phase_file.exists():
            # Try completed phases
            for year in ["2026", "2025"]:
                phase_file = self.registry_path / "phases" / "completed" / year / f"{phase_id}.yaml"
                if phase_file.exists():
                    break
        
        if not phase_file.exists():
            raise FileNotFoundError(f"Phase file not found: {phase_id}")
        
        with open(phase_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def format_autonomous_header(self, context: ContinuationContext) -> str:
        """Generate minimal header for autonomous execution.
        
        Args:
            context: Continuation context
            
        Returns:
            Formatted header string
        """
        next_phase = context.next_phase or "unknown"
        
        return f"""## 🏗️ CORTEX Architect (Autonomous)
**Mode:** EXEC | **Phase:** {next_phase} | **Status:** 🔵 Executing

**Autonomous Continuation:** Challenge bypassed (continuation intent detected)

---
"""
    
    def should_bypass_challenge(self, user_request: str) -> Dict[str, Any]:
        """Determine if challenge should be bypassed.
        
        This is the main entry point for prompt integration.
        
        Args:
            user_request: User's request string
            
        Returns:
            Decision dictionary with keys:
                - bypass: bool (should bypass challenge?)
                - reason: str (why bypass/not bypass)
                - next_phase: Optional[str] (phase to execute)
                - context: ContinuationContext
        """
        context = self.analyze_continuation_context(user_request)
        
        return {
            "bypass": context.should_continue,
            "reason": context.continuation_reason,
            "next_phase": context.next_phase,
            "context": context
        }
    
    def generate_exec_template(self, context: ContinuationContext) -> str:
        """Generate execution template for autonomous continuation.
        
        Args:
            context: Continuation context
            
        Returns:
            Formatted execution template
        """
        if not context.next_phase:
            return "❌ No next phase available. All phases complete or no active phases."
        
        try:
            phase_plan = self.get_phase_plan(context.next_phase)
        except FileNotFoundError:
            return f"❌ Phase file not found: {context.next_phase}"
        
        # Extract phase details
        phase_id = phase_plan.get("phase_id", context.next_phase)
        title = phase_plan.get("title", "Unknown Phase")
        objectives = phase_plan.get("objectives", [])
        estimated_hours = phase_plan.get("estimated_hours", "Unknown")
        
        template = self.format_autonomous_header(context)
        template += f"""
## 🚀 {title} (Autonomous Execution)

**Phase:** {phase_id}  
**Estimated Effort:** {estimated_hours}h  
**Approach:** TDD-First (RED→GREEN→REFACTOR)

### Objectives
"""
        
        for i, obj in enumerate(objectives, 1):
            template += f"{i}. {obj}\n"
        
        template += """
### Execution Plan

**Status:** Executing autonomously (no approval required)

---
"""
        
        return template


# Convenience function for prompt integration
def check_autonomous_continuation(user_request: str) -> Dict[str, Any]:
    """Check if request should trigger autonomous continuation.
    
    This is the main function used by prompts/agents.
    
    Args:
        user_request: User's request string
        
    Returns:
        Decision dictionary (see should_bypass_challenge)
    """
    executor = AutonomousPlanExecutor()
    return executor.should_bypass_challenge(user_request)
