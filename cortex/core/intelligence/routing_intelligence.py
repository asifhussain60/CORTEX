"""
Routing Intelligence Module

Tracks routing decisions vs outcomes to detect misrouting patterns.

AC-INT-RT-001-01: Record routing outcomes
AC-INT-RT-001-02: Calculate routing accuracy  
AC-INT-RT-003-03: Detect misrouting patterns
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from cortex.brain.core.result import Result, Ok, Err


class RoutingAnalyzer:
    """
    Analyzes routing decisions to identify misrouting patterns.
    
    Tracks whether routing decisions lead to successful outcomes
    or require fallback to different handlers.
    """
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialize routing analyzer.
        
        Args:
            db_path: Path to SQLite database (uses default if None)
        """
        if db_path is None:
            from cortex.core.path_resolver import resolve_path, get_project_root
            db_path = str(resolve_path("cortex_brain/state/governance.db"))
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize routing_outcomes table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routing_outcomes (
                id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                decided_handler TEXT NOT NULL,
                actual_handler TEXT NOT NULL,
                success INTEGER NOT NULL,
                reason TEXT,
                duration_ms INTEGER,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create indices for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_routing_timestamp 
            ON routing_outcomes(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_routing_handlers 
            ON routing_outcomes(decided_handler, actual_handler)
        """)
        
        conn.commit()
        conn.close()
    
    def record_routing_outcome(
        self,
        decision_id: str,
        decided_handler: str,
        actual_handler: str,
        success: bool,
        reason: str,
        duration_ms: int
    ) -> Result[str]:
        """
        Record outcome of a routing decision.
        
        AC-INT-RT-001-01: Stores routing outcome to database
        
        Args:
            decision_id: ID of the routing decision from audit trail
            decided_handler: Handler selected by router
            actual_handler: Handler that actually executed (may differ if fallback)
            success: Whether routing was successful
            reason: Explanation of outcome
            duration_ms: Time taken to execute
            
        Returns:
            Success message or error
        """
        try:
            outcome_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO routing_outcomes 
                (id, decision_id, decided_handler, actual_handler, success, reason, duration_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                outcome_id,
                decision_id,
                decided_handler,
                actual_handler,
                1 if success else 0,
                reason,
                duration_ms,
                timestamp
            ))
            
            conn.commit()
            conn.close()
            
            return Ok(f"Routing outcome recorded: {outcome_id}")
        
        except Exception as e:
            return Err(f"Failed to record routing outcome: {str(e)}")
    
    def get_routing_accuracy(
        self,
        handler_name: Optional[str] = None,
        days: int = 7
    ) -> Result[Dict[str, Any]]:
        """
        Calculate routing accuracy metrics.
        
        AC-INT-RT-001-02: Calculates routing success rate
        
        Args:
            handler_name: Optional filter for specific handler
            days: Time window in days
            
        Returns:
            Dict with total_decisions, successful_routes, accuracy_rate
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if handler_name:
                cursor.execute("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN decided_handler = actual_handler THEN 1 ELSE 0 END) as successful
                    FROM routing_outcomes
                    WHERE timestamp >= ? AND decided_handler = ?
                """, (cutoff_date, handler_name))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN decided_handler = actual_handler THEN 1 ELSE 0 END) as successful
                    FROM routing_outcomes
                    WHERE timestamp >= ?
                """, (cutoff_date,))
            
            row = cursor.fetchone()
            conn.close()
            
            total = row[0] if row else 0
            successful = row[1] if row and row[1] else 0
            accuracy = successful / total if total > 0 else 0.0
            
            result = {
                "total_decisions": total,
                "successful_routes": successful,
                "accuracy_rate": accuracy
            }
            
            if handler_name:
                result["handler_name"] = handler_name
            
            return Ok(result)
        
        except Exception as e:
            return Err(f"Failed to calculate routing accuracy: {str(e)}")
    
    def detect_misrouting_patterns(
        self,
        days: int = 7,
        min_occurrences: int = 2
    ) -> Result[List[Dict[str, Any]]]:
        """
        Identify recurring misrouting patterns.
        
        AC-INT-RT-001-03: Detects patterns where decided != actual
        
        Args:
            days: Time window in days
            min_occurrences: Minimum pattern occurrences to report
            
        Returns:
            List of patterns with handler pairs and occurrence counts
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    decided_handler,
                    actual_handler,
                    COUNT(*) as occurrences,
                    MIN(timestamp) as first_seen,
                    MAX(timestamp) as last_seen,
                    reason
                FROM routing_outcomes
                WHERE timestamp >= ?
                  AND decided_handler != actual_handler
                GROUP BY decided_handler, actual_handler
                HAVING COUNT(*) >= ?
                ORDER BY occurrences DESC
            """, (cutoff_date, min_occurrences))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "decided_handler": row[0],
                    "actual_handler": row[1],
                    "occurrences": row[2],
                    "first_seen": row[3],
                    "last_seen": row[4],
                    "reason": row[5]
                })
            
            conn.close()
            
            return Ok(patterns)
        
        except Exception as e:
            return Err(f"Failed to detect misrouting patterns: {str(e)}")
