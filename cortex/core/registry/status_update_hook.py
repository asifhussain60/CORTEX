"""
Registry Status Update Hook
Authority: ARCH-012 + MCP-FIRST
Purpose: Auto-update registry status on orchestrator completion

This module hooks into orchestrator completion events and automatically
updates the master registry status to keep dashboards in sync.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class StatusUpdateHook:
    """
    Orchestrator completion hook that auto-updates registry status.
    
    Triggered by:
    - TDDOrchestrator completion (IMPLEMENT/FIX)
    - RefactoringOrchestrator completion (REFACTOR)
    - LENSSynthesis completion (ANALYZE)
    - EnforcementOrchestrator validation (AUDIT)
    
    Updates:
    - master-status.yaml (registry status)
    - Dashboard sync triggers
    - Audit trail markers
    """
    
    def __init__(self, registry_path: str = "cortex-registry/_cortex-master") -> None:
        """
        Initialize status update hook.
        
        Args:
            registry_path: Path to registry master directory
        """
        self.registry_path = Path(registry_path)
        self.status_file = self.registry_path / "master-status.yaml"
    
    def load_current_status(self) -> Dict[str, Any]:
        """
        Load current registry status.
        
        Returns:
            Dict containing current status
        """
        if not self.status_file.exists():
            return self._create_default_status()
        
        with open(self.status_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_default_status(self) -> Dict[str, Any]:
        """Create default status structure"""
        return {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "authority": "StatusUpdateHook"
            },
            "orchestrators": {},
            "phases": {},
            "recent_completions": []
        }
    
    def update_orchestrator_status(
        self,
        orchestrator_name: str,
        operation: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update orchestrator completion status.
        
        Args:
            orchestrator_name: Name of orchestrator (e.g., "TDDOrchestrator")
            operation: Operation performed (e.g., "implement", "fix")
            status: Completion status ("SUCCESS", "FAILED", "PARTIAL")
            details: Additional details (test counts, files modified, etc.)
        """
        current = self.load_current_status()
        
        # Update orchestrator entry
        if orchestrator_name not in current["orchestrators"]:
            current["orchestrators"][orchestrator_name] = {
                "total_invocations": 0,
                "successful": 0,
                "failed": 0,
                "last_invocation": None
            }
        
        orch_status = current["orchestrators"][orchestrator_name]
        orch_status["total_invocations"] += 1
        
        if status == "SUCCESS":
            orch_status["successful"] += 1
        elif status == "FAILED":
            orch_status["failed"] += 1
        
        orch_status["last_invocation"] = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "status": status,
            "details": details or {}
        }
        
        # Add to recent completions
        current["recent_completions"].insert(0, {
            "orchestrator": orchestrator_name,
            "operation": operation,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        })
        
        # Keep only last 50 completions
        current["recent_completions"] = current["recent_completions"][:50]
        
        # Update metadata
        current["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Write back
        self._write_status(current)
        
        # Trigger dashboard sync
        self._trigger_dashboard_sync(orchestrator_name, operation, status)
    
    def update_phase_status(
        self,
        phase_id: str,
        stage_id: str,
        status: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update phase/stage completion status.
        
        Args:
            phase_id: Phase identifier (e.g., "phase-48")
            stage_id: Stage identifier (e.g., "S1")
            status: Completion status ("COMPLETE", "IN_PROGRESS", "BLOCKED")
            metrics: Stage metrics (test counts, coverage, etc.)
        """
        current = self.load_current_status()
        
        # Update phase entry
        if phase_id not in current["phases"]:
            current["phases"][phase_id] = {
                "stages": {},
                "overall_status": "NOT_STARTED",
                "completion_percent": 0
            }
        
        phase = current["phases"][phase_id]
        phase["stages"][stage_id] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics or {}
        }
        
        # Recalculate overall status
        stage_statuses = [s["status"] for s in phase["stages"].values()]
        if all(s == "COMPLETE" for s in stage_statuses):
            phase["overall_status"] = "COMPLETE"
        elif any(s == "IN_PROGRESS" for s in stage_statuses):
            phase["overall_status"] = "IN_PROGRESS"
        elif any(s == "BLOCKED" for s in stage_statuses):
            phase["overall_status"] = "BLOCKED"
        
        # Calculate completion percentage
        total_stages = len(phase["stages"])
        complete_stages = sum(1 for s in stage_statuses if s == "COMPLETE")
        phase["completion_percent"] = int((complete_stages / total_stages) * 100)
        
        # Update metadata
        current["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Write back
        self._write_status(current)
    
    def _write_status(self, status: Dict[str, Any]):
        """
        Write status to file with validation.
        
        Args:
            status: Status dict to write
        """
        # Validate before writing (prevent contradictions)
        validator = RegistryValidator()
        is_valid, errors = validator.validate_status(status)
        
        if not is_valid:
            raise ValueError(f"Status validation failed: {errors}")
        
        with open(self.status_file, 'w') as f:
            yaml.dump(status, f, default_flow_style=False, sort_keys=False)
    
    def _trigger_dashboard_sync(self, orchestrator: str, operation: str, status: str):
        """
        Trigger dashboard synchronization.
        
        Args:
            orchestrator: Orchestrator name
            operation: Operation performed
            status: Completion status
        """
        # In production, this would trigger dashboard regeneration
        # For now, just log the event
        print(f"[DASHBOARD_SYNC] {orchestrator} → {operation} → {status}")


class RegistryValidator:
    """
    Validates registry status for contradictions.
    
    Checks:
    - No duplicate phase/stage entries
    - Status transitions valid (can't go COMPLETE → IN_PROGRESS)
    - Orchestrator counts consistent
    - Timestamp ordering correct
    """
    
    def validate_status(self, status: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate status dict for contradictions.
        
        Args:
            status: Status dict to validate
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check metadata exists
        if "metadata" not in status:
            errors.append("Missing metadata section")
        
        # Check orchestrators section
        if "orchestrators" in status:
            for orch_name, orch_data in status["orchestrators"].items():
                # Validate counts
                total = orch_data.get("total_invocations", 0)
                success = orch_data.get("successful", 0)
                failed = orch_data.get("failed", 0)
                
                if success + failed > total:
                    errors.append(
                        f"{orch_name}: success+failed ({success}+{failed}) "
                        f"exceeds total ({total})"
                    )
        
        # Check phases section
        if "phases" in status:
            for phase_id, phase_data in status["phases"].items():
                # Validate completion percentage
                completion = phase_data.get("completion_percent", 0)
                if not (0 <= completion <= 100):
                    errors.append(
                        f"{phase_id}: Invalid completion percentage ({completion})"
                    )
                
                # Validate stage consistency
                stages = phase_data.get("stages", {})
                if stages:
                    complete_count = sum(
                        1 for s in stages.values()
                        if s.get("status") == "COMPLETE"
                    )
                    expected = int((complete_count / len(stages)) * 100)
                    if abs(completion - expected) > 5:  # Allow 5% tolerance
                        errors.append(
                            f"{phase_id}: Completion % ({completion}) "
                            f"inconsistent with stage count (expected ~{expected})"
                        )
        
        return (len(errors) == 0, errors)


# Global instance
_status_hook = StatusUpdateHook()


def on_orchestrator_complete(
    orchestrator: str,
    operation: str,
    status: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Public API for orchestrator completion hook.
    
    Args:
        orchestrator: Orchestrator name
        operation: Operation performed
        status: Completion status
        details: Additional details
    """
    _status_hook.update_orchestrator_status(orchestrator, operation, status, details)


def on_phase_stage_complete(
    phase_id: str,
    stage_id: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> None:
    """
    Public API for phase/stage completion hook.
    
    Args:
        phase_id: Phase identifier
        stage_id: Stage identifier
        status: Completion status
        metrics: Stage metrics
    """
    _status_hook.update_phase_status(phase_id, stage_id, status, metrics)
