"""Database Bloat Cleaner - SQLite VACUUM and WAL cleanup

Cleaner plugin for VacuumOrchestrator that handles:
- Running VACUUM on bloated databases
- Cleaning up large WAL journal files
- Removing orphaned -wal and -shm files

Authority: VAC-001-05 (Vacuum Orchestrator), Phase 92 (Health)
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .base import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
)


class DatabaseBloatCleaner(CleanerInterface):
    """Cleaner for SQLite database bloat and WAL management.
    
    Analyzes SQLite databases for bloat and performs cleanup operations:
    - VACUUM command to reclaim space
    - WAL checkpoint to truncate journals
    - Removal of orphaned -wal and -shm files
    
    Attributes:
        name: "DatabaseBloatCleaner"
        version: "1.0.0"
        domain: "database_cleanup"
        bloat_threshold_mb: Size threshold for VACUUM (default: 10MB)
        wal_ratio_threshold: WAL/DB ratio threshold (default: 0.5)
    
    Usage:
        ```python
        cleaner = DatabaseBloatCleaner(config={
            "repo_root": "/path/to/repo",
            "dry_run": False,
            "bloat_threshold_mb": 10,
        })
        
        analysis = cleaner.analyze()
        if analysis.issues_found > 0:
            report = cleaner.execute(analysis.plan)
        ```
    """
    
    @property
    def name(self) -> str:
        """Return cleaner name."""
        return "Database Bloat Cleaner"
    
    @property
    def version(self) -> str:
        """Return cleaner version."""
        return "1.0.0"
    
    @property
    def domain(self) -> str:
        """Return cleaner domain."""
        return "database_bloat"
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize Database Bloat Cleaner.
        
        Args:
            config: Configuration with:
                - repo_root: Repository root path
                - dry_run: If True, only report without changes
                - bloat_threshold_mb: Size threshold in MB (default: 10)
                - wal_ratio_threshold: WAL/DB ratio (default: 0.5)
                - skip_production_db: Skip governance.db (default: True)
        """
        super().__init__(config)
        
        self.bloat_threshold_mb = config.get("bloat_threshold_mb", 10)
        self.wal_ratio_threshold = config.get("wal_ratio_threshold", 0.5)
        self.skip_production_db = config.get("skip_production_db", True)
    
    def analyze(self) -> Analysis:
        """Analyze databases for bloat and WAL issues.
        
        Scans for .db files and checks:
        1. Database size vs threshold
        2. WAL journal size ratio
        3. Orphaned WAL/SHM files
        4. Duplicate databases with same schema
        
        Returns:
            Analysis with detected issues and cleanup plan
        """
        start_time = time.time()
        logs: List[str] = []
        actions: List[Dict[str, Any]] = []
        
        logs.append(f"Scanning {self.repo_root} for database bloat...")
        
        # Find all database files
        db_files = list(self.repo_root.rglob("*.db"))
        files_scanned = len(db_files)
        
        # Track schemas for duplicate detection
        schema_map: Dict[str, List[Path]] = {}
        
        for db_path in db_files:
            # Skip production database if configured
            if self.skip_production_db and db_path.name == "governance.db":
                logs.append(f"Skipping production database: {db_path.name}")
                continue
            
            # Skip test databases using relative path
            try:
                rel_path = db_path.relative_to(self.repo_root)
            except ValueError:
                continue
            if "test" in str(rel_path).lower() or ".pytest_cache" in str(rel_path):
                continue
            
            # Check database size
            try:
                size_mb = db_path.stat().st_size / (1024 * 1024)
            except OSError:
                continue
            
            if size_mb > self.bloat_threshold_mb:
                actions.append({
                    "type": "vacuum",
                    "path": str(db_path),
                    "size_mb": size_mb,
                    "reason": f"Size {size_mb:.2f}MB exceeds threshold {self.bloat_threshold_mb}MB",
                })
                logs.append(f"Bloated database: {db_path.name} ({size_mb:.2f}MB)")
            
            # Check WAL journal
            wal_path = db_path.with_suffix(".db-wal")
            if wal_path.exists():
                wal_size = wal_path.stat().st_size
                db_size = db_path.stat().st_size
                
                if db_size > 0:
                    wal_ratio = wal_size / db_size
                    
                    if wal_ratio > self.wal_ratio_threshold:
                        actions.append({
                            "type": "wal_checkpoint",
                            "path": str(db_path),
                            "wal_path": str(wal_path),
                            "wal_ratio": wal_ratio,
                            "reason": f"WAL ratio {wal_ratio:.2%} exceeds threshold {self.wal_ratio_threshold:.0%}",
                        })
                        logs.append(f"Large WAL journal: {wal_path.name} ({wal_ratio:.2%} of DB)")
            
            # Collect schemas for duplicate detection
            try:
                conn = sqlite3.connect(str(db_path))
                tables = conn.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name"
                ).fetchall()
                conn.close()
                schema_key = "|".join(t[0] for t in tables if t[0])
                if schema_key:
                    schema_map.setdefault(schema_key, []).append(db_path)
            except sqlite3.Error:
                pass
        
        # Detect duplicate databases (same schema, different locations)
        for schema_key, paths in schema_map.items():
            if len(paths) > 1:
                paths.sort(key=lambda p: p.stat().st_size, reverse=True)
                for dup_path in paths[1:]:
                    actions.append({
                        "type": "delete_duplicate",
                        "path": str(dup_path),
                        "canonical": str(paths[0]),
                        "reason": f"Duplicate of {paths[0].name}",
                    })
                    logs.append(f"Duplicate database: {dup_path.name}")
        
        # Find orphaned WAL/SHM files (no corresponding .db)
        for wal_path in self.repo_root.rglob("*.db-wal"):
            db_path_for_wal = wal_path.with_name(wal_path.name.replace("-wal", ""))
            if not db_path_for_wal.exists():
                actions.append({
                    "type": "delete_orphan",
                    "path": str(wal_path),
                    "reason": f"No matching database for {wal_path.name}",
                })
                logs.append(f"Orphaned WAL file: {wal_path.name}")
        
        for shm_path in self.repo_root.rglob("*.db-shm"):
            db_path_for_shm = shm_path.with_name(shm_path.name.replace("-shm", ""))
            if not db_path_for_shm.exists():
                actions.append({
                    "type": "delete_orphan",
                    "path": str(shm_path),
                    "reason": f"No matching database for {shm_path.name}",
                })
                logs.append(f"Orphaned SHM file: {shm_path.name}")
        
        issues_found = len(actions)
        logs.append(f"Analysis complete: {issues_found} issues found in {files_scanned} databases")
        
        return Analysis(
            cleaner_id=self.domain,
            timestamp=datetime.now().isoformat(),
            files_scanned=files_scanned,
            issues_found=issues_found,
            plan={"actions": actions, "retention_days": self.config.get("retention_days", 30)},
            logs=logs,
        )
    
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute database cleanup plan.
        
        Dispatches on action type from unified actions list:
        - vacuum: VACUUM on bloated databases
        - wal_checkpoint: WAL checkpoint on large journals
        - delete_orphan: Remove orphaned WAL/SHM files
        - delete_duplicate: Remove duplicate databases
        - retention_purge: Delete rows older than retention threshold
        
        Args:
            plan: Cleanup plan from analyze() with ``actions`` list
        
        Returns:
            Report with actions taken and results
        """
        logs: List[str] = []
        errors: List[str] = []
        changes: Dict[str, int] = {
            "vacuumed": 0,
            "checkpointed": 0,
            "orphans_deleted": 0,
            "duplicates_deleted": 0,
            "rows_purged": 0,
        }
        retention_days = plan.get("retention_days", 30)
        
        if self.dry_run:
            logs.append("DRY RUN - No changes will be made")
        
        for action in plan.get("actions", []):
            action_type = action["type"]
            action_path = Path(action["path"])
            
            if action_type == "vacuum":
                if self.dry_run:
                    logs.append(f"[DRY RUN] Would VACUUM: {action_path.name}")
                else:
                    try:
                        conn = sqlite3.connect(str(action_path))
                        conn.execute("VACUUM")
                        conn.close()
                        changes["vacuumed"] += 1
                        logs.append(f"VACUUM completed: {action_path.name}")
                    except (sqlite3.Error, OSError) as e:
                        errors.append(f"VACUUM failed for {action_path.name}: {e}")
            
            elif action_type == "wal_checkpoint":
                if self.dry_run:
                    logs.append(f"[DRY RUN] Would checkpoint WAL: {action_path.name}")
                else:
                    try:
                        conn = sqlite3.connect(str(action_path))
                        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                        conn.close()
                        changes["checkpointed"] += 1
                        logs.append(f"WAL checkpoint completed: {action_path.name}")
                    except (sqlite3.Error, OSError) as e:
                        errors.append(f"WAL checkpoint failed for {action_path.name}: {e}")
            
            elif action_type == "delete_orphan":
                if self.dry_run:
                    logs.append(f"[DRY RUN] Would remove: {action_path.name}")
                else:
                    try:
                        action_path.unlink()
                        changes["orphans_deleted"] += 1
                        logs.append(f"Removed: {action_path.name}")
                    except OSError as e:
                        errors.append(f"Failed to remove {action_path.name}: {e}")
            
            elif action_type == "delete_duplicate":
                if self.dry_run:
                    logs.append(f"[DRY RUN] Would remove duplicate: {action_path.name}")
                else:
                    try:
                        action_path.unlink()
                        changes["duplicates_deleted"] += 1
                        logs.append(f"Removed duplicate: {action_path.name}")
                    except OSError as e:
                        errors.append(f"Failed to remove {action_path.name}: {e}")
            
            elif action_type == "retention_purge":
                table = action.get("table", "logs")
                column = action.get("column", "timestamp")
                if self.dry_run:
                    logs.append(f"[DRY RUN] Would purge old rows from {table}")
                else:
                    try:
                        conn = sqlite3.connect(str(action_path))
                        cursor = conn.execute(
                            f"DELETE FROM {table} WHERE {column} < datetime('now', ?)",
                            (f"-{retention_days} days",),
                        )
                        purged = cursor.rowcount
                        conn.commit()
                        conn.close()
                        changes["rows_purged"] += purged
                        logs.append(f"Purged {purged} rows from {table}")
                    except (sqlite3.Error, OSError) as e:
                        errors.append(f"Retention purge failed for {table}: {e}")
            
            else:
                errors.append(f"Unknown action type: {action_type}")
        
        actions_taken = sum(changes.values())
        if errors and actions_taken == 0:
            status = "FAILED"
        elif errors:
            status = "PARTIAL"
        else:
            status = "SUCCESS"
        
        logs.append(f"Cleanup complete: {actions_taken} actions, {len(errors)} errors")
        
        return Report(
            cleaner_id=self.domain,
            timestamp=datetime.now().isoformat(),
            status=status,
            actions_taken=actions_taken,
            changes=changes,
            errors=errors,
            logs=logs,
        )
    
    def rollback(self) -> RollbackResult:
        """Rollback database cleanup operations.
        
        Note: Database VACUUM and WAL checkpoint operations cannot be
        fully rolled back. Returns PARTIAL to indicate limited support.
        
        Returns:
            RollbackResult indicating partial rollback capability
        """
        return RollbackResult(
            cleaner_id=self.domain,
            timestamp=datetime.now().isoformat(),
            status="PARTIAL",
            files_restored=0,
            errors=["Database VACUUM operations cannot be rolled back"],
        )


__all__ = [
    "DatabaseBloatCleaner",
]
