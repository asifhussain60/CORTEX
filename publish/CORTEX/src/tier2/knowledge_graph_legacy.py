"""
CORTEX Tier 2: Knowledge Graph
Long-term memory with FTS5 semantic search and pattern relationships.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import json


class PatternType(Enum):
    """Pattern classification types."""
    WORKFLOW = "workflow"          # Recurring successful workflows
    PRINCIPLE = "principle"         # Core principles (immutable)
    ANTI_PATTERN = "anti_pattern"  # What to avoid
    SOLUTION = "solution"           # Proven solutions to problems
    CONTEXT = "context"            # Contextual knowledge


class RelationshipType(Enum):
    """Pattern relationship types."""
    EXTENDS = "extends"              # Pattern B extends Pattern A
    RELATES_TO = "relates_to"        # General relationship
    RELATED_TO = "related_to"        # Alias for relates_to
    CONTRADICTS = "contradicts"      # Patterns conflict
    SUPERSEDES = "supersedes"        # New pattern replaces old


@dataclass
class Pattern:
    """Pattern data structure."""
    pattern_id: str
    title: str
    content: str
    pattern_type: PatternType
    confidence: float
    created_at: str
    last_accessed: str
    access_count: int
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_pinned: bool = False
    scope: str = "cortex"  # NEW: Boundary enforcement ('cortex' or 'application')
    namespaces: Optional[List[str]] = None  # NEW: Multi-app support (JSON array)


class KnowledgeGraph:
    """
    Knowledge Graph (Tier 2): Long-term pattern storage with FTS5 search.
    
    Features:
    - SQLite + FTS5 for semantic search
    - Pattern relationships (graph structure)
    - Confidence decay based on access patterns
    - Tag-based organization
    - BM25 ranking for search results
    
    Performance:
    - Search queries: <150ms
    - Pattern retrieval: <50ms
    - Relationship traversal: <100ms
    """
    
    # Confidence decay settings (Governance Rule #12)
    DECAY_RATE = 0.01  # 1% per day
    DECAY_THRESHOLD = 60  # Days before decay starts
    MIN_CONFIDENCE = 0.3  # Delete below this
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize Knowledge Graph.
        
        Args:
            db_path: Path to SQLite database file (default: cortex-brain/tier2/knowledge_graph.db)
        """
        if db_path is None:
            # Default location
            brain_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier2"
            brain_dir.mkdir(parents=True, exist_ok=True)
            db_path = brain_dir / "knowledge_graph.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database schema with FTS5 support."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patterns table (core storage)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP NOT NULL,
                last_accessed TIMESTAMP NOT NULL,
                access_count INTEGER DEFAULT 0,
                source TEXT,
                metadata TEXT,
                is_pinned INTEGER DEFAULT 0,
                scope TEXT DEFAULT 'cortex',
                namespaces TEXT DEFAULT '["CORTEX-core"]',
                CHECK (confidence >= 0.0 AND confidence <= 1.0),
                CHECK (pattern_type IN ('workflow', 'principle', 'anti_pattern', 'solution', 'context')),
                CHECK (scope IN ('cortex', 'application'))
            )
        """)
        
        # Pattern relationships (graph edges)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_pattern TEXT NOT NULL,
                to_pattern TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_pattern) REFERENCES patterns(pattern_id) ON DELETE CASCADE,
                FOREIGN KEY (to_pattern) REFERENCES patterns(pattern_id) ON DELETE CASCADE,
                CHECK (strength >= 0.0 AND strength <= 1.0),
                CHECK (relationship_type IN ('extends', 'relates_to', 'related_to', 'contradicts', 'supersedes')),
                UNIQUE (from_pattern, to_pattern, relationship_type)
            )
        """)
        
        # Pattern tags (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id) ON DELETE CASCADE,
                UNIQUE (pattern_id, tag)
            )
        """)
        
        # Confidence decay log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confidence_decay_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                old_confidence REAL,
                new_confidence REAL,
                decay_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id) ON DELETE CASCADE
            )
        """)
        
        # FTS5 virtual table for semantic search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS pattern_fts USING fts5(
                pattern_id UNINDEXED,
                title,
                content,
                content='patterns',
                content_rowid='id'
            )
        """)
        
        # Triggers to keep FTS5 in sync (only title and content, not tags)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
                INSERT INTO pattern_fts(rowid, pattern_id, title, content)
                VALUES (new.id, new.pattern_id, new.title, new.content);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
                DELETE FROM pattern_fts WHERE rowid = old.id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE OF title, content ON patterns BEGIN
                UPDATE pattern_fts SET title = new.title, content = new.content
                WHERE rowid = new.id;
            END
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pattern_type ON patterns(pattern_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON patterns(confidence)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON patterns(last_accessed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scope ON patterns(scope)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_namespaces ON patterns(namespaces)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag ON pattern_tags(tag)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_from ON pattern_relationships(from_pattern)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_to ON pattern_relationships(to_pattern)")
        
        conn.commit()
        conn.close()
    
    def add_pattern(
        self,
        pattern_id: str,
        title: str,
        content: str,
        pattern_type: PatternType,
        confidence: float = 1.0,
        scope: str = "cortex",  # Boundary enforcement ('cortex' | 'application')
        namespaces: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Pattern:
        """Add a new pattern to the knowledge graph."""
        if scope not in ["cortex", "application"]:
            raise ValueError(f"Invalid scope: {scope}. Must be 'cortex' or 'application'")
        if namespaces is None:
            namespaces = ["CORTEX-core"]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        namespaces_json = json.dumps(namespaces)

        cursor.execute(
            """
            INSERT INTO patterns (
                pattern_id, title, content, pattern_type, confidence,
                created_at, last_accessed, access_count, source, metadata,
                scope, namespaces
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pattern_id,
                title,
                content,
                pattern_type.value,
                confidence,
                now,
                now,
                0,
                source,
                metadata_json,
                scope,
                namespaces_json,
            ),
        )

        if tags:
            for tag in tags:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO pattern_tags (pattern_id, tag)
                    VALUES (?, ?)
                    """,
                    (pattern_id, tag),
                )

        conn.commit()
        conn.close()

        return Pattern(
            pattern_id=pattern_id,
            title=title,
            content=content,
            pattern_type=pattern_type,
            confidence=confidence,
            created_at=now,
            last_accessed=now,
            access_count=0,
            source=source,
            metadata=metadata,
            scope=scope,
            namespaces=namespaces,
        )
    
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """
        Retrieve a pattern by ID and update access timestamp.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Pattern object or None if not found
        """
        conn = sqlite3.connect(self.db_path)
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
            conn.close()
            return None

        now = datetime.now().isoformat()
        cursor.execute(
            """
            UPDATE patterns
            SET last_accessed = ?, access_count = access_count + 1
            WHERE pattern_id = ?
            """,
            (now, pattern_id),
        )

        conn.commit()
        conn.close()

        metadata = json.loads(row[9]) if row[9] else None
        namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]

        return Pattern(
            pattern_id=row[0],
            title=row[1],
            content=row[2],
            pattern_type=PatternType(row[3]),
            confidence=row[4],
            created_at=row[5],
            last_accessed=now,
            access_count=row[7] + 1,
            source=row[8],
            metadata=metadata,
            is_pinned=bool(row[10]),
            scope=row[11] if row[11] else "cortex",
            namespaces=namespaces,
        )
    
    def update_pattern(
        self,
        pattern_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update pattern properties.
        
        Args:
            pattern_id: Pattern to update
            title: New title (optional)
            content: New content (optional)
            confidence: New confidence (optional)
            metadata: New metadata (optional)
        
        Returns:
            True if updated, False if pattern not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if confidence is not None:
            updates.append("confidence = ?")
            params.append(confidence)
        
        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))
        
        if not updates:
            conn.close()
            return False
        
        # Execute update
        query = f"UPDATE patterns SET {', '.join(updates)} WHERE pattern_id = ?"
        params.append(pattern_id)
        
        cursor.execute(query, params)
        updated = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return updated
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete a pattern from the knowledge graph.
        
        Args:
            pattern_id: Pattern to delete
        
        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_patterns_by_type(self, pattern_type: PatternType) -> List[Pattern]:
        """
        Get all patterns of a specific type.
        
        Args:
            pattern_type: Type to filter by
        
        Returns:
            List of Pattern objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata, is_pinned,
                   scope, namespaces
            FROM patterns
            WHERE pattern_type = ?
            ORDER BY confidence DESC, last_accessed DESC
        """, (pattern_type.value,))
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            patterns.append(Pattern(
                pattern_id=row[0],
                title=row[1],
                content=row[2],
                pattern_type=PatternType(row[3]),
                confidence=row[4],
                created_at=row[5],
                last_accessed=row[6],
                access_count=row[7],
                source=row[8],
                metadata=metadata,
                is_pinned=bool(row[10]),
                scope=row[11] if row[11] else "cortex",
                namespaces=namespaces
            ))
        
        return patterns
    
    def search_patterns(self, query: str, limit: int = 20) -> List[Pattern]:
        """
        Search patterns using FTS5 full-text search with BM25 ranking.
        
        Supports:
        - Simple keywords: "testing"
        - Phrase search: '"test driven development"'
        - Boolean: "testing AND refactoring"
        - Prefix: "refactor*"
        - NOT: "testing NOT manual"
        
        Args:
            query: Search query (FTS5 syntax)
            limit: Maximum results to return
        
        Returns:
            List of Pattern objects, ranked by relevance
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FTS5 search with BM25 ranking
        cursor.execute("""
            SELECT p.pattern_id, p.title, p.content, p.pattern_type, p.confidence,
                   p.created_at, p.last_accessed, p.access_count, p.source, p.metadata, p.is_pinned,
                   p.scope, p.namespaces,
                   bm25(pattern_fts) as rank
            FROM patterns p
            JOIN pattern_fts ON p.id = pattern_fts.rowid
            WHERE pattern_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            patterns.append(Pattern(
                pattern_id=row[0],
                title=row[1],
                content=row[2],
                pattern_type=PatternType(row[3]),
                confidence=row[4],
                created_at=row[5],
                last_accessed=row[6],
                access_count=row[7],
                source=row[8],
                metadata=metadata,
                is_pinned=bool(row[10]),
                scope=row[11] if row[11] else "cortex",
                namespaces=namespaces
            ))
        
        return patterns
    
    def search_patterns_with_namespace(
        self,
        query: str,
        current_namespace: Optional[str] = None,
        include_generic: bool = True,
        limit: int = 20
    ) -> List[Pattern]:
        """
        Search patterns with namespace boosting for context-aware results.
        
        Priority ranking:
        1. Current namespace patterns (weight 2.0)
        2. Generic patterns (weight 1.5 if include_generic=True)
        3. Other namespace patterns (weight 0.5)
        
        Args:
            query: Search query (FTS5 syntax)
            current_namespace: Current application context (e.g., 'KSESSIONS')
            include_generic: Include generic CORTEX patterns (default True)
            limit: Maximum results to return
        
        Returns:
            List of Pattern objects, ranked by relevance and namespace priority
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FTS5 search with BM25 ranking
        cursor.execute("""
            SELECT p.pattern_id, p.title, p.content, p.pattern_type, p.confidence,
                   p.created_at, p.last_accessed, p.access_count, p.source, p.metadata, p.is_pinned,
                   p.scope, p.namespaces,
                   bm25(pattern_fts) as rank
            FROM patterns p
            JOIN pattern_fts ON p.id = pattern_fts.rowid
            WHERE pattern_fts MATCH ?
            ORDER BY rank
        """, (query,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Parse patterns and apply namespace boosting
        patterns_with_scores = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            
            pattern = Pattern(
                pattern_id=row[0],
                title=row[1],
                content=row[2],
                pattern_type=PatternType(row[3]),
                confidence=row[4],
                created_at=row[5],
                last_accessed=row[6],
                access_count=row[7],
                source=row[8],
                metadata=metadata,
                is_pinned=bool(row[10]),
                scope=row[11] if row[11] else "cortex",
                namespaces=namespaces
            )
            
            # Calculate namespace boost
            base_score = row[13]  # BM25 rank
            boost = 1.0
            
            if current_namespace and current_namespace in namespaces:
                # Current namespace match - highest priority
                boost = 2.0
            elif pattern.scope == "cortex" and include_generic:
                # Generic patterns always included with medium priority
                boost = 1.5
            elif current_namespace:
                # Other namespaces - lower priority
                boost = 0.5
            
            # Apply boost (BM25 scores are negative, so multiply)
            final_score = base_score * boost
            patterns_with_scores.append((pattern, final_score))
        
        # Sort by boosted score and return top N
        patterns_with_scores.sort(key=lambda x: x[1])  # BM25 lower is better
        return [p[0] for p in patterns_with_scores[:limit]]
    
    def get_patterns_by_namespace(self, namespace: str) -> List[Pattern]:
        """
        Get all patterns for a specific namespace.
        
        Args:
            namespace: Namespace to filter by (e.g., 'KSESSIONS', 'CORTEX-core')
        
        Returns:
            List of Pattern objects in the namespace
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # JSON LIKE query to find namespace in array
        cursor.execute("""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata, is_pinned,
                   scope, namespaces
            FROM patterns
            WHERE namespaces LIKE ?
            ORDER BY confidence DESC, last_accessed DESC
        """, (f'%"{namespace}"%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            
            # Verify namespace is actually in the array (LIKE can have false positives)
            if namespace in namespaces:
                patterns.append(Pattern(
                    pattern_id=row[0],
                    title=row[1],
                    content=row[2],
                    pattern_type=PatternType(row[3]),
                    confidence=row[4],
                    created_at=row[5],
                    last_accessed=row[6],
                    access_count=row[7],
                    source=row[8],
                    metadata=metadata,
                    is_pinned=bool(row[10]),
                    scope=row[11] if row[11] else "cortex",
                    namespaces=namespaces
                ))
        
        return patterns
    
    def get_generic_patterns(self) -> List[Pattern]:
        """
        Get all generic (CORTEX core) patterns.
        
        Returns:
            List of Pattern objects with scope='cortex'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata, is_pinned,
                   scope, namespaces
            FROM patterns
            WHERE scope = 'cortex'
            ORDER BY confidence DESC, last_accessed DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            patterns.append(Pattern(
                pattern_id=row[0],
                title=row[1],
                content=row[2],
                pattern_type=PatternType(row[3]),
                confidence=row[4],
                created_at=row[5],
                last_accessed=row[6],
                access_count=row[7],
                source=row[8],
                metadata=metadata,
                is_pinned=bool(row[10]),
                scope=row[11] if row[11] else "cortex",
                namespaces=namespaces
            ))
        
        return patterns
    
    def get_application_patterns(self) -> List[Pattern]:
        """
        Get all application-specific patterns.
        
        Returns:
            List of Pattern objects with scope='application'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata, is_pinned,
                   scope, namespaces
            FROM patterns
            WHERE scope = 'application'
            ORDER BY confidence DESC, last_accessed DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            patterns.append(Pattern(
                pattern_id=row[0],
                title=row[1],
                content=row[2],
                pattern_type=PatternType(row[3]),
                confidence=row[4],
                created_at=row[5],
                last_accessed=row[6],
                access_count=row[7],
                source=row[8],
                metadata=metadata,
                is_pinned=bool(row[10]),
                scope=row[11] if row[11] else "cortex",
                namespaces=namespaces
            ))
        
        return patterns
    
    def link_patterns(
        self,
        from_pattern: str,
        to_pattern: str,
        relationship_type: RelationshipType,
        strength: float = 1.0
    ) -> bool:
        """
        Create a relationship between two patterns.
        
        Args:
            from_pattern: Source pattern ID
            to_pattern: Target pattern ID
            relationship_type: Type of relationship
            strength: Relationship strength (0.0 to 1.0)
        
        Returns:
            True if created, False if already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO pattern_relationships (from_pattern, to_pattern, relationship_type, strength)
                VALUES (?, ?, ?, ?)
            """, (from_pattern, to_pattern, relationship_type.value, strength))
            
            conn.commit()
            created = True
        except sqlite3.IntegrityError:
            # Relationship already exists
            created = False
        
        conn.close()
        return created
    
    def get_related_patterns(
        self,
        pattern_id: str,
        max_depth: int = 1,
        min_strength: float = 0.5
    ) -> List[Pattern]:
        """
        Get patterns related to a given pattern (graph traversal).
        
        Args:
            pattern_id: Starting pattern
            max_depth: Maximum traversal depth
            min_strength: Minimum relationship strength
        
        Returns:
            List of related Pattern objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Track visited patterns to avoid cycles
        visited = {pattern_id}
        current_level = {pattern_id}
        related_ids = set()
        
        for depth in range(max_depth):
            if not current_level:
                break
            
            next_level = set()
            
            for current_id in current_level:
                # Get directly related patterns
                cursor.execute("""
                    SELECT to_pattern
                    FROM pattern_relationships
                    WHERE from_pattern = ? AND strength >= ?
                """, (current_id, min_strength))
                
                for (related_id,) in cursor.fetchall():
                    if related_id not in visited:
                        visited.add(related_id)
                        related_ids.add(related_id)
                        next_level.add(related_id)
            
            current_level = next_level
        
        # Fetch full pattern data for related IDs
        if not related_ids:
            conn.close()
            return []
        
        placeholders = ','.join('?' * len(related_ids))
        cursor.execute(f"""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata, is_pinned,
                   scope, namespaces
            FROM patterns
            WHERE pattern_id IN ({placeholders})
        """, list(related_ids))
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            patterns.append(Pattern(
                pattern_id=row[0],
                title=row[1],
                content=row[2],
                pattern_type=PatternType(row[3]),
                confidence=row[4],
                created_at=row[5],
                last_accessed=row[6],
                access_count=row[7],
                source=row[8],
                metadata=metadata,
                is_pinned=bool(row[10]),
                scope=row[11] if row[11] else "cortex",
                namespaces=namespaces
            ))
        
        return patterns
    
    def apply_confidence_decay(self) -> Dict[str, int]:
        """
        Apply confidence decay to patterns based on access patterns.
        
        Implements Governance Rule #12: Confidence Decay
        - Patterns decay 1% per day after 60 days of no access
        - Patterns below 0.3 confidence are deleted
        - Pinned patterns are protected from decay
        
        Returns:
            Dict with 'decayed_count' and 'deleted_count'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        decay_threshold_date = (now - timedelta(days=self.DECAY_THRESHOLD)).isoformat()
        
        # Get patterns eligible for decay/deletion (old OR low confidence, not pinned)
        cursor.execute("""
            SELECT pattern_id, confidence, last_accessed
            FROM patterns
            WHERE is_pinned = 0
              AND (last_accessed < ? OR confidence <= ?)
        """, (decay_threshold_date, self.MIN_CONFIDENCE))
        
        decayed_count = 0
        deleted_count = 0
        
        for pattern_id, confidence, last_accessed in cursor.fetchall():
            # Check if already below threshold
            if confidence < self.MIN_CONFIDENCE:
                # Delete immediately
                cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
                deleted_count += 1
                
                # Log deletion
                cursor.execute("""
                    INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, confidence, 0.0, "Deleted: Already below minimum confidence"))
                continue
            
            # Calculate decay
            last_access_date = datetime.fromisoformat(last_accessed)
            days_since_access = (now - last_access_date).days
            days_to_decay = max(0, days_since_access - self.DECAY_THRESHOLD)
            
            # Skip if no decay needed
            if days_to_decay == 0:
                continue
            
            # Apply decay
            decay_amount = self.DECAY_RATE * days_to_decay
            new_confidence = max(0.0, confidence - decay_amount)
            
            if new_confidence < self.MIN_CONFIDENCE:
                # Delete pattern
                cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
                deleted_count += 1
                
                # Log deletion
                cursor.execute("""
                    INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, confidence, new_confidence, "Deleted: Decayed below minimum confidence"))
            else:
                # Update confidence
                cursor.execute("""
                    UPDATE patterns SET confidence = ? WHERE pattern_id = ?
                """, (new_confidence, pattern_id))
                decayed_count += 1
                
                # Log decay
                cursor.execute("""
                    INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, confidence, new_confidence, f"Decayed: {days_to_decay} days since last access"))
        
        conn.commit()
        conn.close()
        
        return {
            'decayed_count': decayed_count,
            'deleted_count': deleted_count
        }
    
    def pin_pattern(self, pattern_id: str) -> bool:
        """
        Pin a pattern to protect it from confidence decay.
        
        Args:
            pattern_id: Pattern to pin
        
        Returns:
            True if pinned, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE patterns SET is_pinned = 1 WHERE pattern_id = ?", (pattern_id,))
        pinned = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return pinned
    
    def get_decay_log(self, pattern_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get confidence decay history.
        
        Args:
            pattern_id: Filter by pattern (optional)
            limit: Maximum entries to return
        
        Returns:
            List of decay log entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if pattern_id:
            cursor.execute("""
                SELECT pattern_id, old_confidence, new_confidence, decay_date, reason
                FROM confidence_decay_log
                WHERE pattern_id = ?
                ORDER BY decay_date DESC
                LIMIT ?
            """, (pattern_id, limit))
        else:
            cursor.execute("""
                SELECT pattern_id, old_confidence, new_confidence, decay_date, reason
                FROM confidence_decay_log
                ORDER BY decay_date DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        log_entries = []
        for row in rows:
            log_entries.append({
                'pattern_id': row[0],
                'old_confidence': row[1],
                'new_confidence': row[2],
                'decay_date': row[3],
                'reason': row[4]
            })
        
        return log_entries
    
    def get_pattern_tags(self, pattern_id: str) -> List[str]:
        """
        Get all tags for a pattern.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            List of tag strings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tag FROM pattern_tags WHERE pattern_id = ? ORDER BY tag
        """, (pattern_id,))
        
        tags = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tags
    
    def find_patterns_by_tag(self, tag: str) -> List[Pattern]:
        """
        Find all patterns with a specific tag.
        
        Args:
            tag: Tag to search for
        
        Returns:
            List of Pattern objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.pattern_id, p.title, p.content, p.pattern_type, p.confidence,
                   p.created_at, p.last_accessed, p.access_count, p.source, p.metadata, p.is_pinned,
                   p.scope, p.namespaces
            FROM patterns p
            JOIN pattern_tags t ON p.pattern_id = t.pattern_id
            WHERE t.tag = ?
            ORDER BY p.confidence DESC, p.last_accessed DESC
        """, (tag,))
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            patterns.append(Pattern(
                pattern_id=row[0],
                title=row[1],
                content=row[2],
                pattern_type=PatternType(row[3]),
                confidence=row[4],
                created_at=row[5],
                last_accessed=row[6],
                access_count=row[7],
                source=row[8],
                metadata=metadata,
                is_pinned=bool(row[10]),
                scope=row[11] if row[11] else "cortex",
                namespaces=namespaces
            ))
        
        return patterns
    
    def get_tag_cloud(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get tag frequency statistics (tag cloud).
        
        Args:
            limit: Maximum tags to return
        
        Returns:
            List of dicts with 'tag' and 'count'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tag, COUNT(*) as count
            FROM pattern_tags
            GROUP BY tag
            ORDER BY count DESC, tag
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'tag': row[0], 'count': row[1]} for row in rows]
    
    def close(self):
        """Close any open database connections."""
        # SQLite connections are opened/closed per operation
        # This is here for API completeness
        pass
