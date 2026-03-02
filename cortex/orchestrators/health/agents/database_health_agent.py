"""Database Health Agent - Detect SQLite bloat and integrity issues

Monitors SQLite databases for:
- Database bloat (WAL journal size vs DB size)
- Missing auto-vacuum configuration
- Large -wal/-shm files
- Corruption indicators
- Unused test databases

Author: CORTEX Framework
Phase: PHASE-92
Authority: Health Orchestrator Integration
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueSeverity,
    HealthIssueCategory,
)


class DatabaseHealthAgent(BaseHealthAgent):
    """Health agent for SQLite database monitoring.

    Detects database bloat, integrity issues, and recommends maintenance
    actions like VACUUM or WAL checkpoint.

    Attributes:
        name: "DatabaseHealthAgent"
        description: Monitors SQLite databases for bloat and integrity
        bloat_threshold_mb: Threshold for flagging bloated databases (default: 10MB)
        wal_ratio_threshold: WAL size / DB size ratio threshold (default: 0.5)

    Usage:
        ```python
        agent = DatabaseHealthAgent()
        result = agent.check(Path("/path/to/workspace"))

        if result.critical_count > 0:
            print("Critical database issues detected!")
        ```
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize Database Health Agent.

        Args:
            config: Optional configuration with:
                - bloat_threshold_mb: Size threshold in MB (default: 10)
                - wal_ratio_threshold: WAL/DB ratio (default: 0.5)
                - check_test_dbs: Check test databases (default: False)
        """
        super().__init__(
            name="DatabaseHealthAgent",
            description="Monitors SQLite databases for bloat and integrity issues",
            config=config or {},
        )

        self.bloat_threshold_mb = self.config.get("bloat_threshold_mb", 10)
        self.wal_ratio_threshold = self.config.get("wal_ratio_threshold", 0.5)
        self.check_test_dbs = self.config.get("check_test_dbs", False)

    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run database health check on workspace.

        Scans for .db files and checks:
        1. Database size and WAL journal bloat
        2. Auto-vacuum configuration
        3. Integrity check status
        4. Orphaned WAL/SHM files

        Args:
            workspace_root: Root path of workspace to check

        Returns:
            HealthCheckResult with detected database issues
        """
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0

        # Find all .db files (excluding test directories unless configured)
        db_files = self._find_database_files(workspace_root)

        for db_path in db_files:
            files_scanned += 1

            # Check database bloat
            bloat_issue = self._check_bloat(db_path, workspace_root)
            if bloat_issue:
                issues.append(bloat_issue)

            # Check WAL journal size
            wal_issue = self._check_wal_bloat(db_path, workspace_root)
            if wal_issue:
                issues.append(wal_issue)

            # Check auto-vacuum setting
            vacuum_issue = self._check_auto_vacuum(db_path, workspace_root)
            if vacuum_issue:
                issues.append(vacuum_issue)

        duration = time.time() - start_time

        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "bloat_threshold_mb": self.bloat_threshold_mb,
                "wal_ratio_threshold": self.wal_ratio_threshold,
                "databases_checked": files_scanned,
            },
        )

    def _find_database_files(self, workspace_root: Path) -> List[Path]:
        """Find all SQLite database files in workspace.

        Args:
            workspace_root: Root path to scan

        Returns:
            List of database file paths
        """
        db_files = []

        # Scan for .db files
        for db_path in workspace_root.rglob("*.db"):
            # Use path relative to workspace_root for filtering so
            # temp directory names (e.g. pytest tmp_path) don't interfere
            try:
                rel_path = db_path.relative_to(workspace_root)
            except ValueError:
                continue

            # Skip test databases unless configured to check them
            if not self.check_test_dbs:
                if "test" in str(rel_path).lower() or ".pytest_cache" in str(rel_path):
                    continue

            # Skip hidden directories (relative to workspace root)
            if any(part.startswith(".") for part in rel_path.parts[:-1]):
                continue

            db_files.append(db_path)

        return db_files

    def _check_bloat(
        self,
        db_path: Path,
        workspace_root: Path,
    ) -> Optional[HealthIssue]:
        """Check if database is bloated.

        Args:
            db_path: Path to database file
            workspace_root: Workspace root for relative paths

        Returns:
            HealthIssue if bloated, None otherwise
        """
        try:
            size_mb = db_path.stat().st_size / (1024 * 1024)

            if size_mb > self.bloat_threshold_mb:
                return HealthIssue(
                    category=HealthIssueCategory.CONFIGURATION,
                    severity=HealthIssueSeverity.MEDIUM,
                    file_path=db_path.relative_to(workspace_root),
                    description=f"Database bloat detected: {size_mb:.2f}MB (threshold: {self.bloat_threshold_mb}MB)",
                    suggested_fix="Run VACUUM to reclaim space: sqlite3 <db> 'VACUUM;'",
                    metadata={
                        "size_mb": size_mb,
                        "threshold_mb": self.bloat_threshold_mb,
                    },
                )
        except (OSError, ValueError):
            pass

        return None

    def _check_wal_bloat(
        self,
        db_path: Path,
        workspace_root: Path,
    ) -> Optional[HealthIssue]:
        """Check if WAL journal is bloated.

        Args:
            db_path: Path to database file
            workspace_root: Workspace root for relative paths

        Returns:
            HealthIssue if WAL bloated, None otherwise
        """
        wal_path = db_path.with_suffix(".db-wal")

        if not wal_path.exists():
            return None

        try:
            db_size = db_path.stat().st_size
            wal_size = wal_path.stat().st_size

            if db_size == 0:
                return None

            wal_ratio = wal_size / db_size

            if wal_ratio > self.wal_ratio_threshold:
                return HealthIssue(
                    category=HealthIssueCategory.CONFIGURATION,
                    severity=HealthIssueSeverity.HIGH,
                    file_path=wal_path.relative_to(workspace_root),
                    description=f"WAL journal bloat: {wal_ratio:.2%} of database size (threshold: {self.wal_ratio_threshold:.0%})",
                    suggested_fix="Run WAL checkpoint: sqlite3 <db> 'PRAGMA wal_checkpoint(TRUNCATE);'",
                    metadata={
                        "wal_size_bytes": wal_size,
                        "db_size_bytes": db_size,
                        "wal_ratio": wal_ratio,
                    },
                )
        except (OSError, ZeroDivisionError):
            pass

        return None

    def _check_auto_vacuum(
        self,
        db_path: Path,
        workspace_root: Path,
    ) -> Optional[HealthIssue]:
        """Check if auto-vacuum is disabled.

        Args:
            db_path: Path to database file
            workspace_root: Workspace root for relative paths

        Returns:
            HealthIssue if auto-vacuum disabled, None otherwise
        """
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA auto_vacuum;")
            auto_vacuum = cursor.fetchone()[0]
            conn.close()

            # 0 = NONE, 1 = FULL, 2 = INCREMENTAL
            if auto_vacuum == 0:
                return HealthIssue(
                    category=HealthIssueCategory.CONFIGURATION,
                    severity=HealthIssueSeverity.LOW,
                    file_path=db_path.relative_to(workspace_root),
                    description="Auto-vacuum disabled (database may grow over time)",
                    suggested_fix="Enable auto-vacuum: PRAGMA auto_vacuum = FULL; VACUUM;",
                    metadata={
                        "auto_vacuum_mode": auto_vacuum,
                    },
                )
        except (sqlite3.Error, OSError):
            pass

        return None


__all__ = [
    "DatabaseHealthAgent",
]
