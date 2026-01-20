#!/usr/bin/env python3
"""
AC-AR-010-02: Automated Folder Structure Migration Script

Migrates CORTEX from dual structure (cortex_brain/ + src/) to unified structure (cortex/).
Implements 4-phase migration strategy with checksum verification and rollback capability.

Usage:
    python scripts/migrate_folder_structure.py --dry-run
    python scripts/migrate_folder_structure.py --execute
    python scripts/migrate_folder_structure.py --rollback
"""

import os
import sys
import json
import hashlib
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationMapping:
    """Represents a single file/folder migration mapping."""
    source: str
    destination: str
    file_type: str  # 'file' or 'directory'
    priority: int = 0  # Lower = execute first (for dependency ordering)


class MigrationValidator:
    """Validates preconditions and mappings before migration."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def validate_git_clean(self) -> bool:
        """Ensure working directory is clean."""
        logger.info("Validating git status...")
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                logger.error("Git working directory not clean. Commit changes first.")
                logger.error(result.stdout)
                return False
            logger.info("✓ Git status clean")
            return True
        except Exception as e:
            logger.error(f"Failed to check git status: {e}")
            return False

    def validate_current_structure(self) -> bool:
        """Verify current folder structure exists."""
        logger.info("Validating current structure...")
        cortex_brain = self.project_root / "cortex_brain"
        src = self.project_root / "src"
        
        if not cortex_brain.exists():
            logger.error(f"cortex_brain/ not found at {cortex_brain}")
            return False
        if not src.exists():
            logger.error(f"src/ not found at {src}")
            return False
        
        logger.info(f"✓ cortex_brain/ found ({self._count_files(cortex_brain)} files)")
        logger.info(f"✓ src/ found ({self._count_files(src)} files)")
        return True

    def validate_mappings(self, mappings: List[MigrationMapping]) -> bool:
        """Validate migration mappings."""
        logger.info(f"Validating {len(mappings)} migration mappings...")
        for mapping in mappings:
            source = self.project_root / mapping.source
            if not source.exists():
                logger.warning(f"Source not found: {mapping.source}")
        logger.info("✓ Mappings validated")
        return True

    @staticmethod
    def _count_files(directory: Path) -> int:
        """Count files in directory."""
        return sum(1 for _ in directory.rglob('*') if _.is_file())


class FileMigrator:
    """Executes file migration with integrity verification."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.checksums_before: Dict[str, str] = {}
        self.checksums_after: Dict[str, str] = {}
        self.migration_log: List[Dict] = []

    def safe_move(self, source: Path, dest: Path) -> bool:
        """Move file/folder with checksum verification."""
        try:
            # Hash source before move
            source_hash = self._hash_path(source)
            self.checksums_before[str(source)] = source_hash

            if self.dry_run:
                logger.info(f"[DRY-RUN] Would move: {source} → {dest}")
                return True

            # Create destination parent directories
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Move the file/folder
            logger.info(f"Moving: {source} → {dest}")
            shutil.move(str(source), str(dest))

            # Hash destination after move
            dest_hash = self._hash_path(dest)
            self.checksums_after[str(dest)] = dest_hash

            # Log the migration
            self.migration_log.append({
                'source': str(source),
                'destination': str(dest),
                'source_hash': source_hash,
                'dest_hash': dest_hash,
                'status': 'success'
            })

            return True
        except Exception as e:
            logger.error(f"Failed to move {source} to {dest}: {e}")
            self.migration_log.append({
                'source': str(source),
                'destination': str(dest),
                'status': 'failed',
                'error': str(e)
            })
            return False

    def verify_checksums(self) -> bool:
        """Verify checksums match before/after."""
        logger.info("Verifying checksums...")
        if not self.checksums_before or not self.checksums_after:
            logger.warning("No checksums to verify (dry-run mode?)")
            return True

        all_match = True
        for dest, dest_hash in self.checksums_after.items():
            # Find corresponding source
            for log_entry in self.migration_log:
                if log_entry['destination'] == dest:
                    source_hash = log_entry['source_hash']
                    if source_hash != dest_hash:
                        logger.error(f"CHECKSUM MISMATCH: {dest}")
                        logger.error(f"  Before: {source_hash}")
                        logger.error(f"  After:  {dest_hash}")
                        all_match = False
                    break

        if all_match:
            logger.info("✓ All checksums verified")
        return all_match

    def generate_report(self, report_path: Path) -> None:
        """Generate migration report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'total_moves': len(self.migration_log),
            'successful': sum(1 for m in self.migration_log if m['status'] == 'success'),
            'failed': sum(1 for m in self.migration_log if m['status'] == 'failed'),
            'migrations': self.migration_log
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"✓ Report generated: {report_path}")
        logger.info(f"  Total moves: {report['total_moves']}")
        logger.info(f"  Successful: {report['successful']}")
        logger.info(f"  Failed: {report['failed']}")

    def create_rollback_script(self, script_path: Path) -> None:
        """Create rollback script from migration log."""
        rollback_commands = []

        # Reverse the migration log order
        for log_entry in reversed(self.migration_log):
            if log_entry['status'] == 'success':
                source = log_entry['destination']
                dest = log_entry['source']
                rollback_commands.append(f"mv '{source}' '{dest}'")

        rollback_script = "#!/bin/bash\n"
        rollback_script += "# Generated rollback script - reverses migration\n"
        rollback_script += "set -e\n\n"
        for cmd in rollback_commands:
            rollback_script += f"{cmd}\n"

        with open(script_path, 'w') as f:
            f.write(rollback_script)

        os.chmod(script_path, 0o755)
        logger.info(f"✓ Rollback script created: {script_path}")

    @staticmethod
    def _hash_path(path: Path) -> str:
        """Calculate hash of file/folder contents."""
        hasher = hashlib.md5()

        if path.is_file():
            with open(path, 'rb') as f:
                hasher.update(f.read())
        elif path.is_dir():
            # For directories, hash all files
            for file_path in sorted(path.rglob('*')):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())

        return hasher.hexdigest()


class MigrationMappingBuilder:
    """Builds complete migration mapping from current structure."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def build_mappings(self) -> List[MigrationMapping]:
        """Build complete migration mappings."""
        mappings = []

        # cortex_brain/tier0/* → cortex/core/ + cortex/brain/tier0/
        mappings.extend(self._map_tier0())

        # cortex_brain/tier1/* → cortex/brain/tier1/
        mappings.extend(self._map_tier1())

        # cortex_brain/tier2/* → cortex/brain/tier2/
        mappings.extend(self._map_tier2())

        # cortex_brain/tier3/* → cortex/brain/tier3/
        mappings.extend(self._map_tier3())

        # cortex_brain/[other]/* → cortex/brain/ (special handling)
        mappings.extend(self._map_cortex_brain_other())

        # src/api/* → cortex/api/
        mappings.extend(self._map_src_api())

        # src/orchestrators/* → cortex/orchestrators/
        mappings.extend(self._map_src_orchestrators())

        # src/knowledge/* → cortex/knowledge/
        mappings.extend(self._map_src_knowledge())

        # src/infrastructure/* → cortex/infrastructure/
        mappings.extend(self._map_src_infrastructure())

        # src/tools/* → cortex/tools/
        mappings.extend(self._map_src_tools())

        # src/[other]/* → cortex/[mapped_location]/
        mappings.extend(self._map_src_other())

        # Sort by priority (tier0 first, then tier1, etc.)
        mappings.sort(key=lambda m: m.priority)

        return mappings

    def _map_tier0(self) -> List[MigrationMapping]:
        """Map tier0 files (governance, audit, schemas, state, config, registry)."""
        mappings = []
        tier0_src = self.project_root / "cortex_brain" / "tier0"

        if tier0_src.exists():
            for item in tier0_src.iterdir():
                if item.name in ['governance', 'audit', 'schemas']:
                    # governance, audit, schemas → cortex/core/
                    dest = self.project_root / "cortex" / "core" / item.name
                    mappings.append(MigrationMapping(
                        source=str(item.relative_to(self.project_root)),
                        destination=str(dest.relative_to(self.project_root)),
                        file_type='directory' if item.is_dir() else 'file',
                        priority=10
                    ))
                else:
                    # Other tier0 items → cortex/brain/tier0/
                    dest = self.project_root / "cortex" / "brain" / "tier0" / item.name
                    mappings.append(MigrationMapping(
                        source=str(item.relative_to(self.project_root)),
                        destination=str(dest.relative_to(self.project_root)),
                        file_type='directory' if item.is_dir() else 'file',
                        priority=10
                    ))

        return mappings

    def _map_tier1(self) -> List[MigrationMapping]:
        """Map tier1 files → cortex/brain/tier1/"""
        mappings = []
        tier1_src = self.project_root / "cortex_brain" / "tier1"

        if tier1_src.exists():
            for item in tier1_src.iterdir():
                dest = self.project_root / "cortex" / "brain" / "tier1" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=20
                ))

        return mappings

    def _map_tier2(self) -> List[MigrationMapping]:
        """Map tier2 files → cortex/brain/tier2/"""
        mappings = []
        tier2_src = self.project_root / "cortex_brain" / "tier2"

        if tier2_src.exists():
            for item in tier2_src.iterdir():
                dest = self.project_root / "cortex" / "brain" / "tier2" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=30
                ))

        return mappings

    def _map_tier3(self) -> List[MigrationMapping]:
        """Map tier3 files → cortex/brain/tier3/"""
        mappings = []
        tier3_src = self.project_root / "cortex_brain" / "tier3"

        if tier3_src.exists():
            for item in tier3_src.iterdir():
                dest = self.project_root / "cortex" / "brain" / "tier3" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=40
                ))

        return mappings

    def _map_cortex_brain_other(self) -> List[MigrationMapping]:
        """Map other cortex_brain items."""
        mappings = []
        cortex_brain = self.project_root / "cortex_brain"

        if cortex_brain.exists():
            for item in cortex_brain.iterdir():
                if item.name.startswith('tier'):
                    continue  # Skip tier directories (already handled)
                if item.name.startswith('.'):
                    continue  # Skip hidden

                # Map config, registry, state, etc. to cortex/core/ or cortex/brain/
                if item.name in ['config', 'registry', 'state']:
                    dest = self.project_root / "cortex" / "core" / item.name
                else:
                    dest = self.project_root / "cortex" / "brain" / item.name

                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=50
                ))

        return mappings

    def _map_src_api(self) -> List[MigrationMapping]:
        """Map src/api/* → cortex/api/"""
        mappings = []
        src_api = self.project_root / "src" / "api"

        if src_api.exists():
            for item in src_api.iterdir():
                dest = self.project_root / "cortex" / "api" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=60
                ))

        return mappings

    def _map_src_orchestrators(self) -> List[MigrationMapping]:
        """Map src/orchestrators/* → cortex/orchestrators/"""
        mappings = []
        src_orch = self.project_root / "src" / "orchestrators"

        if src_orch.exists():
            for item in src_orch.iterdir():
                dest = self.project_root / "cortex" / "orchestrators" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=60
                ))

        return mappings

    def _map_src_knowledge(self) -> List[MigrationMapping]:
        """Map src/knowledge/* → cortex/knowledge/"""
        mappings = []
        src_know = self.project_root / "src" / "knowledge"

        if src_know.exists():
            for item in src_know.iterdir():
                dest = self.project_root / "cortex" / "knowledge" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=60
                ))

        return mappings

    def _map_src_infrastructure(self) -> List[MigrationMapping]:
        """Map src/infrastructure/* → cortex/infrastructure/"""
        mappings = []
        src_infra = self.project_root / "src" / "infrastructure"

        if src_infra.exists():
            for item in src_infra.iterdir():
                dest = self.project_root / "cortex" / "infrastructure" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=70
                ))

        return mappings

    def _map_src_tools(self) -> List[MigrationMapping]:
        """Map src/tools/* → cortex/tools/"""
        mappings = []
        src_tools = self.project_root / "src" / "tools"

        if src_tools.exists():
            for item in src_tools.iterdir():
                dest = self.project_root / "cortex" / "tools" / item.name
                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=70
                ))

        return mappings

    def _map_src_other(self) -> List[MigrationMapping]:
        """Map other src/* directories."""
        mappings = []
        src = self.project_root / "src"
        handled = {'api', 'orchestrators', 'knowledge', 'infrastructure', 'tools'}

        if src.exists():
            for item in src.iterdir():
                if item.name in handled or item.name.startswith('.'):
                    continue

                # Map everything else to cortex/brain/ for now
                # This can be refined later per-item
                dest = self.project_root / "cortex" / "brain" / item.name

                mappings.append(MigrationMapping(
                    source=str(item.relative_to(self.project_root)),
                    destination=str(dest.relative_to(self.project_root)),
                    file_type='directory' if item.is_dir() else 'file',
                    priority=80
                ))

        return mappings


