"""
Log Growth Monitoring System - Real-time alerting for database growth
AC-ID: AC-PHASE-3-LOG-MONITORING-001
Purpose: Alert when governance.db exceeds thresholds

Thresholds:
- WARNING: > 500 MB
- CRITICAL: > 1 GB
- EMERGENCY: > 2 GB
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AlertLevel(str, Enum):
    """Alert severity levels."""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class DatabaseMetrics:
    """Database health metrics snapshot."""
    timestamp: datetime
    total_size_mb: float
    table_metrics: Dict[str, Dict[str, Any]]
    alert_level: AlertLevel
    alert_message: Optional[str] = None


class LogGrowthMonitor:
    """Monitors database log growth and raises alerts."""

    # Thresholds (in MB)
    THRESHOLD_WARNING = 500
    THRESHOLD_CRITICAL = 1000
    THRESHOLD_EMERGENCY = 2000

    # Growth rate thresholds (MB per day)
    GROWTH_RATE_WARNING = 50  # Growing > 50 MB per day
    GROWTH_RATE_CRITICAL = 100  # Growing > 100 MB per day

    def __init__(self, db_path: str, alert_handler=None) -> None:
        """Initialize monitoring system.
        
        Args:
            db_path: Path to governance.db
            alert_handler: Optional custom alert handler function
        """
        self.db_path = db_path
        self.alert_handler = alert_handler or self._default_alert_handler
        self.logger = logging.getLogger(__name__)
        self.previous_size_mb: Optional[float] = None

    def _default_alert_handler(self, alert_level: AlertLevel, message: str) -> None:
        """Default alert handler - logs to file and console."""
        timestamp = datetime.now().isoformat()
        alert_msg = f"[{timestamp}] {alert_level.value}: {message}"

        if alert_level == AlertLevel.HEALTHY:
            self.logger.info(alert_msg)
        elif alert_level == AlertLevel.WARNING:
            self.logger.warning(alert_msg)
        elif alert_level in (AlertLevel.CRITICAL, AlertLevel.EMERGENCY):
            self.logger.error(alert_msg)

    def get_database_size(self) -> float:
        """Get total database size in MB.
        
        Returns:
            Database size in megabytes
        """
        try:
            size_bytes = Path(self.db_path).stat().st_size
            return round(size_bytes / (1024 * 1024), 2)
        except FileNotFoundError:
            self.logger.error(f"Database file not found: {self.db_path}")
            return 0.0

    def get_table_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for each table in database.
        
        Returns:
            Dictionary with table size and row count statistics
        """
        metrics = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                # Get approximate table size using page count
                cursor.execute(f"SELECT SUM(pgsize) FROM dbstat WHERE name='{table_name}'")
                result = cursor.fetchone()
                table_size_bytes = result[0] if result and result[0] else 0

                metrics[table_name] = {
                    "row_count": row_count,
                    "size_bytes": table_size_bytes,
                    "size_mb": round(table_size_bytes / (1024 * 1024), 2),
                    "growth_potential": "HIGH" if row_count > 10000 else "MEDIUM" if row_count > 1000 else "LOW",
                }

            conn.close()
            return metrics

        except sqlite3.Error as e:
            self.logger.error(f"Failed to get table metrics: {e}")
            return {}

    def check_growth_rate(self, current_size_mb: float) -> Optional[AlertLevel]:
        """Check if database is growing too fast.
        
        Args:
            current_size_mb: Current database size
            
        Returns:
            Alert level if growth rate is concerning, else None
        """
        if self.previous_size_mb is None:
            return None

        growth_mb = current_size_mb - self.previous_size_mb
        
        if growth_mb > self.GROWTH_RATE_CRITICAL:
            return AlertLevel.CRITICAL
        elif growth_mb > self.GROWTH_RATE_WARNING:
            return AlertLevel.WARNING

        return None

    def determine_alert_level(self, size_mb: float) -> AlertLevel:
        """Determine alert level based on database size.
        
        Args:
            size_mb: Database size in MB
            
        Returns:
            Alert level (HEALTHY, WARNING, CRITICAL, or EMERGENCY)
        """
        if size_mb >= self.THRESHOLD_EMERGENCY:
            return AlertLevel.EMERGENCY
        elif size_mb >= self.THRESHOLD_CRITICAL:
            return AlertLevel.CRITICAL
        elif size_mb >= self.THRESHOLD_WARNING:
            return AlertLevel.WARNING
        else:
            return AlertLevel.HEALTHY

    def generate_alert_message(
        self, alert_level: AlertLevel, size_mb: float, metrics: Dict[str, Any]
    ) -> str:
        """Generate detailed alert message.
        
        Args:
            alert_level: Current alert level
            size_mb: Database size in MB
            metrics: Table metrics
            
        Returns:
            Formatted alert message
        """
        msg = f"Database size: {size_mb} MB"

        if alert_level == AlertLevel.EMERGENCY:
            msg += f"\n⚠️ EMERGENCY: Database exceeds {self.THRESHOLD_EMERGENCY} MB!"
            msg += "\n   ACTION REQUIRED: Run immediate cleanup"
            msg += f"\n   Largest tables: {self._get_top_tables(metrics, 3)}"

        elif alert_level == AlertLevel.CRITICAL:
            msg += f"\n⚠️ CRITICAL: Database exceeds {self.THRESHOLD_CRITICAL} MB"
            msg += "\n   ACTION: Schedule cleanup soon"
            msg += f"\n   Largest tables: {self._get_top_tables(metrics, 3)}"

        elif alert_level == AlertLevel.WARNING:
            msg += f"\n⚠️ WARNING: Database exceeds {self.THRESHOLD_WARNING} MB"
            msg += "\n   ACTION: Monitor growth"
            msg += f"\n   Largest tables: {self._get_top_tables(metrics, 2)}"

        else:
            msg += "\n✅ Database size is healthy"

        return msg

    @staticmethod
    def _get_top_tables(metrics: Dict[str, Any], top_n: int) -> str:
        """Get string representation of top N tables by size.
        
        Args:
            metrics: Table metrics dictionary
            top_n: Number of top tables to include
            
        Returns:
            Formatted string of top tables
        """
        sorted_tables = sorted(
            metrics.items(), key=lambda x: x[1]["size_mb"], reverse=True
        )[:top_n]
        
        return "; ".join(
            f"{name} ({info['size_mb']} MB, {info['row_count']} rows)"
            for name, info in sorted_tables
        )

    def check_health(self) -> DatabaseMetrics:
        """Run complete health check.
        
        Returns:
            DatabaseMetrics snapshot with alert information
        """
        current_size_mb = self.get_database_size()
        table_metrics = self.get_table_metrics()

        # Determine alert level
        alert_level = self.determine_alert_level(current_size_mb)

        # Check growth rate
        growth_alert = self.check_growth_rate(current_size_mb)
        if growth_alert and growth_alert.value > alert_level.value:
            alert_level = growth_alert

        # Generate message
        alert_message = self.generate_alert_message(alert_level, current_size_mb, table_metrics)

        # Send alert
        self.alert_handler(alert_level, alert_message)

        # Update previous size for next check
        self.previous_size_mb = current_size_mb

        return DatabaseMetrics(
            timestamp=datetime.now(),
            total_size_mb=current_size_mb,
            table_metrics=table_metrics,
            alert_level=alert_level,
            alert_message=alert_message,
        )


