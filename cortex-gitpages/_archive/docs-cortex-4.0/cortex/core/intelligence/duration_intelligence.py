"""
Duration Intelligence Module

Builds duration baselines and detects slow operations.

AC-INT-DUR-002-01: Record operation durations
AC-INT-DUR-002-02: Calculate duration baselines (p50/p95/p99)
AC-INT-DUR-002-03: Detect slow operations
AC-INT-DUR-002-04: Handler average durations
"""

import sqlite3
import uuid
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from cortex.brain.core.result import Result, Ok, Err


class DurationAnalyzer:
    """
    Analyzes operation durations to establish baselines and detect slowness.
    
    Tracks p50, p95, p99 percentiles per operation type to identify
    performance degradation early.
    """
    
    VALID_OPERATION_TYPES = ["implement", "fix", "refactor", "discovery", "validation"]
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialize duration analyzer.
        
        Args:
            db_path: Path to SQLite database (uses default if None)
        """
        if db_path is None:
            from cortex.core.path_resolver import PathResolver
            resolver = PathResolver()
            db_path = str(resolver.resolve_path("cortex_brain/state/governance.db"))
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize operation_durations table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_durations (
                id TEXT PRIMARY KEY,
                operation_type TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                handler_name TEXT NOT NULL,
                success INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create indices for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_duration_operation 
            ON operation_durations(operation_type, timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_duration_handler 
            ON operation_durations(handler_name, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def record_operation_duration(
        self,
        operation_type: str,
        duration_ms: int,
        handler_name: str,
        success: bool
    ) -> Result[str]:
        """
        Record duration of an operation.
        
        AC-INT-DUR-002-01: Stores operation duration to database
        
        Args:
            operation_type: Type of operation (implement, fix, refactor, etc.)
            duration_ms: Duration in milliseconds
            handler_name: Handler that executed the operation
            success: Whether operation succeeded
            
        Returns:
            Success message or error
        """
        try:
            duration_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO operation_durations 
                (id, operation_type, duration_ms, handler_name, success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                duration_id,
                operation_type,
                duration_ms,
                handler_name,
                1 if success else 0,
                timestamp
            ))
            
            conn.commit()
            conn.close()
            
            return Ok(f"Operation duration recorded: {duration_id}")
        
        except Exception as e:
            return Err(f"Failed to record operation duration: {str(e)}")
    
    def get_duration_baseline(
        self,
        operation_type: str,
        days: int = 30
    ) -> Result[Dict[str, Any]]:
        """
        Calculate duration baseline statistics.
        
        AC-INT-DUR-002-02: Calculates p50, p95, p99, min, max, mean
        
        Args:
            operation_type: Filter by operation type
            days: Time window in days
            
        Returns:
            Dict with percentiles and statistics
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT duration_ms
                FROM operation_durations
                WHERE operation_type = ? AND timestamp >= ?
                ORDER BY duration_ms
            """, (operation_type, cutoff_date))
            
            durations = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not durations:
                return Ok({
                    "operation_type": operation_type,
                    "count": 0,
                    "p50": 0,
                    "p95": 0,
                    "p99": 0,
                    "min": 0,
                    "max": 0,
                    "mean": 0
                })
            
            baseline = {
                "operation_type": operation_type,
                "count": len(durations),
                "p50": self._percentile(durations, 50),
                "p95": self._percentile(durations, 95),
                "p99": self._percentile(durations, 99),
                "min": min(durations),
                "max": max(durations),
                "mean": statistics.mean(durations)
            }
            
            return Ok(baseline)
        
        except Exception as e:
            return Err(f"Failed to calculate duration baseline: {str(e)}")
    
    def detect_slow_operations(
        self,
        operation_type: str,
        percentile_threshold: int = 99,
        days: int = 7
    ) -> Result[List[Dict[str, Any]]]:
        """
        Detect operations exceeding percentile threshold.
        
        AC-INT-DUR-002-03: Identifies slow operations vs baseline
        
        Args:
            operation_type: Filter by operation type
            percentile_threshold: Percentile to compare against (95 or 99)
            days: Time window in days
            
        Returns:
            List of slow operations with context
        """
        try:
            # Get baseline
            baseline_result = self.get_duration_baseline(operation_type, days=30)
            if baseline_result.is_err():
                return Err(baseline_result.unwrap_err())
            
            baseline = baseline_result.unwrap()
            threshold_key = f"p{percentile_threshold}"
            threshold_value = baseline.get(threshold_key, 0)
            
            if threshold_value == 0:
                return Ok([])
            
            # Find operations exceeding threshold
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    operation_type,
                    duration_ms,
                    handler_name,
                    timestamp
                FROM operation_durations
                WHERE operation_type = ? 
                  AND timestamp >= ?
                  AND duration_ms > ?
                ORDER BY duration_ms DESC
            """, (operation_type, cutoff_date, threshold_value))
            
            slow_ops = []
            for row in cursor.fetchall():
                slow_ops.append({
                    "operation_id": row[0],
                    "operation_type": row[1],
                    "duration_ms": row[2],
                    "handler": row[3],
                    "timestamp": row[4],
                    "baseline_p99": baseline["p99"],
                    "excess_ms": row[2] - threshold_value
                })
            
            conn.close()
            
            return Ok(slow_ops)
        
        except Exception as e:
            return Err(f"Failed to detect slow operations: {str(e)}")
    
    def get_handler_average_duration(
        self,
        handler_name: str,
        days: int = 7
    ) -> Result[Dict[str, Any]]:
        """
        Calculate average durations for a handler.
        
        AC-INT-DUR-002-04: Handler performance comparison
        
        Args:
            handler_name: Handler to analyze
            days: Time window in days
            
        Returns:
            Dict with handler averages by operation type
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    operation_type,
                    AVG(duration_ms) as avg_duration,
                    COUNT(*) as count
                FROM operation_durations
                WHERE handler_name = ? AND timestamp >= ?
                GROUP BY operation_type
            """, (handler_name, cutoff_date))
            
            operation_types = {}
            for row in cursor.fetchall():
                operation_types[row[0]] = {
                    "average_duration_ms": round(row[1], 2),
                    "operation_count": row[2]
                }
            
            conn.close()
            
            return Ok({
                "handler_name": handler_name,
                "operation_types": operation_types,
                "time_window_days": days
            })
        
        except Exception as e:
            return Err(f"Failed to get handler average duration: {str(e)}")
    
    @staticmethod
    def _percentile(data: List[int], percentile: int) -> float:
        """Calculate percentile from sorted data"""
        if not data:
            return 0.0
        
        n = len(data)
        k = (n - 1) * percentile / 100
        f = int(k)
        c = f + 1
        
        if c >= n:
            return float(data[-1])
        
        d0 = data[f] * (c - k)
        d1 = data[c] * (k - f)
        return d0 + d1
