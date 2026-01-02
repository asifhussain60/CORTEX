"""
Migration: Add Orchestrator Tracking to Tier 1 Sessions.

Adds three columns to support cross-session context middleware:
- orchestrator_used: Which orchestrator handled the session
- primary_intent: User's main intent for the session
- artifacts_generated: JSON array of artifact IDs

Part of CORTEX v5 Phase 4.5: Cross-Session Context Middleware.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
from pathlib import Path
from typing import Optional
import logging


def migrate(db_path: Optional[Path] = None) -> bool:
    """
    Add orchestrator tracking columns to Tier 1 sessions table.
    
    Args:
        db_path: Path to working_memory.db (defaults to standard location)
    
    Returns:
        True if migration successful, False otherwise
    """
    if not db_path:
        db_path = Path("cortex-brain/tier1/working_memory.db")
    
    logger = logging.getLogger("cortex.tier1.migration")
    
    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(sessions)")
        columns = {row[1] for row in cursor.fetchall()}
        
        migrations_needed = []
        
        if "orchestrator_used" not in columns:
            migrations_needed.append("orchestrator_used")
        
        if "primary_intent" not in columns:
            migrations_needed.append("primary_intent")
        
        if "artifacts_generated" not in columns:
            migrations_needed.append("artifacts_generated")
        
        if not migrations_needed:
            logger.info("Migration already applied - all columns exist")
            conn.close()
            return True
        
        # Apply migrations
        logger.info(f"Applying migrations: {migrations_needed}")
        
        if "orchestrator_used" in migrations_needed:
            cursor.execute("ALTER TABLE sessions ADD COLUMN orchestrator_used TEXT")
            logger.info("✓ Added orchestrator_used column")
        
        if "primary_intent" in migrations_needed:
            cursor.execute("ALTER TABLE sessions ADD COLUMN primary_intent TEXT")
            logger.info("✓ Added primary_intent column")
        
        if "artifacts_generated" in migrations_needed:
            cursor.execute("ALTER TABLE sessions ADD COLUMN artifacts_generated TEXT")
            logger.info("✓ Added artifacts_generated column")
        
        # Add index for orchestrator lookups
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_orchestrator 
                ON sessions(orchestrator_used)
            """)
            logger.info("✓ Created idx_sessions_orchestrator index")
        except sqlite3.OperationalError as e:
            logger.warning(f"Index creation skipped: {e}")
        
        conn.commit()
        logger.info(f"✅ Migration complete: {len(migrations_needed)} columns added")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False
    
    finally:
        conn.close()
    
    return True


def rollback(db_path: Optional[Path] = None) -> bool:
    """
    Rollback orchestrator tracking migration (SQLite doesn't support DROP COLUMN easily).
    
    Note: This recreates the table without the new columns.
    Use with caution - backs up existing data first.
    """
    if not db_path:
        db_path = Path("cortex-brain/tier1/working_memory.db")
    
    logger = logging.getLogger("cortex.tier1.migration")
    logger.warning("Rollback requested - this will recreate sessions table")
    
    # For safety, this is intentionally not implemented
    # SQLite ALTER TABLE DROP COLUMN is complex and risky
    logger.error("Rollback not implemented - manual intervention required")
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = migrate()
    exit(0 if success else 1)
