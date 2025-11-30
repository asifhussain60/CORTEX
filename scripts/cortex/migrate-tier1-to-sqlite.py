#!/usr/bin/env python3
"""
CORTEX Brain Tier 1 Migration Script

Purpose: Migrate conversation data from JSONL to SQLite
Author: CORTEX Development Team
Version: 1.0

Migrates:
- conversation-history.jsonl → tier1_conversations + tier1_messages
- conversation-context.jsonl → tier1_messages (context resolution)

Usage:
    python migrate-tier1-to-sqlite.py [--db-path cortex-brain.db] [--source-dir cortex-brain]

Features:
- Preserves FIFO queue (keeps last 20 conversations)
- Extracts messages from conversation objects
- Maintains conversation continuity
- Validates data integrity
- Idempotent (safe to run multiple times)
"""

import sqlite3
import json
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import uuid


def get_project_root() -> Path:
    """Get CORTEX project root directory"""
    # Script is in CORTEX/scripts/
    return Path(__file__).parent.parent.absolute()


def load_jsonl_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file and return list of JSON objects"""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path} (skipping)")
        return []
    
    conversations = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                conversations.append(obj)
            except json.JSONDecodeError as e:
                print(f"⚠️  Line {line_num}: Invalid JSON - {e}")
                continue
    
    return conversations


def extract_messages_from_conversation(conv: Dict[str, Any], conv_id: str) -> List[Dict[str, Any]]:
    """Extract messages array from conversation object"""
    messages = []
    
    # Check if conversation has messages array
    if 'messages' in conv and isinstance(conv['messages'], list):
        for seq_num, msg in enumerate(conv['messages'], 1):
            message = {
                'message_id': msg.get('id', f"msg-{uuid.uuid4().hex[:8]}"),
                'conversation_id': conv_id,
                'sequence_number': seq_num,
                'role': 'user',  # Default to user, override if specified
                'content': msg.get('text', msg.get('content', '')),
                'timestamp': msg.get('timestamp', conv.get('started', datetime.now().isoformat())),
                'intent_detected': msg.get('intent'),
                'context_ref': msg.get('context_ref'),
            }
            messages.append(message)
    
    return messages


def migrate_tier1_conversations(
    cursor: sqlite3.Cursor,
    conversations: List[Dict[str, Any]],
    max_conversations: int = 20
) -> Dict[str, int]:
    """
    Migrate conversation data to tier1_conversations and tier1_messages
    
    Args:
        cursor: Database cursor
        conversations: List of conversation objects from JSONL
        max_conversations: Maximum conversations to keep (FIFO)
    
    Returns:
        Dictionary with migration statistics
    """
    stats = {
        'conversations_migrated': 0,
        'messages_migrated': 0,
        'conversations_skipped': 0,
        'errors': 0
    }
    
    # Sort conversations by creation date (oldest first)
    sorted_convs = sorted(
        conversations,
        key=lambda c: c.get('started', c.get('timestamp', ''))
    )
    
    # Keep only last N conversations (FIFO)
    recent_convs = sorted_convs[-max_conversations:] if len(sorted_convs) > max_conversations else sorted_convs
    
    if len(sorted_convs) > max_conversations:
        print(f"⚠️  Trimming to {max_conversations} most recent conversations (FIFO)")
        stats['conversations_skipped'] = len(sorted_convs) - max_conversations
    
    # Migrate each conversation
    for queue_pos, conv in enumerate(recent_convs, 1):
        try:
            conv_id = conv.get('conversation_id', f"conv-{uuid.uuid4().hex[:8]}")
            title = conv.get('title', 'Untitled Conversation')
            status = 'complete' if conv.get('ended') or conv.get('active') == False else 'active'
            created_at = conv.get('started', conv.get('timestamp', datetime.now().isoformat()))
            updated_at = conv.get('ended', created_at)
            completed_at = conv.get('ended')
            message_count = conv.get('message_count', len(conv.get('messages', [])))
            intent = conv.get('intent')
            outcome = conv.get('outcome')
            
            # Extract metadata
            entities = conv.get('entities_discussed', [])
            if isinstance(entities, list):
                primary_entity = entities[0] if entities else None
            else:
                primary_entity = entities
            
            files_modified = conv.get('files_modified', [])
            if isinstance(files_modified, list):
                related_files = json.dumps(files_modified)
            else:
                related_files = json.dumps([files_modified] if files_modified else [])
            
            commits = conv.get('associated_commits', [])
            associated_commits = json.dumps(commits) if commits else None
            
            # Insert conversation
            cursor.execute("""
                INSERT OR REPLACE INTO tier1_conversations (
                    conversation_id, topic, status, created_at, updated_at, completed_at,
                    message_count, intent, outcome, primary_entity, related_files,
                    associated_commits, queue_position
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conv_id, title, status, created_at, updated_at, completed_at,
                message_count, intent, outcome, primary_entity, related_files,
                associated_commits, queue_pos
            ))
            
            stats['conversations_migrated'] += 1
            
            # Extract and insert messages
            messages = extract_messages_from_conversation(conv, conv_id)
            for msg in messages:
                cursor.execute("""
                    INSERT OR REPLACE INTO tier1_messages (
                        message_id, conversation_id, sequence_number, role, content,
                        timestamp, intent_detected, resolved_references, agent_used
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg['message_id'],
                    msg['conversation_id'],
                    msg['sequence_number'],
                    msg['role'],
                    msg['content'],
                    msg['timestamp'],
                    msg.get('intent_detected'),
                    json.dumps({msg['context_ref']: None}) if msg.get('context_ref') else None,
                    msg.get('agent_used')
                ))
                
                stats['messages_migrated'] += 1
        
        except Exception as e:
            print(f"✗ Error migrating conversation {conv.get('conversation_id', 'unknown')}: {e}")
            stats['errors'] += 1
    
    return stats


def migrate_tier1(db_path: str, source_dir: Path) -> Dict[str, Any]:
    """
    Main migration function for Tier 1
    
    Args:
        db_path: Path to SQLite database
        source_dir: Path to cortex-brain directory
    
    Returns:
        Dictionary with migration statistics
    """
    print(f"🧠 CORTEX Brain Tier 1 Migration")
    print(f"=" * 60)
    print(f"Database: {db_path}")
    print(f"Source: {source_dir}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"✓ Connected to database")
    
    # Load conversation history
    history_file = source_dir / "conversation-history.jsonl"
    context_file = source_dir / "conversation-context.jsonl"
    
    print(f"\n📋 Loading conversation data...")
    history_conversations = load_jsonl_file(history_file)
    context_conversations = load_jsonl_file(context_file)
    
    # Merge conversations (deduplicate by conversation_id)
    all_conversations = {conv['conversation_id']: conv for conv in history_conversations}
    for conv in context_conversations:
        conv_id = conv.get('conversation_id')
        if conv_id and conv_id not in all_conversations:
            all_conversations[conv_id] = conv
    
    conversations_list = list(all_conversations.values())
    
    print(f"✓ Loaded {len(conversations_list)} unique conversations")
    
    # Migrate conversations
    print(f"\n🔄 Migrating to database...")
    stats = migrate_tier1_conversations(cursor, conversations_list)
    
    # Commit changes
    conn.commit()
    print(f"✓ Changes committed")
    
    # Validate migration
    print(f"\n🔍 Validating migration...")
    cursor.execute("SELECT COUNT(*) FROM tier1_conversations")
    db_conv_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tier1_messages")
    db_msg_count = cursor.fetchone()[0]
    
    print(f"✓ Database contains:")
    print(f"  - {db_conv_count} conversations")
    print(f"  - {db_msg_count} messages")
    
    # Close connection
    conn.close()
    
    # Print final statistics
    print(f"\n📊 Migration Statistics:")
    print(f"  Conversations migrated: {stats['conversations_migrated']}")
    print(f"  Messages migrated: {stats['messages_migrated']}")
    print(f"  Conversations skipped (FIFO): {stats['conversations_skipped']}")
    print(f"  Errors: {stats['errors']}")
    print()
    
    if stats['errors'] == 0:
        print(f"✅ Tier 1 migration complete!")
    else:
        print(f"⚠️  Tier 1 migration complete with {stats['errors']} errors")
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Migrate CORTEX Brain Tier 1 data to SQLite')
    parser.add_argument(
        '--db-path',
        default='cortex-brain/cortex-brain.db',
        help='Path to SQLite database (default: cortex-brain/cortex-brain.db)'
    )
    parser.add_argument(
        '--source-dir',
        default='cortex-brain',
        help='Path to cortex-brain directory (default: cortex-brain)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    project_root = get_project_root()
    db_path = project_root / args.db_path
    source_dir = project_root / args.source_dir
    
    # Run migration
    try:
        migrate_tier1(str(db_path), source_dir)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise


if __name__ == '__main__':
    main()
