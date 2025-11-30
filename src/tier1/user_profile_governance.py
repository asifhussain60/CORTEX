"""
User Profile Governance Extensions - Sprint 1 Day 3

Adds governance-related fields to user profile system for
first-time acknowledgment tracking.

SCHEMA ADDITIONS:
- acknowledged_rulebook: BOOLEAN flag (0/1)
- rulebook_acknowledged_at: TIMESTAMP of acknowledgment
- onboarding_completed: BOOLEAN flag for full onboarding status

MIGRATION:
This module provides safe migration that:
1. Checks if columns already exist
2. Adds columns only if missing
3. Sets sensible defaults (acknowledged=0 for existing users)
4. Preserves all existing data

USAGE:
    from src.tier1.user_profile_governance import UserProfileGovernance
    
    governance = UserProfileGovernance()
    
    # Check if user has acknowledged rulebook
    if not governance.has_acknowledged_rulebook():
        # Show onboarding flow
        pass
    
    # Mark as acknowledged
    governance.mark_rulebook_acknowledged()

SPRINT 1 DAY 3-4: First-Time Acknowledgment
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class UserProfileGovernance:
    """
    Manages governance-related aspects of user profile.
    
    Handles rulebook acknowledgment, onboarding completion,
    and governance flag tracking.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize UserProfileGovernance.
        
        Args:
            db_path: Path to user profile database. If None, uses default.
        """
        if db_path is None:
            db_path = Path("cortex-brain/tier1/working_memory.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure base table exists
        self._init_base_table()
        
        # Run migration to add governance columns
        self._migrate_governance_columns()
        
        logger.info(f"UserProfileGovernance initialized (db: {self.db_path})")
    
    def _init_base_table(self):
        """
        Initialize base user_profile table if it doesn't exist.
        
        Creates minimal schema compatible with user_profile_manager.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    interaction_mode TEXT NOT NULL CHECK(interaction_mode IN ('autonomous', 'guided', 'educational', 'pair')) DEFAULT 'guided',
                    experience_level TEXT NOT NULL CHECK(experience_level IN ('junior', 'mid', 'senior', 'expert')) DEFAULT 'mid',
                    tech_stack_preference TEXT DEFAULT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    persistent_flag BOOLEAN NOT NULL DEFAULT 1
                )
            """)
            
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_single_profile ON user_profile(id)
            """)
            
            # Ensure single row exists
            cursor.execute("SELECT COUNT(*) FROM user_profile")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO user_profile (id, interaction_mode, experience_level)
                    VALUES (1, 'guided', 'mid')
                """)
            
            conn.commit()
            conn.close()
            
            logger.info("Base user_profile table initialized")
        
        except Exception as e:
            logger.error(f"Failed to initialize base table: {e}")
            raise
    
    def _migrate_governance_columns(self):
        """
        Safely add governance columns to user_profile table.
        
        Checks if columns exist before adding to avoid SQL errors.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check existing columns
            cursor.execute("PRAGMA table_info(user_profile)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            # Add acknowledged_rulebook column if missing
            if "acknowledged_rulebook" not in existing_columns:
                cursor.execute("""
                    ALTER TABLE user_profile 
                    ADD COLUMN acknowledged_rulebook INTEGER DEFAULT 0
                """)
                logger.info("Added acknowledged_rulebook column to user_profile")
            
            # Add rulebook_acknowledged_at column if missing
            if "rulebook_acknowledged_at" not in existing_columns:
                cursor.execute("""
                    ALTER TABLE user_profile 
                    ADD COLUMN rulebook_acknowledged_at TIMESTAMP DEFAULT NULL
                """)
                logger.info("Added rulebook_acknowledged_at column to user_profile")
            
            # Add onboarding_completed column if missing
            if "onboarding_completed" not in existing_columns:
                cursor.execute("""
                    ALTER TABLE user_profile 
                    ADD COLUMN onboarding_completed INTEGER DEFAULT 0
                """)
                logger.info("Added onboarding_completed column to user_profile")
            
            conn.commit()
            conn.close()
            
            logger.debug("Governance column migration completed successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Failed to migrate governance columns: {e}")
            raise
    
    def has_acknowledged_rulebook(self) -> bool:
        """
        Check if user has acknowledged the rulebook.
        
        Returns:
            True if acknowledged, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT acknowledged_rulebook 
                FROM user_profile 
                WHERE id = 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                # No profile exists, user hasn't acknowledged
                return False
            
            return bool(row[0])
        
        except sqlite3.Error as e:
            logger.error(f"Failed to check rulebook acknowledgment: {e}")
            return False
    
    def mark_rulebook_acknowledged(self) -> bool:
        """
        Mark that user has acknowledged the rulebook.
        
        Sets acknowledged_rulebook=1 and records timestamp.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Check if profile exists
            cursor.execute("SELECT COUNT(*) FROM user_profile WHERE id = 1")
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profile 
                    SET acknowledged_rulebook = 1,
                        rulebook_acknowledged_at = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = 1
                """, (now,))
            else:
                # Create new profile with defaults
                cursor.execute("""
                    INSERT INTO user_profile (
                        id, 
                        interaction_mode, 
                        experience_level, 
                        acknowledged_rulebook,
                        rulebook_acknowledged_at
                    )
                    VALUES (1, 'guided', 'mid', 1, ?)
                """, (now,))
            
            conn.commit()
            conn.close()
            
            logger.info("Rulebook acknowledgment recorded successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to mark rulebook as acknowledged: {e}")
            return False
    
    def get_acknowledgment_status(self) -> Dict[str, Any]:
        """
        Get detailed acknowledgment status for user.
        
        Returns:
            Dict with keys:
                - acknowledged: Boolean flag
                - acknowledged_at: Timestamp string or None
                - onboarding_completed: Boolean flag
                - needs_onboarding: Boolean (True if first-time user)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    acknowledged_rulebook,
                    rulebook_acknowledged_at,
                    onboarding_completed
                FROM user_profile 
                WHERE id = 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                # New user - needs onboarding
                return {
                    "acknowledged": False,
                    "acknowledged_at": None,
                    "onboarding_completed": False,
                    "needs_onboarding": True
                }
            
            acknowledged, acknowledged_at, onboarding_completed = row
            
            return {
                "acknowledged": bool(acknowledged),
                "acknowledged_at": acknowledged_at,
                "onboarding_completed": bool(onboarding_completed),
                "needs_onboarding": not bool(acknowledged)
            }
        
        except sqlite3.Error as e:
            logger.error(f"Failed to get acknowledgment status: {e}")
            return {
                "acknowledged": False,
                "acknowledged_at": None,
                "onboarding_completed": False,
                "needs_onboarding": True,
                "error": str(e)
            }
    
    def mark_onboarding_completed(self) -> bool:
        """
        Mark that user has completed full onboarding flow.
        
        This is called after all 3 steps of onboarding are complete.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if profile exists
            cursor.execute("SELECT COUNT(*) FROM user_profile WHERE id = 1")
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profile 
                    SET onboarding_completed = 1,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = 1
                """)
            else:
                # Create new profile with defaults
                cursor.execute("""
                    INSERT INTO user_profile (
                        id, 
                        interaction_mode, 
                        experience_level, 
                        onboarding_completed
                    )
                    VALUES (1, 'guided', 'mid', 1)
                """)
            
            conn.commit()
            conn.close()
            
            logger.info("Onboarding completion recorded successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to mark onboarding as completed: {e}")
            return False
    
    def reset_acknowledgment(self) -> bool:
        """
        Reset acknowledgment status (for testing or re-onboarding).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_profile 
                SET acknowledged_rulebook = 0,
                    rulebook_acknowledged_at = NULL,
                    onboarding_completed = 0,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Acknowledgment status reset successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to reset acknowledgment: {e}")
            return False
