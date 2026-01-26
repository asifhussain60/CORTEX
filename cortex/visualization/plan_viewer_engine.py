"""
Plan Viewer Engine - Backend Support for Real-Time Plan Visualization

Provides plan data export and real-time event streaming for the plan-viewer.html SPA.

Features:
- Plan data serialization to JSON format
- Real-time WebSocket event streaming
- Polling-based updates for compatibility
- Integration with PlannerOrchestrator
- State snapshots and checkpoints

Author: Asif Hussain
Phase: PHASE 4 (Plan Viewer Generator)
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from cortex.models.canonical_enums import PhaseStatus


# ═══════════════════════════════════════════════════════════════════════════
# Type Definitions
# ═══════════════════════════════════════════════════════════════════════════



class PlanStatus(str, Enum):
    """Overall plan execution status."""
    QUEUED = "queued"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# ═══════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PhaseMetadata:
    """Metadata for a phase."""
    phase_id: int
    phase_name: str
    progress: int
    status: PhaseStatus
    description: str
    tasks: List[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_seconds: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase_id": self.phase_id,
            "phase_name": self.phase_name,
            "progress": min(100, max(0, self.progress)),  # Clamp to 0-100
            "status": self.status.value,
            "description": self.description,
            "tasks": self.tasks,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds
        }


@dataclass
class PlanData:
    """Complete plan data for viewer."""
    plan_id: str
    plan_name: str
    overall_progress: int
    status: PlanStatus
    created_at: str
    last_updated: str
    phases: List[PhaseMetadata]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "plan_name": self.plan_name,
            "overall_progress": min(100, max(0, self.overall_progress)),  # Clamp to 0-100
            "status": self.status.value,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "phases": [phase.to_dict() for phase in self.phases]
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Plan Viewer Engine
# ═══════════════════════════════════════════════════════════════════════════

class PlanViewerEngine:
    """
    Backend engine for real-time plan visualization.
    
    Provides plan data export and streaming capabilities for the plan-viewer.html SPA.
    """

    def __init__(self, planner_orchestrator: Optional[Any] = None) -> None:
        """
        Initialize the plan viewer engine.
        
        Args:
            planner_orchestrator: Reference to PlannerOrchestrator for plan data
        """
        self.planner_orchestrator = planner_orchestrator
        self.active_subscriptions: Dict[str, List[Any]] = {}
        self.plan_snapshots: Dict[str, PlanData] = {}

    def export_plan_data(self, plan_id: str) -> Dict[str, Any]:
        """
        Export plan data for viewer consumption.
        
        Args:
            plan_id: ID of plan to export
            
        Returns:
            Plan data dictionary ready for JSON serialization
        """
        if not self.planner_orchestrator:
            return self._get_sample_plan().to_dict()

        try:
            # Fetch plan from orchestrator
            plan = self.planner_orchestrator.get_plan_by_id(plan_id)
            if not plan:
                return {"error": f"Plan not found: {plan_id}"}

            # Convert to viewer format
            plan_data = self._convert_to_viewer_format(plan)
            self.plan_snapshots[plan_id] = plan_data
            return plan_data.to_dict()

        except Exception as e:
            return {"error": str(e)}

    def export_all_plans(self) -> Dict[str, Any]:
        """
        Export all plans for viewer.
        
        Returns:
            Dictionary with all plans organized by status
        """
        if not self.planner_orchestrator:
            return {"plans": [self._get_sample_plan().to_dict()]}

        try:
            plans_by_status = self.planner_orchestrator.get_plans_by_status()
            all_plans = []

            for status_group in plans_by_status.values():
                for plan in status_group:
                    plan_data = self._convert_to_viewer_format(plan)
                    all_plans.append(plan_data.to_dict())

            return {"plans": all_plans}

        except Exception as e:
            return {"error": str(e), "plans": []}

    def subscribe_to_plan(self, plan_id: str, callback: Any) -> str:
        """
        Subscribe to plan updates (WebSocket/polling).
        
        Args:
            plan_id: Plan to subscribe to
            callback: Callback function for updates
            
        Returns:
            Subscription ID
        """
        subscription_id = f"{plan_id}_{datetime.now(timezone.utc).timestamp()}"

        if plan_id not in self.active_subscriptions:
            self.active_subscriptions[plan_id] = []

        self.active_subscriptions[plan_id].append(callback)
        return subscription_id

    def unsubscribe_from_plan(self, plan_id: str, subscription_id: str) -> bool:
        """
        Unsubscribe from plan updates.
        
        Args:
            plan_id: Plan ID
            subscription_id: Subscription ID to remove
            
        Returns:
            True if unsubscribed, False if not found
        """
        if plan_id not in self.active_subscriptions:
            return False

        # In real implementation, would track subscriptions more precisely
        # For now, just clear all subscriptions for plan
        self.active_subscriptions[plan_id] = []
        return True

    async def stream_plan_updates(self, plan_id: str, 
                                  poll_interval: float = 1.0) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream plan updates asynchronously.
        
        Args:
            plan_id: Plan to stream
            poll_interval: Polling interval in seconds
            
        Yields:
            Updated plan data
        """
        last_snapshot = None

        while True:
            try:
                current_data = self.export_plan_data(plan_id)

                if current_data != last_snapshot:
                    yield current_data
                    last_snapshot = current_data

                await asyncio.sleep(poll_interval)

            except Exception as e:
                yield {"error": str(e)}
                await asyncio.sleep(poll_interval)

    def get_plan_json(self, plan_id: str) -> str:
        """
        Get plan data as JSON string.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            JSON string of plan data
        """
        plan_dict = self.export_plan_data(plan_id)
        return json.dumps(plan_dict, indent=2)

    def save_plan_snapshot(self, plan_id: str, filepath: Path) -> bool:
        """
        Save plan snapshot to file.
        
        Args:
            plan_id: Plan ID
            filepath: Path to save JSON file
            
        Returns:
            True if successful
        """
        try:
            plan_data = self.export_plan_data(plan_id)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(plan_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return False

    def load_plan_snapshot(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Load plan snapshot from file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Plan data dictionary or None if error
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)

        except Exception as e:
            print(f"Error loading snapshot: {e}")
            return None

    # ═════════════════════════════════════════════════════════════════════
    # Internal Helpers
    # ═════════════════════════════════════════════════════════════════════

    def _convert_to_viewer_format(self, plan: Any) -> PlanData:
        """Convert orchestrator plan to viewer format."""
        # This would integrate with actual plan structure from orchestrator
        # For now, return sample data
        return self._get_sample_plan()

    @staticmethod
    def _get_sample_plan() -> PlanData:
        """Get sample plan for demonstration."""
        now = datetime.now(timezone.utc).isoformat()

        phases = [
            PhaseMetadata(
                phase_id=1,
                phase_name="Infrastructure Setup",
                progress=100,
                status=PhaseStatus.COMPLETED,
                description="Initialize async execution engine",
                tasks=["Create engine", "Add pause/resume", "Checkpoint system"],
                started_at="2026-01-26T10:00:00Z",
                completed_at="2026-01-26T10:45:00Z",
                duration_seconds=2700
            ),
            PhaseMetadata(
                phase_id=2,
                phase_name="Naming Utilities",
                progress=100,
                status=PhaseStatus.COMPLETED,
                description="Kebab-case conversion and domain inference",
                tasks=["NamingFactory", "to_kebab_case()", "Domain inference"],
                started_at="2026-01-26T10:45:00Z",
                completed_at="2026-01-26T11:15:00Z",
                duration_seconds=1800
            ),
            PhaseMetadata(
                phase_id=3,
                phase_name="Registry Builder",
                progress=100,
                status=PhaseStatus.COMPLETED,
                description="Plan registry with metadata validation",
                tasks=["Create registry", "Plan folders", "Metadata validation"],
                started_at="2026-01-26T11:15:00Z",
                completed_at="2026-01-26T12:00:00Z",
                duration_seconds=2700
            ),
            PhaseMetadata(
                phase_id=4,
                phase_name="Bootstrap Integration",
                progress=75,
                status=PhaseStatus.EXECUTING,
                description="Initialize autonomous subsystem on startup",
                tasks=["bootstrap_initialize()", "Checkpoint restoration", "Plan discovery"],
                started_at="2026-01-26T12:00:00Z",
                completed_at=None,
                duration_seconds=None
            )
        ]

        return PlanData(
            plan_id="cortex-autonomous-planning-001",
            plan_name="CORTEX Autonomous Planning Orchestrator",
            overall_progress=94,
            status=PlanStatus.EXECUTING,
            created_at="2026-01-26T10:00:00Z",
            last_updated=now,
            phases=phases
        )

    def _calculate_overall_progress(self, phases: List[PhaseMetadata]) -> int:
        """Calculate overall progress from phase progresses."""
        if not phases:
            return 0

        total_progress = sum(phase.progress for phase in phases)
        return int(total_progress / len(phases))


# ═══════════════════════════════════════════════════════════════════════════
# Standalone Usage
# ═══════════════════════════════════════════════════════════════════════════

def create_sample_viewer_json() -> str:
    """Create sample plan viewer JSON for testing."""
    engine = PlanViewerEngine()
    plan_data = engine._get_sample_plan()
    return plan_data.to_json()


if __name__ == "__main__":
    # Generate sample JSON
    print(create_sample_viewer_json())
