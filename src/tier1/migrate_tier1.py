#!/usr/bin/env python3
"""
CORTEX Tier 1 Migration Script
Migrates conversation data from JSONL to SQLite

Task 0.5.1: Tier 1 Migration Script
Duration: 1-1.5 hours
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse


class Tier1Migrator:
    """Migrates Tier 1 conversation data from JSONL to SQLite"""
    
    def __init__(self, source_jsonl: Path, target_db: Path):
        """
        Initialize migrator
        
        Args:
            source_jsonl: Path to conversation-history.jsonl
            target_db: Path to target SQLite database
        """
        self.source_jsonl = source_jsonl
        self.target_db = target_db
        self.stats = {
            'conversations_migrated': 0,
            'messages_migrated': 0,
            'entities_migrated': 0,
            'files_migrated': 0,
            'errors': []
        }
    
    def create_schema(self, conn: sqlite3.Connection):
        """Create Tier 1 database schema"""
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                started TIMESTAMP NOT NULL,
                ended TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                intent TEXT,
                outcome TEXT,
                note TEXT,
                source TEXT,
                session_id TEXT,
                import_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                role TEXT,
                user TEXT,
                intent TEXT,
                content TEXT,
                context_ref TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                    ON DELETE CASCADE
            )
        """)
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                entity TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                    ON DELETE CASCADE,
                UNIQUE(conversation_id, entity)
            )
        """)
        
        # Files modified table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files_modified (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                    ON DELETE CASCADE,
                UNIQUE(conversation_id, file_path)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_started 
            ON conversations(started DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_active 
            ON conversations(active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation 
            ON messages(conversation_id, timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_conversation 
            ON entities(conversation_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_conversation 
            ON files_modified(conversation_id)
        """)
        
        conn.commit()
    
    def migrate_conversation(self, conn: sqlite3.Connection, conv_data: Dict) -> bool:
        """
        Migrate a single conversation record
        
        Args:
            conn: Database connection
            conv_data: Conversation data from JSONL
            
        Returns:
            True if successful, False otherwise
        """
        cursor = conn.cursor()
        
        try:
            # Extract conversation fields
            conversation_id = conv_data.get('conversation_id')
            if not conversation_id:
                self.stats['errors'].append(f"Missing conversation_id in record")
                return False
            
            # Insert conversation
            cursor.execute("""
                INSERT OR REPLACE INTO conversations (
                    conversation_id, title, started, ended, message_count,
                    active, intent, outcome, note, source, session_id, import_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                conv_data.get('title', ''),
                conv_data.get('started'),
                conv_data.get('ended'),
                conv_data.get('message_count', 0),
                conv_data.get('active', False),
                conv_data.get('intent'),
                conv_data.get('outcome'),
                conv_data.get('note'),
                conv_data.get('source', 'migration'),
                conv_data.get('session_id'),
                conv_data.get('import_date')
            ))
            
            self.stats['conversations_migrated'] += 1
            
            # Migrate messages
            messages = conv_data.get('messages', [])
            for msg in messages:
                self._migrate_message(cursor, conversation_id, msg)
            
            # Migrate entities
            entities = conv_data.get('entities_discussed', [])
            if isinstance(entities, list):
                for entity in entities:
                    self._migrate_entity(cursor, conversation_id, entity)
            
            # Migrate files
            files = conv_data.get('files_modified', [])
            if isinstance(files, str):
                files = [files]
            elif isinstance(files, list):
                pass
            else:
                files = []
            
            for file_path in files:
                self._migrate_file(cursor, conversation_id, file_path)
            
            conn.commit()
            return True
            
        except Exception as e:
            self.stats['errors'].append(
                f"Error migrating conversation {conversation_id}: {str(e)}"
            )
            conn.rollback()
            return False
    
    def _migrate_message(self, cursor: sqlite3.Cursor, conversation_id: str, msg_data: Dict):
        """Migrate a single message"""
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO messages (
                    id, conversation_id, timestamp, role, user, intent,
                    content, context_ref, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                msg_data.get('id'),
                conversation_id,
                msg_data.get('timestamp'),
                msg_data.get('role'),
                msg_data.get('user'),
                msg_data.get('intent'),
                msg_data.get('text') or msg_data.get('content', ''),
                msg_data.get('context_ref'),
                msg_data.get('session_id')
            ))
            self.stats['messages_migrated'] += 1
        except Exception as e:
            self.stats['errors'].append(
                f"Error migrating message {msg_data.get('id')}: {str(e)}"
            )
    
    def _migrate_entity(self, cursor: sqlite3.Cursor, conversation_id: str, entity: str):
        """Migrate a single entity"""
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO entities (conversation_id, entity)
                VALUES (?, ?)
            """, (conversation_id, entity))
            self.stats['entities_migrated'] += 1
        except Exception as e:
            self.stats['errors'].append(
                f"Error migrating entity {entity}: {str(e)}"
            )
    
    def _migrate_file(self, cursor: sqlite3.Cursor, conversation_id: str, file_path: str):
        """Migrate a single file reference"""
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO files_modified (conversation_id, file_path)
                VALUES (?, ?)
            """, (conversation_id, file_path))
            self.stats['files_migrated'] += 1
        except Exception as e:
            self.stats['errors'].append(
                f"Error migrating file {file_path}: {str(e)}"
            )
    
    def migrate(self) -> Dict:
        """
        Execute migration from JSONL to SQLite
        
        Returns:
            Migration statistics dictionary
        """
        if not self.source_jsonl.exists():
            self.stats['errors'].append(f"Source file not found: {self.source_jsonl}")
            return self.stats
        
        # Create database connection
        conn = sqlite3.connect(self.target_db)
        
        try:
            # Create schema
            print("Creating database schema...")
            self.create_schema(conn)
            
            # Read and migrate JSONL
            print(f"Reading from {self.source_jsonl}...")
            with open(self.source_jsonl, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        conv_data = json.loads(line)
                        self.migrate_conversation(conn, conv_data)
                    except json.JSONDecodeError as e:
                        self.stats['errors'].append(
                            f"JSON error on line {line_num}: {str(e)}"
                        )
            
            print("\nMigration complete!")
            print(f"Conversations: {self.stats['conversations_migrated']}")
            print(f"Messages: {self.stats['messages_migrated']}")
            print(f"Entities: {self.stats['entities_migrated']}")
            print(f"Files: {self.stats['files_migrated']}")
            
            if self.stats['errors']:
                print(f"\nErrors: {len(self.stats['errors'])}")
                for error in self.stats['errors'][:10]:  # Show first 10
                    print(f"  - {error}")
            
            return self.stats
            
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Migrate CORTEX Tier 1 data from JSONL to SQLite'
    )
    parser.add_argument(
        '--source',
        type=Path,
        help='Source conversation-history.jsonl file',
        default=Path(__file__).parent.parent.parent.parent / 
                'cortex-brain' / 'conversation-history.jsonl'
    )
    parser.add_argument(
        '--target',
        type=Path,
        help='Target SQLite database file',
        default=Path(__file__).parent.parent.parent.parent / 
                'cortex-brain' / 'left-hemisphere' / 'tier1' / 'conversations.db'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate data without writing to database'
    )
    
    args = parser.parse_args()
    
    # Ensure target directory exists
    args.target.parent.mkdir(parents=True, exist_ok=True)
    
    # Run migration
    migrator = Tier1Migrator(args.source, args.target)
    stats = migrator.migrate()
    
    # Exit with error code if there were errors
    if stats['errors']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

