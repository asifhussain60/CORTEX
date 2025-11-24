"""
CORTEX Planning: Two-Way Sync Manager
Synchronizes active planning files with database tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import threading


class PlanningFileWatcher(FileSystemEventHandler):
    """
    Watches planning files for changes and triggers sync to database
    
    Monitors:
    - cortex-brain/documents/planning/features/active/*.md
    - cortex-brain/documents/planning/ado/active/*.md
    """
    
    def __init__(self, sync_manager):
        """
        Initialize file watcher
        
        Args:
            sync_manager: PlanSyncManager instance to handle sync operations
        """
        self.sync_manager = sync_manager
        self.last_modified = {}
        self.debounce_seconds = 1.0  # Prevent multiple rapid triggers
    
    def on_modified(self, event: FileModifiedEvent):
        """
        Handle file modification event
        
        Args:
            event: Watchdog file modification event
        """
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only process .md files in active planning directories
        if not self._is_active_planning_file(file_path):
            return
        
        # Debounce rapid modifications
        now = time.time()
        if file_path in self.last_modified:
            if now - self.last_modified[file_path] < self.debounce_seconds:
                return
        
        self.last_modified[file_path] = now
        
        # Trigger sync to database
        try:
            self.sync_manager.sync_file_to_database(file_path)
        except Exception as e:
            print(f"[PlanningFileWatcher] Error syncing {file_path}: {e}")
    
    def _is_active_planning_file(self, file_path: Path) -> bool:
        """
        Check if file is in active planning directory
        
        Args:
            file_path: File path to check
        
        Returns:
            True if in active planning directory
        """
        path_str = str(file_path).replace('\\', '/')
        
        active_dirs = [
            'cortex-brain/documents/planning/features/active',
            'cortex-brain/documents/planning/ado/active',
        ]
        
        return any(active_dir in path_str for active_dir in active_dirs) and file_path.suffix == '.md'


class PlanSyncManager:
    """
    Two-Way Sync Manager for Planning Files ↔ Database
    
    Features:
    - File change monitoring → auto-update database
    - Database query → locate and load files
    - Conflict resolution (file vs DB divergence)
    - Status propagation (approved, blocked, completed)
    """
    
    def __init__(self, db_path: Optional[str] = None, planning_root: Optional[Path] = None):
        """
        Initialize plan sync manager
        
        Args:
            db_path: Path to planning database (default: cortex-brain/tier2/planning-tracker.db)
            planning_root: Root directory for planning files (default: cortex-brain/documents/planning)
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            db_path = project_root / "cortex-brain" / "tier2" / "planning-tracker.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set planning root
        if planning_root is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            self.planning_root = project_root / "cortex-brain" / "documents" / "planning"
        else:
            self.planning_root = Path(planning_root)
        
        self._initialize_database()
        
        # File watcher (starts on demand)
        self.observer = None
        self.watcher = None
    
    def _initialize_database(self):
        """Create planning tracker database schema"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                plan_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                plan_type TEXT,
                file_path TEXT UNIQUE,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_sync DATETIME,
                metadata_json TEXT
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_type ON plans(plan_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_updated ON plans(updated_at)")
        
        conn.commit()
        conn.close()
    
    def start_file_watcher(self):
        """
        Start file system watcher for automatic sync
        
        Monitors planning directories and syncs changes to database
        """
        if self.observer is not None:
            print("[PlanSyncManager] File watcher already running")
            return
        
        planning_root = self.planning_root
        
        if not planning_root.exists():
            print(f"[PlanSyncManager] Planning directory not found: {planning_root}")
            return
        
        self.watcher = PlanningFileWatcher(self)
        self.observer = Observer()
        self.observer.schedule(self.watcher, str(planning_root), recursive=True)
        self.observer.start()
        
        print(f"[PlanSyncManager] File watcher started on {planning_root}")
    
    def stop_file_watcher(self):
        """Stop file system watcher"""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("[PlanSyncManager] File watcher stopped")
    
    def sync_file_to_database(self, file_path: Path) -> Dict[str, Any]:
        """
        Sync file changes to database
        
        Extracts metadata from file and updates database record
        
        Args:
            file_path: Path to planning file
        
        Returns:
            Sync result dict with status
        """
        if not file_path.exists():
            return {"success": False, "error": "File not found"}
        
        # Extract metadata from file
        metadata = self._extract_file_metadata(file_path)
        
        if not metadata:
            return {"success": False, "error": "Could not extract metadata"}
        
        # Update or insert database record
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Check if plan exists
            cursor.execute("SELECT plan_id FROM plans WHERE file_path = ?", (str(file_path),))
            existing = cursor.fetchone()
            
            now = datetime.now()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE plans 
                    SET title = ?,
                        status = ?,
                        updated_at = ?,
                        last_sync = ?,
                        metadata_json = ?
                    WHERE file_path = ?
                """, (
                    metadata['title'],
                    metadata['status'],
                    now,
                    now,
                    json.dumps(metadata),
                    str(file_path)
                ))
            else:
                # Insert new record
                plan_id = metadata.get('plan_id', f"plan_{int(now.timestamp())}")
                cursor.execute("""
                    INSERT INTO plans (plan_id, title, plan_type, file_path, status, created_at, updated_at, last_sync, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    plan_id,
                    metadata['title'],
                    metadata.get('plan_type', 'feature'),
                    str(file_path),
                    metadata['status'],
                    now,
                    now,
                    now,
                    json.dumps(metadata)
                ))
            
            conn.commit()
            return {
                "success": True,
                "plan_id": existing['plan_id'] if existing else plan_id,
                "action": "updated" if existing else "created"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def sync_database_to_file(self, plan_id: str) -> Dict[str, Any]:
        """
        Sync database status to file
        
        Updates file metadata section with database status
        
        Args:
            plan_id: Plan ID to sync
        
        Returns:
            Sync result dict
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get plan record
        cursor.execute("SELECT * FROM plans WHERE plan_id = ?", (plan_id,))
        plan = cursor.fetchone()
        conn.close()
        
        if not plan:
            return {"success": False, "error": "Plan not found in database"}
        
        file_path = Path(plan['file_path'])
        
        if not file_path.exists():
            return {"success": False, "error": "File not found", "file_path": str(file_path)}
        
        # Update file metadata section
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Update status in file
            updated_content = self._update_file_status(content, plan['status'])
            
            file_path.write_text(updated_content, encoding='utf-8')
            
            return {"success": True, "file_path": str(file_path)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def resolve_plan_by_name(self, plan_name: str) -> Optional[Dict[str, Any]]:
        """
        Find plan by name (searches both database and filesystem)
        
        Args:
            plan_name: Plan name or partial name
        
        Returns:
            Plan info dict or None if not found
        """
        # Search database first (fastest)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM plans 
            WHERE title LIKE ? OR plan_id LIKE ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (f"%{plan_name}%", f"%{plan_name}%"))
        
        plan = cursor.fetchone()
        conn.close()
        
        if plan:
            return {
                "plan_id": plan['plan_id'],
                "title": plan['title'],
                "file_path": plan['file_path'],
                "status": plan['status'],
                "plan_type": plan['plan_type'],
                "source": "database"
            }
        
        # Fallback: Search filesystem
        if not self.planning_root.exists():
            return None
        
        # Search active directories
        for active_dir in ['features/active', 'ado/active']:
            search_dir = self.planning_root / active_dir
            if not search_dir.exists():
                continue
            
            for file_path in search_dir.glob("*.md"):
                if plan_name.lower() in file_path.stem.lower():
                    # Extract metadata and return
                    metadata = self._extract_file_metadata(file_path)
                    if metadata:
                        return {
                            "plan_id": metadata.get('plan_id', file_path.stem),
                            "title": metadata['title'],
                            "file_path": str(file_path),
                            "status": metadata['status'],
                            "plan_type": metadata.get('plan_type', 'feature'),
                            "source": "filesystem"
                        }
        
        return None
    
    def validate_sync_integrity(self) -> Dict[str, Any]:
        """
        Validate sync integrity between database and files
        
        Checks for:
        - Orphaned DB records (file deleted)
        - Orphaned files (not in DB)
        - Status divergence (file vs DB status differs)
        
        Returns:
            Validation report dict
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all plans from database
        cursor.execute("SELECT plan_id, file_path, status FROM plans")
        db_plans = cursor.fetchall()
        conn.close()
        
        orphaned_db_records = []
        status_divergence = []
        
        # Check DB records
        for plan in db_plans:
            file_path = Path(plan['file_path'])
            
            if not file_path.exists():
                orphaned_db_records.append({
                    "plan_id": plan['plan_id'],
                    "file_path": plan['file_path']
                })
            else:
                # Check status divergence
                file_metadata = self._extract_file_metadata(file_path)
                if file_metadata and file_metadata['status'] != plan['status']:
                    status_divergence.append({
                        "plan_id": plan['plan_id'],
                        "db_status": plan['status'],
                        "file_status": file_metadata['status']
                    })
        
        # Check for orphaned files
        orphaned_files = []
        
        if self.planning_root.exists():
            db_paths = {plan['file_path'] for plan in db_plans}
            
            for active_dir in ['features/active', 'ado/active']:
                search_dir = self.planning_root / active_dir
                if not search_dir.exists():
                    continue
                
                for file_path in search_dir.glob("*.md"):
                    if str(file_path) not in db_paths:
                        orphaned_files.append(str(file_path))
        
        return {
            "orphaned_db_records": orphaned_db_records,
            "orphaned_files": orphaned_files,
            "status_divergence": status_divergence,
            "issues_found": len(orphaned_db_records) + len(orphaned_files) + len(status_divergence)
        }
    
    def _extract_file_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from planning file
        
        Args:
            file_path: Path to planning file
        
        Returns:
            Metadata dict or None if extraction fails
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract title (first heading)
            title = "Untitled Plan"
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # Extract status (from file location)
            # Normalize path separators for cross-platform compatibility
            file_path_normalized = str(file_path).replace('\\', '/')
            status = 'active'
            if '/approved/' in file_path_normalized:
                status = 'approved'
            elif '/completed/' in file_path_normalized:
                status = 'completed'
            elif '/blocked/' in file_path_normalized:
                status = 'blocked'
            
            # Extract plan type
            plan_type = 'feature'
            if '/ado/' in file_path_normalized:
                plan_type = 'ado'
            
            return {
                "title": title,
                "status": status,
                "plan_type": plan_type,
                "file_path": str(file_path)
            }
        
        except Exception as e:
            print(f"[PlanSyncManager] Error extracting metadata from {file_path}: {e}")
            return None
    
    def _update_file_status(self, content: str, new_status: str) -> str:
        """
        Update status in file content
        
        Args:
            content: File content
            new_status: New status to set
        
        Returns:
            Updated content
        """
        # Simple implementation: Add/update status marker at top
        lines = content.split('\n')
        
        # Check if status marker exists
        status_line_index = None
        for i, line in enumerate(lines):
            if line.startswith('**Status:**'):
                status_line_index = i
                break
        
        new_status_line = f"**Status:** {new_status.title()}"
        
        if status_line_index is not None:
            # Update existing
            lines[status_line_index] = new_status_line
        else:
            # Add after title
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    lines.insert(i + 1, new_status_line)
                    lines.insert(i + 2, "")
                    break
        
        return '\n'.join(lines)