def setup_monitoring(db_path: str, check_interval_seconds: int = 3600) -> LogGrowthMonitor:
    """Set up background monitoring for database growth.
    
    Args:
        db_path: Path to governance.db
        check_interval_seconds: How often to check (default: hourly)
        
    Returns:
        Configured monitor instance
    """
    monitor = LogGrowthMonitor(db_path)
    
    # In production, this would be run by a scheduler (APScheduler, etc.)
    # For now, return the monitor for manual or external scheduling
    logging.info(f"Log growth monitoring initialized for {db_path}")
    logging.info(f"Check interval: {check_interval_seconds} seconds")
    logging.info(f"Thresholds: WARNING={monitor.THRESHOLD_WARNING}MB, "
                f"CRITICAL={monitor.THRESHOLD_CRITICAL}MB, "
                f"EMERGENCY={monitor.THRESHOLD_EMERGENCY}MB")
    
    return monitor


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("cortex_logs/db_monitoring.log"),
            logging.StreamHandler(),
        ],
    )

    # Initialize monitor
    db_path = Path(__file__).parent.parent.parent / "cortex_brain" / "state" / "governance.db"
    monitor = setup_monitoring(str(db_path))

    # Run health check
    print("\n" + "=" * 70)
    print("DATABASE LOG GROWTH MONITOR")
    print("=" * 70)
    
    metrics = monitor.check_health()
    
    print(f"\nTimestamp: {metrics.timestamp.isoformat()}")
    print(f"Total Size: {metrics.total_size_mb} MB")
    print(f"Alert Level: {metrics.alert_level.value}")
    print(f"Message:\n{metrics.alert_message}")
    print("\nTable Breakdown:")
    for table_name, table_info in sorted(
        metrics.table_metrics.items(), key=lambda x: x[1]["size_mb"], reverse=True
    )[:5]:
        print(f"  {table_name}: {table_info['size_mb']} MB ({table_info['row_count']} rows)")
    
    print("=" * 70 + "\n")
