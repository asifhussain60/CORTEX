"""
Page Tracking & Context Retention - Phase 2 Milestone 2.3

Tracks TDD session state, enables resume capability,
and maintains context across multiple features.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2
"""

import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from workflows.tdd_state_machine import TDDStateMachine, TDDState


@dataclass
class PageLocation:
    """Exact location in code where work stopped."""
    filepath: str
    line_number: int
    column_offset: int
    function_name: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class TDDContext:
    """Complete TDD session context."""
    session_id: str
    feature_name: str
    current_state: str  # TDDState value
    last_location: Optional[PageLocation] = None
    test_files: List[str] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)
    notes: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "session_id": self.session_id,
            "feature_name": self.feature_name,
            "current_state": self.current_state,
            "last_location": asdict(self.last_location) if self.last_location else None,
            "test_files": self.test_files,
            "source_files": self.source_files,
            "notes": self.notes,
            "last_updated": self.last_updated.isoformat(),
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TDDContext':
        """Create instance from dictionary."""
        last_location = None
        if data.get("last_location"):
            last_location = PageLocation(**data["last_location"])
        
        return cls(
            session_id=data["session_id"],
            feature_name=data["feature_name"],
            current_state=data["current_state"],
            last_location=last_location,
            test_files=data.get("test_files", []),
            source_files=data.get("source_files", []),
            notes=data.get("notes", ""),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )


class PageTracker:
    """
    Tracks page locations and TDD session context.
    
    Enables pause/resume of TDD workflows with complete
    context restoration including file locations, test state,
    and work-in-progress notes.
    """
    
    def __init__(self, storage_path: str = "cortex-brain/tier1/tdd_sessions.db"):
        """
        Initialize page tracker with persistent storage.
        
        Args:
            storage_path: Path to SQLite database for session storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tdd_sessions (
                    session_id TEXT PRIMARY KEY,
                    feature_name TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    last_location_json TEXT,
                    test_files_json TEXT,
                    source_files_json TEXT,
                    notes TEXT,
                    last_updated TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # State machine snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS state_machine_snapshots (
                    session_id TEXT PRIMARY KEY,
                    snapshot_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES tdd_sessions(session_id)
                )
            """)
            
            conn.commit()
    
    def save_context(self, context: TDDContext, state_machine: Optional[TDDStateMachine] = None) -> bool:
        """
        Save TDD session context to persistent storage.
        
        Args:
            context: TDD context to save
            state_machine: Optional state machine to snapshot
            
        Returns:
            True if saved successfully
        """
        conn = None
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Serialize complex fields
            last_location_json = json.dumps(asdict(context.last_location)) if context.last_location else None
            test_files_json = json.dumps(context.test_files)
            source_files_json = json.dumps(context.source_files)
            
            # Upsert session
            cursor.execute("""
                INSERT OR REPLACE INTO tdd_sessions
                (session_id, feature_name, current_state, last_location_json,
                 test_files_json, source_files_json, notes, last_updated, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(
                    (SELECT created_at FROM tdd_sessions WHERE session_id = ?),
                    ?
                ))
            """, (
                context.session_id,
                context.feature_name,
                context.current_state,
                last_location_json,
                test_files_json,
                source_files_json,
                context.notes,
                context.last_updated.isoformat(),
                context.session_id,
                datetime.now().isoformat()
            ))
            
            # Save state machine snapshot if provided
            if state_machine:
                snapshot_json = json.dumps(state_machine.session.to_dict())
                cursor.execute("""
                    INSERT OR REPLACE INTO state_machine_snapshots
                    (session_id, snapshot_json, created_at)
                    VALUES (?, ?, ?)
                """, (
                    context.session_id,
                    snapshot_json,
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving context: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def load_context(self, session_id: str) -> Optional[TDDContext]:
        """
        Load TDD session context from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            TDDContext if found, None otherwise
        """
        conn = None
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, feature_name, current_state, last_location_json,
                       test_files_json, source_files_json, notes, last_updated
                FROM tdd_sessions
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Deserialize complex fields
            last_location = None
            if row[3]:
                last_location_data = json.loads(row[3])
                last_location = PageLocation(**last_location_data)
            
            test_files = json.loads(row[4]) if row[4] else []
            source_files = json.loads(row[5]) if row[5] else []
            
            return TDDContext(
                session_id=row[0],
                feature_name=row[1],
                current_state=row[2],
                last_location=last_location,
                test_files=test_files,
                source_files=source_files,
                notes=row[6],
                last_updated=datetime.fromisoformat(row[7]),
            )
            
        except Exception as e:
            print(f"Error loading context: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def load_state_machine(self, session_id: str) -> Optional[TDDStateMachine]:
        """
        Load TDD state machine snapshot from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            TDDStateMachine if found, None otherwise
        """
        conn = None
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT snapshot_json
                FROM state_machine_snapshots
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Deserialize state machine
            # Note: TDDStateMachine.load_session expects a file path
            # For now, we'll reconstruct manually
            # TODO: Enhance TDDStateMachine to support dict loading
            
            return None  # Placeholder for now
            
        except Exception as e:
            print(f"Error loading state machine: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def list_active_sessions(self) -> List[TDDContext]:
        """
        List all active TDD sessions.
        
        Returns:
            List of active session contexts
        """
        conn = None
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, feature_name, current_state, last_location_json,
                       test_files_json, source_files_json, notes, last_updated
                FROM tdd_sessions
                WHERE current_state NOT IN ('done', 'error')
                ORDER BY last_updated DESC
            """)
            
            contexts = []
            for row in cursor.fetchall():
                last_location = None
                if row[3]:
                    last_location_data = json.loads(row[3])
                    last_location = PageLocation(**last_location_data)
                
                test_files = json.loads(row[4]) if row[4] else []
                source_files = json.loads(row[5]) if row[5] else []
                
                contexts.append(TDDContext(
                    session_id=row[0],
                    feature_name=row[1],
                    current_state=row[2],
                    last_location=last_location,
                    test_files=test_files,
                    source_files=source_files,
                    notes=row[6],
                    last_updated=datetime.fromisoformat(row[7]),
                ))
            
            return contexts
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete TDD session from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted successfully
        """
        conn = None
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Delete state machine snapshot
            cursor.execute("DELETE FROM state_machine_snapshots WHERE session_id = ?", (session_id,))
            
            # Delete session
            cursor.execute("DELETE FROM tdd_sessions WHERE session_id = ?", (session_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def update_page_location(self, session_id: str, location: PageLocation) -> bool:
        """
        Update current page location for session.
        
        Args:
            session_id: Session identifier
            location: New page location
            
        Returns:
            True if updated successfully
        """
        context = self.load_context(session_id)
        if not context:
            return False
        
        context.last_location = location
        context.last_updated = datetime.now()
        
        return self.save_context(context)
    
    def add_note(self, session_id: str, note: str) -> bool:
        """
        Add note to session context.
        
        Args:
            session_id: Session identifier
            note: Note to add
            
        Returns:
            True if added successfully
        """
        context = self.load_context(session_id)
        if not context:
            return False
        
        context.notes = f"{context.notes}\n{note}".strip()
        context.last_updated = datetime.now()
        
        return self.save_context(context)
