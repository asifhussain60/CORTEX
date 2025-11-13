"""
Database migration: Add session support to Tier 1.

Adds session tracking tables and enhances conversations table with session metadata.
CORTEX 3.0 feature: Session-based conversation boundaries.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys


def migrate_tier1_add_sessions(db_path: Path) -> bool:
    """
    Add session support to existing Tier 1 database.
    
    Changes:
    - Add sessions table
    - Add session_id, last_activity, workflow_state columns to conversations
    - Add indexes for session queries
    - Backfill existing conversations with default session
    
    Args:
        db_path: Path to Tier 1 SQLite database
    
    Returns:
        True if migration successful, False otherwise
    """
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"[ERROR] Database not found: {db_path}")
        return False
    
    print(f"[MIGRATION] Starting session support migration for: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Step 1: Create sessions table
        print("[MIGRATION] Creating sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                workspace_path TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                conversation_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                last_activity TEXT NOT NULL
            )
        """)
        
        # Step 2: Add session-related columns to conversations
        print("[MIGRATION] Adding session columns to conversations table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(conversations)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        if 'session_id' not in existing_columns:
            cursor.execute("ALTER TABLE conversations ADD COLUMN session_id TEXT")
        
        if 'last_activity' not in existing_columns:
            cursor.execute("ALTER TABLE conversations ADD COLUMN last_activity TEXT")
        
        if 'workflow_state' not in existing_columns:
            cursor.execute("ALTER TABLE conversations ADD COLUMN workflow_state TEXT")
        
        # Step 3: Create indexes
        print("[MIGRATION] Creating indexes...")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_active 
            ON sessions(is_active, workspace_path)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_last_activity 
            ON sessions(last_activity DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_session 
            ON conversations(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_last_activity 
            ON conversations(last_activity DESC)
        """)
        
        # Step 4: Backfill existing conversations with default session
        print("[MIGRATION] Backfilling existing conversations...")
        
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE session_id IS NULL")
        null_session_count = cursor.fetchone()[0]
        
        if null_session_count > 0:
            # Create default legacy session
            now = datetime.now().isoformat()
            default_session_id = "session_legacy_migration"
            
            cursor.execute("""
                INSERT OR IGNORE INTO sessions 
                (session_id, workspace_path, start_time, last_activity, is_active, conversation_count)
                VALUES (?, 'legacy_workspace', ?, ?, 0, ?)
            """, (default_session_id, now, now, null_session_count))
            
            # Update conversations with null session_id
            cursor.execute("""
                UPDATE conversations 
                SET session_id = ?,
                    last_activity = updated_at,
                    workflow_state = 'COMPLETE'
                WHERE session_id IS NULL
            """, (default_session_id,))
            
            print(f"[MIGRATION] Backfilled {null_session_count} conversations with legacy session")
        
        conn.commit()
        print("[MIGRATION] ✅ Session support migration complete!")
        
        # Verification
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE session_id IS NOT NULL")
        linked_conv_count = cursor.fetchone()[0]
        
        print(f"[MIGRATION] Verification: {session_count} sessions, {linked_conv_count} linked conversations")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run migration from command line."""
    if len(sys.argv) < 2:
        print("Usage: python migration_add_sessions.py <path_to_tier1_db>")
        print("Example: python migration_add_sessions.py cortex-brain/tier1/working_memory.db")
        sys.exit(1)
    
    db_path = Path(sys.argv[1])
    success = migrate_tier1_add_sessions(db_path)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
