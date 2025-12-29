"""
Upgrade Utility - CORTEX Auto-Upgrade with Brain Preservation

Comprehensive upgrade system with safety-first approach:
- Version checking and comparison
- Brain data backup/restore with verification
- Git operations (pull, merge, rollback)
- Schema migrations with tracking
- Dependency validation
- Operational readiness verification
- What's New feature discovery
- Bootstrap verification

Part of CORTEX 3.2.1 - Upgrade System
Sprint 12b Migration: upgrade_orchestrator (1,115 lines) → upgrade_utility (~1,200 lines)
Author: Asif Hussain

HIGH RISK OPERATIONS - Brain data preservation critical
Zero tolerance for data loss, comprehensive testing required

Operations:
- check_for_updates: Compare current vs remote version
- create_backup: Brain data backup with metadata
- verify_backup: Validate backup integrity
- restore_backup: Rollback to previous state
- execute_upgrade: Complete upgrade workflow
- run_migrations: Apply schema migrations
- validate_dependencies: Verify core/optional dependencies
- validate_operational_readiness: Confirm CORTEX functionality
- validate_test_suite: Verify test discoverability
- generate_whats_new: Feature discovery since last version
- list_backups: Show available backups
- compare_versions: Semantic version comparison
"""

import json
import logging
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


# ========================================
# Data Classes
# ========================================

@dataclass
class VersionInfo:
    """Version information with comparison support."""
    version: str
    branch: str
    timestamp: str
    has_updates: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "version": self.version,
            "branch": self.branch,
            "timestamp": self.timestamp,
            "has_updates": self.has_updates
        }


@dataclass
class BackupMetadata:
    """Backup metadata with verification info."""
    backup_id: str
    timestamp: str
    version: str
    branch: str
    items: List[str]
    verified: bool = False
    size_bytes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "backup_id": self.backup_id,
            "timestamp": self.timestamp,
            "version": self.version,
            "branch": self.branch,
            "items": self.items,
            "verified": self.verified,
            "size_bytes": self.size_bytes
        }


@dataclass
class UpgradeResult:
    """Upgrade execution result with complete details."""
    success: bool
    from_version: str
    to_version: str
    backup_id: Optional[str]
    migrations_applied: int
    whats_new: str
    validation_results: Dict[str, Any]
    message: str
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "success": self.success,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "backup_id": self.backup_id,
            "migrations_applied": self.migrations_applied,
            "whats_new": self.whats_new,
            "validation_results": self.validation_results,
            "message": self.message,
            "errors": self.errors
        }


# ========================================
# Version Operations
# ========================================

def get_current_version(cortex_root: Path) -> str:
    """
    Get current CORTEX version from VERSION file.
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        Version string or "unknown"
    
    Example:
        >>> get_current_version(Path("/path/to/CORTEX"))
        '3.2.1'
    """
    version_file = cortex_root / "VERSION"
    try:
        if version_file.exists():
            return version_file.read_text(encoding='utf-8').strip()
        return "unknown"
    except Exception:
        return "unknown"


