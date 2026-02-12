"""
Progress Tracking for Autonomous Execution (ENH-067)

Provides real-time progress tracking with:
- Stage status updates
- Dashboard integration (SQLite)
- Metrics collection
- Progress visualization

Author: Asif Hussain
AC_START: AC-WAVE-N-002
"""

import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from cortex.execution.autonomous_executor import (
    Plan,
    Stage,
    StageStatus,
)


@dataclass
class ProgressSnapshot:
    """Snapshot of execution progress at a point in time."""
    timestamp: float
    plan_id: str
    total_stages: int
    completed_stages: int
    failed_stages: int
    in_progress_stages: int
    token_usage: int
    
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_stages == 0:
            return 0.0
        return (self.completed_stages / self.total_stages) * 100


class ProgressTracker:
    """
    Tracks autonomous execution progress with dashboard integration.
    
    Features:
    - Real-time stage status updates
    - SQLite dashboard persistence
    - Progress metrics collection
    - Execution history tracking
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize progress tracker.
        
        Args:
            db_path: Optional path to SQLite database for dashboard integration
        """
        self.db_path = db_path
        self.current_plan: Optional[Plan] = None
        self.snapshots: List[ProgressSnapshot] = []
        self.stage_timings: Dict[str, Dict[str, float]] = {}
        
        if self.db_path:
            self._ensure_tables()
    
    def initialize_plan(self, plan: Plan) -> None:
        """
        Initialize tracking for a new plan.
        
        Args:
            plan: Plan to track
        """
        self.current_plan = plan
        self.snapshots = []
        self.stage_timings = {}
        
        # Create initial snapshot
        snapshot = self._create_snapshot(token_usage=0)
        self.snapshots.append(snapshot)
        
        # Persist to dashboard if available
        if self.db_path:
            self._persist_plan_start(plan)
    
    def update_stage(self, stage_id: str, status: StageStatus) -> None:
        """
        Update stage status.
        
        Args:
            stage_id: Stage identifier
            status: New status
        """
        if not self.current_plan:
            return
        
        # Find stage in plan
        stage = self._find_stage(stage_id)
        if not stage:
            return
        
        # Update stage status
        old_status = stage.status
        stage.status = status
        
        # Track timing
        if status == StageStatus.IN_PROGRESS:
            self.stage_timings[stage_id] = {"start": time.time()}
        elif status in [StageStatus.COMPLETED, StageStatus.FAILED, StageStatus.SKIPPED]:
            if stage_id in self.stage_timings:
                self.stage_timings[stage_id]["end"] = time.time()
        
        # Create snapshot
        token_usage = sum(
            s.estimated_tokens
            for s in self.current_plan.stages
            if s.status == StageStatus.COMPLETED
        )
        snapshot = self._create_snapshot(token_usage)
        self.snapshots.append(snapshot)
        
        # Persist to dashboard
        if self.db_path:
            self._persist_stage_update(stage_id, status)
    
    def get_current_snapshot(self) -> Optional[ProgressSnapshot]:
        """Get most recent progress snapshot."""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive progress summary.
        
        Returns:
            Dictionary with progress metrics
        """
        if not self.current_plan:
            return {}
        
        snapshot = self.get_current_snapshot()
        if not snapshot:
            return {}
        
        # Calculate stage timings
        avg_stage_duration = 0.0
        completed_timings = [
            t["end"] - t["start"]
            for t in self.stage_timings.values()
            if "end" in t
        ]
        if completed_timings:
            avg_stage_duration = sum(completed_timings) / len(completed_timings)
        
        # Estimate remaining time
        remaining_stages = snapshot.total_stages - snapshot.completed_stages
        estimated_remaining_time = remaining_stages * avg_stage_duration
        
        return {
            "plan_id": snapshot.plan_id,
            "completion_percentage": snapshot.completion_percentage(),
            "completed_stages": snapshot.completed_stages,
            "failed_stages": snapshot.failed_stages,
            "total_stages": snapshot.total_stages,
            "token_usage": snapshot.token_usage,
            "avg_stage_duration_seconds": avg_stage_duration,
            "estimated_remaining_seconds": estimated_remaining_time,
            "snapshots_count": len(self.snapshots),
        }
    
    def _find_stage(self, stage_id: str) -> Optional[Stage]:
        """Find stage by ID in current plan."""
        if not self.current_plan:
            return None
        
        for stage in self.current_plan.stages:
            if stage.id == stage_id:
                return stage
        
        return None
    
    def _create_snapshot(self, token_usage: int) -> ProgressSnapshot:
        """Create progress snapshot from current plan state."""
        if not self.current_plan:
            return ProgressSnapshot(
                timestamp=time.time(),
                plan_id="",
                total_stages=0,
                completed_stages=0,
                failed_stages=0,
                in_progress_stages=0,
                token_usage=0,
            )
        
        completed = sum(1 for s in self.current_plan.stages if s.status == StageStatus.COMPLETED)
        failed = sum(1 for s in self.current_plan.stages if s.status == StageStatus.FAILED)
        in_progress = sum(1 for s in self.current_plan.stages if s.status == StageStatus.IN_PROGRESS)
        
        return ProgressSnapshot(
            timestamp=time.time(),
            plan_id=self.current_plan.id,
            total_stages=len(self.current_plan.stages),
            completed_stages=completed,
            failed_stages=failed,
            in_progress_stages=in_progress,
            token_usage=token_usage,
        )
    
    def _ensure_tables(self) -> None:
        """Ensure dashboard database tables exist."""
        if not self.db_path:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_plans (
                plan_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                total_stages INTEGER,
                start_time REAL,
                status TEXT
            )
        """)
        
        # Stages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_stages (
                stage_id TEXT PRIMARY KEY,
                plan_id TEXT,
                name TEXT NOT NULL,
                status TEXT,
                start_time REAL,
                end_time REAL,
                FOREIGN KEY (plan_id) REFERENCES execution_plans (plan_id)
            )
        """)
        
        # Progress snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT,
                timestamp REAL,
                completed_stages INTEGER,
                failed_stages INTEGER,
                token_usage INTEGER,
                FOREIGN KEY (plan_id) REFERENCES execution_plans (plan_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _persist_plan_start(self, plan: Plan) -> None:
        """Persist plan start to dashboard."""
        if not self.db_path:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO execution_plans
            (plan_id, name, description, total_stages, start_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            plan.id,
            plan.name,
            plan.description,
            len(plan.stages),
            time.time(),
            "running"
        ))
        
        # Insert stages
        for stage in plan.stages:
            cursor.execute("""
                INSERT OR REPLACE INTO execution_stages
                (stage_id, plan_id, name, status, start_time, end_time)
                VALUES (?, ?, ?, ?, NULL, NULL)
            """, (
                stage.id,
                plan.id,
                stage.name,
                stage.status.value
            ))
        
        conn.commit()
        conn.close()
    
    def _persist_stage_update(self, stage_id: str, status: StageStatus) -> None:
        """Persist stage status update to dashboard."""
        if not self.db_path:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update stage
        cursor.execute("""
            UPDATE execution_stages
            SET status = ?
            WHERE stage_id = ?
        """, (status.value, stage_id))
        
        # Insert snapshot
        snapshot = self.get_current_snapshot()
        if snapshot:
            cursor.execute("""
                INSERT INTO progress_snapshots
                (plan_id, timestamp, completed_stages, failed_stages, token_usage)
                VALUES (?, ?, ?, ?, ?)
            """, (
                snapshot.plan_id,
                snapshot.timestamp,
                snapshot.completed_stages,
                snapshot.failed_stages,
                snapshot.token_usage
            ))
        
        conn.commit()
        conn.close()


# AC_COMPLETE: AC-WAVE-N-002 ✅ Progress tracker implementation
