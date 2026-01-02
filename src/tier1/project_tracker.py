"""
Project Tracker - Manages active planning project state for cross-session continuations.

Part of CORTEX v5 Option B: Planning Orchestrator Integration with Tier 1.
Enables project-level continuation when user says "continue" without active orchestrator.

Architecture:
    Planning Orchestrator → ProjectTracker.update_project_state()
                         → Writes to tier1_active_projects table
    
    User: "continue" → Middleware detects no orchestrator session
                    → ProjectTracker.get_active_project()
                    → Returns project context (<200 tokens)
                    → Routes to Planning Orchestrator

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ActiveProject:
    """Represents an active planning project."""
    project_id: str
    plan_name: str
    plan_path: str
    current_phase: Optional[str] = None
    current_task: Optional[str] = None
    last_completed: Optional[str] = None
    status: str = 'active'
    progress_percentage: int = 0
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    completed_at: Optional[str] = None
    next_action: Optional[str] = None
    artifacts_path: Optional[List[str]] = None
    orchestrator_used: Optional[str] = None


class ProjectTracker:
    """
    Manages active planning project state in Tier 1.
    
    Used by Planning Orchestrator to persist project state and by
    CrossSessionContextMiddleware to enable project-level continuations.
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize project tracker.
        
        Args:
            db_path: Path to Tier 1 SQLite database
        """
        self.db_path = Path(db_path)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure tier1_active_projects table exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Schema already created in cortex-brain/schema.sql
        # This just ensures it exists if running standalone
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tier1_active_projects (
                project_id TEXT PRIMARY KEY,
                plan_name TEXT NOT NULL,
                plan_path TEXT NOT NULL,
                current_phase TEXT,
                current_task TEXT,
                last_completed TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                progress_percentage INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                last_updated TEXT NOT NULL DEFAULT (datetime('now')),
                completed_at TEXT,
                next_action TEXT,
                artifacts_path TEXT,
                orchestrator_used TEXT,
                
                CHECK (status IN ('active', 'paused', 'complete')),
                CHECK (progress_percentage >= 0 AND progress_percentage <= 100)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_active_projects_status 
            ON tier1_active_projects(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_active_projects_updated 
            ON tier1_active_projects(last_updated DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def create_or_update_project(
        self,
        project_id: str,
        plan_name: str,
        plan_path: str,
        current_phase: Optional[str] = None,
        current_task: Optional[str] = None,
        last_completed: Optional[str] = None,
        status: str = 'active',
        progress_percentage: int = 0,
        next_action: Optional[str] = None,
        artifacts_path: Optional[List[str]] = None,
        orchestrator_used: str = 'planning_v5'
    ) -> bool:
        """
        Create new project or update existing project state.
        
        Called by Planning Orchestrator after:
        - Plan creation
        - Phase completion
        - Task completion
        
        Args:
            project_id: Unique project identifier (e.g., "cortex-v5-holistic-refactor")
            plan_name: Human-readable plan name
            plan_path: Path to planning folder
            current_phase: Current phase (e.g., "Phase 5")
            current_task: Current task (e.g., "Task 5.1")
            last_completed: Last completed phase/task
            status: Project status (active/paused/complete)
            progress_percentage: Overall progress (0-100)
            next_action: Next recommended action
            artifacts_path: List of key artifact paths
            orchestrator_used: Orchestrator that updated this project
        
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO tier1_active_projects (
                    project_id, plan_name, plan_path,
                    current_phase, current_task, last_completed,
                    status, progress_percentage,
                    created_at, last_updated,
                    next_action, artifacts_path, orchestrator_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    plan_name = excluded.plan_name,
                    current_phase = excluded.current_phase,
                    current_task = excluded.current_task,
                    last_completed = excluded.last_completed,
                    status = excluded.status,
                    progress_percentage = excluded.progress_percentage,
                    last_updated = excluded.last_updated,
                    next_action = excluded.next_action,
                    artifacts_path = excluded.artifacts_path,
                    orchestrator_used = excluded.orchestrator_used
            """, (
                project_id, plan_name, plan_path,
                current_phase, current_task, last_completed,
                status, progress_percentage,
                now, now,
                next_action,
                json.dumps(artifacts_path or []),
                orchestrator_used
            ))
            
            conn.commit()
            success = True
        except Exception as e:
            conn.rollback()
            success = False
            raise RuntimeError(f"Failed to create/update project: {e}")
        finally:
            conn.close()
        
        return success
    
    def get_active_project(self) -> Optional[ActiveProject]:
        """
        Get the most recently updated active project.
        
        Used by CrossSessionContextMiddleware for project-level continuations.
        
        Returns:
            ActiveProject object if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tier1_active_projects
            WHERE status = 'active'
            ORDER BY last_updated DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return ActiveProject(
            project_id=row['project_id'],
            plan_name=row['plan_name'],
            plan_path=row['plan_path'],
            current_phase=row['current_phase'],
            current_task=row['current_task'],
            last_completed=row['last_completed'],
            status=row['status'],
            progress_percentage=row['progress_percentage'],
            created_at=row['created_at'],
            last_updated=row['last_updated'],
            completed_at=row['completed_at'],
            next_action=row['next_action'],
            artifacts_path=json.loads(row['artifacts_path'] or '[]'),
            orchestrator_used=row['orchestrator_used']
        )
    
    def get_project_by_id(self, project_id: str) -> Optional[ActiveProject]:
        """
        Get specific project by ID.
        
        Args:
            project_id: Project identifier
        
        Returns:
            ActiveProject object if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tier1_active_projects
            WHERE project_id = ?
        """, (project_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return ActiveProject(
            project_id=row['project_id'],
            plan_name=row['plan_name'],
            plan_path=row['plan_path'],
            current_phase=row['current_phase'],
            current_task=row['current_task'],
            last_completed=row['last_completed'],
            status=row['status'],
            progress_percentage=row['progress_percentage'],
            created_at=row['created_at'],
            last_updated=row['last_updated'],
            completed_at=row['completed_at'],
            next_action=row['next_action'],
            artifacts_path=json.loads(row['artifacts_path'] or '[]'),
            orchestrator_used=row['orchestrator_used']
        )
    
    def mark_project_complete(self, project_id: str) -> bool:
        """
        Mark project as complete.
        
        Args:
            project_id: Project identifier
        
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE tier1_active_projects
            SET status = 'complete',
                completed_at = ?,
                last_updated = ?,
                progress_percentage = 100
            WHERE project_id = ?
        """, (now, now, project_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def pause_project(self, project_id: str) -> bool:
        """
        Pause project (temporarily inactive).
        
        Args:
            project_id: Project identifier
        
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE tier1_active_projects
            SET status = 'paused',
                last_updated = ?
            WHERE project_id = ?
        """, (now, project_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def resume_project(self, project_id: str) -> bool:
        """
        Resume paused project.
        
        Args:
            project_id: Project identifier
        
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE tier1_active_projects
            SET status = 'active',
                last_updated = ?
            WHERE project_id = ?
        """, (now, project_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_all_active_projects(self) -> List[ActiveProject]:
        """
        Get all active projects ordered by last updated.
        
        Returns:
            List of ActiveProject objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tier1_active_projects
            WHERE status = 'active'
            ORDER BY last_updated DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            ActiveProject(
                project_id=row['project_id'],
                plan_name=row['plan_name'],
                plan_path=row['plan_path'],
                current_phase=row['current_phase'],
                current_task=row['current_task'],
                last_completed=row['last_completed'],
                status=row['status'],
                progress_percentage=row['progress_percentage'],
                created_at=row['created_at'],
                last_updated=row['last_updated'],
                completed_at=row['completed_at'],
                next_action=row['next_action'],
                artifacts_path=json.loads(row['artifacts_path'] or '[]'),
                orchestrator_used=row['orchestrator_used']
            )
            for row in rows
        ]
    
    def get_lightweight_project_context(self) -> Optional[Dict[str, Any]]:
        """
        Get lightweight project context for middleware injection (<200 tokens).
        
        Used by CrossSessionContextMiddleware.enrich_context() when no
        orchestrator session found but active project exists.
        
        Returns:
            Lightweight dict with essential project info, or None if no active project
        
        Example:
            {
                "project_id": "cortex-v5-holistic-refactor",
                "plan_name": "CORTEX v5 Holistic Refactor",
                "current_phase": "Phase 5",
                "current_task": "Task 5.1",
                "last_completed": "Phase 5.1a",
                "progress": 40,
                "next_action": "/CORTEX Plan ADO Orchestrator v2 Migration",
                "orchestrator": "planning_v5"
            }
        """
        project = self.get_active_project()
        
        if not project:
            return None
        
        return {
            "project_id": project.project_id,
            "plan_name": project.plan_name,
            "current_phase": project.current_phase,
            "current_task": project.current_task,
            "last_completed": project.last_completed,
            "progress": project.progress_percentage,
            "next_action": project.next_action,
            "orchestrator": project.orchestrator_used or "planning_v5"
        }
