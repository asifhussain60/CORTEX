"""
Brain Initialization Orchestrator

Handles first-run brain setup, database initialization, schema application,
and repair of corrupted/missing components.

Responsibilities:
- Detect first-run vs existing installation
- Create brain directory structure (tier1/, tier2/, tier3/)
- Initialize all 3 tier databases with schemas
- Track schema versions
- Repair missing or corrupted tables

Usage:
    >>> from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
    >>> orchestrator = BrainInitOrchestrator(brain_path="/path/to/cortex-brain")
    >>> if orchestrator.is_first_run():
    ...     result = orchestrator.initialize_brain()
    ...     print(f"Initialized: {result['success']}")

Author: Asif Hussain
Phase: 7.3 - Brain Initialization System
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import json


class BrainInitOrchestrator:
    """
    Orchestrates brain initialization and maintenance.
    
    Handles first-run setup, schema application, and repair operations
    across all 3 brain tiers.
    """
    
    def __init__(self, brain_path: str):
        """
        Initialize orchestrator with brain path.
        
        Args:
            brain_path: Absolute path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.tier1_path = self.brain_path / "tier1"
        self.tier2_path = self.brain_path / "tier2"
        self.tier3_path = self.brain_path / "tier3"
        
        self.tier1_db = self.tier1_path / "working_memory.db"
        self.tier2_db = self.tier2_path / "knowledge_graph.db"
        self.tier3_db = self.tier3_path / "development_context.db"
    
    def is_first_run(self) -> bool:
        """
        Check if this is a first-run (no databases exist).
        
        Returns:
            True if no tier databases exist, False otherwise
        """
        return not (
            self.tier1_db.exists() or
            self.tier2_db.exists() or
            self.tier3_db.exists()
        )
    
    def initialize_brain(self) -> Dict[str, Any]:
        """
        Initialize complete brain structure from scratch.
        
        Creates directory structure and initializes all 3 tier databases
        with their respective schemas.
        
        Returns:
            Dict with success status and details
        """
        # Check if already initialized
        if not self.is_first_run():
            return {
                'success': True,
                'already_initialized': True,
                'message': 'Brain already initialized'
            }
        
        # Create directory structure
        self.tier1_path.mkdir(parents=True, exist_ok=True)
        self.tier2_path.mkdir(parents=True, exist_ok=True)
        self.tier3_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize each tier
        tier1_result = self.setup_tier1()
        tier2_result = self.setup_tier2()
        tier3_result = self.setup_tier3()
        
        # Check all succeeded
        success = all([
            tier1_result['success'],
            tier2_result['success'],
            tier3_result['success']
        ])
        
        return {
            'success': success,
            'tier1': tier1_result,
            'tier2': tier2_result,
            'tier3': tier3_result,
            'timestamp': datetime.now().isoformat()
        }
    
    def setup_tier1(self) -> Dict[str, Any]:
        """
        Setup Tier 1 (Working Memory) database.
        
        Creates database and applies schema for:
        - conversations table (FIFO 70-conversation limit)
        - entities table (extracted entities)
        - metadata table (system metadata, versions)
        
        Returns:
            Dict with success status and table count
        """
        try:
            conn = sqlite3.connect(str(self.tier1_db))
            cursor = conn.cursor()
            
            # Conversations table (FIFO working memory)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    token_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Entities table (extracted from conversations)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_value TEXT NOT NULL,
                    context TEXT,
                    extracted_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            # Metadata table (system metadata, schema versions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
                ON conversations(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entities_conversation
                ON entities(conversation_id)
            """)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'tables_created': 3,
                'database': str(self.tier1_db)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def setup_tier2(self) -> Dict[str, Any]:
        """
        Setup Tier 2 (Knowledge Graph) database.
        
        Creates database and applies schema for:
        - patterns table (learned patterns)
        - relationships table (code relationships)
        - pattern_fts (FTS5 full-text search)
        
        Returns:
            Dict with success status and table count
        """
        try:
            conn = sqlite3.connect(str(self.tier2_db))
            cursor = conn.cursor()
            
            # Patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0,
                    source TEXT,
                    metadata TEXT,
                    is_pinned INTEGER DEFAULT 0,
                    scope TEXT DEFAULT 'cortex',
                    namespaces TEXT DEFAULT '[]'
                )
            """)
            
            # Relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    relationship_id TEXT UNIQUE NOT NULL,
                    file_a TEXT NOT NULL,
                    file_b TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    context TEXT,
                    created_at TEXT NOT NULL
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
            
            # FTS5 triggers to keep in sync
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
                CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
                    UPDATE pattern_fts SET
                        pattern_id = new.pattern_id,
                        title = new.title,
                        content = new.content
                    WHERE rowid = new.id;
                END
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_type
                ON patterns(pattern_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_files
                ON relationships(file_a, file_b)
            """)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'tables_created': 2,  # patterns, relationships (pattern_fts is virtual)
                'fts5_enabled': True,
                'database': str(self.tier2_db)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def setup_tier3(self) -> Dict[str, Any]:
        """
        Setup Tier 3 (Development Context) database.
        
        Creates database and applies schema for:
        - code_metrics table (file metrics)
        - git_activity table (commit tracking)
        - project_insights table (learned insights)
        
        Returns:
            Dict with success status and table count
        """
        try:
            conn = sqlite3.connect(str(self.tier3_db))
            cursor = conn.cursor()
            
            # Code metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    lines_of_code INTEGER DEFAULT 0,
                    complexity INTEGER DEFAULT 0,
                    last_modified TEXT,
                    change_frequency INTEGER DEFAULT 0,
                    hotspot_score REAL DEFAULT 0.0,
                    measured_at TEXT NOT NULL
                )
            """)
            
            # Git activity table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS git_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_hash TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    lines_added INTEGER DEFAULT 0,
                    lines_removed INTEGER DEFAULT 0,
                    commit_message TEXT,
                    author TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Project insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    related_files TEXT,
                    confidence REAL DEFAULT 0.8,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_file
                ON code_metrics(file_path)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_git_activity_file
                ON git_activity(file_path)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_git_activity_timestamp
                ON git_activity(timestamp DESC)
            """)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'tables_created': 3,
                'database': str(self.tier3_db)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_schema_versions(self) -> Dict[str, int]:
        """
        Get current schema versions for all tiers.
        
        Reads from metadata table (if exists) or returns defaults.
        
        Returns:
            Dict with tier names and version numbers
        """
        versions = {}
        
        # Get Tier 1 version (stored in Tier 1 metadata)
        if self.tier1_db.exists():
            try:
                conn = sqlite3.connect(str(self.tier1_db))
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value FROM metadata WHERE key = 'schema_version_tier1'
                """)
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    versions['tier1'] = int(json.loads(row[0])['version'])
                else:
                    versions['tier1'] = 1  # Default version
            except:
                versions['tier1'] = 1
        else:
            versions['tier1'] = 0  # Not initialized
        
        # Get Tier 2 version
        if self.tier2_db.exists():
            try:
                # Check if metadata stored in Tier 1
                if self.tier1_db.exists():
                    conn = sqlite3.connect(str(self.tier1_db))
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT value FROM metadata WHERE key = 'schema_version_tier2'
                    """)
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row:
                        versions['tier2'] = int(json.loads(row[0])['version'])
                    else:
                        versions['tier2'] = 1
                else:
                    versions['tier2'] = 1
            except:
                versions['tier2'] = 1
        else:
            versions['tier2'] = 0
        
        # Get Tier 3 version
        if self.tier3_db.exists():
            try:
                if self.tier1_db.exists():
                    conn = sqlite3.connect(str(self.tier1_db))
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT value FROM metadata WHERE key = 'schema_version_tier3'
                    """)
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row:
                        versions['tier3'] = int(json.loads(row[0])['version'])
                    else:
                        versions['tier3'] = 1
                else:
                    versions['tier3'] = 1
            except:
                versions['tier3'] = 1
        else:
            versions['tier3'] = 0
        
        return versions
    
    def repair_brain(self) -> Dict[str, Any]:
        """
        Repair brain by re-applying schemas.
        
        Checks for missing tables and recreates them. Does NOT drop
        existing data.
        
        Returns:
            Dict with repair status and count of fixes
        """
        repairs_made = 0
        repairs_log = []
        
        # Repair Tier 1
        if self.tier1_db.exists():
            try:
                conn = sqlite3.connect(str(self.tier1_db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                expected_tables = ['conversations', 'entities', 'metadata']
                missing = [t for t in expected_tables if t not in tables]
                
                if missing:
                    self.setup_tier1()
                    repairs_made += len(missing)
                    repairs_log.append(f"Tier 1: Repaired {len(missing)} tables")
            except:
                pass
        
        # Repair Tier 2
        if self.tier2_db.exists():
            try:
                conn = sqlite3.connect(str(self.tier2_db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                expected_tables = ['patterns', 'relationships', 'pattern_fts']
                missing = [t for t in expected_tables if t not in tables]
                
                if missing:
                    self.setup_tier2()
                    repairs_made += len(missing)
                    repairs_log.append(f"Tier 2: Repaired {len(missing)} tables")
            except:
                pass
        
        # Repair Tier 3
        if self.tier3_db.exists():
            try:
                conn = sqlite3.connect(str(self.tier3_db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                expected_tables = ['code_metrics', 'git_activity', 'project_insights']
                missing = [t for t in expected_tables if t not in tables]
                
                if missing:
                    self.setup_tier3()
                    repairs_made += len(missing)
                    repairs_log.append(f"Tier 3: Repaired {len(missing)} tables")
            except:
                pass
        
        return {
            'success': True,
            'repairs_made': repairs_made,
            'log': repairs_log
        }
