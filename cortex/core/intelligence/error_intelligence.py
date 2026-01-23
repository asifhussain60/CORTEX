"""
Error Pattern Intelligence Module

Aggregates errors to detect recurring patterns and brittle handlers.

AC-INT-ERR-003-01: Record error occurrences
AC-INT-ERR-003-02: Detect error patterns
AC-INT-ERR-003-03: Error frequency by handler
AC-INT-ERR-003-04: Detect new errors
"""

import sqlite3
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from cortex.brain.core.result import Result, Ok, Err


class ErrorAnalyzer:
    """
    Analyzes error occurrences to identify patterns and brittle components.
    
    Tracks error types, handlers, and operation contexts to detect
    recurring failures and systemic issues.
    """
    
    SENSITIVE_KEYS = ["password", "api_key", "token", "secret", "auth"]
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialize error analyzer.
        
        Args:
            db_path: Path to SQLite database (uses default if None)
        """
        if db_path is None:
            from cortex.core.path_resolver import resolve_path
            db_path = str(resolve_path("cortex_brain/state/governance.db"))
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize error_occurrences table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_occurrences (
                id TEXT PRIMARY KEY,
                error_type TEXT NOT NULL,
                handler TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                context TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create indices for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_error_type 
            ON error_occurrences(error_type, handler, operation_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_error_timestamp 
            ON error_occurrences(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_error_handler 
            ON error_occurrences(handler, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def record_error(
        self,
        error_type: str,
        handler: str,
        operation_type: str,
        context: Dict[str, Any]
    ) -> Result[str]:
        """
        Record an error occurrence.
        
        AC-INT-ERR-003-01: Stores error with sanitized context
        
        Args:
            error_type: Type/class of error (e.g., ValueError, TypeError)
            handler: Handler where error occurred
            operation_type: Operation being performed
            context: Error context (will be sanitized)
            
        Returns:
            Success message or error
        """
        try:
            error_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            # Sanitize sensitive data from context
            sanitized_context = self._sanitize_context(context)
            context_json = json.dumps(sanitized_context)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO error_occurrences 
                (id, error_type, handler, operation_type, context, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                error_id,
                error_type,
                handler,
                operation_type,
                context_json,
                timestamp
            ))
            
            conn.commit()
            conn.close()
            
            return Ok(f"Error recorded: {error_id}")
        
        except Exception as e:
            return Err(f"Failed to record error: {str(e)}")
    
    def get_error_patterns(
        self,
        days: int = 7,
        min_occurrence: int = 3
    ) -> Result[List[Dict[str, Any]]]:
        """
        Identify recurring error patterns.
        
        AC-INT-ERR-003-02: Detects patterns meeting occurrence threshold
        
        Args:
            days: Time window in days
            min_occurrence: Minimum occurrences to be considered a pattern
            
        Returns:
            List of error patterns with counts and timestamps
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    error_type,
                    handler,
                    operation_type,
                    COUNT(*) as count,
                    MIN(timestamp) as first_seen,
                    MAX(timestamp) as last_seen
                FROM error_occurrences
                WHERE timestamp >= ?
                GROUP BY error_type, handler, operation_type
                HAVING COUNT(*) >= ?
                ORDER BY count DESC
            """, (cutoff_date, min_occurrence))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "error_type": row[0],
                    "handler": row[1],
                    "operation_type": row[2],
                    "count": row[3],
                    "first_seen": row[4],
                    "last_seen": row[5]
                })
            
            conn.close()
            
            return Ok(patterns)
        
        except Exception as e:
            return Err(f"Failed to detect error patterns: {str(e)}")
    
    def get_error_frequency_by_handler(
        self,
        days: int = 7
    ) -> Result[List[Dict[str, Any]]]:
        """
        Calculate error frequency grouped by handler.
        
        AC-INT-ERR-003-03: Handler brittleness metrics
        
        Args:
            days: Time window in days
            
        Returns:
            List of handlers with error counts, sorted by frequency
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    handler,
                    COUNT(*) as total_errors,
                    COUNT(DISTINCT error_type) as unique_error_types
                FROM error_occurrences
                WHERE timestamp >= ?
                GROUP BY handler
                ORDER BY total_errors DESC
            """, (cutoff_date,))
            
            frequencies = []
            for row in cursor.fetchall():
                frequencies.append({
                    "handler": row[0],
                    "total_errors": row[1],
                    "unique_error_types": row[2]
                })
            
            conn.close()
            
            return Ok(frequencies)
        
        except Exception as e:
            return Err(f"Failed to get error frequency by handler: {str(e)}")
    
    def detect_new_errors(
        self,
        recent_days: int = 7,
        baseline_days: int = 30
    ) -> Result[List[Dict[str, Any]]]:
        """
        Detect errors not seen in historical baseline.
        
        AC-INT-ERR-003-04: Identifies novel error types
        
        Args:
            recent_days: Recent period to check for new errors
            baseline_days: Historical baseline period
            
        Returns:
            List of new error types with first occurrence details
        """
        try:
            recent_cutoff = (datetime.utcnow() - timedelta(days=recent_days)).isoformat()
            baseline_cutoff = (datetime.utcnow() - timedelta(days=baseline_days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get error types from recent period
            cursor.execute("""
                SELECT DISTINCT error_type, handler, operation_type
                FROM error_occurrences
                WHERE timestamp >= ?
            """, (recent_cutoff,))
            recent_errors = cursor.fetchall()
            
            # Get error types from baseline period (before recent)
            cursor.execute("""
                SELECT DISTINCT error_type, handler, operation_type
                FROM error_occurrences
                WHERE timestamp >= ? AND timestamp < ?
            """, (baseline_cutoff, recent_cutoff))
            baseline_errors = {(row[0], row[1], row[2]) for row in cursor.fetchall()}
            
            # Find errors in recent that are NOT in baseline
            new_errors = []
            for error_type, handler, operation_type in recent_errors:
                if (error_type, handler, operation_type) not in baseline_errors:
                    # Get first occurrence
                    cursor.execute("""
                        SELECT MIN(timestamp)
                        FROM error_occurrences
                        WHERE error_type = ? AND handler = ? AND operation_type = ?
                    """, (error_type, handler, operation_type))
                    first_occurrence = cursor.fetchone()[0]
                    
                    new_errors.append({
                        "error_type": error_type,
                        "handler": handler,
                        "operation_type": operation_type,
                        "first_occurrence": first_occurrence
                    })
            
            conn.close()
            
            return Ok(new_errors)
        
        except Exception as e:
            return Err(f"Failed to detect new errors: {str(e)}")
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from error context.
        
        Args:
            context: Raw context dictionary
            
        Returns:
            Sanitized context with sensitive fields masked
        """
        sanitized = {}
        
        for key, value in context.items():
            # Check if key contains sensitive terms
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYS):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_context(value)
            else:
                # Truncate very long values to prevent DB bloat
                if isinstance(value, str) and len(value) > 500:
                    sanitized[key] = value[:500] + "...[truncated]"
                else:
                    sanitized[key] = value
        
        return sanitized
