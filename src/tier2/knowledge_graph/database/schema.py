"""
Knowledge Graph Database Schema

Handles database initialization and schema management.
"""

import sqlite3
from pathlib import Path


class DatabaseSchema:
    """
    Manages Knowledge Graph database schema.
    
    Responsibilities:
    - Create tables (patterns, relationships, tags, decay log)
    - Create FTS5 virtual table for search
    - Set up triggers for FTS5 sync
    - Create performance indexes
    """
    
    @staticmethod
    def initialize(db_path: Path) -> None:
        """
        Initialize database schema with all tables, indexes, and triggers.
        
        Args:
            db_path: Path to SQLite database file
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        DatabaseSchema._create_patterns_table(cursor)
        DatabaseSchema._create_relationships_table(cursor)
        DatabaseSchema._create_tags_table(cursor)
        DatabaseSchema._create_decay_log_table(cursor)
        DatabaseSchema._create_fts_table(cursor)
        
        # Create triggers
        DatabaseSchema._create_fts_triggers(cursor)
        
        # Create indexes
        DatabaseSchema._create_indexes(cursor)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def _create_patterns_table(cursor: sqlite3.Cursor) -> None:
        """Create patterns table (core storage)."""
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
                scope TEXT DEFAULT 'generic',
                namespaces TEXT DEFAULT '["CORTEX-core"]',
                CHECK (confidence >= 0.0 AND confidence <= 1.0),
                CHECK (pattern_type IN ('workflow', 'principle', 'anti_pattern', 'solution', 'context')),
                CHECK (scope IN ('generic', 'application'))
            )
        """)
    
    @staticmethod
    def _create_relationships_table(cursor: sqlite3.Cursor) -> None:
        """Create pattern relationships table (graph edges)."""
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
    
    @staticmethod
    def _create_tags_table(cursor: sqlite3.Cursor) -> None:
        """Create pattern tags table (many-to-many)."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id) ON DELETE CASCADE,
                UNIQUE (pattern_id, tag)
            )
        """)
    
    @staticmethod
    def _create_decay_log_table(cursor: sqlite3.Cursor) -> None:
        """Create confidence decay log table."""
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
    
    @staticmethod
    def _create_fts_table(cursor: sqlite3.Cursor) -> None:
        """Create FTS5 virtual table for semantic search."""
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS pattern_fts USING fts5(
                pattern_id UNINDEXED,
                title,
                content,
                content='patterns',
                content_rowid='id'
            )
        """)
    
    @staticmethod
    def _create_fts_triggers(cursor: sqlite3.Cursor) -> None:
        """Create triggers to keep FTS5 in sync with patterns table."""
        # Insert trigger
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
                INSERT INTO pattern_fts(rowid, pattern_id, title, content)
                VALUES (new.id, new.pattern_id, new.title, new.content);
            END
        """)
        
        # Delete trigger
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
                DELETE FROM pattern_fts WHERE rowid = old.id;
            END
        """)
        
        # Update trigger
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE OF title, content ON patterns BEGIN
                UPDATE pattern_fts SET title = new.title, content = new.content
                WHERE rowid = new.id;
            END
        """)
    
    @staticmethod
    def _create_indexes(cursor: sqlite3.Cursor) -> None:
        """Create performance indexes."""
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pattern_type ON patterns(pattern_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON patterns(confidence)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON patterns(last_accessed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scope ON patterns(scope)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_namespaces ON patterns(namespaces)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag ON pattern_tags(tag)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_from ON pattern_relationships(from_pattern)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_to ON pattern_relationships(to_pattern)")
