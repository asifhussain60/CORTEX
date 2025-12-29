#!/usr/bin/env python3
"""
Analyze Conversation Storage Discrepancy
Compares active database vs JSONL archive
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

CORTEX_ROOT = Path(__file__).parent.parent
BRAIN_PATH = CORTEX_ROOT / "cortex-brain"

def analyze_database():
    """Analyze conversations.db"""
    print("📊 Analyzing conversations.db...")
    
    db_path = BRAIN_PATH / "tier1" / "conversations.db"
    if not db_path.exists():
        print("  ❌ Database not found")
        return None
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='conversations'")
    schema = cursor.fetchone()
    print(f"\n  Schema: {schema[0] if schema else 'Not found'}")
    
    # Get count and details
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total = cursor.fetchone()[0]
    
    # Get column names
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\n  Columns: {', '.join(columns)}")
    
    # Get all conversations
    cursor.execute(f"SELECT * FROM conversations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    conversations = []
    for row in rows:
        conv = dict(zip(columns, row))
        conversations.append(conv)
    
    conn.close()
    
    print(f"\n  ✅ Found {total} conversations in database")
    return conversations

def analyze_jsonl():
    """Analyze conversation-history.jsonl"""
    print("\n📋 Analyzing conversation-history.jsonl...")
    
    jsonl_path = BRAIN_PATH / "conversation-history.jsonl"
    if not jsonl_path.exists():
        print("  ❌ JSONL file not found")
        return None
    
    conversations = []
    with open(jsonl_path, 'r') as f:
        for line in f:
            if line.strip():
                conversations.append(json.loads(line))
    
    print(f"\n  ✅ Found {len(conversations)} conversations in JSONL")
    
    # Show sample
    if conversations:
        print("\n  Sample conversation:")
        sample = conversations[-1]
        print(f"    ID: {sample.get('conversation_id', 'N/A')}")
        print(f"    Date: {sample.get('timestamp', 'N/A')}")
        print(f"    Source: {sample.get('source', 'N/A')}")
        print(f"    Messages: {len(sample.get('messages', []))}")
    
    return conversations

def compare_storage():
    """Compare database vs JSONL storage"""
    print("\n" + "="*60)
    print("CONVERSATION STORAGE ANALYSIS")
    print("="*60)
    
    db_conversations = analyze_database()
    jsonl_conversations = analyze_jsonl()
    
    print("\n" + "="*60)
    print("COMPARISON")
    print("="*60)
    
    db_count = len(db_conversations) if db_conversations else 0
    jsonl_count = len(jsonl_conversations) if jsonl_conversations else 0
    
    print(f"\n  Database:  {db_count} conversations")
    print(f"  JSONL:     {jsonl_count} conversations")
    print(f"  Difference: {abs(db_count - jsonl_count)} conversations")
    
    if db_count < jsonl_count:
        print("\n  💡 EXPLANATION:")
        print("     The database contains only ACTIVE conversations (working memory).")
        print("     The JSONL contains ALL conversations (complete archive).")
        print("     This is expected - older conversations are archived/rotated.")
        print("\n  ✅ This is NORMAL BEHAVIOR for FIFO queue management.")
        print("     - Database: Active working memory (3-20 recent)")
        print("     - JSONL: Complete historical archive (all conversations)")
    elif db_count > jsonl_count:
        print("\n  ⚠️  WARNING: Database has MORE than JSONL!")
        print("     This suggests JSONL archiving may not be working.")
        print("     Recommendation: Check conversation capture automation.")
    else:
        print("\n  ℹ️  Counts match - both storage systems in sync.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    compare_storage()
