"""
CORTEX 3.0 - Tier 1 Migration: Add Conversation Import Support

Adds columns to support manual conversation import (Channel 2 of dual-channel memory):
- conversation_type: Distinguishes between live conversations and imported ones
- import_source: Tracks where imported conversation came from
- quality_score: Semantic quality rating (0-100)
- semantic_elements: JSON of extracted semantic elements

This enables CORTEX 3.0's dual-channel memory system:
- Channel 1: Ambient daemon (execution-focused, automatic)
- Channel 2: Manual conversation import (strategy-focused, user-driven)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def migrate_add_conversation_import(db_path: str):
    """
    Add conversation import support to Tier 1 database.
    
    Args:
        db_path: Path to tier1-working-memory.db
    """
    db = Path(db_path)
    
    if not db.exists():
        print(f"❌ Database not found: {db_path}")
        print(f"   Please ensure Tier 1 database exists before running migration.")
        return False
    
    print(f"🔄 CORTEX 3.0 Migration: Add Conversation Import Support")
    print(f"   Database: {db_path}")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='conversations'
        """)
        
        if not cursor.fetchone():
            print("❌ Conversations table not found!")
            print("   Please run base Tier 1 migration first.")
            conn.close()
            return False
        
        print("✅ Found conversations table")
        print()
        
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'conversation_type' in columns:
            print("⚠️  Migration already applied - conversation_type column exists")
            print("   Skipping duplicate migration.")
            conn.close()
            return True
        
        print("📝 Adding new columns...")
        print()
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        try:
            # Add conversation_type column
            print("   • Adding conversation_type column (default: 'live')")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN conversation_type TEXT DEFAULT 'live'
            """)
            
            # Add import_source column
            print("   • Adding import_source column (tracks import file)")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN import_source TEXT
            """)
            
            # Add quality_score column
            print("   • Adding quality_score column (0-100 semantic quality)")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN quality_score INTEGER DEFAULT 0
            """)
            
            # Add semantic_elements column
            print("   • Adding semantic_elements column (JSON metadata)")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN semantic_elements TEXT
            """)
            
            # Commit transaction
            conn.commit()
            
            print()
            print("✅ Migration completed successfully!")
            print()
            print("📊 New Schema:")
            print("   conversations table now supports:")
            print("   - conversation_type: 'live' | 'imported'")
            print("   - import_source: path to source file")
            print("   - quality_score: 0-100 (semantic value)")
            print("   - semantic_elements: JSON (challenges, phases, decisions)")
            print()
            print("🎉 CORTEX 3.0 Channel 2 (Manual Import) ready!")
            
            return True
            
        except Exception as e:
            # Rollback on error
            conn.rollback()
            print(f"❌ Migration failed: {e}")
            print("   Database rolled back to previous state.")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()


def verify_migration(db_path: str):
    """
    Verify migration was applied correctly.
    
    Args:
        db_path: Path to database
        
    Returns:
        True if verified
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type
        
        required_columns = {
            'conversation_type': 'TEXT',
            'import_source': 'TEXT',
            'quality_score': 'INTEGER',
            'semantic_elements': 'TEXT'
        }
        
        missing = []
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                missing.append(col_name)
        
        if missing:
            print(f"❌ Verification failed - missing columns: {missing}")
            return False
        
        print("✅ Migration verified - all columns present")
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migration_add_conversation_import.py <path_to_tier1_db>")
        print()
        print("Example:")
        print("  python migration_add_conversation_import.py cortex-brain/tier1-working-memory.db")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    # Run migration
    success = migrate_add_conversation_import(db_path)
    
    if success:
        # Verify
        verify_migration(db_path)
        sys.exit(0)
    else:
        sys.exit(1)
