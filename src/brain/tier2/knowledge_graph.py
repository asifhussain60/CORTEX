"""
Tier 2: Knowledge Graph for CORTEX 4.0

Long-term pattern learning with namespace isolation.
- Storage: ~/.cortex/shared/tier2/knowledge-graph.db (centralized)
- Features: FTS5 search, pattern decay, cross-project insights
- Namespace: Workspace-based isolation

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from dataclasses import dataclass
import uuid


@dataclass
class Pattern:
    """Pattern data model."""
    pattern_id: str
    title: str
    pattern_type: str
    confidence: float
    context: Dict[str, Any]
    namespace: str
    created_at: datetime
    last_used: Optional[datetime]
    usage_count: int


class KnowledgeGraph:
    """
    Tier 2: Knowledge Graph - Long-term pattern learning
    
    Features:
    - Centralized storage with namespace isolation
    - FTS5 full-text search
    - Pattern confidence tracking
    - Usage-based relevance
    
    Usage:
        kg = KnowledgeGraph(db_path, namespace="cortex")
        
        # Store pattern
        pattern_id = kg.store_pattern(
            title="TDD Workflow",
            pattern_type="workflow",
            context={"phases": ["red", "green", "refactor"]}
        )
        
        # Search patterns
        patterns = kg.search_patterns("TDD")
    """
    
    def __init__(
        self,
        db_path: Path,
        namespace: str = "default",
        confidence_threshold: float = 0.5
    ):
        """
        Initialize knowledge graph.
        
        Args:
            db_path: Path to knowledge-graph.db
            namespace: Namespace for pattern isolation
            confidence_threshold: Minimum confidence for retrieval
        """
        self.db_path = Path(db_path)
        self.namespace = namespace
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema
        self._initialize_schema()
        
        self.logger.debug(f"Knowledge Graph initialized: {db_path} (namespace: {namespace})")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_schema(self):
        """Create database schema with FTS5 support."""
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
                    namespace TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            # FTS5 full-text search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
                    pattern_id UNINDEXED,
                    title,
                    context_json,
                    namespace UNINDEXED,
                    content='patterns',
                    content_rowid='rowid'
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_namespace 
                ON patterns(namespace, confidence DESC)
            """)
            
            conn.commit()
    
    def store_pattern(
        self,
        title: str,
        pattern_type: str,
        context: Dict[str, Any],
        confidence: float = 0.5
    ) -> str:
        """
        Store a new pattern.
        
        Args:
            title: Pattern title
            pattern_type: Pattern type (workflow, code_pattern, etc.)
            context: Pattern context
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            Pattern ID
        """
        pattern_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        context_json = json.dumps(context)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert pattern
            cursor.execute("""
                INSERT INTO patterns (pattern_id, title, pattern_type, confidence, context_json, namespace, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pattern_id, title, pattern_type, confidence, context_json, self.namespace, created_at))
            
            # Insert into FTS
            cursor.execute("""
                INSERT INTO patterns_fts (pattern_id, title, context_json, namespace)
                VALUES (?, ?, ?, ?)
            """, (pattern_id, title, context_json, self.namespace))
            
            conn.commit()
        
        self.logger.debug(f"Stored pattern: {pattern_id} ({title})")
        return pattern_id
    
    def search_patterns(self, query: str, limit: int = 10) -> List[Pattern]:
        """
        Search patterns using FTS5.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of patterns
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # FTS5 full-text search with namespace filter
            cursor.execute("""
                SELECT p.*
                FROM patterns p
                JOIN patterns_fts fts ON p.rowid = fts.rowid
                WHERE patterns_fts MATCH ?
                AND p.namespace = ?
                AND p.confidence >= ?
                ORDER BY p.usage_count DESC, p.confidence DESC
                LIMIT ?
            """, (query, self.namespace, self.confidence_threshold, limit))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append(Pattern(
                    pattern_id=row["pattern_id"],
                    title=row["title"],
                    pattern_type=row["pattern_type"],
                    confidence=row["confidence"],
                    context=json.loads(row["context_json"]) if row["context_json"] else {},
                    namespace=row["namespace"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_used=datetime.fromisoformat(row["last_used"]) if row["last_used"] else None,
                    usage_count=row["usage_count"]
                ))
            
            return patterns
    
    def get_pattern_count(self) -> int:
        """
        Get pattern count for current namespace.
        
        Returns:
            Number of patterns
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM patterns WHERE namespace = ?
            """, (self.namespace,))
            return cursor.fetchone()[0]
    
    def increment_usage(self, pattern_id: str):
        """
        Increment pattern usage count.
        
        Args:
            pattern_id: Pattern ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patterns
                SET usage_count = usage_count + 1, last_used = ?
                WHERE pattern_id = ?
            """, (datetime.now().isoformat(), pattern_id))
            conn.commit()
    
    def close(self):
        """Close knowledge graph (cleanup)."""
        self.logger.debug("Knowledge Graph closed")
