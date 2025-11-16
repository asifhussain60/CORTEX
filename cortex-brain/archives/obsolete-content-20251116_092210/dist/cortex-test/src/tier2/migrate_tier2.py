#!/usr/bin/env python3
"""
CORTEX Tier 2 Migration Script
Migrates knowledge graph data from YAML to SQLite with FTS5

Task 0.5.2: Tier 2 Migration Script
Duration: 1-1.5 hours
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse
import yaml


class Tier2Migrator:
    """Migrates Tier 2 knowledge graph from YAML to SQLite with FTS5"""
    
    def __init__(self, source_yaml: Path, target_db: Path):
        """
        Initialize migrator
        
        Args:
            source_yaml: Path to knowledge-graph.yaml
            target_db: Path to target SQLite database
        """
        self.source_yaml = source_yaml
        self.target_db = target_db
        self.stats = {
            'patterns_migrated': 0,
            'workflow_patterns': 0,
            'intent_patterns': 0,
            'file_relationships': 0,
            'validation_insights': 0,
            'errors': []
        }
    
    def create_schema(self, conn: sqlite3.Connection):
        """Create Tier 2 database schema with FTS5"""
        cursor = conn.cursor()
        
        # Pattern store table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                description TEXT,
                confidence REAL DEFAULT 0.5,
                frequency INTEGER DEFAULT 1,
                impact TEXT,
                last_seen TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Pattern details (JSON storage for complex structures)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id)
                    ON DELETE CASCADE,
                UNIQUE(pattern_id, key)
            )
        """)
        
        # File relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file1 TEXT NOT NULL,
                file2 TEXT NOT NULL,
                relationship_type TEXT,
                strength REAL DEFAULT 0.5,
                co_modification_rate REAL,
                last_seen TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file1, file2)
            )
        """)
        
        # FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
                pattern_id UNINDEXED,
                category,
                pattern_type,
                description,
                content='patterns',
                content_rowid='rowid'
            )
        """)
        
        # Triggers to keep FTS5 in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
                INSERT INTO patterns_fts(rowid, pattern_id, category, pattern_type, description)
                VALUES (new.rowid, new.pattern_id, new.category, new.pattern_type, new.description);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
                DELETE FROM patterns_fts WHERE rowid = old.rowid;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
                DELETE FROM patterns_fts WHERE rowid = old.rowid;
                INSERT INTO patterns_fts(rowid, pattern_id, category, pattern_type, description)
                VALUES (new.rowid, new.pattern_id, new.category, new.pattern_type, new.description);
            END
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_category 
            ON patterns(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_confidence 
            ON patterns(confidence DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_last_seen 
            ON patterns(last_seen DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_relationships 
            ON file_relationships(file1, file2)
        """)
        
        conn.commit()
    
    def migrate_validation_insights(self, conn: sqlite3.Connection, insights: Dict):
        """Migrate validation_insights section"""
        cursor = conn.cursor()
        
        for insight_name, insight_data in insights.items():
            try:
                pattern_id = f"validation_{insight_name}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO patterns (
                        pattern_id, category, pattern_type, description,
                        confidence, frequency, impact, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern_id,
                    'validation',
                    'insight',
                    insight_data.get('issue') or insight_data.get('explanation', ''),
                    insight_data.get('confidence', 0.8),
                    insight_data.get('frequency', 1),
                    insight_data.get('impact', 'medium'),
                    insight_data.get('last_seen')
                ))
                
                # Store detailed fields
                for key, value in insight_data.items():
                    if key not in ['confidence', 'frequency', 'impact', 'last_seen', 'issue', 'explanation']:
                        import json
                        cursor.execute("""
                            INSERT OR REPLACE INTO pattern_details (pattern_id, key, value)
                            VALUES (?, ?, ?)
                        """, (pattern_id, key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)))
                
                self.stats['validation_insights'] += 1
                
            except Exception as e:
                self.stats['errors'].append(
                    f"Error migrating validation insight {insight_name}: {str(e)}"
                )
    
    def migrate_workflow_patterns(self, conn: sqlite3.Connection, workflows: Dict):
        """Migrate workflow_patterns section"""
        cursor = conn.cursor()
        
        for workflow_name, workflow_data in workflows.items():
            try:
                pattern_id = f"workflow_{workflow_name}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO patterns (
                        pattern_id, category, pattern_type, description,
                        confidence, frequency, impact, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern_id,
                    'workflow',
                    workflow_data.get('pattern', 'general'),
                    workflow_data.get('description', ''),
                    workflow_data.get('success_rate', 0.8),
                    1,
                    'high',
                    datetime.now().isoformat()
                ))
                
                # Store workflow steps and details
                import json
                for key, value in workflow_data.items():
                    if key not in ['pattern', 'description', 'success_rate']:
                        cursor.execute("""
                            INSERT OR REPLACE INTO pattern_details (pattern_id, key, value)
                            VALUES (?, ?, ?)
                        """, (pattern_id, key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)))
                
                self.stats['workflow_patterns'] += 1
                
            except Exception as e:
                self.stats['errors'].append(
                    f"Error migrating workflow pattern {workflow_name}: {str(e)}"
                )
    
    def migrate_intent_patterns(self, conn: sqlite3.Connection, intents: Dict):
        """Migrate intent_patterns section"""
        cursor = conn.cursor()
        
        for intent_name, intent_data in intents.items():
            try:
                pattern_id = f"intent_{intent_name}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO patterns (
                        pattern_id, category, pattern_type, description,
                        confidence, frequency, impact, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern_id,
                    'intent',
                    'routing',
                    intent_data.get('description', ''),
                    intent_data.get('confidence', 0.85),
                    intent_data.get('frequency', 1),
                    'high',
                    datetime.now().isoformat()
                ))
                
                # Store intent patterns
                import json
                for key, value in intent_data.items():
                    if key not in ['description', 'confidence', 'frequency']:
                        cursor.execute("""
                            INSERT OR REPLACE INTO pattern_details (pattern_id, key, value)
                            VALUES (?, ?, ?)
                        """, (pattern_id, key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)))
                
                self.stats['intent_patterns'] += 1
                
            except Exception as e:
                self.stats['errors'].append(
                    f"Error migrating intent pattern {intent_name}: {str(e)}"
                )
    
    def migrate_file_relationships(self, conn: sqlite3.Connection, relationships: Dict):
        """Migrate file_relationships section"""
        cursor = conn.cursor()
        
        for rel_key, rel_data in relationships.items():
            try:
                # Parse file1 and file2 from key or data
                files = rel_key.split('_x_')
                if len(files) != 2:
                    continue
                
                cursor.execute("""
                    INSERT OR REPLACE INTO file_relationships (
                        file1, file2, relationship_type, strength,
                        co_modification_rate, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    files[0],
                    files[1],
                    rel_data.get('type', 'co_modification'),
                    rel_data.get('strength', 0.5),
                    rel_data.get('co_modification_rate', 0.5),
                    rel_data.get('last_seen', datetime.now().isoformat())
                ))
                
                self.stats['file_relationships'] += 1
                
            except Exception as e:
                self.stats['errors'].append(
                    f"Error migrating file relationship {rel_key}: {str(e)}"
                )
    
    def migrate(self) -> Dict:
        """
        Execute migration from YAML to SQLite
        
        Returns:
            Migration statistics dictionary
        """
        if not self.source_yaml.exists():
            self.stats['errors'].append(f"Source file not found: {self.source_yaml}")
            return self.stats
        
        # Create database connection
        conn = sqlite3.connect(self.target_db)
        
        try:
            # Create schema
            print("Creating database schema with FTS5...")
            self.create_schema(conn)
            
            # Read YAML
            print(f"Reading from {self.source_yaml}...")
            with open(self.source_yaml, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Migrate each section
            if 'validation_insights' in data:
                print("Migrating validation insights...")
                self.migrate_validation_insights(conn, data['validation_insights'])
            
            if 'workflow_patterns' in data:
                print("Migrating workflow patterns...")
                self.migrate_workflow_patterns(conn, data['workflow_patterns'])
            
            if 'intent_patterns' in data:
                print("Migrating intent patterns...")
                self.migrate_intent_patterns(conn, data['intent_patterns'])
            
            if 'file_relationships' in data:
                print("Migrating file relationships...")
                self.migrate_file_relationships(conn, data['file_relationships'])
            
            conn.commit()
            
            print("\nMigration complete!")
            print(f"Validation insights: {self.stats['validation_insights']}")
            print(f"Workflow patterns: {self.stats['workflow_patterns']}")
            print(f"Intent patterns: {self.stats['intent_patterns']}")
            print(f"File relationships: {self.stats['file_relationships']}")
            print(f"Total patterns: {self.stats['patterns_migrated']}")
            
            if self.stats['errors']:
                print(f"\nErrors: {len(self.stats['errors'])}")
                for error in self.stats['errors'][:10]:
                    print(f"  - {error}")
            
            return self.stats
            
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Migrate CORTEX Tier 2 data from YAML to SQLite with FTS5'
    )
    parser.add_argument(
        '--source',
        type=Path,
        help='Source knowledge-graph.yaml file',
        default=Path(__file__).parent.parent.parent.parent / 
                'cortex-brain' / 'knowledge-graph.yaml'
    )
    parser.add_argument(
        '--target',
        type=Path,
        help='Target SQLite database file',
        default=Path(__file__).parent.parent.parent.parent / 
                'cortex-brain' / 'right-hemisphere' / 'tier2' / 'patterns.db'
    )
    
    args = parser.parse_args()
    
    # Ensure target directory exists
    args.target.parent.mkdir(parents=True, exist_ok=True)
    
    # Run migration
    migrator = Tier2Migrator(args.source, args.target)
    stats = migrator.migrate()
    
    # Exit with error code if there were errors
    if stats['errors']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