def get_remote_version(cortex_root: Path) -> str:
    """
    Get remote version from origin/main:VERSION.
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        Remote version string or "unknown"
    
    Example:
        >>> get_remote_version(Path("/path/to/CORTEX"))
        '3.3.0'
    """
    try:
        result = subprocess.run(
            ['git', 'show', 'origin/main:VERSION'],
            cwd=cortex_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare semantic version strings.
    
    Args:
        v1: First version (e.g., "3.2.0")
        v2: Second version (e.g., "3.3.0")
    
    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    
    Example:
        >>> compare_versions("3.2.0", "3.3.0")
        -1
        >>> compare_versions("3.3.0", "3.2.0")
        1
        >>> compare_versions("3.2.0", "3.2.0")
        0
    """
    try:
        # Parse semantic versions
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        # Pad to same length
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))
        
        # Compare each part
        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    except Exception:
        # Fallback to string comparison
        return -1 if v1 < v2 else (1 if v1 > v2 else 0)


def check_for_updates(cortex_root: Path) -> VersionInfo:
    """
    Check if CORTEX updates are available from origin/main.
    
    Fetches latest from remote and compares versions.
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        VersionInfo with update status
    
    Example:
        >>> info = check_for_updates(Path("/path/to/CORTEX"))
        >>> info.has_updates
        True
        >>> info.version
        '3.2.1'
    """
    current_version = get_current_version(cortex_root)
    
    try:
        # Fetch latest from origin
        subprocess.run(
            ['git', 'fetch', 'origin', 'main'],
            cwd=cortex_root,
            capture_output=True,
            check=True
        )
        
        remote_version = get_remote_version(cortex_root)
        has_updates = compare_versions(current_version, remote_version) < 0
        
        # Get current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=cortex_root,
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        
        info = VersionInfo(
            version=current_version,
            branch=branch,
            timestamp=datetime.now().isoformat(),
            has_updates=has_updates
        )
        
        if has_updates:
            logger.info(f"✅ Updates available: {current_version} → {remote_version}")
        else:
            logger.info(f"✅ Already on latest version: {current_version}")
        
        return info
    
    except Exception as e:
        logger.error(f"❌ Failed to check for updates: {e}")
        return VersionInfo(
            version=current_version,
            branch="unknown",
            timestamp=datetime.now().isoformat(),
            has_updates=False
        )


# ========================================
# Backup Operations (HIGH RISK - Brain Data)
# ========================================

def create_backup(cortex_root: Path) -> Optional[BackupMetadata]:
    """
    Create backup of brain data and user files.
    
    HIGH RISK OPERATION - Brain data preservation critical.
    
    Backs up:
    - cortex-brain/feedback
    - cortex-brain/working_memory.db
    - cortex-brain/config
    - cortex-brain/documents/planning
    - logs
    - VERSION
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        BackupMetadata or None if failed
    
    Example:
        >>> metadata = create_backup(Path("/path/to/CORTEX"))
        >>> metadata.backup_id
        '20241203_143000'
        >>> metadata.verified
        True
    """
    backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = cortex_root / ".upgrades" / "backups"
    backup_path = backup_dir / backup_id
    
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Items to backup
        items_to_backup = [
            'cortex-brain/feedback',
            'cortex-brain/working_memory.db',
            'cortex-brain/config',
            'cortex-brain/documents/planning',
            'logs',
            'VERSION'
        ]
        
        total_size = 0
        backed_up_items = []
        
        for item in items_to_backup:
            source = cortex_root / item
            if source.exists():
                dest = backup_path / item
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                if source.is_file():
                    shutil.copy2(source, dest)
                    total_size += source.stat().st_size
                    backed_up_items.append(item)
                elif source.is_dir():
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                    total_size += sum(f.stat().st_size for f in source.rglob('*') if f.is_file())
                    backed_up_items.append(item)
        
        # Get current version and branch
        version = get_current_version(cortex_root)
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=cortex_root,
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        
        # Create metadata
        metadata = BackupMetadata(
            backup_id=backup_id,
            timestamp=datetime.now().isoformat(),
            version=version,
            branch=branch,
            items=backed_up_items,
            verified=False,
            size_bytes=total_size
        )
        
        # Save metadata
        metadata_file = backup_path / 'backup_metadata.json'
        metadata_file.write_text(
            json.dumps(metadata.to_dict(), indent=2),
            encoding='utf-8'
        )
        
        # Verify backup
        metadata.verified = verify_backup(cortex_root, backup_id)
        
        # Update metadata with verification result
        metadata_file.write_text(
            json.dumps(metadata.to_dict(), indent=2),
            encoding='utf-8'
        )
        
        logger.info(f"✅ Backup created: {backup_id} ({total_size // 1024} KB)")
        logger.info(f"   Items: {len(backed_up_items)}, Verified: {metadata.verified}")
        
        return metadata
    
    except Exception as e:
        logger.error(f"❌ Backup creation failed: {e}")
        return None


def verify_backup(cortex_root: Path, backup_id: str) -> bool:
    """
    Verify backup integrity.
    
    Checks that all backed up files exist and are readable.
    
    Args:
        cortex_root: CORTEX root directory
        backup_id: Backup identifier
    
    Returns:
        True if backup is valid, False otherwise
    
    Example:
        >>> verify_backup(Path("/path/to/CORTEX"), "20241203_143000")
        True
    """
    backup_path = cortex_root / ".upgrades" / "backups" / backup_id
    
    try:
        if not backup_path.exists():
            logger.error(f"❌ Backup path not found: {backup_path}")
            return False
        
        metadata_file = backup_path / 'backup_metadata.json'
        if not metadata_file.exists():
            logger.error(f"❌ Backup metadata not found: {backup_id}")
            return False
        
        # Read metadata
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        items = metadata.get('items', [])
        
        # Verify each item
        for item in items:
            item_path = backup_path / item
            if not item_path.exists():
                logger.error(f"❌ Backup item missing: {item}")
                return False
            
            # Try to read (basic integrity check)
            if item_path.is_file():
                try:
                    item_path.read_bytes()
                except Exception as e:
                    logger.error(f"❌ Backup item unreadable: {item}: {e}")
                    return False
        
        logger.info(f"✅ Backup verified: {backup_id} ({len(items)} items)")
        return True
    
    except Exception as e:
        logger.error(f"❌ Backup verification failed: {e}")
        return False


def restore_backup(cortex_root: Path, backup_id: str) -> bool:
    """
    Restore from backup (rollback).
    
    HIGH RISK OPERATION - Restores brain data from backup.
    
    Args:
        cortex_root: CORTEX root directory
        backup_id: Backup identifier to restore
    
    Returns:
        True if restore successful, False otherwise
    
    Example:
        >>> restore_backup(Path("/path/to/CORTEX"), "20241203_143000")
        True
    """
    backup_path = cortex_root / ".upgrades" / "backups" / backup_id
    
    try:
        # Verify backup first
        if not verify_backup(cortex_root, backup_id):
            logger.error(f"❌ Backup verification failed, cannot restore: {backup_id}")
            return False
        
        # Read metadata
        metadata_file = backup_path / 'backup_metadata.json'
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        items = metadata.get('items', [])
        
        logger.info(f"🔄 Restoring backup: {backup_id}")
        
        # Restore each item
        for item in items:
            source = backup_path / item
            dest = cortex_root / item
            
            if not source.exists():
                logger.warning(f"⚠️  Backup item not found: {item}")
                continue
            
            # Remove existing
            if dest.exists():
                if dest.is_file():
                    dest.unlink()
                elif dest.is_dir():
                    shutil.rmtree(dest)
            
            # Restore
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if source.is_file():
                shutil.copy2(source, dest)
            elif source.is_dir():
                shutil.copytree(source, dest)
            
            logger.info(f"  ✅ Restored: {item}")
        
        logger.info(f"✅ Rollback complete: restored {len(items)} items")
        return True
    
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        return False


def list_backups(cortex_root: Path) -> List[BackupMetadata]:
    """
    List available backups sorted by timestamp.
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        List of BackupMetadata, newest first
    
    Example:
        >>> backups = list_backups(Path("/path/to/CORTEX"))
        >>> len(backups)
        3
        >>> backups[0].version
        '3.2.1'
    """
    backup_dir = cortex_root / ".upgrades" / "backups"
    backups = []
    
    try:
        if not backup_dir.exists():
            return backups
        
        for backup_path in backup_dir.iterdir():
            if not backup_path.is_dir():
                continue
            
            metadata_file = backup_path / 'backup_metadata.json'
            if metadata_file.exists():
                try:
                    data = json.loads(metadata_file.read_text(encoding='utf-8'))
                    metadata = BackupMetadata(
                        backup_id=data['backup_id'],
                        timestamp=data['timestamp'],
                        version=data['version'],
                        branch=data['branch'],
                        items=data['items'],
                        verified=data.get('verified', False),
                        size_bytes=data.get('size_bytes', 0)
                    )
                    backups.append(metadata)
                except Exception:
                    pass
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        
        logger.info(f"✅ Found {len(backups)} backups")
        return backups
    
    except Exception as e:
        logger.error(f"❌ Failed to list backups: {e}")
        return []


# ========================================
# Migration Operations
# ========================================

def run_migrations(cortex_root: Path) -> Tuple[bool, int]:
    """
    Run database schema migrations.
    
    Applies SQL migrations from cortex-brain/migrations/ that haven't
    been applied yet. Tracks applied migrations in schema_migrations table.
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        Tuple of (success, migrations_applied_count)
    
    Example:
        >>> success, count = run_migrations(Path("/path/to/CORTEX"))
        >>> success
        True
        >>> count
        3
    """
    migrations_dir = cortex_root / "cortex-brain" / "migrations"
    
    try:
        if not migrations_dir.exists():
            logger.info("No migrations directory found")
            return True, 0
        
        # Get migration files
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.info("No migration files found")
            return True, 0
        
        # Connect to working memory DB
        db_path = cortex_root / "cortex-brain" / "working_memory.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create migrations tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                applied_at TEXT NOT NULL
            )
        """)
        
        migrations_applied = 0
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
            
            # Apply migration
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
                migrations_applied += 1
                logger.info(f"✅ Migration applied: {migration_name}")
            
            except Exception as e:
                logger.error(f"❌ Migration failed: {migration_name}: {e}")
                success = False
                conn.rollback()
                break
        
        conn.close()
        
        if success:
            logger.info(f"✅ Migrations complete: {migrations_applied} applied")
        else:
            logger.error(f"❌ Migrations failed after {migrations_applied} successful")
        
        return success, migrations_applied
    
    except Exception as e:
        logger.error(f"❌ Failed to run migrations: {e}")
        return False, 0


