"""
Plan Registry system.

SQLite-based registry for indexing and tracking plan files.
"""
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.workflows.plan_metadata import PlanMetadata, PlanMetadataExtractor, PlanMetadataError


class PlanRegistryError(Exception):
    """Raised when plan registry operations fail."""
    pass


class PlanRegistry:
    """
    SQLite-based registry for plan management.
    
    Provides:
    - Automatic scanning and indexing of plan files
    - Fast lookup by plan_id
    - Filtering by status and priority
    - Incremental updates (detects changed files)
    
    Usage:
        registry = PlanRegistry(Path("/path/to/cortex-brain"))
        registry.scan_and_index()
        plan = registry.get_plan("CORTEX-001")
    """
    
    def __init__(self, brain_path: Path):
        """
        Initialize plan registry.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.brain_path = brain_path
        self.db_path = brain_path / "planning-registry.db"
        self.planning_dir = brain_path / "documents" / "planning"
        
        # Create database and schema
        self._init_database()
        
        # Metadata extractor
        self.extractor = PlanMetadataExtractor()
    
    def _init_database(self) -> None:
        """Initialize SQLite database and create schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                plan_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_date TEXT NOT NULL,
                updated_date TEXT,
                estimated_hours INTEGER NOT NULL,
                actual_hours INTEGER,
                completion_percentage INTEGER,
                assigned_to TEXT,
                indexed_at TEXT NOT NULL
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON plans(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_priority 
            ON plans(priority)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status_priority 
            ON plans(status, priority)
        """)
        
        conn.commit()
        conn.close()
    
    def scan_and_index(self) -> int:
        """
        Scan planning directory and index all plan files.
        
        Recursively scans for .md files with YAML frontmatter.
        Updates existing plans if they've changed.
        
        Returns:
            Number of plans indexed
        """
        if not self.planning_dir.exists():
            return 0
        
        indexed_count = 0
        
        # Find all markdown files recursively
        for plan_file in self.planning_dir.rglob("*.md"):
            try:
                # Extract metadata
                metadata = self.extractor.extract(plan_file)
                
                # Add to registry (upsert)
                self.add_plan(metadata, plan_file)
                indexed_count += 1
                
            except PlanMetadataError:
                # Skip files without valid frontmatter
                continue
        
        return indexed_count
    
    def add_plan(self, metadata: PlanMetadata, file_path: Path) -> None:
        """
        Add or update plan in registry.
        
        Args:
            metadata: Plan metadata
            file_path: Full path to plan file
        """
        # Convert to relative path from brain_path
        try:
            relative_path = file_path.relative_to(self.brain_path)
        except ValueError:
            # If file is not under brain_path, store absolute path
            relative_path = file_path
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Upsert plan (INSERT OR REPLACE)
        cursor.execute("""
            INSERT OR REPLACE INTO plans (
                plan_id, title, status, priority, file_path,
                created_date, updated_date, estimated_hours,
                actual_hours, completion_percentage, assigned_to,
                indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.plan_id,
            metadata.title,
            metadata.status,
            metadata.priority,
            str(relative_path),
            metadata.created_date.isoformat(),
            metadata.updated_date.isoformat() if metadata.updated_date else None,
            metadata.estimated_hours,
            metadata.actual_hours,
            metadata.completion_percentage,
            metadata.assigned_to,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve plan by ID.
        
        Args:
            plan_id: Unique plan identifier
            
        Returns:
            Plan dictionary or None if not found
        """
        result = self._execute_query(
            "SELECT * FROM plans WHERE plan_id = ?",
            (plan_id,)
        )
        
        if not result:
            return None
        
        return self._row_to_dict(result[0])
    
    def list_plans(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List plans with optional filters.
        
        Args:
            status: Filter by status (proposed, approved, in-progress, completed, cancelled)
            priority: Filter by priority (low, medium, high, critical)
            
        Returns:
            List of plan dictionaries
        """
        # Build query
        query = "SELECT * FROM plans WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY priority DESC, created_date DESC"
        
        # Execute query
        results = self._execute_query(query, tuple(params))
        
        # Convert to dictionaries
        return [self._row_to_dict(row) for row in results]
    
    def search_plans(self, query: str) -> List[Dict[str, Any]]:
        """
        Search plans by keyword in title or plan_id.
        
        Args:
            query: Search term (case-insensitive)
            
        Returns:
            List of matching plan dictionaries
        """
        search_term = f"%{query}%"
        
        results = self._execute_query(
            """
            SELECT * FROM plans 
            WHERE plan_id LIKE ? OR title LIKE ?
            ORDER BY priority DESC, created_date DESC
            """,
            (search_term, search_term)
        )
        
        return [self._row_to_dict(row) for row in results]
    
    def update_plan_status(self, plan_id: str, new_status: str) -> bool:
        """
        Update plan status.
        
        Args:
            plan_id: Plan to update
            new_status: New status value
            
        Returns:
            True if updated, False if plan not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE plans SET status = ?, updated_date = ? WHERE plan_id = ?",
            (new_status, datetime.now().isoformat(), plan_id)
        )
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def _execute_query(
        self,
        query: str,
        params: tuple = ()
    ) -> List[tuple]:
        """
        Execute SQL query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        return results
    
    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        """
        Convert database row to dictionary.
        
        Args:
            row: Database row tuple
            
        Returns:
            Dictionary with column names as keys
        """
        # Column order from CREATE TABLE statement
        columns = [
            "plan_id", "title", "status", "priority", "file_path",
            "created_date", "updated_date", "estimated_hours",
            "actual_hours", "completion_percentage", "assigned_to",
            "indexed_at"
        ]
        
        return dict(zip(columns, row))
