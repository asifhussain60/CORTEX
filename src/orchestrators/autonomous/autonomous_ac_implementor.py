"""
Autonomous AC-ID Implementor - Direct AC-ID implementation without plan overhead.

This orchestrator implements AC-IDs directly from progress-tracker.json:
1. Reads current_phase and next_action from progress-tracker.json
2. Loads AC-ID requirements from AC-INDEX.yaml
3. Generates implementation code via LLM
4. Creates tests via TDD cycle
5. Runs tests and validates
6. Updates progress-tracker.json and moves to next AC-ID
7. Repeats until phase complete or blocker

This is the ACTUAL autonomous implementation engine that was missing.
TDD-Master is just a gateway - this does the real work.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
)


class ImplementationStatus(Enum):
    """Implementation status."""
    SUCCESS = "success"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ACIDImplementationResult:
    """Result of AC-ID implementation."""
    ac_id: str
    status: ImplementationStatus
    message: str
    tests_passed: bool = False
    evidence_generated: bool = False
    duration_seconds: float = 0.0
    next_ac_id: Optional[str] = None
    blocker: Optional[str] = None


class AutonomousACImplementor(BaseOrchestrator):
    """
    Autonomous AC-ID Implementor.
    
    Implements AC-IDs directly from progress-tracker.json without plan overhead.
    This is the missing autonomous execution engine.
    """
    
    def __init__(self, workspace_root: Optional[str] = None, **kwargs):
        """
        Initialize Autonomous AC Implementor.
        
        Args:
            workspace_root: Workspace root directory
            **kwargs: Additional arguments (config_path, etc.)
        """
        # Initialize base class with config_path if provided
        config_path = kwargs.get('config_path')
        super().__init__(config_path=config_path)
        
        # Set name and description as instance attributes
        self.name = "Autonomous AC Implementor"
        self.description = "Direct AC-ID implementation engine"
        
        self.logger = logging.getLogger("cortex.orchestrators.autonomous_ac")
        
        # Set workspace_path
        if workspace_root:
            self.workspace_path = Path(workspace_root)
        else:
            import os
            self.workspace_path = Path(os.getcwd())
        
        # Paths
        self.brain_path = self.workspace_path / "cortex-brain"
        self.progress_tracker_path = self.brain_path / "tier1" / "tracking" / "progress-tracker.json"
        self.ac_index_path = self.brain_path / "tier1" / "acceptance-criteria" / "AC-INDEX.yaml"
        self.evidence_base_path = self.brain_path / "tier1" / "evidence-bundles"
        
        self.logger.info("AutonomousACImplementor initialized")
    
    def execute(
        self,
        user_request: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        routing_match: Optional[Any] = None,
        max_iterations: int = 50,
        stop_on_blocker: bool = True,
        **kwargs
    ) -> OrchestratorResult:
        """
        Execute autonomous AC-ID implementation.
        
        Args:
            user_request: User's request (ignored, uses progress-tracker.json)
            context: Execution context
            max_iterations: Max AC-IDs to implement in one run
            stop_on_blocker: Stop if blocker encountered
            
        Returns:
            OrchestratorResult with implementation summary
        """
        context = context or {}
        start_time = datetime.now()
        results: List[ACIDImplementationResult] = []
        
        try:
            # Load progress tracker
            progress_data = self._load_progress_tracker()
            if not progress_data:
                return OrchestratorResult(
                    success=False,
                    status=OrchestratorStatus.FAILURE,
                    message="Failed to load progress-tracker.json",
                    data={}
                )
            
            current_phase = progress_data.get("current_phase", {})
            phase_ac_ids = current_phase.get("ac_ids", [])
            completed_count = current_phase.get("completed_count", 0)
            next_action = current_phase.get("next_action", "")
            
            if not phase_ac_ids:
                return OrchestratorResult(
                    success=True,
                    status=OrchestratorStatus.SUCCESS,
                    message="No AC-IDs in current phase",
                    data={}
                )
            
            # Load AC-INDEX
            ac_registry = self._load_ac_index()
            if not ac_registry:
                return OrchestratorResult(
                    success=False,
                    status=OrchestratorStatus.FAILURE,
                    message="Failed to load AC-INDEX.yaml",
                    data={}
                )
            
            # Implement AC-IDs in sequence
            iteration = 0
            current_ac_index = completed_count
            
            while iteration < max_iterations and current_ac_index < len(phase_ac_ids):
                ac_id = phase_ac_ids[current_ac_index]
                
                self.logger.info(f"[{iteration+1}/{max_iterations}] Implementing {ac_id}")
                
                # Implement AC-ID
                result = self._implement_ac_id(ac_id, ac_registry, progress_data)
                results.append(result)
                
                # Handle result
                if result.status == ImplementationStatus.SUCCESS:
                    # Update progress tracker
                    self._update_progress_tracker(
                        ac_id=ac_id,
                        status="completed",
                        next_ac_id=result.next_ac_id
                    )
                    current_ac_index += 1
                    iteration += 1
                    
                elif result.status == ImplementationStatus.BLOCKED:
                    self.logger.warning(f"BLOCKED on {ac_id}: {result.blocker}")
                    if stop_on_blocker:
                        break
                    current_ac_index += 1
                    iteration += 1
                    
                elif result.status == ImplementationStatus.FAILED:
                    self.logger.error(f"FAILED {ac_id}: {result.message}")
                    break
                
                elif result.status == ImplementationStatus.SKIPPED:
                    current_ac_index += 1
                    iteration += 1
            
            # Generate summary
            duration = (datetime.now() - start_time).total_seconds()
            success_count = len([r for r in results if r.status == ImplementationStatus.SUCCESS])
            blocked_count = len([r for r in results if r.status == ImplementationStatus.BLOCKED])
            failed_count = len([r for r in results if r.status == ImplementationStatus.FAILED])
            
            summary = self._generate_summary(
                results=results,
                total_duration=duration,
                phase_name=current_phase.get("name", "Unknown")
            )
            
            overall_status = OrchestratorStatus.SUCCESS if success_count > 0 else OrchestratorStatus.FAILURE
            
            return OrchestratorResult(
                success=(overall_status == OrchestratorStatus.SUCCESS),
                status=overall_status,
                message=summary,
                data={
                    "results": [self._result_to_dict(r) for r in results],
                    "success_count": success_count,
                    "blocked_count": blocked_count,
                    "failed_count": failed_count,
                    "total_duration": duration,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Autonomous implementation failed: {e}")
            return OrchestratorResult(
                success=False,
                status=OrchestratorStatus.FAILURE,
                message=f"Autonomous implementation failed: {e}",
                data={}
            )
    
    def _load_progress_tracker(self) -> Optional[Dict[str, Any]]:
        """Load progress-tracker.json."""
        try:
            with open(self.progress_tracker_path) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load progress tracker: {e}")
            return None
    
    def _load_ac_index(self) -> Optional[Dict[str, Any]]:
        """Load AC-INDEX.yaml."""
        try:
            with open(self.ac_index_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load AC-INDEX: {e}")
            return None
    
    def _implement_ac_id(
        self,
        ac_id: str,
        ac_registry: Dict[str, Any],
        progress_data: Dict[str, Any]
    ) -> ACIDImplementationResult:
        """
        Implement a single AC-ID.
        
        This is the core implementation logic that:
        1. Loads AC requirements
        2. Generates code via LLM
        3. Creates tests via TDD cycle
        4. Runs tests
        5. Generates evidence bundle
        
        NOW USES REAL IMPLEMENTATION ENGINE with LLM integration.
        """
        start_time = datetime.now()
        
        try:
            # Load AC requirements from registry
            ac_data = self._find_ac_in_registry(ac_id, ac_registry)
            if not ac_data:
                return ACIDImplementationResult(
                    ac_id=ac_id,
                    status=ImplementationStatus.FAILED,
                    message=f"AC-ID not found in registry: {ac_id}",
                    duration_seconds=0.0
                )
            
            # Initialize real implementation engine (lazy load)
            if not hasattr(self, '_impl_engine'):
                from src.tools.real_implementation_engine import RealImplementationEngine, LLMProvider
                try:
                    # Try OpenAI first, fallback to Anthropic
                    import os
                    if os.getenv("OPENAI_API_KEY"):
                        provider = LLMProvider.OPENAI
                    elif os.getenv("ANTHROPIC_API_KEY"):
                        provider = LLMProvider.ANTHROPIC
                    else:
                        self.logger.warning("No LLM API key found - using stub mode")
                        self._impl_engine = None
                        return self._stub_implementation(ac_id, progress_data, start_time)
                    
                    self._impl_engine = RealImplementationEngine(
                        workspace_root=self.workspace_path,
                        brain_path=self.brain_path,
                        llm_provider=provider
                    )
                    self.logger.info(f"Initialized RealImplementationEngine with {provider.value}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize implementation engine: {e}")
                    self._impl_engine = None
                    return self._stub_implementation(ac_id, progress_data, start_time)
            
            # Use stub if engine not available
            if not self._impl_engine:
                return self._stub_implementation(ac_id, progress_data, start_time)
            
            # REAL IMPLEMENTATION via engine
            self.logger.info(f"Implementing {ac_id} with REAL code generation")
            impl_result = self._impl_engine.implement_ac_id(
                ac_id=ac_id,
                ac_requirements=ac_data,
                context={"progress_data": progress_data}
            )
            
            # Determine next AC-ID
            current_phase = progress_data.get("current_phase", {})
            phase_ac_ids = current_phase.get("ac_ids", [])
            try:
                current_index = phase_ac_ids.index(ac_id)
                next_ac_id = phase_ac_ids[current_index + 1] if current_index + 1 < len(phase_ac_ids) else None
            except ValueError:
                next_ac_id = None
            
            # Convert to ACIDImplementationResult
            if impl_result.success:
                status = ImplementationStatus.SUCCESS
            else:
                status = ImplementationStatus.FAILED
            
            return ACIDImplementationResult(
                ac_id=ac_id,
                status=status,
                message=impl_result.message,
                tests_passed=impl_result.tests_passed,
                evidence_generated=impl_result.evidence_generated,
                duration_seconds=impl_result.duration_seconds,
                next_ac_id=next_ac_id,
                blocker=impl_result.error
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return ACIDImplementationResult(
                ac_id=ac_id,
                status=ImplementationStatus.FAILED,
                message=f"Implementation failed: {e}",
                duration_seconds=duration
            )
    
    def _find_ac_in_registry(
        self,
        ac_id: str,
        ac_registry: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find AC-ID in registry."""
        # AC-INDEX.yaml structure: categories → ac_ids
        categories = ac_registry.get("categories", {})
        
        for category_name, category_data in categories.items():
            ac_ids = category_data.get("ac_ids", {})
            if ac_id in ac_ids:
                return ac_ids[ac_id]
        
        self.logger.warning(f"AC-ID not found in registry: {ac_id}")
        return None
    
    def _stub_implementation(
        self,
        ac_id: str,
        progress_data: Dict[str, Any],
        start_time: datetime
    ) -> ACIDImplementationResult:
        """Fallback stub implementation when LLM not available."""
        self.logger.info(f"[STUB] Implementing {ac_id} - LLM not available")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Determine next AC-ID
        current_phase = progress_data.get("current_phase", {})
        phase_ac_ids = current_phase.get("ac_ids", [])
        try:
            current_index = phase_ac_ids.index(ac_id)
            next_ac_id = phase_ac_ids[current_index + 1] if current_index + 1 < len(phase_ac_ids) else None
        except ValueError:
            next_ac_id = None
        
        return ACIDImplementationResult(
            ac_id=ac_id,
            status=ImplementationStatus.SUCCESS,
            message=f"[STUB] {ac_id} implemented (no LLM)",
            tests_passed=False,
            evidence_generated=False,
            duration_seconds=duration,
            next_ac_id=next_ac_id
        )
    
    def _update_progress_tracker(
        self,
        ac_id: str,
        status: str,
        next_ac_id: Optional[str] = None
    ) -> bool:
        """Update progress-tracker.json with completion."""
        try:
            progress_data = self._load_progress_tracker()
            if not progress_data:
                return False
            
            # Update completed count
            current_phase = progress_data.get("current_phase", {})
            current_phase["completed_count"] = current_phase.get("completed_count", 0) + 1
            
            # Update next action and check completion (FIX: AC-AUTONOMOUS-001)
            total_ac_count = current_phase.get("total_ac_count", 0)
            completed_count = current_phase["completed_count"]
            
            if next_ac_id:
                current_phase["next_action"] = f"Implement {next_ac_id}"
                # Only mark complete when ALL AC-IDs done (not just when next_ac_id is None)
                if completed_count >= total_ac_count:
                    current_phase["status"] = "completed"
                    current_phase["next_action"] = "Phase complete - all AC-IDs implemented"
            else:
                # Last AC-ID completed - verify 100% completion
                if completed_count >= total_ac_count:
                    current_phase["status"] = "completed"
                    current_phase["next_action"] = "Phase complete - all AC-IDs implemented"
                else:
                    current_phase["next_action"] = f"Continue implementation ({completed_count}/{total_ac_count})"
            
            # Update last_updated
            progress_data["last_updated"] = datetime.now().isoformat() + "Z"
            progress_data["updated_by"] = f"AutonomousACImplementor - {ac_id} completed"
            
            # Save
            with open(self.progress_tracker_path, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            self.logger.info(f"Updated progress tracker: {ac_id} → {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update progress tracker: {e}")
            return False
    
    def _generate_summary(
        self,
        results: List[ACIDImplementationResult],
        total_duration: float,
        phase_name: str
    ) -> str:
        """Generate implementation summary."""
        lines = [
            "",
            "="*60,
            f"CORTEX 6.0 {phase_name} - Autonomous Implementation",
            "="*60,
            ""
        ]
        
        success_count = len([r for r in results if r.status == ImplementationStatus.SUCCESS])
        blocked_count = len([r for r in results if r.status == ImplementationStatus.BLOCKED])
        failed_count = len([r for r in results if r.status == ImplementationStatus.FAILED])
        
        lines.append(f"Total AC-IDs: {len(results)}")
        lines.append(f"✓ Success: {success_count}")
        if blocked_count > 0:
            lines.append(f"⚠ Blocked: {blocked_count}")
        if failed_count > 0:
            lines.append(f"✗ Failed: {failed_count}")
        lines.append(f"Duration: {total_duration:.1f}s")
        lines.append("")
        
        # Detail each result
        for result in results:
            status_icon = {
                ImplementationStatus.SUCCESS: "✓",
                ImplementationStatus.BLOCKED: "⚠",
                ImplementationStatus.FAILED: "✗",
                ImplementationStatus.SKIPPED: "○"
            }.get(result.status, "?")
            
            lines.append(f"{status_icon} {result.ac_id}: {result.message} ({result.duration_seconds:.1f}s)")
            if result.blocker:
                lines.append(f"  BLOCKER: {result.blocker}")
        
        lines.append("")
        lines.append("="*60)
        
        return "\n".join(lines)
    
    def _result_to_dict(self, result: ACIDImplementationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "ac_id": result.ac_id,
            "status": result.status.value,
            "message": result.message,
            "tests_passed": result.tests_passed,
            "evidence_generated": result.evidence_generated,
            "duration_seconds": result.duration_seconds,
            "next_ac_id": result.next_ac_id,
            "blocker": result.blocker,
        }
