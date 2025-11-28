"""
Upgrade Orchestrator - Auto-upgrade CORTEX from origin/main
Addresses Gap #10: Deployment to local folder requires manual distribution

Purpose:
- Checks for available CORTEX updates
- Backs up brain data before upgrade
- Pulls from origin/main
- Runs post-upgrade migrations
- Provides rollback on failure
- Shows 'What's New' with features added since user's version

Version: 1.1 (Added Enhancement Catalog integration)
Author: GitHub Copilot
Created: 2024-11-25
Updated: 2024-11-28 (Enhancement Catalog integration)
"""

import os
import shutil
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import logging
import json

# Enhancement Catalog imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.enhancement_catalog import EnhancementCatalog, FeatureType
from discovery.enhancement_discovery import EnhancementDiscoveryEngine

logger = logging.getLogger(__name__)


class UpgradeOrchestrator:
    """
    Orchestrates CORTEX auto-upgrade from remote repository.
    
    Features:
    - Version checking against origin/main
    - Brain data backup before upgrade
    - Git pull from origin/main
    - Post-upgrade migrations
    - Rollback on failure
    - Preserves user data (brain, feedback, logs)
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize upgrade orchestrator.
        
        Args:
            cortex_root: Path to CORTEX root (default: current directory)
        """
        self.cortex_root = Path(cortex_root) if cortex_root else Path.cwd()
        self.version_file = self.cortex_root / "VERSION"
        self.backup_dir = self.cortex_root / ".upgrades" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def check_for_updates(self) -> Tuple[bool, str, str]:
        """
        Check if updates are available.
        
        Returns:
            Tuple of (has_updates, current_version, latest_version)
        """
        current_version = self._get_current_version()
        
        try:
            # Fetch latest from origin
            subprocess.run(
                ['git', 'fetch', 'origin', 'main'],
                cwd=self.cortex_root,
                capture_output=True,
                check=True
            )
            
            # Get remote version
            latest_version = self._get_remote_version()
            
            # Compare versions
            has_updates = self._compare_versions(current_version, latest_version) < 0
            
            return (has_updates, current_version, latest_version)
        
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return (False, current_version, current_version)
    
    def upgrade(self, backup: bool = True, auto_migrate: bool = True) -> Tuple[bool, str]:
        """
        Upgrade CORTEX to latest version from origin/main.
        
        Args:
            backup: Create backup before upgrade (default: True)
            auto_migrate: Run migrations automatically (default: True)
        
        Returns:
            Tuple of (success, message)
        """
        # Check for updates
        has_updates, current_version, latest_version = self.check_for_updates()
        
        if not has_updates:
            return (True, f"Already on latest version: {current_version}")
        
        logger.info(f"Upgrading from {current_version} to {latest_version}")
        
        # Create backup
        backup_id = None
        if backup:
            backup_id = self._create_backup()
            if not backup_id:
                return (False, "Failed to create backup")
            logger.info(f"Created backup: {backup_id}")
        
        # Save current branch
        current_branch = self._get_current_branch()
        
        try:
            # Pull from origin/main
            logger.info("Pulling updates from origin/main...")
            
            # If on main, just pull
            if current_branch == 'main':
                result = subprocess.run(
                    ['git', 'pull', 'origin', 'main'],
                    cwd=self.cortex_root,
                    capture_output=True,
                    text=True,
                    check=False
                )
            else:
                # Merge origin/main into current branch
                result = subprocess.run(
                    ['git', 'merge', 'origin/main', '--no-edit'],
                    cwd=self.cortex_root,
                    capture_output=True,
                    text=True,
                    check=False
                )
            
            if result.returncode != 0:
                error_msg = f"Git operation failed: {result.stderr}"
                logger.error(error_msg)
                
                # Rollback
                if backup_id:
                    self._rollback(backup_id)
                
                return (False, error_msg)
            
            logger.info("✅ Updates pulled successfully")
            
            # Run migrations if requested
            if auto_migrate:
                migration_success = self._run_migrations()
                if not migration_success:
                    logger.warning("⚠️  Some migrations failed (non-critical)")
            
            # Verify upgrade
            new_version = self._get_current_version()
            if new_version == latest_version:
                # Generate "What's New" report
                whats_new = self._generate_whats_new(current_version, new_version)
                
                message = f"✅ Upgraded successfully: {current_version} → {new_version}"
                if backup_id:
                    message += f"\n📦 Backup created: {backup_id}"
                if whats_new:
                    message += f"\n\n{whats_new}"
                
                # Log upgrade review in catalog
                self._log_upgrade_review(new_version)
                
                return (True, message)
            else:
                logger.warning(f"Version mismatch after upgrade: expected {latest_version}, got {new_version}")
                return (True, f"Upgrade completed but version mismatch detected")
        
        except Exception as e:
            error_msg = f"Upgrade failed: {e}"
            logger.error(error_msg)
            
            # Rollback
            if backup_id:
                self._rollback(backup_id)
            
            return (False, error_msg)
    
    def _get_current_version(self) -> str:
        """Get current CORTEX version."""
        try:
            if self.version_file.exists():
                return self.version_file.read_text(encoding='utf-8').strip()
            return "unknown"
        except Exception:
            return "unknown"
    
    def _get_remote_version(self) -> str:
        """Get remote version from origin/main."""
        try:
            result = subprocess.run(
                ['git', 'show', 'origin/main:VERSION'],
                cwd=self.cortex_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare version strings.
        
        Returns:
            -1 if v1 < v2, 0 if equal, 1 if v1 > v2
        """
        try:
            # Parse semantic versions (e.g., "3.2.0")
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            # Pad to same length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            # Compare
            for i in range(max_len):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1
            
            return 0
        except Exception:
            # Fallback to string comparison
            return -1 if v1 < v2 else (1 if v1 > v2 else 0)
    
    def _get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.cortex_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return "main"
    
    def _create_backup(self) -> Optional[str]:
        """
        Create backup of brain data and user files.
        
        Returns:
            Backup ID (timestamp) or None if failed
        """
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / backup_id
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup items
            items_to_backup = [
                'cortex-brain/feedback',
                'cortex-brain/working_memory.db',
                'cortex-brain/config',
                'cortex-brain/documents/planning',
                'logs',
                'VERSION'
            ]
            
            for item in items_to_backup:
                source = self.cortex_root / item
                if source.exists():
                    dest = backup_path / item
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source.is_file():
                        shutil.copy2(source, dest)
                    elif source.is_dir():
                        shutil.copytree(source, dest, dirs_exist_ok=True)
            
            # Save metadata
            metadata = {
                'backup_id': backup_id,
                'timestamp': datetime.now().isoformat(),
                'version': self._get_current_version(),
                'branch': self._get_current_branch(),
                'items': items_to_backup
            }
            
            metadata_file = backup_path / 'backup_metadata.json'
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            
            logger.info(f"Backup created: {backup_path}")
            return backup_id
        
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def _rollback(self, backup_id: str) -> bool:
        """
        Rollback to backup.
        
        Args:
            backup_id: Backup identifier
        
        Returns:
            True if successful, False otherwise
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        try:
            logger.info(f"Rolling back to backup: {backup_id}")
            
            # Load metadata
            metadata_file = backup_path / 'backup_metadata.json'
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                items = metadata.get('items', [])
            else:
                # Fallback to standard items
                items = [
                    'cortex-brain/feedback',
                    'cortex-brain/working_memory.db',
                    'cortex-brain/config',
                    'cortex-brain/documents/planning',
                    'logs',
                    'VERSION'
                ]
            
            # Restore items
            for item in items:
                source = backup_path / item
                dest = self.cortex_root / item
                
                if source.exists():
                    # Remove existing
                    if dest.exists():
                        if dest.is_file():
                            dest.unlink()
                        elif dest.is_dir():
                            shutil.rmtree(dest)
                    
                    # Restore from backup
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if source.is_file():
                        shutil.copy2(source, dest)
                    elif source.is_dir():
                        shutil.copytree(source, dest, dirs_exist_ok=True)
            
            logger.info("✅ Rollback completed")
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _run_migrations(self) -> bool:
        """
        Run post-upgrade migrations.
        
        Returns:
            True if all migrations succeeded, False if any failed
        """
        migrations_dir = self.cortex_root / "cortex-brain" / "migrations"
        
        if not migrations_dir.exists():
            logger.info("No migrations directory found")
            return True
        
        # Get list of migration files
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.info("No migrations to run")
            return True
        
        logger.info(f"Found {len(migration_files)} migration(s)")
        
        # Connect to database
        db_path = self.cortex_root / "cortex-brain" / "working_memory.db"
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create migrations tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name TEXT UNIQUE NOT NULL,
                    applied_at TEXT NOT NULL
                )
            """)
            
            success = True
            
            for migration_file in migration_files:
                migration_name = migration_file.name
                
                # Check if already applied
                cursor.execute(
                    "SELECT 1 FROM schema_migrations WHERE migration_name = ?",
                    (migration_name,)
                )
                
                if cursor.fetchone():
                    logger.info(f"⏭️  Skipping (already applied): {migration_name}")
                    continue
                
                # Run migration
                try:
                    logger.info(f"🔄 Running migration: {migration_name}")
                    sql = migration_file.read_text(encoding='utf-8')
                    cursor.executescript(sql)
                    
                    # Record migration
                    cursor.execute(
                        "INSERT INTO schema_migrations (migration_name, applied_at) VALUES (?, ?)",
                        (migration_name, datetime.now().isoformat())
                    )
                    
                    conn.commit()
                    logger.info(f"✅ Migration applied: {migration_name}")
                
                except Exception as e:
                    logger.error(f"❌ Migration failed: {migration_name}: {e}")
                    success = False
                    conn.rollback()
            
            conn.close()
            return success
        
        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, str]]:
        """
        List available backups.
        
        Returns:
            List of backup metadata dictionaries
        """
        backups = []
        
        for backup_path in self.backup_dir.iterdir():
            if not backup_path.is_dir():
                continue
            
            metadata_file = backup_path / 'backup_metadata.json'
            if metadata_file.exists():
                try:
                    metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                    backups.append(metadata)
                except Exception:
                    pass
        
        return sorted(backups, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    def _generate_whats_new(self, from_version: str, to_version: str) -> str:
        """
        Generate 'What's New' report showing features added since from_version.
        
        Args:
            from_version: Starting version (user's old version)
            to_version: Target version (new version)
        
        Returns:
            Formatted markdown string with new features grouped by category
        """
        try:
            catalog = EnhancementCatalog()
            
            # Get last upgrade review timestamp
            last_review = catalog.get_last_review_timestamp('upgrade')
            
            # Discover new features since last review
            engine = EnhancementDiscoveryEngine(self.cortex_root)
            discovered = engine.discover_since(last_review) if last_review else engine.discover_all()
            
            if not discovered:
                return ""
            
            # Update catalog
            for feature in discovered:
                catalog.add_feature(
                    name=feature.name,
                    feature_type=self._map_feature_type(feature.type),
                    description=feature.description or "",
                    source=feature.source
                )
            
            # Group by type
            by_type: Dict[str, List] = {}
            for feature in discovered:
                ftype = feature.type
                if ftype not in by_type:
                    by_type[ftype] = []
                by_type[ftype].append(feature)
            
            # Build report
            lines = [""]
            lines.append("📢 **What's New in this Version:**")
            lines.append("")
            lines.append(f"🎯 **{len(discovered)} new feature(s)** added since version {from_version}")
            lines.append("")
            
            # Sort by type (operations first, then agents, etc.)
            type_order = ['operation', 'agent', 'orchestrator', 'workflow', 'template', 'documentation', 'integration', 'utility']
            sorted_types = sorted(by_type.keys(), key=lambda t: type_order.index(t) if t in type_order else 999)
            
            for ftype in sorted_types:
                features = by_type[ftype]
                lines.append(f"**{ftype.capitalize()}s ({len(features)}):**")
                for feature in sorted(features, key=lambda f: f.name):
                    lines.append(f"  • {feature.name} - {feature.description or 'No description'}")
                lines.append("")
            
            lines.append("💡 **Tip:** Say 'help' to explore new capabilities")
            
            return "\n".join(lines)
        
        except Exception as e:
            logger.error(f"Failed to generate What's New report: {e}")
            return ""
    
    def _map_feature_type(self, discovery_type: str) -> FeatureType:
        """
        Map discovery type string to FeatureType enum.
        
        Args:
            discovery_type: Discovery type string
        
        Returns:
            FeatureType enum value
        """
        mapping = {
            'operation': FeatureType.OPERATION,
            'agent': FeatureType.AGENT,
            'orchestrator': FeatureType.ORCHESTRATOR,
            'workflow': FeatureType.WORKFLOW,
            'template': FeatureType.TEMPLATE,
            'documentation': FeatureType.DOCUMENTATION,
            'integration': FeatureType.INTEGRATION,
            'utility': FeatureType.UTILITY,
        }
        return mapping.get(discovery_type.lower(), FeatureType.UTILITY)
    
    def _log_upgrade_review(self, version: str) -> None:
        """
        Log upgrade review event in catalog.
        
        Args:
            version: Version upgraded to
        """
        try:
            catalog = EnhancementCatalog()
            catalog.log_review('upgrade', metadata={'version': version})
            logger.info(f"Logged upgrade review for version {version}")
        except Exception as e:
            logger.error(f"Failed to log upgrade review: {e}")


def main():
    """CLI entry point for upgrade operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Upgrade Orchestrator")
    parser.add_argument('--check', action='store_true', help="Check for updates")
    parser.add_argument('--upgrade', action='store_true', help="Upgrade to latest version")
    parser.add_argument('--no-backup', action='store_true', help="Skip backup before upgrade")
    parser.add_argument('--list-backups', action='store_true', help="List available backups")
    parser.add_argument('--rollback', type=str, metavar='BACKUP_ID', help="Rollback to backup")
    
    args = parser.parse_args()
    
    orchestrator = UpgradeOrchestrator()
    
    if args.check:
        has_updates, current, latest = orchestrator.check_for_updates()
        print(f"Current version: {current}")
        print(f"Latest version: {latest}")
        if has_updates:
            print("✅ Updates available!")
        else:
            print("ℹ️  Already on latest version")
    
    elif args.upgrade:
        backup = not args.no_backup
        success, message = orchestrator.upgrade(backup=backup)
        print(message)
        exit(0 if success else 1)
    
    elif args.list_backups:
        backups = orchestrator.list_backups()
        if not backups:
            print("No backups found")
        else:
            print(f"Found {len(backups)} backup(s):\n")
            for backup in backups:
                print(f"  ID: {backup['backup_id']}")
                print(f"  Version: {backup['version']}")
                print(f"  Date: {backup['timestamp']}")
                print(f"  Branch: {backup['branch']}")
                print()
    
    elif args.rollback:
        success = orchestrator._rollback(args.rollback)
        if success:
            print(f"✅ Rolled back to backup: {args.rollback}")
        else:
            print(f"❌ Rollback failed")
        exit(0 if success else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
