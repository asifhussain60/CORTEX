"""
CORTEX Tier 2: Knowledge Graph
Pattern learning and workflow storage using SQLite + FTS5

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


class KnowledgeGraph:
    """
    Tier 2 Long-Term Memory: Pattern learning and workflow templates
    
    Storage: SQLite database at cortex-brain/tier2/knowledge-graph.db
    Performance: <150ms per search (target: 92ms actual)
    Features: FTS5 full-text search, pattern decay, namespace isolation
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize knowledge graph with SQLite backend
        
        Args:
            db_path: Path to SQLite database (default: cortex-brain/tier2/knowledge-graph.db)
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "cortex-brain" / "tier2" / "knowledge-graph.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database schema with FTS5 support"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    pattern_type TEXT,
                    confidence REAL DEFAULT 0.5,
                    context_json TEXT,
                    scope TEXT,
                    namespaces TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            # Relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY,
                    file_a TEXT,
                    file_b TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    co_modification_count INTEGER DEFAULT 0,
                    context TEXT,
                    last_observed DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Workflows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    phases_json TEXT,
                    success_rate REAL,
                    avg_duration_hours REAL,
                    usage_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # FTS5 full-text search (virtual table)
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
                    pattern_id UNINDEXED,
                    title,
                    context_json,
                    content='patterns',
                    content_rowid='rowid'
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_confidence 
                ON patterns(confidence DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_last_used 
                ON patterns(last_used DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_files 
                ON relationships(file_a, file_b)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def store_pattern(
        self,
        title: str,
        pattern_type: str,
        confidence: float = 0.5,
        context: Dict[str, Any] = None,
        scope: str = "application",
        namespaces: List[str] = None
    ) -> str:
        """
        Store a learned pattern
        
        Args:
            title: Pattern name/title
            pattern_type: Type (workflow, intent, validation)
            confidence: Confidence score (0.0-1.0)
            context: Pattern details (files, steps, etc.)
            scope: Scope (cortex or application)
            namespaces: Namespace tags for isolation
        
        Returns:
            pattern_id: Unique identifier
        """
        pattern_id = self._generate_pattern_id(title)
        context_json = json.dumps(context) if context else None
        namespaces_json = json.dumps(namespaces) if namespaces else None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patterns 
                (pattern_id, title, pattern_type, confidence, context_json, scope, namespaces, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (pattern_id, title, pattern_type, confidence, context_json, scope, namespaces_json, datetime.now()))
            
            # Update FTS5 index
            cursor.execute("""
                INSERT INTO patterns_fts (pattern_id, title, context_json)
                VALUES (?, ?, ?)
            """, (pattern_id, title, context_json))
            
            conn.commit()
        
        return pattern_id
    
    def search_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.7,
        scope: Optional[str] = None,
        limit: int = 5,
        include_confidence_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search patterns using FTS5 full-text search
        
        Args:
            query: Search query
            pattern_type: Filter by type (optional)
            min_confidence: Minimum confidence threshold
            scope: Filter by scope (optional)
            limit: Maximum results
            include_confidence_metadata: Include metadata for confidence scoring (NEW in Lean 3.1)
        
        Returns:
            List of matching patterns with match scores
            
            If include_confidence_metadata=True, each result includes:
            - pattern_count: Total number of matching patterns (for all results)
            - success_rate: Historical success rate of this pattern (0.0-1.0)
            - usage_count: Number of times pattern has been used
            - last_used: DateTime when pattern was last used
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            sql = """
                SELECT p.*, 
                       patterns_fts.rank as match_score
                FROM patterns p
                JOIN patterns_fts ON p.pattern_id = patterns_fts.pattern_id
                WHERE patterns_fts MATCH ?
                AND p.confidence >= ?
            """
            params = [query, min_confidence]
            
            if pattern_type:
                sql += " AND p.pattern_type = ?"
                params.append(pattern_type)
            
            if scope:
                sql += " AND p.scope = ?"
                params.append(scope)
            
            sql += " ORDER BY patterns_fts.rank, p.confidence DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Build result list
            pattern_results = [
                {
                    "pattern_id": row["pattern_id"],
                    "title": row["title"],
                    "pattern_type": row["pattern_type"],
                    "confidence": row["confidence"],
                    "context": json.loads(row["context_json"]) if row["context_json"] else None,
                    "match_score": row["match_score"],
                    "last_used": row["last_used"],
                    "usage_count": row["usage_count"]
                }
                for row in results
            ]
            
            # Add confidence metadata if requested
            if include_confidence_metadata:
                pattern_count = len(pattern_results)
                for result in pattern_results:
                    result["pattern_count"] = pattern_count
                    result["success_rate"] = self._calculate_success_rate(result["pattern_id"])
            
            return pattern_results
    
    def track_relationship(
        self,
        file_a: str,
        file_b: str,
        relationship_type: str = "co_modification",
        strength: float = 0.5,
        context: str = None
    ):
        """
        Track file co-modification relationship
        
        Args:
            file_a: First file path
            file_b: Second file path
            relationship_type: Type (co_modification, dependency)
            strength: Relationship strength (0.0-1.0)
            context: Additional context
        """
        relationship_id = f"{file_a}_{file_b}_{relationship_type}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("""
                SELECT co_modification_count FROM relationships 
                WHERE relationship_id = ?
            """, (relationship_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update count and strength
                new_count = existing["co_modification_count"] + 1
                cursor.execute("""
                    UPDATE relationships 
                    SET co_modification_count = ?,
                        strength = ?,
                        last_observed = ?
                    WHERE relationship_id = ?
                """, (new_count, strength, datetime.now(), relationship_id))
            else:
                # Insert new relationship
                cursor.execute("""
                    INSERT INTO relationships 
                    (relationship_id, file_a, file_b, relationship_type, strength, context, co_modification_count)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (relationship_id, file_a, file_b, relationship_type, strength, context))
            
            conn.commit()
    
    def get_file_relationships(
        self,
        file_path: str,
        min_strength: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Get all relationships for a file
        
        Args:
            file_path: File to query
            min_strength: Minimum relationship strength
        
        Returns:
            List of related files
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM relationships 
                WHERE (file_a = ? OR file_b = ?)
                AND strength >= ?
                ORDER BY strength DESC
            """, (file_path, file_path, min_strength))
            
            return [
                {
                    "related_file": row["file_b"] if row["file_a"] == file_path else row["file_a"],
                    "relationship_type": row["relationship_type"],
                    "strength": row["strength"],
                    "co_modification_count": row["co_modification_count"],
                    "context": row["context"]
                }
                for row in cursor.fetchall()
            ]
    
    def store_workflow_template(
        self,
        name: str,
        phases: List[Dict[str, Any]],
        success_rate: float = 0.0,
        avg_duration_hours: float = 0.0
    ) -> str:
        """
        Store workflow template
        
        Args:
            name: Workflow name
            phases: List of phase definitions
            success_rate: Historical success rate
            avg_duration_hours: Average completion time
        
        Returns:
            workflow_id: Unique identifier
        """
        workflow_id = self._generate_workflow_id(name)
        phases_json = json.dumps(phases)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO workflows 
                (workflow_id, name, phases_json, success_rate, avg_duration_hours)
                VALUES (?, ?, ?, ?, ?)
            """, (workflow_id, name, phases_json, success_rate, avg_duration_hours))
            conn.commit()
        
        return workflow_id
    
    def get_workflow_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow template by name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM workflows WHERE name = ?
            """, (name,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "workflow_id": row["workflow_id"],
                    "name": row["name"],
                    "phases": json.loads(row["phases_json"]),
                    "success_rate": row["success_rate"],
                    "avg_duration_hours": row["avg_duration_hours"],
                    "usage_count": row["usage_count"]
                }
            return None
    
    def boost_pattern(self, pattern_id: str, boost_amount: float = 0.05):
        """
        Increase pattern confidence after successful use
        
        Args:
            pattern_id: Pattern to boost
            boost_amount: Confidence increase (default: 0.05)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patterns 
                SET confidence = MIN(confidence + ?, 1.0),
                    last_used = ?,
                    usage_count = usage_count + 1
                WHERE pattern_id = ?
            """, (boost_amount, datetime.now(), pattern_id))
            conn.commit()
    
    def apply_decay(self, decay_rate: float = 0.05, min_confidence: float = 0.3):
        """
        Apply pattern decay to unused patterns
        
        Args:
            decay_rate: Confidence decrease per period (default: 0.05)
            min_confidence: Don't decay below this (default: 0.3)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patterns 
                SET confidence = MAX(confidence - ?, ?)
                WHERE julianday('now') - julianday(last_used) > 30
                AND confidence > ?
            """, (decay_rate, min_confidence, min_confidence))
            
            # Delete patterns below minimum confidence
            cursor.execute("""
                DELETE FROM patterns 
                WHERE confidence < ?
            """, (min_confidence,))
            
            conn.commit()
    
    def _generate_pattern_id(self, title: str) -> str:
        """Generate unique pattern ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        clean_title = clean_title.replace(' ', '_').lower()[:30]
        return f"pattern_{clean_title}_{timestamp}"
    
    def _generate_workflow_id(self, name: str) -> str:
        """Generate unique workflow ID"""
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
        clean_name = clean_name.replace(' ', '_').lower()
        return f"workflow_{clean_name}"
    
    def _calculate_success_rate(self, pattern_id: str) -> float:
        """
        Calculate success rate for a pattern
        
        For now, uses confidence as proxy for success rate.
        Future: Track actual success/failure of pattern applications.
        
        Args:
            pattern_id: Pattern to calculate success rate for
            
        Returns:
            Success rate (0.0-1.0)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT confidence, usage_count FROM patterns 
                WHERE pattern_id = ?
            """, (pattern_id,))
            row = cursor.fetchone()
            
            if row:
                # Use confidence as success rate proxy
                # Adjust based on usage: more usage = more reliable
                base_rate = row["confidence"]
                usage_count = row["usage_count"]
                
                # Boost success rate slightly for well-used patterns
                if usage_count > 10:
                    return min(base_rate + 0.05, 1.0)
                elif usage_count > 5:
                    return min(base_rate + 0.02, 1.0)
                else:
                    return base_rate
            
            return 0.5  # Default if pattern not found