def main():
    """Main migration orchestrator."""
    parser = argparse.ArgumentParser(
        description='Migrate CORTEX from dual to unified folder structure'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without making changes'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the migration (default if no flags)'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Execute rollback script'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Default to dry-run if no action specified
    if not args.execute and not args.rollback:
        args.dry_run = True

    project_root = Path(__file__).parent.parent

    if args.rollback:
        logger.error("Rollback not yet implemented in this script")
        logger.info("Use: scripts/rollback_migration.sh")
        return 1

    # Phase 1: Preparation & Validation
    logger.info("=" * 80)
    logger.info("PHASE 1: PREPARATION & VALIDATION")
    logger.info("=" * 80)

    validator = MigrationValidator(project_root)

    if not validator.validate_git_clean():
        logger.error("Validation failed: Git not clean")
        return 1

    if not validator.validate_current_structure():
        logger.error("Validation failed: Current structure invalid")
        return 1

    # Build mappings
    logger.info("Building migration mappings...")
    builder = MigrationMappingBuilder(project_root)
    mappings = builder.build_mappings()
    logger.info(f"✓ Generated {len(mappings)} migration mappings")

    if not validator.validate_mappings(mappings):
        logger.error("Validation failed: Mappings invalid")
        return 1

    # Phase 2: Structural Migration (if execute)
    if args.execute:
        logger.info("=" * 80)
        logger.info("PHASE 2: STRUCTURAL MIGRATION")
        logger.info("=" * 80)

        migrator = FileMigrator(project_root, dry_run=False)

        # Create cortex/ root
        cortex_root = project_root / "cortex"
        if not cortex_root.exists():
            cortex_root.mkdir()
            logger.info(f"Created cortex/ root")

        # Execute migrations
        success_count = 0
        for i, mapping in enumerate(mappings, 1):
            source = project_root / mapping.source
            dest = project_root / mapping.destination

            if source.exists():
                if migrator.safe_move(source, dest):
                    success_count += 1
                logger.info(f"[{i}/{len(mappings)}] {mapping.source}")

        logger.info(f"✓ Migrated {success_count}/{len(mappings)} items")

        # Phase 3: Verification
        logger.info("=" * 80)
        logger.info("PHASE 3: VERIFICATION")
        logger.info("=" * 80)

        if not migrator.verify_checksums():
            logger.error("Checksum verification failed!")
            return 1

        # Generate reports
        report_path = project_root / "migration_report.json"
        migrator.generate_report(report_path)

        rollback_script = project_root / "scripts" / "rollback_migration.sh"
        migrator.create_rollback_script(rollback_script)

        logger.info("=" * 80)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Report: {report_path}")
        logger.info(f"Rollback: {rollback_script}")

    else:
        # Dry-run mode
        logger.info("=" * 80)
        logger.info("DRY-RUN MODE")
        logger.info("=" * 80)

        migrator = FileMigrator(project_root, dry_run=True)
        cortex_root = project_root / "cortex"

        for i, mapping in enumerate(mappings, 1):
            source = project_root / mapping.source
            dest = project_root / mapping.destination

            if source.exists():
                migrator.safe_move(source, dest)
                logger.info(f"[{i}/{len(mappings)}] {mapping.source} → {mapping.destination}")

        logger.info("=" * 80)
        logger.info(f"DRY-RUN COMPLETE: {len(mappings)} items would be migrated")
        logger.info("Run with --execute to perform actual migration")
        logger.info("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
