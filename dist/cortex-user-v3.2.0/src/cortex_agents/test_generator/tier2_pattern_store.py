"""
Tier 2 Knowledge Graph - Pattern Storage System

Stores and retrieves business logic patterns using SQLite FTS5 for intelligent
test generation. Supports similarity search, confidence scoring, and pattern lifecycle.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import json
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime


@dataclass
class BusinessPattern:
    """Business logic pattern for test generation"""
    pattern_id: Optional[int]
    domain: str  # authentication, validation, calculation, etc.
    operation: str  # login, validate_email, calculate_total, etc.
    pattern_type: str  # precondition, postcondition, invariant, edge_case
    description: str
    assertion_template: str  # e.g., "assert result is not None"
    confidence: float  # 0.0-1.0
    usage_count: int
    success_count: int
    created_at: str
    last_used: Optional[str]
    metadata: Dict  # Additional context (file paths, function names, etc.)


class Tier2PatternStore:
    """
    SQLite FTS5-backed pattern storage with similarity search.
    
    Features:
    - Full-text search for pattern discovery
    - Confidence-based ranking
    - Pattern lifecycle management
    - Performance optimized (<150ms retrieval)
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize pattern store.
        
        Args:
            db_path: Path to SQLite database. Defaults to cortex-brain/tier2/patterns.db
        """
        if db_path is None:
            brain_root = Path(__file__).parent.parent.parent.parent / "cortex-brain"
            tier2_dir = brain_root / "tier2"
            tier2_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(tier2_dir / "patterns.db")
        
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema with FTS5 support"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Main patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                operation TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                description TEXT NOT NULL,
                assertion_template TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_used TEXT,
                metadata TEXT
            )
        """)
        
        # FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
                domain,
                operation,
                pattern_type,
                description,
                assertion_template,
                content='patterns',
                content_rowid='pattern_id'
            )
        """)
        
        # Triggers to keep FTS5 in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
                INSERT INTO patterns_fts(rowid, domain, operation, pattern_type, description, assertion_template)
                VALUES (new.pattern_id, new.domain, new.operation, new.pattern_type, new.description, new.assertion_template);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
                DELETE FROM patterns_fts WHERE rowid = old.pattern_id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
                UPDATE patterns_fts SET 
                    domain = new.domain,
                    operation = new.operation,
                    pattern_type = new.pattern_type,
                    description = new.description,
                    assertion_template = new.assertion_template
                WHERE rowid = new.pattern_id;
            END
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_domain ON patterns(domain)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_confidence ON patterns(confidence DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_used ON patterns(last_used DESC)
        """)
        
        self.conn.commit()
    
    def store_pattern(self, pattern: BusinessPattern) -> int:
        """
        Store a business pattern.
        
        Args:
            pattern: Pattern to store
            
        Returns:
            pattern_id of stored pattern
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO patterns (
                domain, operation, pattern_type, description,
                assertion_template, confidence, usage_count,
                success_count, created_at, last_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern.domain,
            pattern.operation,
            pattern.pattern_type,
            pattern.description,
            pattern.assertion_template,
            pattern.confidence,
            pattern.usage_count,
            pattern.success_count,
            pattern.created_at,
            pattern.last_used,
            json.dumps(pattern.metadata)
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def search_patterns(
        self,
        query: str,
        domain: Optional[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10
    ) -> List[BusinessPattern]:
        """
        Search patterns using FTS5 full-text search.
        
        Args:
            query: Search query (function name, description, etc.)
            domain: Filter by domain (optional)
            min_confidence: Minimum confidence threshold
            limit: Maximum results to return
            
        Returns:
            List of matching patterns, ranked by relevance and confidence
        """
        start_time = time.time()
        
        cursor = self.conn.cursor()
        
        # Build query with domain filter if provided
        if domain:
            cursor.execute("""
                SELECT p.*, 
                       patterns_fts.rank as fts_rank
                FROM patterns p
                JOIN patterns_fts ON p.pattern_id = patterns_fts.rowid
                WHERE patterns_fts MATCH ?
                  AND p.domain = ?
                  AND p.confidence >= ?
                ORDER BY 
                    patterns_fts.rank,
                    p.confidence DESC,
                    p.last_used DESC
                LIMIT ?
            """, (query, domain, min_confidence, limit))
        else:
            cursor.execute("""
                SELECT p.*,
                       patterns_fts.rank as fts_rank
                FROM patterns p
                JOIN patterns_fts ON p.pattern_id = patterns_fts.rowid
                WHERE patterns_fts MATCH ?
                  AND p.confidence >= ?
                ORDER BY 
                    patterns_fts.rank,
                    p.confidence DESC,
                    p.last_used DESC
                LIMIT ?
            """, (query, min_confidence, limit))
        
        results = []
        for row in cursor.fetchall():
            pattern = BusinessPattern(
                pattern_id=row['pattern_id'],
                domain=row['domain'],
                operation=row['operation'],
                pattern_type=row['pattern_type'],
                description=row['description'],
                assertion_template=row['assertion_template'],
                confidence=row['confidence'],
                usage_count=row['usage_count'],
                success_count=row['success_count'],
                created_at=row['created_at'],
                last_used=row['last_used'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            results.append(pattern)
        
        elapsed = (time.time() - start_time) * 1000
        
        # Performance check (Tier 2 target: <150ms)
        if elapsed > 150:
            print(f"⚠️  Pattern search took {elapsed:.1f}ms (target: <150ms)")
        
        return results
    
    def get_pattern_by_id(self, pattern_id: int) -> Optional[BusinessPattern]:
        """
        Get a specific pattern by ID.
        
        Args:
            pattern_id: Pattern ID to retrieve
            
        Returns:
            Pattern if found, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM patterns WHERE pattern_id = ?
        """, (pattern_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return BusinessPattern(
            pattern_id=row['pattern_id'],
            domain=row['domain'],
            operation=row['operation'],
            pattern_type=row['pattern_type'],
            description=row['description'],
            assertion_template=row['assertion_template'],
            confidence=row['confidence'],
            usage_count=row['usage_count'],
            success_count=row['success_count'],
            created_at=row['created_at'],
            last_used=row['last_used'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def get_patterns_by_domain(
        self,
        domain: str,
        min_confidence: float = 0.5,
        limit: int = 20
    ) -> List[BusinessPattern]:
        """
        Get all patterns for a specific domain.
        
        Args:
            domain: Domain to filter by
            min_confidence: Minimum confidence threshold
            limit: Maximum results
            
        Returns:
            List of patterns ordered by confidence
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM patterns
            WHERE domain = ?
              AND confidence >= ?
            ORDER BY confidence DESC, last_used DESC
            LIMIT ?
        """, (domain, min_confidence, limit))
        
        results = []
        for row in cursor.fetchall():
            pattern = BusinessPattern(
                pattern_id=row['pattern_id'],
                domain=row['domain'],
                operation=row['operation'],
                pattern_type=row['pattern_type'],
                description=row['description'],
                assertion_template=row['assertion_template'],
                confidence=row['confidence'],
                usage_count=row['usage_count'],
                success_count=row['success_count'],
                created_at=row['created_at'],
                last_used=row['last_used'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            results.append(pattern)
        
        return results
    
    def update_pattern_usage(self, pattern_id: int, success: bool):
        """
        Update pattern usage statistics.
        
        Args:
            pattern_id: Pattern ID to update
            success: Whether the pattern was successfully used
        """
        cursor = self.conn.cursor()
        
        if success:
            cursor.execute("""
                UPDATE patterns
                SET usage_count = usage_count + 1,
                    success_count = success_count + 1,
                    last_used = ?,
                    confidence = CASE
                        WHEN usage_count = 0 THEN 0.7
                        ELSE MIN(1.0, (success_count + 1.0) / (usage_count + 1.0) * 0.9 + 0.1)
                    END
                WHERE pattern_id = ?
            """, (datetime.now().isoformat(), pattern_id))
        else:
            cursor.execute("""
                UPDATE patterns
                SET usage_count = usage_count + 1,
                    last_used = ?,
                    confidence = CASE
                        WHEN usage_count = 0 THEN 0.3
                        ELSE MAX(0.1, (success_count + 0.0) / (usage_count + 1.0) * 0.9 + 0.1)
                    END
                WHERE pattern_id = ?
            """, (datetime.now().isoformat(), pattern_id))
        
        self.conn.commit()
    
    def get_pattern_stats(self) -> Dict:
        """
        Get pattern store statistics.
        
        Returns:
            Dictionary with stats (total patterns, by domain, avg confidence, etc.)
        """
        cursor = self.conn.cursor()
        
        # Total patterns
        cursor.execute("SELECT COUNT(*) as total FROM patterns")
        total = cursor.fetchone()['total']
        
        # Patterns by domain
        cursor.execute("""
            SELECT domain, COUNT(*) as count
            FROM patterns
            GROUP BY domain
            ORDER BY count DESC
        """)
        by_domain = {row['domain']: row['count'] for row in cursor.fetchall()}
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) as avg_conf FROM patterns")
        avg_confidence = cursor.fetchone()['avg_conf'] or 0.0
        
        # High confidence patterns (>0.8)
        cursor.execute("SELECT COUNT(*) as high_conf FROM patterns WHERE confidence > 0.8")
        high_confidence = cursor.fetchone()['high_conf']
        
        return {
            'total_patterns': total,
            'patterns_by_domain': by_domain,
            'average_confidence': round(avg_confidence, 2),
            'high_confidence_patterns': high_confidence
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
