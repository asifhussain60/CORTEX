"""
Pattern Store Module

Handles all pattern storage operations including:
- Pattern creation and persistence
- Pattern retrieval by ID
- Pattern updates
- Pattern deletion (with cascade)
- Batch operations

Responsibilities (Single Responsibility Principle):
    - CRUD operations for patterns
    - Confidence score management
    - Access tracking (last_accessed, access_count)
    - Pattern validation

Performance Targets:
    - Pattern storage: <20ms
    - Pattern retrieval by ID: <10ms
    - Batch insert (100 patterns): <200ms

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_store import PatternStore
    >>> from tier2.knowledge_graph.database import DatabaseConnection
    >>> 
    >>> db = DatabaseConnection()
    >>> store = PatternStore(db)
    >>> 
    >>> pattern = store.store_pattern(
    ...     title="TDD Workflow",
    ...     content="Always write tests first",
    ...     pattern_type="workflow",
    ...     confidence=0.95
    ... )
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import json


class PatternType(Enum):
    """Pattern classification types."""
    WORKFLOW = "workflow"          # Recurring successful workflows
    PRINCIPLE = "principle"         # Core principles (immutable)
    ANTI_PATTERN = "anti_pattern"  # What to avoid
    SOLUTION = "solution"           # Proven solutions to problems
    CONTEXT = "context"            # Contextual knowledge


class PatternStore:
    """
    Manages pattern storage operations for Knowledge Graph.
    
    This class handles all CRUD operations for patterns, ensuring data
    integrity and proper confidence score management.
    
    Attributes:
        db: DatabaseConnection instance for database access
    
    Methods:
        store_pattern: Create new pattern or update existing
        get_pattern: Retrieve pattern by ID
        update_pattern: Modify existing pattern
        delete_pattern: Remove pattern (with cascade)
        list_patterns: Query patterns with filters
    """
    
    def __init__(self, db):
        """
        Initialize Pattern Store.
        
        Args:
            db: DatabaseConnection instance
        """
        self.db = db
    
    def store_pattern(
        self,
        pattern_id: str,
        title: str,
        content: str,
        pattern_type: str,
        confidence: float = 1.0,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_pinned: bool = False,
        scope: str = "cortex",
        namespaces: Optional[List[str]] = None,
        is_cortex_internal: bool = False
    ) -> Dict[str, Any]:
        """
        Store a new pattern in the Knowledge Graph with namespace protection.
        
        Args:
            pattern_id: Unique identifier for the pattern
            title: Pattern title (human-readable)
            content: Pattern description/content
            pattern_type: Type of pattern (workflow, principle, etc.)
            confidence: Confidence score (0.0-1.0)
            source: Source of the pattern (optional)
            metadata: Additional metadata as dict (optional)
            is_pinned: Whether pattern is pinned (immune to decay)
            scope: 'cortex' or 'application' (boundary enforcement)
            namespaces: List of namespace tags (default: ["CORTEX-core"])
            is_cortex_internal: True if called from CORTEX framework code
        
        Returns:
            Dictionary with stored pattern data including generated ID
        
        Raises:
            ValueError: If validation fails or namespace protection violated
            sqlite3.IntegrityError: If pattern_id already exists
        
        Performance: ~20ms
        """
        # Validation
        if not (0.0 <= confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
        
        if scope not in ("cortex", "application"):
            raise ValueError(f"Scope must be 'cortex' or 'application', got {scope}")
        
        # Default namespaces
        if namespaces is None:
            namespaces = ["CORTEX-core"]
        
        # NAMESPACE PROTECTION: Block user code from writing to cortex.* namespace
        for namespace in namespaces:
            if namespace.startswith("cortex.") and not is_cortex_internal:
                raise ValueError(
                    f"cortex.* namespace is protected. "
                    f"Only CORTEX framework can write to '{namespace}'. "
                    f"Use workspace.* namespace for application patterns."
                )
        
        # Convert metadata and namespaces to JSON
        metadata_json = json.dumps(metadata) if metadata else None
        namespaces_json = json.dumps(namespaces)
        
        now = datetime.now().isoformat()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert pattern
            cursor.execute("""
                INSERT INTO patterns (
                    pattern_id, title, content, pattern_type, confidence,
                    created_at, last_accessed, access_count, source, metadata,
                    is_pinned, scope, namespaces
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id, title, content, pattern_type, confidence,
                now, now, 0, source, metadata_json,
                1 if is_pinned else 0, scope, namespaces_json
            ))
            
            conn.commit()
            
            return {
                "pattern_id": pattern_id,
                "title": title,
                "content": content,
                "pattern_type": pattern_type,
                "confidence": confidence,
                "created_at": now,
                "last_accessed": now,
                "access_count": 0,
                "source": source,
                "metadata": metadata,
                "is_pinned": is_pinned,
                "scope": scope,
                "namespaces": namespaces,
                "_namespace": namespaces[0] if namespaces else None  # Primary namespace
            }
        except Exception as e:
            conn.rollback()
            raise
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Pattern data as dictionary, or None if not found
        
        Side Effects:
            - Updates last_accessed timestamp
            - Increments access_count
        
        Performance: ~10ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get pattern
        cursor.execute("""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata, is_pinned,
                   scope, namespaces
            FROM patterns
            WHERE pattern_id = ?
        """, (pattern_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Update access timestamp and count
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE patterns
            SET last_accessed = ?, access_count = access_count + 1
            WHERE pattern_id = ?
        """, (now, pattern_id))
        
        conn.commit()
        
        # Parse metadata and namespaces
        metadata = json.loads(row[9]) if row[9] else None
        namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
        
        return {
            "pattern_id": row[0],
            "title": row[1],
            "content": row[2],
            "pattern_type": row[3],
            "confidence": row[4],
            "created_at": row[5],
            "last_accessed": now,  # Use updated timestamp
            "access_count": row[7] + 1,  # Incremented count
            "source": row[8],
            "metadata": metadata,
            "is_pinned": bool(row[10]),
            "scope": row[11] if row[11] else "cortex",
            "namespaces": namespaces
        }
    
    def update_pattern(
        self,
        pattern_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing pattern.
        
        Args:
            pattern_id: Pattern to update
            updates: Dictionary of fields to update
        
        Returns:
            True if updated, False if pattern not found
        
        Allowed Updates:
            - title, content, confidence, metadata, is_pinned
        
        Protected Fields (cannot update):
            - pattern_id, created_at, pattern_type
        
        Performance: ~15ms
        """
        if not updates:
            return False
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Protected fields
        protected = {"pattern_id", "created_at", "pattern_type"}
        
        # Build update query dynamically
        update_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in protected:
                continue
            
            # Handle JSON fields
            if field in ("metadata", "namespaces"):
                update_clauses.append(f"{field} = ?")
                params.append(json.dumps(value) if value else None)
            else:
                update_clauses.append(f"{field} = ?")
                params.append(value)
        
        if not update_clauses:
            return False
        
        # Execute update
        query = f"UPDATE patterns SET {', '.join(update_clauses)} WHERE pattern_id = ?"
        params.append(pattern_id)
        
        cursor.execute(query, params)
        updated = cursor.rowcount > 0
        
        conn.commit()
        
        return updated
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete a pattern (cascade deletes relationships and tags).
        
        Args:
            pattern_id: Pattern to delete
        
        Returns:
            True if deleted, False if pattern not found
        
        Cascade Deletes:
            - pattern_relationships (both directions)
            - pattern_tags
        
        Performance: ~25ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        
        return deleted
    
    def list_patterns(
        self,
        pattern_type: Optional[str] = None,
        scope: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List patterns with optional filters.
        
        Args:
            pattern_type: Filter by pattern type
            scope: Filter by scope ('cortex' or 'application')
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
        
        Returns:
            List of pattern dictionaries
        
        Performance: ~30ms for 100 patterns
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        params = []
        
        if pattern_type:
            where_clauses.append("pattern_type = ?")
            params.append(pattern_type)
        
        if scope:
            where_clauses.append("scope = ?")
            params.append(scope)
        
        where_clauses.append("confidence >= ?")
        params.append(min_confidence)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Execute query
        query = f"""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata,
                   is_pinned, scope, namespaces
            FROM patterns
            WHERE {where_sql}
            ORDER BY confidence DESC, last_accessed DESC
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            
            patterns.append({
                "pattern_id": row[0],
                "title": row[1],
                "content": row[2],
                "pattern_type": row[3],
                "confidence": row[4],
                "created_at": row[5],
                "last_accessed": row[6],
                "access_count": row[7],
                "source": row[8],
                "metadata": metadata,
                "is_pinned": bool(row[10]),
                "scope": row[11] if row[11] else "cortex",
                "namespaces": namespaces,
                "_namespace": namespaces[0] if namespaces else None  # Primary namespace
            })
        
        return patterns
