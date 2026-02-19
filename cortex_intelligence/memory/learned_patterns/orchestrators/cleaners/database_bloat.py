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
        return "DatabaseBloatCleaner"
    
    @property
    def version(self) -> str:
        """Return cleaner version."""
        return "1.0.0"
    
    @property
    def domain(self) -> str:
        """Return cleaner domain."""
        return "database_cleanup"
    
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
        
        Returns:
            Analysis with detected issues and cleanup plan
        """
        start_time = time.time()
        logs = []
        plan: Dict[str, Any] = {
            "databases_to_vacuum": [],
            "wal_files_to_checkpoint": [],
            "orphaned_files_to_remove": [],
        }
        
        logs.append(f"Scanning {self.repo_root} for database bloat...")
        
        # Find all database files
        db_files = list(self.repo_root.rglob("*.db"))
        files_scanned = len(db_files)
        
        for db_path in db_files:
            # Skip production database if configured
            if self.skip_production_db and db_path.name == "governance.db":
                logs.append(f"Skipping production database: {db_path.name}")
                continue
            
            # Skip test databases
            if "test" in str(db_path).lower() or ".pytest_cache" in str(db_path):
                continue
            
            # Check database size
            size_mb = db_path.stat().st_size / (1024 * 1024)
            
            if size_mb > self.bloat_threshold_mb:
                plan["databases_to_vacuum"].append({
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
                        plan["wal_files_to_checkpoint"].append({
                            "db_path": str(db_path),
                            "wal_path": str(wal_path),
                            "wal_ratio": wal_ratio,
                            "reason": f"WAL ratio {wal_ratio:.2%} exceeds threshold {self.wal_ratio_threshold:.0%}",
                        })
                        logs.append(f"Large WAL journal: {wal_path.name} ({wal_ratio:.2%} of DB)")
        
        # Find orphaned WAL/SHM files (no corresponding .db)
        for wal_path in self.repo_root.rglob("*.db-wal"):
            db_path = wal_path.with_suffix(".db")
            if not db_path.exists():
                plan["orphaned_files_to_remove"].append(str(wal_path))
                logs.append(f"Orphaned WAL file: {wal_path.name}")
        
        for shm_path in self.repo_root.rglob("*.db-shm"):
            db_path = shm_path.with_suffix(".db")
            if not db_path.exists():
                plan["orphaned_files_to_remove"].append(str(shm_path))
                logs.append(f"Orphaned SHM file: {shm_path.name}")
        
        issues_found = (
            len(plan["databases_to_vacuum"])
            + len(plan["wal_files_to_checkpoint"])
            + len(plan["orphaned_files_to_remove"])
        )
        
        logs.append(f"Analysis complete: {issues_found} issues found in {files_scanned} databases")
        
        return Analysis(
            cleaner_id=self.domain,
            timestamp=datetime.now().isoformat(),
            files_scanned=files_scanned,
            issues_found=issues_found,
            plan=plan,
            logs=logs,
        )
    
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute database cleanup plan.
        
        Performs:
        1. VACUUM on bloated databases
        2. WAL checkpoint on large journals
        3. Remove orphaned WAL/SHM files
        
        Args:
            plan: Cleanup plan from analyze()
        
        Returns:
            Report with actions taken and results
        """
        start_time = time.time()
        logs = []
        errors = []
        changes: Dict[str, int] = {
            "vacuumed": 0,
            "checkpointed": 0,
            "orphans_removed": 0,
        }
        
        if self.dry_run:
            logs.append("DRY RUN - No changes will be made")
        
        # VACUUM bloated databases
        for db_info in plan.get("databases_to_vacuum", []):
            db_path = Path(db_info["path"])
            
            if self.dry_run:
                logs.append(f"[DRY RUN] Would VACUUM: {db_path.name}")
                changes["vacuumed"] += 1
            else:
                try:
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("VACUUM")
                    conn.close()
                    
                    new_size_mb = db_path.stat().st_size / (1024 * 1024)
                    saved_mb = db_info["size_mb"] - new_size_mb
                    
                    logs.append(f"VACUUM completed: {db_path.name} (saved {saved_mb:.2f}MB)")
                    changes["vacuumed"] += 1
                except sqlite3.Error as e:
                    errors.append(f"VACUUM failed for {db_path.name}: {e}")
        
        # Checkpoint WAL journals
        for wal_info in plan.get("wal_files_to_checkpoint", []):
            db_path = Path(wal_info["db_path"])
            
            if self.dry_run:
                logs.append(f"[DRY RUN] Would checkpoint WAL: {db_path.name}")
                changes["checkpointed"] += 1
            else:
                try:
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    conn.close()
                    
                    logs.append(f"WAL checkpoint completed: {db_path.name}")
                    changes["checkpointed"] += 1
                except sqlite3.Error as e:
                    errors.append(f"WAL checkpoint failed for {db_path.name}: {e}")
        
        # Remove orphaned files
        for orphan_path_str in plan.get("orphaned_files_to_remove", []):
            orphan_path = Path(orphan_path_str)
            
            if self.dry_run:
                logs.append(f"[DRY RUN] Would remove: {orphan_path.name}")
                changes["orphans_removed"] += 1
            else:
                try:
                    orphan_path.unlink()
                    logs.append(f"Removed orphaned file: {orphan_path.name}")
                    changes["orphans_removed"] += 1
                except OSError as e:
                    errors.append(f"Failed to remove {orphan_path.name}: {e}")
        
        actions_taken = sum(changes.values())
        status = "SUCCESS" if not errors else ("PARTIAL" if actions_taken > 0 else "FAILED")
        
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
        rolled back. This method exists for interface compliance.
        
        Returns:
            RollbackResult indicating no rollback possible
        """
        return RollbackResult(
            cleaner_id=self.domain,
            timestamp=datetime.now().isoformat(),
            status="FAILED",
            files_restored=0,
            errors=["Database VACUUM operations cannot be rolled back"],
        )


__all__ = [
    "DatabaseBloatCleaner",
]
