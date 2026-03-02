"""Database Migration Cleaner

Detects and migrates database files from repository root to proper locations.

AC-VACUUM-002: Database file organization
Author: CORTEX Framework
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import shutil

# Import base classes from parent cleaners.py module
# Avoid importing from cleaners package to prevent circular imports
import sys

# Add parent directory to path to import cleaners.py
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import from cleaners.py (not the cleaners/ package)
import cleaners

# Use the base classes from cleaners module
Analysis = cleaners.Analysis
CleanerInterface = cleaners.CleanerInterface
Report = cleaners.Report
RollbackResult = cleaners.RollbackResult


class DatabaseMigrationCleaner(CleanerInterface):
    """Cleaner for migrating database files to proper locations."""

    # Database file to target directory mapping
    DB_MIGRATIONS = {
        "intelligence_audit.db": "cortex/orchestrators/intelligence/",
        "contract_validation_audit.db": "cortex/wiring/registry/",
        "observability_audit.db": "cortex/orchestrators/observability/",
        "solid_audit.db": "cortex/orchestrators/quality/",
    }

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize database migration cleaner.

        Args:
            config: Configuration with repo_root and optional database_paths
        """
        super().__init__(config)
        self.repo_root = Path(config.get("repo_root", "."))

        # Allow custom DB path mappings
        custom_paths = config.get("database_paths", {})
        if custom_paths:
            self.db_migrations = {}
            for key, path in custom_paths.items():
                db_name = f"{key}_audit.db" if not key.endswith(".db") else key
                self.db_migrations[db_name] = path
        else:
            self.db_migrations = self.DB_MIGRATIONS.copy()

    @property
    def name(self) -> str:
        """Get cleaner name."""
        return "DatabaseMigrationCleaner"

    @property
    def version(self) -> str:
        """Get cleaner version."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Get cleaner domain."""
        return "database_migration"

    def analyze(self) -> Analysis:
        """Analyze repository for database files in root.

        Returns:
            Analysis with detected database files
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        issues: List[Dict[str, Any]] = []

        # Scan root directory for .db files
        for db_file in self.repo_root.glob("*.db"):
            if db_file.name in self.db_migrations:
                target_dir = self.repo_root / self.db_migrations[db_file.name]

                issues.append({
                    "file": str(db_file),
                    "target": str(target_dir / db_file.name),
                    "size_kb": db_file.stat().st_size / 1024,
                })

                logs.append(f"Found {db_file.name} → {target_dir}")

        plan = {
            "actions": [
                {
                    "action": "move",
                    "source": issue["file"],
                    "target": issue["target"],
                }
                for issue in issues
            ]
        }

        return Analysis(
            cleaner_id=self.domain,
            timestamp=timestamp,
            files_scanned=len(list(self.repo_root.glob("*.db"))),
            issues_found=len(issues),
            plan=plan,
            logs=logs,
        )

    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute database migration plan.

        Args:
            plan: Migration plan from analyze()

        Returns:
            Execution report
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        errors: List[str] = []
        actions_taken = 0
        changes: Dict[str, Any] = {"moved_files": []}

        for action in plan.get("actions", []):
            if action["action"] == "move":
                source = Path(action["source"])
                target = Path(action["target"])

                try:
                    if self.dry_run:
                        logs.append(f"[DRY RUN] Would move {source} → {target}")
                        actions_taken += 1
                    else:
                        # Create target directory if needed
                        target.parent.mkdir(parents=True, exist_ok=True)

                        # Move file
                        shutil.move(str(source), str(target))

                        changes["moved_files"].append({
                            "from": str(source),
                            "to": str(target),
                        })

                        logs.append(f"Moved {source.name} → {target}")
                        actions_taken += 1

                except Exception as e:
                    errors.append(f"Failed to move {source}: {e}")

        status = "SUCCESS" if not errors else "PARTIAL"

        return Report(
            cleaner_id=self.domain,
            timestamp=timestamp,
            status=status,
            actions_taken=actions_taken,
            changes=changes,
            errors=errors,
            logs=logs,
        )

    def rollback(self) -> RollbackResult:
        """Rollback database migrations (not implemented for safety).

        Returns:
            Rollback result indicating manual intervention needed
        """
        return RollbackResult(
            cleaner_id=self.domain,
            timestamp=datetime.now().isoformat(),
            status="NOT_IMPLEMENTED",
            files_restored=0,
            errors=["Database rollback requires manual intervention"],
        )


__all__ = ["DatabaseMigrationCleaner"]
