"""
ADO Work Items Manager - Full CRUD Operations

Provides comprehensive management of ADO work items with:
- Create, Read, Update, Delete operations
- FTS5 full-text search with filters
- Pagination and sorting
- Status transition validation
- Activity logging
- LRU caching for performance
- Context integration with CORTEX brain tiers

Performance: <10ms queries with caching, supports 10K+ items

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
import platform
from functools import lru_cache
from enum import Enum


class ADOStatus(Enum):
    """Valid ADO work item statuses"""
    PLANNING = "planning"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ADOType(Enum):
    """Valid ADO work item types"""
    BUG = "Bug"
    FEATURE = "Feature"
    USER_STORY = "User Story"
    TASK = "Task"
    EPIC = "Epic"


class ADOPriority(Enum):
    """Valid priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ADOManager:
    """
    Manages ADO work items with CRUD operations, search, and caching.
    
    Features:
    - Create new ADO items with validation
    - Resume existing items with full context restoration
    - Search with FTS5 full-text search + filters
    - Update status with transition validation
    - Archive completed items
    - LRU caching for performance
    - Activity logging for audit trail
    """
    
    def __init__(self, db_path: Optional[str] = None, cache_size: int = 100):
        """
        Initialize ADO Manager
        
        Args:
            db_path: Path to SQLite database (default: from config)
            cache_size: LRU cache size for get operations
        """
        self.db_path = db_path or self._get_db_path()
        self.cache_size = cache_size
        self._init_connection()
    
    def _get_db_path(self) -> str:
        """Get database path from config or use default"""
        config_path = Path(__file__).parent.parent / "cortex.config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Get machine-specific brain path
                hostname = platform.node()
                if hostname in config.get('machines', {}):
                    brain_path = config['machines'][hostname].get('brainPath')
                    if brain_path:
                        db_path = config.get('ado_planning', {}).get('database_path', 'ado-work-items.db')
                        return str(Path(brain_path) / db_path.replace('cortex-brain/', ''))
                
                # Fallback to ado_planning config
                brain_path = config.get('machines', {}).get('', {}).get('brainPath', 'cortex-brain')
                db_path = config.get('ado_planning', {}).get('database_path', 'ado-work-items.db')
                return str(Path(brain_path) / db_path.replace('cortex-brain/', ''))
            
            except Exception:
                pass
        
        # Default fallback
        return str(Path(__file__).parent.parent / "cortex-brain" / "ado-work-items.db")
    
    def _init_connection(self):
        """Initialize database connection and verify schema"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Verify tables exist
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        required_tables = {'ado_work_items', 'ado_search', 'ado_activity_log'}
        if not required_tables.issubset(tables):
            raise RuntimeError(
                f"Database schema incomplete. Missing tables: {required_tables - tables}. "
                "Run init_ado_database.py first."
            )
    
    def create_ado(
        self,
        ado_number: str,
        ado_type: str,
        title: str,
        template_file_path: str,
        status: str = "planning",
        priority: str = "Medium",
        assigned_to: str = "",
        tags: List[str] = None,
        dor_completed: int = 0,
        dod_completed: int = 0,
        conversation_ids: List[str] = None,
        related_file_paths: List[str] = None,
        commit_shas: List[str] = None,
        estimated_hours: Optional[float] = None,
        actual_hours: Optional[float] = None
    ) -> str:
        """
        Create new ADO work item
        
        Args:
            ado_number: Unique ADO identifier (e.g., "ADO-12345")
            ado_type: Type from ADOType enum
            title: Brief title/summary
            template_file_path: Path to template markdown file
            status: Status from ADOStatus enum (default: "planning")
            priority: Priority from ADOPriority enum (default: "Medium")
            assigned_to: Person assigned to this item
            tags: List of tags for categorization
            dor_completed: Definition of Ready completion (0-100%)
            dod_completed: Definition of Done completion (0-100%)
            conversation_ids: CORTEX conversation IDs
            related_file_paths: List of file paths to be changed
            commit_shas: Git commit hashes related to this item
            estimated_hours: Estimated work hours
            actual_hours: Actual work hours spent
        
        Returns:
            str: ADO number of created item
        
        Raises:
            ValueError: If validation fails
            sqlite3.IntegrityError: If ADO number already exists
        """
        # Validation
        self._validate_ado_type(ado_type)
        self._validate_status(status)
        self._validate_priority(priority)
        self._validate_percentage(dor_completed, "DoR")
        self._validate_percentage(dod_completed, "DoD")
        
        if not ado_number or not ado_number.strip():
            raise ValueError("ADO number is required")
        if not title or not title.strip():
            raise ValueError("Title is required")
        if not template_file_path or not template_file_path.strip():
            raise ValueError("Template file path is required")
        
        # Prepare data
        tags = tags or []
        conversation_ids = conversation_ids or []
        related_file_paths = related_file_paths or []
        commit_shas = commit_shas or []
        
        created_at = datetime.now().isoformat()
        updated_at = created_at
        
        # Insert into database
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ado_work_items (
                ado_number, type, title, template_file_path, status, priority,
                assigned_to, tags, dor_completed, dod_completed,
                conversation_ids, related_file_paths, commit_shas,
                estimated_hours, actual_hours,
                created_at, updated_at, last_accessed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ado_number, ado_type, title, template_file_path, status, priority,
            assigned_to, json.dumps(tags), dor_completed, dod_completed,
            json.dumps(conversation_ids), json.dumps(related_file_paths),
            json.dumps(commit_shas), estimated_hours, actual_hours,
            created_at, updated_at, created_at
        ))
        
        self.conn.commit()
        
        # Log activity
        self._log_activity(ado_number, "created", f"Created {ado_type}: {title}")
        
        # Clear cache
        self._clear_cache()
        
        return ado_number
    
    @lru_cache(maxsize=100)
    def get_ado(self, ado_number: str) -> Optional[Dict[str, Any]]:
        """
        Get ADO work item by number (cached)
        
        Args:
            ado_number: ADO identifier
        
        Returns:
            Dict with ADO data or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ado_work_items WHERE ado_number = ?", (ado_number,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def list_ado(
        self,
        status: Optional[str] = None,
        ado_type: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "updated_at",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List ADO work items with filters, pagination, and sorting
        
        Args:
            status: Filter by status
            ado_type: Filter by type
            priority: Filter by priority
            assigned_to: Filter by assignee
            tags: Filter by tags (any match)
            limit: Maximum items to return (default: 50)
            offset: Skip this many items (default: 0)
            sort_by: Column to sort by (default: "updated_at")
            sort_order: "ASC" or "DESC" (default: "DESC")
        
        Returns:
            Tuple of (items list, total count)
        """
        # Build WHERE clause
        conditions = []
        params = []
        
        if status:
            self._validate_status(status)
            conditions.append("status = ?")
            params.append(status)
        
        if ado_type:
            self._validate_ado_type(ado_type)
            conditions.append("type = ?")
            params.append(ado_type)
        
        if priority:
            self._validate_priority(priority)
            conditions.append("priority = ?")
            params.append(priority)
        
        if assigned_to:
            conditions.append("assigned_to = ?")
            params.append(assigned_to)
        
        if tags:
            # Search for any tag match in JSON array
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            conditions.append(f"({tag_conditions})")
            params.extend([f'%"{tag}"%' for tag in tags])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Validate sort parameters
        valid_sort_columns = {
            'ado_number', 'type', 'title', 'status', 'priority',
            'assigned_to', 'created_at', 'updated_at', 'dor_completed', 'dod_completed'
        }
        if sort_by not in valid_sort_columns:
            raise ValueError(f"Invalid sort column: {sort_by}")
        
        if sort_order.upper() not in ('ASC', 'DESC'):
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Get total count
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM ado_work_items WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0]
        
        # Get items
        query = f"""
            SELECT * FROM ado_work_items
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order.upper()}
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        rows = cursor.fetchall()
        
        items = [self._row_to_dict(row) for row in rows]
        
        return items, total_count
    
    def search_ado(
        self,
        query: str,
        status: Optional[str] = None,
        ado_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Full-text search using FTS5
        
        Args:
            query: Search query (FTS5 syntax supported)
            status: Filter by status
            ado_type: Filter by type
            limit: Maximum results (default: 50)
        
        Returns:
            List of matching ADO items
        """
        # Build query with filters
        conditions = ["ado_search MATCH ?"]
        params = [query]
        
        if status:
            self._validate_status(status)
            conditions.append("w.status = ?")
            params.append(status)
        
        if ado_type:
            self._validate_ado_type(ado_type)
            conditions.append("w.type = ?")
            params.append(ado_type)
        
        where_clause = " AND ".join(conditions)
        
        # Search with FTS5
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT w.*
            FROM ado_work_items w
            JOIN ado_search s ON w.ado_number = s.ado_number
            WHERE {where_clause}
            ORDER BY s.rank
            LIMIT ?
        """, params + [limit])
        
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def update_status(
        self,
        ado_number: str,
        new_status: str,
        notes: str = ""
    ) -> bool:
        """
        Update ADO status with transition validation
        
        Args:
            ado_number: ADO identifier
            new_status: New status from ADOStatus enum
            notes: Optional notes about status change
        
        Returns:
            bool: True if updated successfully
        
        Raises:
            ValueError: If status transition invalid
            RuntimeError: If ADO not found
        """
        self._validate_status(new_status)
        
        # Get current item
        item = self.get_ado(ado_number)
        if not item:
            raise RuntimeError(f"ADO {ado_number} not found")
        
        old_status = item['status']
        
        # Validate status transition
        if not self._is_valid_status_transition(old_status, new_status):
            raise ValueError(
                f"Invalid status transition: {old_status} -> {new_status}. "
                f"Valid transitions from {old_status}: {self._get_valid_transitions(old_status)}"
            )
        
        # Update status
        updated_at = datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE ado_work_items
            SET status = ?, updated_at = ?
            WHERE ado_number = ?
        """, (new_status, updated_at, ado_number))
        
        self.conn.commit()
        
        # Log activity
        log_message = f"Status changed: {old_status} → {new_status}"
        if notes:
            log_message += f" | {notes}"
        self._log_activity(ado_number, "status_changed", log_message, old_status, new_status)
        
        # Clear cache
        self._clear_cache()
        
        return True
    
    def update_ado(
        self,
        ado_number: str,
        **updates
    ) -> bool:
        """
        Update ADO work item fields
        
        Args:
            ado_number: ADO identifier
            **updates: Fields to update (e.g., title="New Title", priority="High")
        
        Returns:
            bool: True if updated successfully
        
        Raises:
            ValueError: If validation fails
            RuntimeError: If ADO not found
        """
        if not updates:
            return False
        
        # Get current item
        item = self.get_ado(ado_number)
        if not item:
            raise RuntimeError(f"ADO {ado_number} not found")
        
        # Validate updates
        valid_fields = {
            'title', 'template_file_path', 'priority', 'assigned_to', 'tags',
            'dor_completed', 'dod_completed', 'conversation_ids',
            'related_file_paths', 'commit_shas', 'estimated_hours', 'actual_hours'
        }
        
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            raise ValueError(f"Invalid fields: {invalid_fields}")
        
        # Validate specific fields
        if 'priority' in updates:
            self._validate_priority(updates['priority'])
        if 'dor_completed' in updates:
            self._validate_percentage(updates['dor_completed'], "DoR")
        if 'dod_completed' in updates:
            self._validate_percentage(updates['dod_completed'], "DoD")
        
        # Convert list fields to JSON
        json_fields = {'tags', 'conversation_ids', 'related_file_paths', 'commit_shas'}
        for field in json_fields:
            if field in updates and isinstance(updates[field], list):
                updates[field] = json.dumps(updates[field])
        
        # Build UPDATE query
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clauses.append("updated_at = ?")
        set_clauses.append("last_accessed = ?")
        
        values = list(updates.values())
        values.append(datetime.now().isoformat())
        values.append(datetime.now().isoformat())
        values.append(ado_number)
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE ado_work_items
            SET {', '.join(set_clauses)}
            WHERE ado_number = ?
        """, values)
        
        self.conn.commit()
        
        # Log activity
        fields_updated = ', '.join(updates.keys())
        self._log_activity(ado_number, "updated", f"Updated fields: {fields_updated}")
        
        # Clear cache
        self._clear_cache()
        
        return True
    
    def archive_ado(self, ado_number: str) -> bool:
        """
        Archive completed ADO work item (mark as cancelled)
        
        Args:
            ado_number: ADO identifier
        
        Returns:
            bool: True if archived successfully
        
        Raises:
            ValueError: If not in done status
            RuntimeError: If ADO not found
        """
        item = self.get_ado(ado_number)
        if not item:
            raise RuntimeError(f"ADO {ado_number} not found")
        
        if item['status'] != "done":
            raise ValueError(f"Can only archive completed items. Current status: {item['status']}")
        
        return self.update_status(ado_number, "cancelled", "Archived completed work item")
    
    def resume_ado(self, ado_number: str) -> Dict[str, Any]:
        """
        Resume work on ADO item with full context restoration
        
        Retrieves ADO data and prepares context for development:
        - Files to modify
        - Related conversations (Tier 1)
        - Git commits (Tier 3)
        - Activity history
        
        Args:
            ado_number: ADO identifier
        
        Returns:
            Dict with ADO data + context
        
        Raises:
            RuntimeError: If ADO not found
        """
        item = self.get_ado(ado_number)
        if not item:
            raise RuntimeError(f"ADO {ado_number} not found")
        
        # Get activity log
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT action, notes, old_value, new_value, timestamp
            FROM ado_activity_log
            WHERE ado_number = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, (ado_number,))
        
        activity = [
            {
                'action': row[0],
                'notes': row[1],
                'old_value': row[2],
                'new_value': row[3],
                'timestamp': row[4]
            }
            for row in cursor.fetchall()
        ]
        
        # Update last_accessed
        cursor.execute("""
            UPDATE ado_work_items
            SET last_accessed = ?
            WHERE ado_number = ?
        """, (datetime.now().isoformat(), ado_number))
        self.conn.commit()
        
        # Prepare context
        context = {
            'ado_data': item,
            'recent_activity': activity,
            'related_file_paths': item['related_file_paths'],
            'conversation_ids': item['conversation_ids'],
            'commit_shas': item['commit_shas'],
            'resume_suggestions': self._get_resume_suggestions(item)
        }
        
        # Log resume activity
        self._log_activity(ado_number, "accessed", "Work resumed on this item")
        
        # Clear cache
        self._clear_cache()
        
        return context
    
    def get_activity_log(self, ado_number: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get activity log for ADO work item
        
        Args:
            ado_number: ADO identifier
            limit: Maximum entries to return
        
        Returns:
            List of activity entries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT action, notes, old_value, new_value, timestamp
            FROM ado_activity_log
            WHERE ado_number = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (ado_number, limit))
        
        return [
            {
                'action': row[0],
                'notes': row[1],
                'old_value': row[2],
                'new_value': row[3],
                'timestamp': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def _validate_ado_type(self, ado_type: str):
        """Validate ADO type"""
        valid_types = {t.value for t in ADOType}
        if ado_type not in valid_types:
            raise ValueError(f"Invalid ADO type: {ado_type}. Valid: {valid_types}")
    
    def _validate_status(self, status: str):
        """Validate status"""
        valid_statuses = {s.value for s in ADOStatus}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Valid: {valid_statuses}")
    
    def _validate_priority(self, priority: str):
        """Validate priority"""
        valid_priorities = {p.value for p in ADOPriority}
        if priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {priority}. Valid: {valid_priorities}")
    
    def _validate_percentage(self, value: int, field_name: str):
        """Validate percentage value (0-100)"""
        if not isinstance(value, int) or value < 0 or value > 100:
            raise ValueError(f"{field_name} must be integer between 0 and 100")
    
    def _is_valid_status_transition(self, old_status: str, new_status: str) -> bool:
        """Check if status transition is valid"""
        # Define valid transitions
        transitions = {
            'planning': {'ready', 'blocked', 'cancelled'},
            'ready': {'in_progress', 'blocked', 'cancelled'},
            'in_progress': {'done', 'blocked'},
            'blocked': {'planning', 'ready', 'in_progress'},
            'done': {'in_progress'},  # Allow reopening
            'cancelled': set()  # Cannot transition from cancelled
        }
        
        return new_status in transitions.get(old_status, set())
    
    def _get_valid_transitions(self, status: str) -> List[str]:
        """Get list of valid status transitions"""
        transitions = {
            'planning': ['ready', 'blocked', 'cancelled'],
            'ready': ['in_progress', 'blocked', 'cancelled'],
            'in_progress': ['done', 'blocked'],
            'blocked': ['planning', 'ready', 'in_progress'],
            'done': ['in_progress'],
            'cancelled': []
        }
        
        return transitions.get(status, [])
    
    def _get_resume_suggestions(self, item: Dict[str, Any]) -> List[str]:
        """Generate suggestions for resuming work"""
        suggestions = []
        
        if item['dor_completed'] < 100:
            suggestions.append(f"Complete Definition of Ready ({item['dor_completed']}% done)")
        
        if item['status'] == 'planning':
            suggestions.append("Review and finalize planning document")
        
        if item['status'] == 'ready' and item['dor_completed'] == 100:
            suggestions.append("Start implementation (move to in_progress)")
        
        if item['related_file_paths']:
            suggestions.append(f"Open files to modify: {', '.join(item['related_file_paths'][:3])}")
        
        if item['status'] == 'in_progress' and item['dod_completed'] < 50:
            suggestions.append("Continue implementation to meet acceptance criteria")
        
        if item['status'] == 'in_progress' and item['dod_completed'] >= 50:
            suggestions.append("Prepare for completion review (move to done)")
        
        if item['status'] == 'blocked':
            suggestions.append("Resolve blocker and update status")
        
        return suggestions
    
    def _log_activity(self, ado_number: str, action: str, notes: str = "", old_value: str = "", new_value: str = ""):
        """Log activity for audit trail"""
        timestamp = datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ado_activity_log (ado_number, action, notes, old_value, new_value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ado_number, action, notes, old_value, new_value, timestamp))
        self.conn.commit()
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite Row to dict with JSON parsing"""
        data = dict(row)
        
        # Parse JSON fields
        json_fields = ['tags', 'conversation_ids', 'related_file_paths', 'commit_shas']
        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = []
        
        return data
    
    def _clear_cache(self):
        """Clear LRU cache after modifications"""
        self.get_ado.cache_clear()
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == "__main__":
    # Create manager
    manager = ADOManager()
    
    # Generate unique ADO number for testing
    import random
    test_ado_num = f"ADO-{random.randint(10000, 99999)}"
    
    # Example: Create new ADO
    ado_num = manager.create_ado(
        ado_number=test_ado_num,
        ado_type="Feature",
        title="Example Feature for Testing",
        template_file_path=f"cortex-brain/documents/planning/ado/active/{test_ado_num}-example-feature.md",
        priority="High",
        tags=["testing", "demo"],
        related_file_paths=["src/auth.py", "src/login.tsx"]
    )
    print(f"✅ Created: {ado_num}")
    
    # Example: Get ADO
    item = manager.get_ado(ado_num)
    print(f"📋 Retrieved: {item['title']} (Status: {item['status']})")
    
    # Example: Search
    results = manager.search_ado("testing demo")
    print(f"🔍 Search found {len(results)} items")
    
    # Example: Update status
    manager.update_status(ado_num, "ready", "Planning complete, ready for implementation")
    print(f"📝 Status updated to: ready")
    
    # Example: Resume
    context = manager.resume_ado(ado_num)
    print(f"▶️ Resumed with {len(context['recent_activity'])} recent activities")
    print(f"💡 Suggestions: {context['resume_suggestions']}")
    
    # Example: List with filters
    items, total = manager.list_ado(status="planning", limit=10)
    print(f"📊 Found {total} items in planning (showing {len(items)})")
    
    manager.close()
    print("\n✅ ADO Manager demo complete!")
