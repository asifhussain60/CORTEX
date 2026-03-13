"""
Root Database Cleaner

Purpose:
    Removes orphaned database files from repository root while
    preserving subdirectory databases.

Authority:
    - AC-VACUUM-REFACTOR-001: Golden test-driven refactoring
    - CORE-008: TDD
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings

Author: CORTEX Architect
Date: 2026-02-15
"""

import shutil
from typing import Dict, Any
from .base import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
)


class RootDatabaseCleaner(CleanerInterface):
    """
    Cleaner for orphaned root database files.

    Deletes:
        - intelligence_audit.db
        - contract_validation_audit.db
        - observability_audit.db
        - solid_audit.db

    Preserves:
        - All databases in subdirectories

    Warns:
        - Unknown database files in root
    """

    # Known audit databases that should be in subdirectories
    KNOWN_ROOT_DATABASES = [
        "intelligence_audit.db",
        "contract_validation_audit.db",
        "observability_audit.db",
        "solid_audit.db",
    ]

    @property
    def name(self) -> str:
        """Return cleaner name."""
        return "Root Database Cleaner"

    @property
    def version(self) -> str:
        """Return cleaner version."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Return cleaner domain."""
        return "root_database"

    def analyze(self) -> Analysis:
        """
        Scan for orphaned root database files.

        Returns:
            Analysis with databases to delete
        """
        self._log("Scanning for root database files...")

        files_to_delete = []
        warnings = []
        files_scanned = 0

        # Check for known database files in root
        files_to_delete = []
        actions = []
        database_paths = self.config.get("database_paths", {})

        for db_name in self.KNOWN_ROOT_DATABASES:
            db_path = self.repo_root / db_name
            if db_path.exists():
                files_to_delete.append(db_name)
                files_scanned += 1

                # If database_paths configured, create action with target
                if database_paths:
                    # Extract domain from db name (e.g., "intelligence_audit.db" -> "intelligence")
                    domain = db_name.replace("_audit.db", "").replace(".db", "")
                    target_path = database_paths.get(domain, "unknown")
                    actions.append(f"{db_name} -> {target_path}")
                else:
                    actions.append(db_name)

        # Check for unknown .db files in root — these are also issues to flag
        for db_file in self.repo_root.glob("*.db"):
            files_scanned += 1
            if db_file.name not in self.KNOWN_ROOT_DATABASES:
                files_to_delete.append(db_file.name)
                warnings.append(f"{db_file.name}: Unknown database file in root")

        plan = {
            "actions": actions if actions else files_to_delete,  # Use enriched actions if available
            "files_to_delete": files_to_delete,  # Keep for backward compat
            "warnings": warnings,
            "known_databases": self.KNOWN_ROOT_DATABASES,
        }

        self._log(f"Found {len(files_to_delete)} database files to delete")
        if warnings:
            for warning in warnings:
                self._log(f"WARNING: {warning}")

        logs = [
            f"Scanned {files_scanned} database files",
            f"Found {len(files_to_delete)} to delete",
            f"Generated {len(warnings)} warnings",
        ]
        for f in files_to_delete:
            logs.append(f"Flagged for deletion: {f}")
        for w in warnings:
            logs.append(f"WARNING: {w}")

        return Analysis(
            cleaner_id=self.domain,
            timestamp=self._timestamp(),
            files_scanned=files_scanned,
            issues_found=len(files_to_delete),
            plan=plan,
            logs=logs,
        )

    def execute(self, plan: Dict[str, Any]) -> Report:
        """
        Execute database cleanup.

        Args:
            plan: Execution plan from analyze()

        Returns:
            Report with deletion results
        """
        self._log("Executing root database cleanup...")

        files_to_delete = plan.get("files_to_delete", [])
        warnings = plan.get("warnings", [])
        deleted_count = 0
        errors = []
        logs = []

        # Create snapshot directory before any deletions (non-dry-run only)
        snapshot_dir = self.repo_root / ".vacuum_snapshots" / "root_database"
        if files_to_delete and not self.dry_run:
            snapshot_dir.mkdir(parents=True, exist_ok=True)

        for db_name in files_to_delete:
            # Support both plain filenames and full paths in the plan
            db_path = self.repo_root / db_name

            if self.dry_run:
                logs.append(f"[DRY RUN] Would delete: {db_name}")
                continue

            try:
                if db_path.exists():
                    # Snapshot before deletion
                    shutil.copy2(db_path, snapshot_dir / db_path.name)
                    db_path.unlink()
                    deleted_count += 1
                    logs.append(f"Deleted: {db_name}")
                    self._log(f"Deleted: {db_name}")
                else:
                    logs.append(f"Already deleted: {db_name}")
            except Exception as e:
                error_msg = f"Failed to delete {db_name}: {e}"
                errors.append(error_msg)
                logs.append(error_msg)
                self._log(error_msg)

        # Add warnings to logs
        for warning in warnings:
            logs.append(f"WARNING: {warning}")

        if self.dry_run:
            status = "DRY_RUN"
        elif len(errors) == 0:
            status = "SUCCESS"
        elif deleted_count == 0:
            status = "FAILED"
        else:
            status = "PARTIAL"

        return Report(
            cleaner_id=self.domain,
            timestamp=self._timestamp(),
            status=status,
            actions_taken=deleted_count,
            changes={"deleted": deleted_count},
            errors=errors,
            logs=logs,
        )

    def rollback(self) -> RollbackResult:
        """
        Rollback database cleanup by restoring files from snapshot.

        Returns:
            RollbackResult with restoration status
        """
        snapshot_dir = self.repo_root / ".vacuum_snapshots" / "root_database"

        if not snapshot_dir.exists():
            return RollbackResult(
                cleaner_id=self.domain,
                timestamp=self._timestamp(),
                status="SUCCESS",
                files_restored=0,
                errors=[],
            )

        restored = 0
        errors = []
        for snapshot_file in snapshot_dir.iterdir():
            dest = self.repo_root / snapshot_file.name
            try:
                shutil.copy2(snapshot_file, dest)
                restored += 1
                self._log(f"Restored: {snapshot_file.name}")
            except Exception as e:
                errors.append(f"Failed to restore {snapshot_file.name}: {e}")

        status = "SUCCESS" if not errors else "PARTIAL"
        return RollbackResult(
            cleaner_id=self.domain,
            timestamp=self._timestamp(),
            status=status,
            files_restored=restored,
            errors=errors,
        )
