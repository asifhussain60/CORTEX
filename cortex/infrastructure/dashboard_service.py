"""
Dashboard Service for Real-Time Progress Monitoring

Provides real-time progress aggregation and display functionality.

AC-NFR-004-02: Dashboard shows real-time progress
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DashboardStatus(Enum):
    """Dashboard operational status."""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class ProgressSnapshot:
    """Snapshot of progress at a point in time."""
    total_items: int
    completed_items: int
    in_progress_items: int
    failed_items: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        processed = self.completed_items + self.failed_items
        if processed == 0:
            return 0.0
        return (self.completed_items / processed) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "in_progress_items": self.in_progress_items,
            "failed_items": self.failed_items,
            "completion_percentage": self.completion_percentage,
            "success_rate": self.success_rate,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ProgressMetrics:
    """Aggregated progress metrics."""
    snapshots: List[ProgressSnapshot] = field(default_factory=list)
    current_status: DashboardStatus = DashboardStatus.STOPPED
    estimated_completion_time: Optional[datetime] = None

    def add_snapshot(self, snapshot: ProgressSnapshot):
        """Add progress snapshot."""
        self.snapshots.append(snapshot)

    def get_latest_snapshot(self) -> Optional[ProgressSnapshot]:
        """Get most recent snapshot."""
        return self.snapshots[-1] if self.snapshots else None

    def get_average_completion_percentage(self) -> float:
        """Get average completion across all snapshots."""
        if not self.snapshots:
            return 0.0
        total = sum(s.completion_percentage for s in self.snapshots)
        return total / len(self.snapshots)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        latest = self.get_latest_snapshot()
        return {
            "current_status": self.current_status.value,
            "snapshot_count": len(self.snapshots),
            "latest_snapshot": latest.to_dict() if latest else None,
            "average_completion": self.get_average_completion_percentage(),
            "estimated_completion": self.estimated_completion_time.isoformat() if self.estimated_completion_time else None
        }


class ProgressAggregator:
    """Aggregates progress from multiple sources."""

    def __init__(self):
        self.progress_by_stage: Dict[str, ProgressSnapshot] = {}
        self.history: List[ProgressSnapshot] = []
        self.lock = None  # For thread-safe operations if needed

    def update_stage_progress(
        self,
        stage_name: str,
        total: int,
        completed: int,
        in_progress: int,
        failed: int
    ) -> ProgressSnapshot:
        """Update progress for a specific stage."""
        snapshot = ProgressSnapshot(
            total_items=total,
            completed_items=completed,
            in_progress_items=in_progress,
            failed_items=failed
        )
        self.progress_by_stage[stage_name] = snapshot
        self.history.append(snapshot)
        logger.debug(f"Updated stage '{stage_name}': {completed}/{total} complete")
        return snapshot

    def get_aggregate_progress(self) -> ProgressSnapshot:
        """Get aggregated progress across all stages."""
        if not self.progress_by_stage:
            return ProgressSnapshot(0, 0, 0, 0)

        total = sum(s.total_items for s in self.progress_by_stage.values())
        completed = sum(s.completed_items for s in self.progress_by_stage.values())
        in_progress = sum(s.in_progress_items for s in self.progress_by_stage.values())
        failed = sum(s.failed_items for s in self.progress_by_stage.values())

        return ProgressSnapshot(
            total_items=total,
            completed_items=completed,
            in_progress_items=in_progress,
            failed_items=failed
        )

    def get_stage_progress(self, stage_name: str) -> Optional[ProgressSnapshot]:
        """Get progress for a specific stage."""
        return self.progress_by_stage.get(stage_name)

    def get_all_stages(self) -> Dict[str, ProgressSnapshot]:
        """Get progress for all stages."""
        return self.progress_by_stage.copy()

    def clear_history(self):
        """Clear progress history."""
        self.history.clear()

    def get_history(self, limit: Optional[int] = None) -> List[ProgressSnapshot]:
        """Get progress history."""
        if limit:
            return self.history[-limit:]
        return self.history.copy()


class DashboardService:
    """
    Real-time dashboard for progress monitoring.
    Aggregates progress from multiple components.
    """

    def __init__(self, aggregator: Optional[ProgressAggregator] = None):
        self.aggregator = aggregator or ProgressAggregator()
        self.metrics = ProgressMetrics()
        self.status = DashboardStatus.STOPPED

    def start(self):
        """Start the dashboard."""
        self.status = DashboardStatus.RUNNING
        self.metrics.current_status = DashboardStatus.RUNNING
        logger.info("Dashboard started")

    def pause(self):
        """Pause the dashboard."""
        self.status = DashboardStatus.PAUSED
        self.metrics.current_status = DashboardStatus.PAUSED
        logger.info("Dashboard paused")

    def stop(self):
        """Stop the dashboard."""
        self.status = DashboardStatus.STOPPED
        self.metrics.current_status = DashboardStatus.STOPPED
        logger.info("Dashboard stopped")

    def update_progress(
        self,
        stage_name: str,
        total: int,
        completed: int,
        in_progress: int,
        failed: int
    ):
        """Update progress for a stage."""
        if self.status == DashboardStatus.STOPPED:
            logger.warning("Cannot update progress: dashboard is stopped")
            return

        snapshot = self.aggregator.update_stage_progress(
            stage_name, total, completed, in_progress, failed
        )
        self.metrics.add_snapshot(snapshot)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        aggregate = self.aggregator.get_aggregate_progress()
        return {
            "status": self.status.value,
            "aggregate_progress": aggregate.to_dict(),
            "stages": {
                name: snap.to_dict()
                for name, snap in self.aggregator.get_all_stages().items()
            },
            "metrics": self.metrics.to_dict()
        }

    def set_estimated_completion(self, completion_time: datetime):
        """Set estimated completion time."""
        self.metrics.estimated_completion_time = completion_time
        logger.info(f"Set estimated completion: {completion_time}")

    def get_summary(self) -> str:
        """Get human-readable dashboard summary."""
        aggregate = self.aggregator.get_aggregate_progress()
        return (
            f"Dashboard ({self.status.value}): "
            f"{aggregate.completed_items}/{aggregate.total_items} complete "
            f"({aggregate.completion_percentage:.1f}%), "
            f"{aggregate.failed_items} failed, "
            f"{aggregate.in_progress_items} in progress"
        )
