"""
CORTEX Tier 3: Architecture Health History Store

Tracks architecture health metrics over time for trend analysis and forecasting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict

# Import centralized config for cross-platform path resolution
from src.config import config


@dataclass
class ArchitectureHealthSnapshot:
    """Single point-in-time architecture health measurement."""
    timestamp: str  # ISO format
    overall_score: float  # 0-100
    layer_scores: Dict[str, int]  # {discovered: 20, imported: 20, etc.}
    trend_direction: str  # "improving", "degrading", "stable"
    debt_estimate_hours: float  # Estimated hours to reach 90%
    feature_count: int
    features_healthy: int  # Score >= 90
    features_warning: int  # Score 70-89
    features_critical: int  # Score < 70
    recommendations: List[str]  # Top 3 recommendations
    metadata: Dict[str, Any]  # Additional context


class ArchitectureHealthStore:
    """
    Manages architecture health history database.
    
    Features:
    - Health snapshot recording
    - Historical trend analysis
    - Debt forecasting data
    - ADR recommendation tracking
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize architecture health store.
        
        Args:
            db_path: Path to SQLite database (default: cortex-brain/tier3/context.db)
        """
        if db_path is None:
            # Use centralized config for cross-platform path resolution
            tier3_dir = config.brain_path / "tier3"
            tier3_dir.mkdir(parents=True, exist_ok=True)
            db_path = tier3_dir / "context.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
    
    def _init_database(self):
        """Create architecture_health_history table and indexes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Architecture health history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS architecture_health_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                overall_score REAL NOT NULL CHECK(overall_score >= 0 AND overall_score <= 100),
                layer_scores TEXT NOT NULL,  -- JSON: {discovered: 20, imported: 20, ...}
                trend_direction TEXT NOT NULL CHECK(trend_direction IN ('improving', 'degrading', 'stable')),
                debt_estimate_hours REAL NOT NULL CHECK(debt_estimate_hours >= 0),
                feature_count INTEGER NOT NULL CHECK(feature_count >= 0),
                features_healthy INTEGER NOT NULL CHECK(features_healthy >= 0),
                features_warning INTEGER NOT NULL CHECK(features_warning >= 0),
                features_critical INTEGER NOT NULL CHECK(features_critical >= 0),
                recommendations TEXT NOT NULL,  -- JSON: ["rec1", "rec2", "rec3"]
                metadata TEXT,  -- JSON: additional context
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for efficient queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_arch_health_timestamp 
            ON architecture_health_history(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_arch_health_score 
            ON architecture_health_history(overall_score)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_arch_health_trend 
            ON architecture_health_history(trend_direction)
        """)
        
        conn.commit()
        conn.close()
    
    def record_snapshot(self, snapshot: ArchitectureHealthSnapshot) -> int:
        """
        Record a health snapshot to history.
        
        Args:
            snapshot: ArchitectureHealthSnapshot instance
            
        Returns:
            ID of inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO architecture_health_history (
                timestamp, overall_score, layer_scores, trend_direction,
                debt_estimate_hours, feature_count, features_healthy,
                features_warning, features_critical, recommendations, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.timestamp,
            snapshot.overall_score,
            json.dumps(snapshot.layer_scores),
            snapshot.trend_direction,
            snapshot.debt_estimate_hours,
            snapshot.feature_count,
            snapshot.features_healthy,
            snapshot.features_warning,
            snapshot.features_critical,
            json.dumps(snapshot.recommendations),
            json.dumps(snapshot.metadata) if snapshot.metadata else None
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_latest_snapshot(self) -> Optional[ArchitectureHealthSnapshot]:
        """
        Get most recent health snapshot.
        
        Returns:
            Latest snapshot or None if no history exists
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM architecture_health_history
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_snapshot(row)
    
    def get_history(
        self, 
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[ArchitectureHealthSnapshot]:
        """
        Get health history snapshots.
        
        Args:
            limit: Maximum number of snapshots to return
            start_date: ISO format start date (inclusive)
            end_date: ISO format end date (inclusive)
            
        Returns:
            List of snapshots ordered by timestamp descending
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM architecture_health_history WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_snapshot(row) for row in rows]
    
    def get_trend_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get simplified trend data for analysis.
        
        Args:
            days: Number of days of history to retrieve
            
        Returns:
            List of {timestamp, overall_score, trend_direction}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get snapshots from last N days
        cursor.execute("""
            SELECT timestamp, overall_score, trend_direction
            FROM architecture_health_history
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp ASC
        """, (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "overall_score": row[1],
                "trend_direction": row[2]
            }
            for row in rows
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics across all history.
        
        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_snapshots,
                MIN(overall_score) as min_score,
                MAX(overall_score) as max_score,
                AVG(overall_score) as avg_score,
                MIN(timestamp) as first_snapshot,
                MAX(timestamp) as latest_snapshot
            FROM architecture_health_history
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or row[0] == 0:
            return {
                "total_snapshots": 0,
                "min_score": None,
                "max_score": None,
                "avg_score": None,
                "first_snapshot": None,
                "latest_snapshot": None
            }
        
        return {
            "total_snapshots": row[0],
            "min_score": row[1],
            "max_score": row[2],
            "avg_score": round(row[3], 2) if row[3] else None,
            "first_snapshot": row[4],
            "latest_snapshot": row[5]
        }
    
    def _row_to_snapshot(self, row: sqlite3.Row) -> ArchitectureHealthSnapshot:
        """Convert database row to ArchitectureHealthSnapshot."""
        return ArchitectureHealthSnapshot(
            timestamp=row['timestamp'],
            overall_score=row['overall_score'],
            layer_scores=json.loads(row['layer_scores']),
            trend_direction=row['trend_direction'],
            debt_estimate_hours=row['debt_estimate_hours'],
            feature_count=row['feature_count'],
            features_healthy=row['features_healthy'],
            features_warning=row['features_warning'],
            features_critical=row['features_critical'],
            recommendations=json.loads(row['recommendations']),
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def vacuum(self):
        """Vacuum the database to reclaim space."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
