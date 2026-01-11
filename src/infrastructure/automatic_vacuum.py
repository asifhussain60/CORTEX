"""
AC-AUDIT-005: Automatic Vacuum

Manages automatic retention-based cleanup of audit logs.
Implements tiered retention policies with configurable thresholds.

Retention tiers:
- CRITICAL/ERROR: 90 days
- WARNING: 60 days
- INFO: 30 days
- DEBUG: 7 days
- TRACE: 1 day

Status: COMPLETE
Author: GitHub Copilot
Version: 1.0.0
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from src.utils.path_utils import audit_logs_path, project_root


@dataclass
class RetentionPolicy:
    """Configuration for retention policy."""
    level: str
    days: int
    
    def __post_init__(self):
        if self.level not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]:
            raise ValueError(f"Invalid log level: {self.level}")
        if self.days < 1:
            raise ValueError(f"Retention days must be >= 1, got {self.days}")


class AutomaticVacuum:
    """
    Manages automatic cleanup of audit logs based on retention policies.
    Ensures logs older than their retention threshold are deleted.
    """
    
    # Default retention policies (in days)
    DEFAULT_RETENTION = {
        "CRITICAL": 90,
        "ERROR": 90,
        "WARNING": 60,
        "INFO": 30,
        "DEBUG": 7,
        "TRACE": 1,
    }
    
    def __init__(
        self,
        retention_policies: Optional[Dict[str, int]] = None,
        db_path: Optional[str] = None,
        dry_run: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize vacuum system.
        
        Args:
            retention_policies: Override default retention (level -> days)
            db_path: Path to audit database (auto-detected if None)
            dry_run: If True, don't actually delete, just report
            logger: Logger instance (default: module logger)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.dry_run = dry_run
        self.db_path = db_path or self._get_default_db_path()
        
        # Merge provided policies with defaults
        self.retention_policies = self.DEFAULT_RETENTION.copy()
        if retention_policies:
            self.retention_policies.update(retention_policies)
            
        # Validate policies
        for level, days in self.retention_policies.items():
            try:
                RetentionPolicy(level, days)
            except ValueError as e:
                raise ValueError(f"Invalid retention policy: {e}")
    
    def _get_default_db_path(self) -> str:
        """Get default audit database path."""
        try:
            db_dir = audit_logs_path()
        except Exception:
            # Fallback for testing
            db_dir = Path(project_root()) / "cortex-brain" / "audit-logs"
        
        return str(db_dir / "audit.db")
    
    def calculate_cutoff_date(self, level: str) -> datetime:
        """
        Calculate cutoff date for a log level.
        
        Args:
            level: Log level string
            
        Returns:
            datetime object representing retention cutoff
        """
        if level not in self.retention_policies:
            raise ValueError(f"Unknown log level: {level}")
        
        days = self.retention_policies[level]
        cutoff = datetime.utcnow() - timedelta(days=days)
        return cutoff
    
    def get_events_to_delete(self, level: str) -> List[Dict]:
        """
        Get all events for a level that should be deleted.
        
        Args:
            level: Log level to check
            
        Returns:
            List of events exceeding retention
        """
        cutoff = self.calculate_cutoff_date(level)
        cutoff_iso = cutoff.isoformat()
        
        events = []
        
        try:
            if not Path(self.db_path).exists():
                return events
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query events for this level older than cutoff
            cursor.execute(
                """
                SELECT * FROM audit_events
                WHERE level = ? AND timestamp < ?
                ORDER BY timestamp ASC
                """,
                (level, cutoff_iso)
            )
            
            for row in cursor.fetchall():
                events.append(dict(row))
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error querying events for deletion: {e}")
        
        return events
    
    def delete_events(self, level: str) -> Tuple[int, int]:
        """
        Delete events for a level that exceed retention.
        
        Args:
            level: Log level to clean
            
        Returns:
            Tuple of (events_deleted, events_examined)
        """
        cutoff = self.calculate_cutoff_date(level)
        cutoff_iso = cutoff.isoformat()
        
        examined = 0
        deleted = 0
        
        try:
            if not Path(self.db_path).exists():
                return deleted, examined
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count events before deletion
            cursor.execute(
                "SELECT COUNT(*) FROM audit_events WHERE level = ? AND timestamp < ?",
                (level, cutoff_iso)
            )
            examined = cursor.fetchone()[0]
            
            if self.dry_run:
                self.logger.info(
                    f"[DRY RUN] Would delete {examined} {level} events "
                    f"older than {cutoff_iso}"
                )
                deleted = examined
            else:
                # Delete events
                cursor.execute(
                    "DELETE FROM audit_events WHERE level = ? AND timestamp < ?",
                    (level, cutoff_iso)
                )
                deleted = cursor.rowcount
                conn.commit()
                
                self.logger.info(
                    f"Deleted {deleted} {level} events older than {cutoff_iso}"
                )
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error deleting {level} events: {e}")
        
        return deleted, examined
    
    def run_vacuum(self) -> Dict[str, Tuple[int, int]]:
        """
        Run complete vacuum operation for all levels.
        
        Returns:
            Dict mapping level -> (deleted, examined) tuples
        """
        self.logger.info("Starting automatic vacuum operation")
        
        results = {}
        total_deleted = 0
        total_examined = 0
        
        for level in ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            deleted, examined = self.delete_events(level)
            results[level] = (deleted, examined)
            total_deleted += deleted
            total_examined += examined
        
        self.logger.info(
            f"Vacuum complete: {total_deleted} events deleted "
            f"({total_examined} examined)"
        )
        
        return results
    
    def get_vacuum_stats(self) -> Dict[str, Dict]:
        """
        Get statistics on events that would be deleted.
        
        Returns:
            Dict with per-level stats (count, oldest_event_date, cutoff_date)
        """
        stats = {}
        
        try:
            if not Path(self.db_path).exists():
                return stats
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for level in self.retention_policies:
                cutoff = self.calculate_cutoff_date(level)
                cutoff_iso = cutoff.isoformat()
                
                # Count old events
                cursor.execute(
                    """
                    SELECT COUNT(*) as count, MIN(timestamp) as oldest
                    FROM audit_events
                    WHERE level = ? AND timestamp < ?
                    """,
                    (level, cutoff_iso)
                )
                
                row = cursor.fetchone()
                count = row["count"] if row["count"] else 0
                oldest = row["oldest"] if row["oldest"] else None
                
                stats[level] = {
                    "events_to_delete": count,
                    "oldest_event": oldest,
                    "cutoff_date": cutoff_iso,
                    "retention_days": self.retention_policies[level],
                }
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error getting vacuum stats: {e}")
        
        return stats


def create_vacuum_scheduler(interval_hours: int = 24) -> Dict:
    """
    Create configuration for scheduled vacuum execution.
    
    Args:
        interval_hours: Run vacuum every N hours
        
    Returns:
        Dict with scheduler configuration
    """
    return {
        "type": "scheduler",
        "interval_hours": interval_hours,
        "action": "automatic_vacuum",
        "enabled": True,
    }
