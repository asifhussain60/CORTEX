"""Dashboard Health Metrics Exporter

Exports health check metrics to SQLite for dashboard visualization.
Integrates with CORTEX dashboard system.

Author: CORTEX Framework
Phase: PHASE-95
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.reports.health_report import HealthReport


class HealthMetricsExporter:
    """Exports health metrics to dashboard database.
    
    Attributes:
        db_path: Path to SQLite database
        conn: Database connection
    """
    
    def __init__(self, db_path: Union[Path, str]) -> None:
        """Initialize exporter.
        
        Args:
            db_path: Path to dashboard SQLite database
        """
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection | None = None
        self._init_tables()
    
    def _init_tables(self) -> None:
        """Create health metrics tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Health scores over time
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                health_score REAL NOT NULL,
                total_issues INTEGER NOT NULL,
                critical_issues INTEGER NOT NULL,
                high_issues INTEGER NOT NULL,
                medium_issues INTEGER NOT NULL,
                low_issues INTEGER NOT NULL,
                files_scanned INTEGER NOT NULL,
                duration_seconds REAL NOT NULL
            )
        """)
        
        # Agent performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                issues_found INTEGER NOT NULL,
                files_scanned INTEGER NOT NULL,
                duration_seconds REAL NOT NULL
            )
        """)
        
        # Issue trends
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issue_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                count INTEGER NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def export_report(self, report: HealthReport) -> None:
        """Export health report to database.
        
        Args:
            report: HealthReport to export
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        # Export overall health score
        cursor.execute("""
            INSERT INTO health_scores (
                timestamp, health_score, total_issues,
                critical_issues, high_issues, medium_issues, low_issues,
                files_scanned, duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            report.metrics.health_score,
            report.metrics.total_issues,
            report.metrics.critical_issues,
            report.metrics.high_issues,
            report.metrics.medium_issues,
            report.metrics.low_issues,
            report.metrics.files_scanned,
            report.metrics.duration_seconds,
        ))
        
        # Export agent performance
        for result in report.agent_results:
            cursor.execute("""
                INSERT INTO agent_performance (
                    timestamp, agent_name, issues_found,
                    files_scanned, duration_seconds
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                timestamp,
                result.agent_name,
                result.issue_count,
                result.files_scanned,
                result.duration_seconds,
            ))
        
        # Export issue trends by category and severity
        issue_counts: Dict[tuple[str, str], int] = {}
        for issue in report.all_issues:
            key = (issue.category.value, issue.severity.value)
            issue_counts[key] = issue_counts.get(key, 0) + 1
        
        for (category, severity), count in issue_counts.items():
            cursor.execute("""
                INSERT INTO issue_trends (
                    timestamp, category, severity, count
                ) VALUES (?, ?, ?, ?)
            """, (timestamp, category, severity, count))
        
        conn.commit()
        conn.close()
    
    def get_health_history(self, days: int = 30) -> list[Dict[str, Any]]:
        """Get health score history.
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            List of health score records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, health_score, total_issues
            FROM health_scores
            WHERE timestamp >= date('now', ? || ' days')
            ORDER BY timestamp DESC
        """, (-days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "health_score": row[1],
                "total_issues": row[2],
            }
            for row in rows
        ]
    
    def get_trend_summary(self) -> Dict[str, Any]:
        """Get trending summary of health metrics.
        
        Returns:
            Dict with trend data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current vs 7 days ago
        cursor.execute("""
            SELECT health_score
            FROM health_scores
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        current = cursor.fetchone()
        
        cursor.execute("""
            SELECT health_score
            FROM health_scores
            WHERE timestamp <= date('now', '-7 days')
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        week_ago = cursor.fetchone()
        
        conn.close()
        
        if current and week_ago:
            trend = current[0] - week_ago[0]
            return {
                "current_score": current[0],
                "week_ago_score": week_ago[0],
                "trend": trend,
                "improving": trend > 0,
            }
        
        return {
            "current_score": current[0] if current else 0.0,
            "trend": 0.0,
            "improving": None,
        }


__all__ = ["HealthMetricsExporter"]
