#!/usr/bin/env python3
"""
Database Log Rotation Policy Implementation
AC-ID: AC-PHASE-2-DB-ROTATION-001
Purpose: Implement 30-day rolling window for governance.db logs

Governance Tables Affected:
- governance_audit_trail (unbounded growth)
- operation_logs (archived daily)
- wiring_status_history (rotated weekly)
- component_health_snapshots (rotated monthly)

Execution: Deploy via cron job (daily at 2 AM)
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cortex_logs/db_rotation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DatabaseLogRotationPolicy:
    """Implements retention and archival policy for governance.db"""

    # Retention periods (days)
    RETENTION_AUDIT_TRAIL = 30  # Keep 30 days of audit trail
    RETENTION_OPERATION_LOGS = 14  # Keep 14 days of operation logs
    RETENTION_HEALTH_SNAPSHOTS = 60  # Keep 60 days of health data
    RETENTION_WIRING_HISTORY = 30  # Keep 30 days of wiring history

    # Archive thresholds (rows)
    ARCHIVE_THRESHOLD = 5000  # Archive when table reaches 5000 rows
    VACUUM_THRESHOLD = 1000  # Vacuum when archived 1000+ rows

    def __init__(self, db_path: str) -> None:
        """Initialize policy manager.

        Args:
            db_path: Path to governance.db
        """
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None
        self.archive_count = 0

    def connect(self) -> bool:
        """Connect to database.

        Returns:
            True if connection successful
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to {self.db_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def get_table_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get size and row count for all tables.

        Returns:
            Dictionary with table statistics
        """
        if not self.conn:
            return {}

        stats = {}
        cursor = self.conn.cursor()

        try:
            # Get list of all tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                # Get table size (pages * page_size)
                cursor.execute("PRAGMA page_count;")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size;")
                page_size = cursor.fetchone()[0]
                table_size_bytes = page_count * page_size

                stats[table_name] = {
                    "row_count": row_count,
                    "size_bytes": table_size_bytes,
                    "size_mb": round(table_size_bytes / (1024 * 1024), 2),
                }

            logger.info(f"Table statistics: {stats}")
            return stats

        except sqlite3.Error as e:
            logger.error(f"Failed to get table stats: {e}")
            return {}

    def rotate_audit_trail(self) -> int:
        """Rotate audit trail - archive old entries.

        Returns:
            Number of rows archived
        """
        if not self.conn:
            return 0

        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=self.RETENTION_AUDIT_TRAIL)).isoformat()

        try:
            # Check if archive table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='governance_audit_trail_archive'"
            )
            if not cursor.fetchone():
                # Create archive table
                cursor.execute("""
                    CREATE TABLE governance_audit_trail_archive (
                        id INTEGER PRIMARY KEY,
                        operation_id TEXT,
                        ac_id TEXT,
                        timestamp DATETIME,
                        status TEXT,
                        details TEXT,
                        archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("Created governance_audit_trail_archive table")

            # Archive old entries
            cursor.execute("""
                INSERT INTO governance_audit_trail_archive
                SELECT id, operation_id, ac_id, timestamp, status, details, CURRENT_TIMESTAMP
                FROM governance_audit_trail
                WHERE timestamp < ?
            """, (cutoff_date,))
            archived_count = cursor.rowcount

            # Delete archived entries from main table
            if archived_count > 0:
                cursor.execute("""
                    DELETE FROM governance_audit_trail
                    WHERE timestamp < ?
                """, (cutoff_date,))
                deleted_count = cursor.rowcount
                self.conn.commit()
                logger.info(f"Archived {archived_count} / deleted {deleted_count} audit trail entries")
                self.archive_count += archived_count
                return archived_count

            return 0

        except sqlite3.Error as e:
            logger.error(f"Failed to rotate audit trail: {e}")
            self.conn.rollback()
            return 0

    def rotate_operation_logs(self) -> int:
        """Rotate operation logs - keep 14 days only.

        Returns:
            Number of rows deleted
        """
        if not self.conn:
            return 0

        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=self.RETENTION_OPERATION_LOGS)).isoformat()

        try:
            cursor.execute("""
                DELETE FROM operation_logs
                WHERE created_at < ?
            """, (cutoff_date,))
            deleted_count = cursor.rowcount

            if deleted_count > 0:
                self.conn.commit()
                logger.info(f"Deleted {deleted_count} old operation log entries")

            return deleted_count

        except sqlite3.Error as e:
            logger.error(f"Failed to rotate operation logs: {e}")
            self.conn.rollback()
            return 0

    def rotate_health_snapshots(self) -> int:
        """Rotate health snapshots - keep 60 days only.

        Returns:
            Number of rows deleted
        """
        if not self.conn:
            return 0

        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=self.RETENTION_HEALTH_SNAPSHOTS)).isoformat()

        try:
            cursor.execute("""
                DELETE FROM component_health_snapshots
                WHERE timestamp < ?
            """, (cutoff_date,))
            deleted_count = cursor.rowcount

            if deleted_count > 0:
                self.conn.commit()
                logger.info(f"Deleted {deleted_count} old health snapshot entries")

            return deleted_count

        except sqlite3.Error as e:
            logger.error(f"Failed to rotate health snapshots: {e}")
            self.conn.rollback()
            return 0

    def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space.

        Returns:
            True if successful
        """
        if not self.conn:
            return False

        try:
            cursor = self.conn.cursor()
            cursor.execute("VACUUM")
            logger.info("Database vacuumed successfully")
            return True

        except sqlite3.Error as e:
            logger.error(f"Vacuum failed: {e}")
            return False

    def execute_rotation_policy(self) -> Dict[str, Any]:
        """Execute complete rotation policy.

        Returns:
            Summary of rotation results
        """
        logger.info("=" * 70)
        logger.info("STARTING DATABASE LOG ROTATION POLICY")
        logger.info("=" * 70)

        if not self.connect():
            return {"success": False, "error": "Connection failed"}

        stats_before = self.get_table_stats()
        results = {
            "timestamp": datetime.now().isoformat(),
            "stats_before": stats_before,
            "rotations": {},
        }

        try:
            # Execute rotations
            results["rotations"]["audit_trail_archived"] = self.rotate_audit_trail()
            results["rotations"]["operation_logs_deleted"] = self.rotate_operation_logs()
            results["rotations"]["health_snapshots_deleted"] = self.rotate_health_snapshots()

            # Vacuum if needed
            if self.archive_count >= self.VACUUM_THRESHOLD:
                vacuum_success = self.vacuum_database()
                results["vacuum_executed"] = vacuum_success

            stats_after = self.get_table_stats()
            results["stats_after"] = stats_after
            results["success"] = True

            logger.info("=" * 70)
            logger.info("ROTATION POLICY COMPLETED SUCCESSFULLY")
            logger.info(f"Results: {results}")
            logger.info("=" * 70)

            return results

        except Exception as e:
            logger.error(f"Unexpected error during rotation: {e}")
            results["success"] = False
            results["error"] = str(e)
            return results

        finally:
            self.disconnect()


def main() -> None:
    """Main entry point."""
    db_path = (
        Path(__file__).parent.parent
        / "cortex_brain"
        / "state"
        / "governance.db"
    )

    policy = DatabaseLogRotationPolicy(str(db_path))
    results = policy.execute_rotation_policy()

    # Print results
    print("\n" + "=" * 70)
    print("DATABASE LOG ROTATION RESULTS")
    print("=" * 70)
    print(f"Success: {results.get('success', False)}")
    print(f"Audit trail archived: {results.get('rotations', {}).get('audit_trail_archived', 0)}")
    print(f"Operation logs deleted: {results.get('rotations', {}).get('operation_logs_deleted', 0)}")
    print(f"Health snapshots deleted: {results.get('rotations', {}).get('health_snapshots_deleted', 0)}")
    print("=" * 70 + "\n")

    # Exit with appropriate code
    exit(0 if results.get("success") else 1)


if __name__ == "__main__":
    main()
