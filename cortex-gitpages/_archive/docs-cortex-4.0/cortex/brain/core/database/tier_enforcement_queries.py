"""
Tier Enforcement Database Operations (AC-REM-002-06/07).

Implements:
1. Schema migration for tier_access_log table
2. Tier access logging to database
3. TIER-0 immutability constraint enforcement

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from cortex.brain.core.path_resolver import resolve_path
from cortex.brain.core.result import Result, Ok, Err


class TierEnforcementDatabase:
    """
    Database operations for tier enforcement (AC-REM-002-06/07).
    
    Provides:
    - Schema initialization (tier_access_log table)
    - Per-turn tier access logging
    - TIER-0 immutability constraint enforcement via triggers
    """
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialize tier enforcement database manager.
        
        Args:
            db_path: Path to governance.db (default: standard location)
        """
        if db_path:
            self.db_path = db_path
        else:
            # Use standard governance database location
            path_result = resolve_path("cortex_brain", "state", "governance.db")
            self.db_path = path_result
        
        self.logger = logging.getLogger(__name__)
    
    def initialize_schema(self) -> Result[None]:
        """
        Initialize tier enforcement schema in governance.db.
        
        Creates:
        - tier_access_log table
        - Indexes for performance
        - Trigger for TIER-0 immutability
        - Views for analysis
        
        Returns:
            Ok(None) if successful, Err(message) otherwise
        
        Implementation for AC-REM-002-06.
        """
        try:
            # Load SQL schema
            schema_path = resolve_path(
                "src", "core", "database", "tier_enforcement_schema.sql"
            )
            
            if not Path(schema_path).exists():
                return Err(f"Schema file not found: {schema_path}")
            
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Connect to database and execute schema
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Execute all SQL statements using executescript()
                # This handles comments, multiline statements, and triggers properly
                cursor.executescript(schema_sql)
                
                conn.commit()
                self.logger.info("Tier enforcement schema initialized successfully")
                return Ok(None)
            
            finally:
                conn.close()
        
        except sqlite3.Error as e:
            error_msg = f"Database error initializing tier enforcement schema: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)
        
        except Exception as e:
            error_msg = f"Error initializing tier enforcement schema: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)
    
    def log_tier_access(
        self,
        turn_number: int,
        orchestrator_id: str,
        rule_id: str,
        access_type: str,
        decision: str = "ALLOWED",
        violation_reason: Optional[str] = None
    ) -> Result[None]:
        """
        Log per-turn tier access to database.
        
        Records tier access attempts for governance enforcement:
        - DECLARE: Orchestrator declares tier access at initialization
        - ACCESS: Normal access to declared tier
        - ATTEMPT_VIOLATION: Attempt to access undeclared tier (denied)
        
        Args:
            turn_number: Current turn number
            orchestrator_id: ID of accessing orchestrator
            rule_id: ID of rule being accessed
            access_type: Type of access (DECLARE/ACCESS/ATTEMPT_VIOLATION)
            decision: Allow/Deny decision
            violation_reason: Reason for denial (if denied)
        
        Returns:
            Ok(None) if logged successfully, Err(message) otherwise
        
        Implementation for AC-REM-002-07.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Insert tier access log entry
                cursor.execute(
                    """
                    INSERT INTO tier_access_log
                    (turn_number, orchestrator_id, rule_id, access_type, decision, violation_reason, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        turn_number,
                        orchestrator_id,
                        rule_id,
                        access_type,
                        decision,
                        violation_reason,
                        datetime.now().isoformat()
                    )
                )
                
                conn.commit()
                return Ok(None)
            
            finally:
                conn.close()
        
        except sqlite3.IntegrityError as e:
            # Ignore duplicates (same turn/orch/rule combination already logged)
            if "UNIQUE constraint failed" in str(e):
                return Ok(None)
            
            error_msg = f"Integrity error logging tier access: {str(e)}"
            self.logger.warning(error_msg)
            return Err(error_msg)
        
        except Exception as e:
            error_msg = f"Error logging tier access: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)
    
    def get_tier_access_summary(
        self,
        turn_number: int,
        orchestrator_id: str
    ) -> Result[Dict[str, Any]]:
        """
        Get summary of tier access for turn and orchestrator.
        
        Returns:
            Dict with counts of allowed/denied accesses, violation details
        
        Used for governance auditing and debugging.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Query access summary
                cursor.execute(
                    """
                    SELECT
                        total_accesses,
                        allowed_count,
                        denied_count,
                        declarations,
                        accesses,
                        violations
                    FROM tier_access_summary
                    WHERE turn_number = ? AND orchestrator_id = ?
                    """,
                    (turn_number, orchestrator_id)
                )
                
                row = cursor.fetchone()
                
                if row:
                    return Ok({
                        "total_accesses": row[0],
                        "allowed": row[1],
                        "denied": row[2],
                        "declarations": row[3],
                        "accesses": row[4],
                        "violations": row[5]
                    })
                else:
                    return Ok({
                        "total_accesses": 0,
                        "allowed": 0,
                        "denied": 0,
                        "declarations": 0,
                        "accesses": 0,
                        "violations": 0
                    })
            
            finally:
                conn.close()
        
        except Exception as e:
            error_msg = f"Error querying tier access summary: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)
    
    def get_tier0_violations(self) -> Result[list]:
        """
        Get all TIER-0 immutability violations.
        
        Returns:
            List of violation records from tier0_immutability_violations view
        """
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM tier0_immutability_violations ORDER BY timestamp DESC")
                
                violations = []
                for row in cursor.fetchall():
                    violations.append({
                        "turn_number": row[0],
                        "orchestrator_id": row[1],
                        "rule_id": row[2],
                        "violation_reason": row[3],
                        "timestamp": row[4]
                    })
                
                return Ok(violations)
            
            finally:
                conn.close()
        
        except Exception as e:
            error_msg = f"Error querying TIER-0 violations: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)
    
    def verify_schema_exists(self) -> Result[bool]:
        """
        Verify tier enforcement schema tables exist.
        
        Returns:
            Ok(True) if schema exists, Ok(False) if missing, Err on error
        """
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Check if tier_access_log table exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='tier_access_log'"
                )
                
                exists = cursor.fetchone() is not None
                return Ok(exists)
            
            finally:
                conn.close()
        
        except Exception as e:
            error_msg = f"Error verifying tier enforcement schema: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)
