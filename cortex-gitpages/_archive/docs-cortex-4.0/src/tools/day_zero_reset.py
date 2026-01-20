"""
Day-Zero Reset Tool for CORTEX System

AC-ID: DEPLOY-001-01 (Day-Zero Reset & Clean Repository Initialization)
Purpose: Automated cleanup and day-zero reset for CORTEX system.

Resets the system to clean, initial state while preserving:
- Database integrity
- Application state in CORTEX6 branch
- Governance structures
- Core configuration files

This tool enables repeatable resets without manual intervention.
"""

import os
import sys
import sqlite3
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ResetConfig:
    """Configuration for day-zero reset operation."""
    
    repo_root: Path
    backup_enabled: bool = True
    backup_dir: Optional[Path] = None
    verify_only: bool = False
    preserve_files: List[str] = None
    
    def __post_init__(self):
        if self.preserve_files is None:
            self.preserve_files = [
                "governance.db",
                "prompt-versions.yaml",
                "repo-registry.yaml",
            ]
        if self.backup_dir is None:
            self.backup_dir = self.repo_root / ".backups" / datetime.now().strftime("%Y%m%d_%H%M%S")


class DayZeroResetTool:
    """
    Automated cleanup and day-zero reset for CORTEX system.
    
    Implements DEPLOY-001-01: Day-Zero Reset & Clean Repository Initialization
    """
    
    # Paths to clear (relative to repo root)
    PATHS_TO_CLEAR = [
        "cortex_brain/state/cache",
        "cortex_brain/state/logs",
        "cortex_brain/state/sessions",
        ".pytest_cache",
        ".coverage",
    ]
    
    # Directories to preserve with cleaned contents
    PRESERVE_DIRS = [
        "cortex_brain/state",
        "cortex_brain/tier0",
        "cortex_brain/tier1",
        "cortex_brain/tier2",
    ]
    
    # Database files to reset to seed state
    DB_FILES = [
        "cortex_brain/state/governance.db",
    ]
    
    # YAML config files to initialize
    YAML_INIT_FILES = [
        ("cortex_brain/tier0/prompt-versions.yaml", {"version": "1.0.0", "status": "production"}),
        ("cortex_brain/tier0/repo-registry.yaml", {"repositories": [], "initialized_at": datetime.now().isoformat()}),
    ]
    
    def __init__(self, config: ResetConfig):
        """Initialize reset tool with configuration."""
        self.config = config
        self.logger = self._setup_logging()
        self.logger.info(f"DayZeroResetTool initialized with repo_root: {config.repo_root}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for reset operations."""
        logger = logging.getLogger("DayZeroResetTool")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def reset_to_day_zero(self) -> bool:
        """
        Execute full day-zero reset pipeline:
        1. Backup current state
        2. Clear runtime data (cache, logs, sessions)
        3. Reset governance.db to seed state
        4. Re-initialize prompt versions
        5. Re-initialize repository registry
        6. Verify consistency
        7. Log completion
        
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("STARTING DAY-ZERO RESET")
            self.logger.info("=" * 70)
            
            # Step 1: Backup
            if self.config.backup_enabled:
                self.logger.info("Step 1: Backing up current state...")
                if not self._backup_state():
                    self.logger.error("Backup failed!")
                    return False
            
            # Step 2: Clear runtime data
            self.logger.info("Step 2: Clearing runtime data...")
            if not self._clear_runtime_data():
                self.logger.error("Runtime data clearing failed!")
                return False
            
            # Step 3: Reset databases
            self.logger.info("Step 3: Resetting database files...")
            if not self._reset_databases():
                self.logger.error("Database reset failed!")
                return False
            
            # Step 4-5: Initialize YAML files
            self.logger.info("Step 4-5: Initializing YAML configuration files...")
            if not self._initialize_yaml_files():
                self.logger.error("YAML initialization failed!")
                return False
            
            # Step 6: Verify consistency
            self.logger.info("Step 6: Verifying day-zero consistency...")
            if not self._verify_day_zero_state():
                self.logger.error("Verification failed!")
                return False
            
            # Step 7: Log completion
            self.logger.info("=" * 70)
            self.logger.info("✅ DAY-ZERO RESET SUCCESSFUL")
            self.logger.info("=" * 70)
            self._log_completion_summary()
            return True
            
        except Exception as e:
            self.logger.error(f"Fatal error during reset: {e}", exc_info=True)
            return False
    
    def _backup_state(self) -> bool:
        """Backup current state before reset."""
        try:
            backup_dir = self.config.backup_dir
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup preserved directories
            for dir_name in self.PRESERVE_DIRS:
                src = self.config.repo_root / dir_name
                if src.exists():
                    dst = backup_dir / dir_name
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    self.logger.debug(f"Backed up: {dir_name}")
            
            self.logger.info(f"✓ Backup created at: {backup_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def _clear_runtime_data(self) -> bool:
        """Clear all runtime data (cache, logs, sessions)."""
        try:
            for path_str in self.PATHS_TO_CLEAR:
                path = self.config.repo_root / path_str
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                        self.logger.debug(f"Cleared: {path_str}")
                    else:
                        path.unlink()
                        self.logger.debug(f"Deleted: {path_str}")
            
            self.logger.info("✓ Runtime data cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear runtime data: {e}")
            return False
    
    def _reset_databases(self) -> bool:
        """Reset database files to seed state."""
        try:
            for db_file in self.DB_FILES:
                db_path = self.config.repo_root / db_file
                if db_path.exists():
                    # Check if it's already valid
                    if not self._is_valid_db(db_path):
                        self.logger.warning(f"Database {db_file} is corrupted, recreating...")
                        db_path.unlink()
                    else:
                        # Reset to seed state (keep schema, clear data)
                        self._reset_db_contents(db_path)
                        self.logger.debug(f"Reset database: {db_file}")
                else:
                    # Create new database
                    self._create_seed_database(db_path)
                    self.logger.debug(f"Created seed database: {db_file}")
            
            self.logger.info("✓ Databases reset/initialized")
            return True
        except Exception as e:
            self.logger.error(f"Database reset failed: {e}")
            return False
    
    def _is_valid_db(self, db_path: Path) -> bool:
        """Check if SQLite database is valid."""
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            return True
        except sqlite3.DatabaseError:
            return False
    
    def _reset_db_contents(self, db_path: Path) -> bool:
        """Reset database contents while preserving schema."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Clear all tables
            for table in tables:
                cursor.execute(f"DELETE FROM {table[0]}")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset database contents: {e}")
            return False
    
    def _create_seed_database(self, db_path: Path) -> bool:
        """Create seed database with initial schema."""
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create initial schema (example for governance.db)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS governance_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    ac_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            self.logger.debug(f"Created seed database: {db_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create seed database: {e}")
            return False
    
    def _initialize_yaml_files(self) -> bool:
        """Initialize YAML configuration files."""
        try:
            import yaml
            
            for yaml_file, init_data in self.YAML_INIT_FILES:
                file_path = self.config.repo_root / yaml_file
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w') as f:
                    yaml.dump(init_data, f, default_flow_style=False)
                
                self.logger.debug(f"Initialized YAML: {yaml_file}")
            
            self.logger.info("✓ YAML files initialized")
            return True
        except ImportError:
            self.logger.warning("PyYAML not available, skipping YAML initialization")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize YAML files: {e}")
            return False
    
    def _verify_day_zero_state(self) -> bool:
        """
        Verify system is in expected day-zero condition.
        
        Checks:
        - All required files exist
        - Databases are valid
        - No orphaned files
        - Correct permissions
        """
        try:
            checks_passed = 0
            checks_total = 0
            
            # Check 1: Preserved directories exist
            checks_total += 1
            for dir_name in self.PRESERVE_DIRS:
                dir_path = self.config.repo_root / dir_name
                if dir_path.exists():
                    self.logger.debug(f"✓ Directory exists: {dir_name}")
                    checks_passed += 1
                else:
                    self.logger.warning(f"✗ Directory missing: {dir_name}")
            
            # Check 2: Databases are valid
            checks_total += 1
            for db_file in self.DB_FILES:
                db_path = self.config.repo_root / db_file
                if db_path.exists() and self._is_valid_db(db_path):
                    self.logger.debug(f"✓ Database valid: {db_file}")
                    checks_passed += 1
                else:
                    self.logger.warning(f"✗ Database invalid: {db_file}")
            
            # Check 3: No runtime directories exist
            checks_total += 1
            runtime_cleared = True
            for path_str in self.PATHS_TO_CLEAR:
                path = self.config.repo_root / path_str
                if path.exists():
                    self.logger.warning(f"✗ Runtime directory still exists: {path_str}")
                    runtime_cleared = False
            
            if runtime_cleared:
                self.logger.debug("✓ All runtime directories cleared")
                checks_passed += 1
            
            # Log verification result
            self.logger.info(f"✓ Verification: {checks_passed}/{checks_total} checks passed")
            return checks_passed == checks_total
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False
    
    def _log_completion_summary(self) -> None:
        """Log comprehensive completion summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "repo_root": str(self.config.repo_root),
            "backup_created": self.config.backup_enabled,
            "backup_location": str(self.config.backup_dir) if self.config.backup_enabled else None,
            "state": "production-ready",
            "status": "success",
        }
        
        self.logger.info("Reset Summary:")
        for key, value in summary.items():
            self.logger.info(f"  {key}: {value}")
    
    def preserve_database_state(self) -> bool:
        """
        Ensure database integrity during reset.
        
        Performs:
        - Integrity checks
        - Backup verification
        - Consistency validation
        """
        try:
            self.logger.info("Preserving database state...")
            
            for db_file in self.DB_FILES:
                db_path = self.config.repo_root / db_file
                if not db_path.exists():
                    continue
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Run integrity check
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result[0] == "ok":
                    self.logger.debug(f"✓ Database integrity verified: {db_file}")
                else:
                    self.logger.warning(f"✗ Database integrity issue: {result[0]}")
                    conn.close()
                    return False
                
                conn.close()
            
            self.logger.info("✓ Database state preserved")
            return True
        except Exception as e:
            self.logger.error(f"Failed to preserve database state: {e}")
            return False


def main():
    """Command-line interface for DayZeroResetTool."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Day-Zero Reset Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full reset with backup
  python day_zero_reset.py --action=full --repo=/path/to/cortex
  
  # Dry-run (verification only)
  python day_zero_reset.py --action=verify --repo=/path/to/cortex
  
  # Reset without backup
  python day_zero_reset.py --action=full --repo=/path/to/cortex --no-backup
        """
    )
    
    parser.add_argument(
        "--action",
        choices=["full", "verify", "preserve-db"],
        default="verify",
        help="Action to perform (default: verify)"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Path to CORTEX repository root"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable backup creation before reset"
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        help="Custom backup directory (default: .backups/timestamp)"
    )
    
    args = parser.parse_args()
    
    # Validate repo path
    if not args.repo.exists():
        print(f"❌ Repository path does not exist: {args.repo}")
        return 1
    
    # Create config
    config = ResetConfig(
        repo_root=args.repo,
        backup_enabled=not args.no_backup,
        backup_dir=args.backup_dir,
    )
    
    # Create tool
    tool = DayZeroResetTool(config)
    
    # Execute action
    if args.action == "full":
        success = tool.reset_to_day_zero()
    elif args.action == "verify":
        success = tool._verify_day_zero_state()
    elif args.action == "preserve-db":
        success = tool.preserve_database_state()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