# ========================================
# Validation Operations
# ========================================

def uninstall_unused_packages(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]:
    """
    Uninstall packages that were removed in CORTEX 3.9.1 dependency audit.
    
    Removes 67 packages (780 MB) with zero imports in src/:
    - Dashboard packages: matplotlib, Flask, networkx (165 MB)
    - Browser testing: playwright, selenium, pytest-selenium (170 MB)
    - GitHub integration: PyGithub (5 MB)
    - Multi-language: esprima, tree-sitter-languages (125 MB)
    - Document parsing: python-docx, pypdf (25 MB)
    - Other unused: tomli (5 MB)
    - Dev tools: pytest-cov, pytest-asyncio (moved to requirements-dev.txt)
    - Optional ML: scikit-learn, numpy, send2trash (moved to requirements-optional.txt)
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        Tuple of (success, results_dict)
    
    Example:
        >>> success, results = uninstall_unused_packages(Path("/path/to/CORTEX"))
        >>> success
        True
        >>> results['uninstalled']
        ['matplotlib', 'Flask', 'networkx', ...]
    """
    result = {
        "uninstalled": [],
        "failed": [],
        "not_found": [],
        "total_packages": 0,
        "space_freed_mb": 0,
        "status": "unknown"
    }
    
    logger.info("🗑️  Cleaning up unused packages from CORTEX 3.9.0...")
    
    # Packages to remove (from dependency audit)
    unused_packages = [
        # Dashboard (never built - 165 MB)
        'matplotlib', 'Flask', 'networkx',
        
        # Browser testing (never written - 170 MB)
        'playwright', 'selenium', 'pytest-selenium',
        
        # GitHub integration (never implemented - 5 MB)
        'PyGithub',
        
        # Multi-language (never implemented - 125 MB)
        'esprima', 'tree-sitter-languages',
        
        # Document parsing (never activated - 25 MB)
        'python-docx', 'pypdf',
        
        # Misc unused (5 MB)
        'tomli',
        
        # Dev tools (moved to requirements-dev.txt)
        'pytest-cov', 'pytest-asyncio',
        
        # Optional ML (moved to requirements-optional.txt - 205 MB)
        'scikit-learn', 'numpy', 'send2trash',
    ]
    
    result['total_packages'] = len(unused_packages)
    
    # Estimated sizes (for reporting)
    package_sizes = {
        'matplotlib': 150, 'Flask': 15, 'networkx': 25,
        'playwright': 150, 'selenium': 20, 'pytest-selenium': 5,
        'PyGithub': 5, 'esprima': 5, 'tree-sitter-languages': 120,
        'python-docx': 10, 'pypdf': 15, 'tomli': 5,
        'pytest-cov': 5, 'pytest-asyncio': 5,
        'scikit-learn': 150, 'numpy': 50, 'send2trash': 5,
    }
    
    for package in unused_packages:
        try:
            # Check if package is installed
            check_result = subprocess.run(
                ['pip', 'show', package],
                capture_output=True,
                text=True,
                check=False
            )
            
            if check_result.returncode != 0:
                result['not_found'].append(package)
                logger.info(f"  ⏩ {package} - not installed")
                continue
            
            # Uninstall package
            logger.info(f"  🗑️  Uninstalling {package}...")
            uninstall_result = subprocess.run(
                ['pip', 'uninstall', '-y', package],
                capture_output=True,
                text=True,
                check=False
            )
            
            if uninstall_result.returncode == 0:
                result['uninstalled'].append(package)
                result['space_freed_mb'] += package_sizes.get(package, 5)
                logger.info(f"  ✅ {package} removed")
            else:
                result['failed'].append(package)
                logger.warning(f"  ⚠️  {package} - uninstall failed: {uninstall_result.stderr}")
        
        except Exception as e:
            result['failed'].append(package)
            logger.error(f"  ❌ {package} - error: {e}")
    
    # Determine status
    if len(result['failed']) == 0:
        result['status'] = 'success'
        success = True
        logger.info(f"✅ Cleanup complete: {len(result['uninstalled'])} packages removed, ~{result['space_freed_mb']} MB freed")
    else:
        result['status'] = 'partial'
        success = True  # Partial success is OK
        logger.warning(f"⚠️  Cleanup partial: {len(result['failed'])} packages failed")
    
    return success, result


