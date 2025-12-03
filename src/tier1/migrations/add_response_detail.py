"""
Database Migration: Add response_detail column to user_profile
Version: 3.3.0
Date: 2025-12-02
Purpose: Support response detail preference (concise/balanced/verbose)
Part of: Phase 5.3 - User Profile Enhancement
"""

import sqlite3
from pathlib import Path
from typing import Optional
import json


def migrate_add_response_detail(db_path: Optional[Path] = None) -> bool:
    """
    Add response_detail column to user_profile table.
    
    Migration Steps:
    1. Add response_detail column (default: 'balanced')
    2. Infer values for existing users based on interaction_mode
    3. Create index for performance
    
    Args:
        db_path: Path to working_memory.db (if None, uses default)
    
    Returns:
        True if migration successful, False otherwise
    """
    if db_path is None:
        db_path = Path("cortex-brain/tier1/working_memory.db")
    
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user_profile)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'response_detail' in columns:
            print("✅ response_detail column already exists")
            conn.close()
            return True
        
        print("📊 Adding response_detail column...")
        
        # Step 1: Add column with default value
        cursor.execute("""
            ALTER TABLE user_profile 
            ADD COLUMN response_detail TEXT 
            CHECK(response_detail IN ('concise', 'balanced', 'verbose')) 
            DEFAULT 'balanced'
        """)
        
        # Step 2: Infer values for existing users based on interaction_mode
        # autonomous → concise
        # guided → balanced
        # educational → verbose
        # pair → balanced
        
        cursor.execute("""
            UPDATE user_profile 
            SET response_detail = CASE 
                WHEN interaction_mode = 'autonomous' THEN 'concise'
                WHEN interaction_mode = 'educational' THEN 'verbose'
                WHEN interaction_mode = 'guided' THEN 'balanced'
                WHEN interaction_mode = 'pair' THEN 'balanced'
                ELSE 'balanced'
            END
            WHERE response_detail IS NULL OR response_detail = 'balanced'
        """)
        
        rows_updated = cursor.rowcount
        
        # Step 3: Create index for performance (optional but recommended)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profile_response_detail 
            ON user_profile(response_detail)
        """)
        
        conn.commit()
        
        print(f"✅ Migration complete:")
        print(f"   - response_detail column added")
        print(f"   - {rows_updated} existing profiles updated with inferred values")
        print(f"   - Performance index created")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def rollback_response_detail(db_path: Optional[Path] = None) -> bool:
    """
    Rollback migration by removing response_detail column.
    
    NOTE: SQLite doesn't support DROP COLUMN directly.
    This creates a new table without the column and copies data.
    
    Args:
        db_path: Path to working_memory.db
    
    Returns:
        True if rollback successful, False otherwise
    """
    if db_path is None:
        db_path = Path("cortex-brain/tier1/working_memory.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Rolling back response_detail migration...")
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(user_profile)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'response_detail' not in columns:
            print("✅ response_detail column doesn't exist (already rolled back)")
            conn.close()
            return True
        
        # SQLite workaround for DROP COLUMN: Create new table, copy data, rename
        cursor.execute("""
            CREATE TABLE user_profile_temp (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                interaction_mode TEXT NOT NULL CHECK(interaction_mode IN ('autonomous', 'guided', 'educational', 'pair')) DEFAULT 'guided',
                experience_level TEXT NOT NULL CHECK(experience_level IN ('junior', 'mid', 'senior', 'expert')) DEFAULT 'mid',
                tech_stack_preference TEXT DEFAULT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                persistent_flag BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        
        # Copy data (excluding response_detail)
        cursor.execute("""
            INSERT INTO user_profile_temp 
            SELECT id, interaction_mode, experience_level, tech_stack_preference, 
                   created_at, last_updated, persistent_flag
            FROM user_profile
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE user_profile")
        
        # Rename new table
        cursor.execute("ALTER TABLE user_profile_temp RENAME TO user_profile")
        
        # Recreate index
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_single_profile ON user_profile(id)
        """)
        
        conn.commit()
        
        print("✅ Rollback complete: response_detail column removed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False


if __name__ == '__main__':
    # Run migration
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        success = rollback_response_detail()
    else:
        success = migrate_add_response_detail()
    
    sys.exit(0 if success else 1)