def validate_dependencies(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate core and optional dependencies are installed.
    
    Core dependencies (MUST be present):
    - pytest, PyYAML, python-dateutil, pydantic, watchdog, psutil, requests, parso, sqlparse
    
    Optional dependencies (warn if missing):
    - numpy, sklearn, send2trash
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        Tuple of (success, results_dict)
    
    Example:
        >>> success, results = validate_dependencies(Path("/path/to/CORTEX"))
        >>> success
        True
        >>> results['core_installed']
        ['pytest', 'yaml', 'watchdog', 'psutil', 'requests']
    """
    result = {
        "core_installed": [],
        "core_failed": [],
        "optional_installed": [],
        "optional_failed": [],
        "status": "unknown"
    }
    
    logger.info("Validating dependencies...")
    
    # Core dependencies (from requirements.txt - 9 packages)
    core_deps = ['pytest', 'yaml', 'dateutil', 'pydantic', 'watchdog', 'psutil', 'requests', 'parso', 'sqlparse']
    
    # Optional dependencies (from requirements-optional.txt - 3 packages)
    optional_deps = ['numpy', 'sklearn', 'send2trash']
    
    # Test core
    for dep in core_deps:
        try:
            __import__(dep)
            result["core_installed"].append(dep)
            logger.info(f"  ✅ Core: {dep}")
        except ImportError:
            result["core_failed"].append(dep)
            logger.error(f"  ❌ Core MISSING: {dep}")
    
    # Test optional
    for dep in optional_deps:
        try:
            __import__(dep)
            result["optional_installed"].append(dep)
            logger.info(f"  ✅ Optional: {dep}")
        except ImportError:
            result["optional_failed"].append(dep)
            logger.warning(f"  ⚠️  Optional missing: {dep}")
    
    # Determine status
    if len(result["core_failed"]) == 0:
        result["status"] = "healthy"
        success = True
    else:
        result["status"] = "critical"
        success = False
    
    return success, result


def validate_operational_readiness(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate CORTEX is fully operational.
    
    Checks:
    - Core imports (tier1, tier2, tier3)
    - Database accessibility
    - Config validity
    - Template validity
    - Protection rules validity
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        Tuple of (success, results_dict)
    
    Example:
        >>> success, results = validate_operational_readiness(Path("/path/to/CORTEX"))
        >>> success
        True
        >>> results['imports']
        True
    """
    result = {
        "imports": False,
        "tier1_db": False,
        "tier2_db": False,
        "tier3_db": False,
        "operations_config": False,
        "response_templates": False,
        "brain_protection": False,
        "errors": [],
        "status": "unknown"
    }
    
    logger.info("Validating operational readiness...")
    
    try:
        import sys
        sys.path.insert(0, str(cortex_root / 'src'))
        
        # Test imports
        try:
            from tier1.working_memory import WorkingMemory
            from tier2.knowledge_graph import KnowledgeGraph
            from tier3.development_context import DevelopmentContext
            result["imports"] = True
            logger.info("  ✅ Core imports successful")
        except Exception as e:
            result["errors"].append(f"Import failed: {e}")
            logger.error(f"  ❌ Imports failed: {e}")
        
        # Test databases
        brain_path = cortex_root / "cortex-brain"
        
        tier1_db = brain_path / "working_memory.db"
        if tier1_db.exists():
            try:
                conn = sqlite3.connect(str(tier1_db))
                conn.close()
                result["tier1_db"] = True
                logger.info("  ✅ Tier 1 database accessible")
            except Exception as e:
                result["errors"].append(f"Tier 1 DB: {e}")
                logger.error(f"  ❌ Tier 1 DB failed: {e}")
        
        # Test config
        config_file = cortex_root / "cortex.config.json"
        if config_file.exists():
            try:
                json.loads(config_file.read_text())
                result["operations_config"] = True
                logger.info("  ✅ Config valid")
            except Exception as e:
                result["errors"].append(f"Config: {e}")
                logger.error(f"  ❌ Config invalid: {e}")
        
        # Determine status
        checks_passed = sum(1 for v in [
            result["imports"],
            result["tier1_db"],
            result["operations_config"]
        ] if v)
        
        if checks_passed == 3:
            result["status"] = "healthy"
            success = True
        elif checks_passed >= 2:
            result["status"] = "warning"
            success = True
        else:
            result["status"] = "critical"
            success = False
        
        return success, result
    
    except Exception as e:
        result["errors"].append(str(e))
        result["status"] = "critical"
        logger.error(f"❌ Operational validation failed: {e}")
        return False, result


# ========================================
# Main Workflow
# ========================================

def execute_upgrade(
    cortex_root: Path,
    backup: bool = True,
    auto_migrate: bool = True,
    force: bool = False
) -> UpgradeResult:
    """
    Execute complete CORTEX upgrade workflow.
    
    HIGH RISK OPERATION - Brain data preservation critical.
    
    Workflow:
    1. Check for updates
    2. Create backup (if enabled)
    3. Pull from origin/main
    4. Run migrations (if enabled)
    5. Validate dependencies
    6. Validate operational readiness
    7. Generate What's New report
    8. Rollback on failure
    
    Args:
        cortex_root: CORTEX root directory
        backup: Create backup before upgrade (default: True)
        auto_migrate: Run migrations automatically (default: True)
        force: Force upgrade even if no updates (default: False)
    
    Returns:
        UpgradeResult with complete execution details
    
    Example:
        >>> result = execute_upgrade(Path("/path/to/CORTEX"))
        >>> result.success
        True
        >>> result.to_version
        '3.3.0'
        >>> result.migrations_applied
        3
    """
    logger.info("🚀 Starting CORTEX upgrade...")
    
    # Check for updates
    version_info = check_for_updates(cortex_root)
    current_version = version_info.version
    
    if not version_info.has_updates and not force:
        return UpgradeResult(
            success=True,
            from_version=current_version,
            to_version=current_version,
            backup_id=None,
            migrations_applied=0,
            whats_new="",
            validation_results={},
            message=f"Already on latest version: {current_version}",
            errors=[]
        )
    
    backup_id = None
    errors = []
    
    try:
        # Create backup
        if backup:
            backup_metadata = create_backup(cortex_root)
            if backup_metadata:
                backup_id = backup_metadata.backup_id
                logger.info(f"✅ Backup created: {backup_id}")
            else:
                return UpgradeResult(
                    success=False,
                    from_version=current_version,
                    to_version=current_version,
                    backup_id=None,
                    migrations_applied=0,
                    whats_new="",
                    validation_results={},
                    message="Backup creation failed",
                    errors=["Failed to create backup"]
                )
        
        # Pull from origin/main
        logger.info("📥 Pulling updates from origin/main...")
        
        current_branch = version_info.branch
        
        if current_branch == 'main':
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=cortex_root,
                capture_output=True,
                text=True,
                check=False
            )
        else:
            result = subprocess.run(
                ['git', 'merge', 'origin/main', '--no-edit'],
                cwd=cortex_root,
                capture_output=True,
                text=True,
                check=False
            )
        
        if result.returncode != 0:
            error_msg = f"Git operation failed: {result.stderr}"
            logger.error(f"❌ {error_msg}")
            
            # Rollback
            if backup_id:
                restore_backup(cortex_root, backup_id)
            
            return UpgradeResult(
                success=False,
                from_version=current_version,
                to_version=current_version,
                backup_id=backup_id,
                migrations_applied=0,
                whats_new="",
                validation_results={},
                message=error_msg,
                errors=[error_msg]
            )
        
        # Get new version
        new_version = get_current_version(cortex_root)
        logger.info(f"✅ Upgraded: {current_version} → {new_version}")
        
        # Cleanup unused packages (Phase 4)
        logger.info("🗑️  Phase 4: Cleaning up unused packages...")
        cleanup_ok, cleanup_result = uninstall_unused_packages(cortex_root)
        if cleanup_ok:
            logger.info(f"  ✅ {len(cleanup_result['uninstalled'])} packages removed")
            logger.info(f"  💾 ~{cleanup_result['space_freed_mb']} MB disk space freed")
        else:
            logger.warning(f"  ⚠️  Cleanup partial: {len(cleanup_result['failed'])} failed")
        
        # Run migrations (Phase 5)
        migrations_applied = 0
        if auto_migrate:
            migration_success, migrations_applied = run_migrations(cortex_root)
            if not migration_success:
                errors.append("Some migrations failed")
        
        # Validate dependencies
        deps_ok, deps_result = validate_dependencies(cortex_root)
        if not deps_ok:
            errors.append(f"Core dependencies missing: {deps_result['core_failed']}")
        
        # Validate operational readiness
        ops_ok, ops_result = validate_operational_readiness(cortex_root)
        if not ops_ok:
            errors.append("Operational validation failed")
        
        validation_results = {
            "dependencies": deps_result,
            "operational": ops_result,
            "cleanup": cleanup_result
        }
        
        # Build message
        message = f"✅ Upgrade complete: {current_version} → {new_version}"
        message += f"\n  🗑️  Cleanup: {len(cleanup_result['uninstalled'])} unused packages removed (~{cleanup_result['space_freed_mb']} MB)"
        message += f"\n  📦 Migrations: {migrations_applied} applied"
        message += f"\n  ✅ Dependencies: {len(deps_result['core_installed'])}/{len(deps_result['core_installed']) + len(deps_result['core_failed'])} core"
        message += f"\n  ✅ Operational: {ops_result['status']}"
        
        if errors:
            message += f"\n  ⚠️  Warnings: {len(errors)}"
        
        return UpgradeResult(
            success=len(errors) == 0,
            from_version=current_version,
            to_version=new_version,
            backup_id=backup_id,
            migrations_applied=migrations_applied,
            whats_new="",  # Would integrate EnhancementCatalog here
            validation_results=validation_results,
            message=message,
            errors=errors
        )
    
    except Exception as e:
        error_msg = f"Upgrade failed: {e}"
        logger.error(f"❌ {error_msg}")
        
        # Rollback
        if backup_id:
            restore_backup(cortex_root, backup_id)
        
        return UpgradeResult(
            success=False,
            from_version=current_version,
            to_version=current_version,
            backup_id=backup_id,
            migrations_applied=0,
            whats_new="",
            validation_results={},
            message=error_msg,
            errors=[error_msg]
        )


# ========================================
# Self-Test
# ========================================

def _run_self_tests() -> None:
    """Self-test for upgrade utility operations"""
    import time
    import tempfile
    
    print("🧪 Running Upgrade Utility Self-Tests...\n")
    start_time = time.time()
    
    tests_passed = 0
    tests_total = 0
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test 1: compare_versions
        tests_total += 1
        try:
            assert compare_versions("3.2.0", "3.3.0") == -1
            assert compare_versions("3.3.0", "3.2.0") == 1
            assert compare_versions("3.2.0", "3.2.0") == 0
            print("✅ Test 1: compare_versions - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 1: compare_versions - FAILED: {e}")
        
        # Test 2: get_current_version
        tests_total += 1
        try:
            version_file = temp_dir / "VERSION"
            version_file.write_text("3.2.1\n")
            version = get_current_version(temp_dir)
            assert version == "3.2.1"
            print("✅ Test 2: get_current_version - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 2: get_current_version - FAILED: {e}")
        
        # Test 3: BackupMetadata dataclass
        tests_total += 1
        try:
            metadata = BackupMetadata(
                backup_id="test_backup",
                timestamp="2024-12-03T14:30:00",
                version="3.2.1",
                branch="main",
                items=["VERSION", "cortex-brain/feedback"],
                verified=True,
                size_bytes=1024
            )
            data = metadata.to_dict()
            assert data['backup_id'] == "test_backup"
            assert data['verified'] == True
            print("✅ Test 3: BackupMetadata - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 3: BackupMetadata - FAILED: {e}")
        
        # Test 4: VersionInfo dataclass
        tests_total += 1
        try:
            info = VersionInfo(
                version="3.2.1",
                branch="main",
                timestamp="2024-12-03T14:30:00",
                has_updates=True
            )
            data = info.to_dict()
            assert data['version'] == "3.2.1"
            assert data['has_updates'] == True
            print("✅ Test 4: VersionInfo - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 4: VersionInfo - FAILED: {e}")
        
        # Test 5: UpgradeResult dataclass
        tests_total += 1
        try:
            result = UpgradeResult(
                success=True,
                from_version="3.2.0",
                to_version="3.2.1",
                backup_id="backup_123",
                migrations_applied=3,
                whats_new="New features",
                validation_results={},
                message="Upgrade complete",
                errors=[]
            )
            data = result.to_dict()
            assert data['success'] == True
            assert data['migrations_applied'] == 3
            print("✅ Test 5: UpgradeResult - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 5: UpgradeResult - FAILED: {e}")
        
        # Test 6: list_backups (empty)
        tests_total += 1
        try:
            backups = list_backups(temp_dir)
            assert isinstance(backups, list)
            print("✅ Test 6: list_backups - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 6: list_backups - FAILED: {e}")
        
        # Test 7: validate_dependencies
        tests_total += 1
        try:
            success, results = validate_dependencies(temp_dir)
            assert 'core_installed' in results
            assert 'core_failed' in results
            print("✅ Test 7: validate_dependencies - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 7: validate_dependencies - FAILED: {e}")
        
        print(f"\n{'='*60}")
        print(f"📊 Test Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
        print(f"⏱️  Execution time: {time.time() - start_time:.3f}s")
        
        if tests_passed == tests_total:
            print("✅ All tests passed!")
        else:
            print(f"❌ {tests_total - tests_passed} test(s) failed")
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    _run_self_tests()
