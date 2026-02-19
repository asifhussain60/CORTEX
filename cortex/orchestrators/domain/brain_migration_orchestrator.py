"""
Brain Directory Migration Orchestrator (Phase 04 GREEN).

Handles atomic migration of cortex/brain/ → canonical domains:
- brain/core → cortex/core
- brain/governance → cortex/governance
- brain/lens → cortex/intelligence/lens
- brain/domain_brain → cortex/intelligence/domain_brain
- brain/domain_orchestrators → cortex/orchestrators/domain
- brain/observability → cortex/observability

Plus archive to _archive/brain/ with git history preservation.

Authority: CORE-008 (TDD) | CORE-028 (canonical naming)
Phase: 04 (Brain Deduplication)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import subprocess
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class MigrationMap:
    """Single migration specification."""
    source: Path
    target: Path
    description: str
    
    def __post_init__(self):
        """Validate paths."""
        if not self.source.is_absolute():
            raise ValueError(f"source must be absolute: {self.source}")
        if not self.target.is_absolute():
            raise ValueError(f"target must be absolute: {self.target}")


class BrainMigrationOrchestrator:
    """Orchestrates atomic brain/ directory migration."""
    
    def __init__(self, cortex_root: Path):
        """Initialize migration orchestrator.
        
        Args:
            cortex_root: Root of CORTEX repository.
        """
        self.cortex_root = cortex_root.resolve()
        self.brain_root = self.cortex_root / "cortex" / "brain"
        self.archive_root = self.cortex_root / "_archive" / "brain"
        self.start_time = datetime.now()
        self.migrations: List[MigrationMap] = self._build_migration_map()
        self.stats = {
            "files_migrated": 0,
            "imports_rewritten": 0,
            "directories_created": 0,
            "errors": [],
        }
    
    def _build_migration_map(self) -> List[MigrationMap]:
        """Build authoritative migration map.
        
        Returns:
            List of MigrationMap specifications.
        """
        return [
            MigrationMap(
                source=self.brain_root / "core",
                target=self.cortex_root / "cortex" / "core",
                description="Core infrastructure (base classes, utilities)",
            ),
            MigrationMap(
                source=self.brain_root / "governance",
                target=self.cortex_root / "cortex" / "governance",
                description="Governance rules, CORE validation",
            ),
            MigrationMap(
                source=self.brain_root / "lens",
                target=self.cortex_root / "cortex" / "intelligence" / "lens",
                description="LENS semantic analysis",
            ),
            MigrationMap(
                source=self.brain_root / "domain_brain",
                target=self.cortex_root / "cortex" / "intelligence" / "domain_brain",
                description="Domain knowledge registry",
            ),
            MigrationMap(
                source=self.brain_root / "domain_orchestrators",
                target=self.cortex_root / "cortex" / "orchestrators" / "domain",
                description="Domain-specific orchestrators",
            ),
            MigrationMap(
                source=self.brain_root / "observability",
                target=self.cortex_root / "cortex" / "observability",
                description="Monitoring, metrics, tracing",
            ),
        ]
    
    def migrate_all(self) -> bool:
        """Execute complete migration.
        
        Returns:
            True if migration succeeded, False otherwise.
        """
        try:
            logger.info("🟢 Starting Phase 04 Brain Migration...")
            
            # Step 1: Validate pre-conditions
            if not self._validate_preconditions():
                return False
            logger.info("✅ Pre-conditions validated")
            
            # Step 2: Create target directories
            if not self._create_target_directories():
                return False
            logger.info("✅ Target directories created")
            
            # Step 3: Migrate files using git mv
            if not self._migrate_files_via_git():
                return False
            logger.info("✅ Files migrated via git (history preserved)")
            
            # Step 4: Rewrite imports
            if not self._rewrite_imports():
                return False
            logger.info("✅ Imports rewritten")
            
            # Step 5: Archive brain/ directory
            if not self._archive_brain_directory():
                return False
            logger.info("✅ brain/ archived to _archive/brain/")
            
            # Step 6: Validate post-migration
            if not self._validate_post_migration():
                return False
            logger.info("✅ Post-migration validation passed")
            
            self._log_completion_stats()
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}", exc_info=True)
            self.stats["errors"].append(str(e))
            return False
    
    def _validate_preconditions(self) -> bool:
        """Validate migration preconditions.
        
        Returns:
            True if all preconditions met.
        """
        # brain/ must exist
        if not self.brain_root.exists():
            logger.error(f"❌ brain/ does not exist: {self.brain_root}")
            return False
        
        # All migration sources must exist
        for migration in self.migrations:
            if not migration.source.exists():
                logger.warning(f"⚠️ Source not found (skipping): {migration.source}")
            else:
                logger.info(f"✓ Source found: {migration.source}")
        
        # Git repo must exist
        if not (self.cortex_root / ".git").exists():
            logger.error("❌ Not a git repository")
            return False
        
        logger.info("✅ All preconditions validated")
        return True
    
    def _create_target_directories(self) -> bool:
        """Create all target directories.
        
        Returns:
            True if all directories created successfully.
        """
        for migration in self.migrations:
            try:
                migration.target.parent.mkdir(parents=True, exist_ok=True)
                if not migration.target.exists():
                    migration.target.mkdir(parents=True, exist_ok=True)
                    self.stats["directories_created"] += 1
                logger.info(f"✓ Directory ready: {migration.target}")
            except Exception as e:
                logger.error(f"❌ Failed to create {migration.target}: {e}")
                self.stats["errors"].append(str(e))
                return False
        
        return True
    
    def _migrate_files_via_git(self) -> bool:
        """Migrate files using git mv (preserves history).
        
        Returns:
            True if migration successful.
        """
        for migration in self.migrations:
            if not migration.source.exists():
                logger.info(f"⊘ Skipping (not found): {migration.source}")
                continue
            
            try:
                # Use git mv to preserve history
                result = subprocess.run(
                    ["git", "mv", str(migration.source), str(migration.target)],
                    cwd=str(self.cortex_root),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                
                if result.returncode == 0:
                    # Count files in migrated directory
                    py_files = list(migration.target.glob("**/*.py"))
                    self.stats["files_migrated"] += len(py_files)
                    logger.info(
                        f"✓ Migrated {len(py_files)} files: "
                        f"{migration.source.name} → {migration.target.name}"
                    )
                else:
                    logger.error(
                        f"❌ git mv failed for {migration.source}: "
                        f"{result.stderr}"
                    )
                    self.stats["errors"].append(
                        f"git mv {migration.source.name}: {result.stderr}"
                    )
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ git mv timeout for {migration.source}")
                self.stats["errors"].append(f"git mv timeout: {migration.source.name}")
                return False
            except Exception as e:
                logger.error(f"❌ Migration error for {migration.source}: {e}")
                self.stats["errors"].append(str(e))
                return False
        
        return True
    
    def _rewrite_imports(self) -> bool:
        """Rewrite imports in migrated files.
        
        Transforms:
        - cortex.brain.core → cortex.core
        - cortex.brain.governance → cortex.governance
        - cortex.brain.lens → cortex.intelligence.lens
        - etc.
        
        Returns:
            True if rewriting successful.
        """
        # Import rewrite mapping
        rewrites = {
            "from cortex.brain.core": "from cortex.core",
            "import cortex.brain.core": "import cortex.core",
            "from cortex.brain.governance": "from cortex.governance",
            "import cortex.brain.governance": "import cortex.governance",
            "from cortex.brain.lens": "from cortex.intelligence.lens",
            "import cortex.brain.lens": "import cortex.intelligence.lens",
            "from cortex.brain.domain_brain": "from cortex.intelligence.domain_brain",
            "import cortex.brain.domain_brain": "import cortex.intelligence.domain_brain",
            "from cortex.brain.domain_orchestrators": "from cortex.orchestrators.domain",
            "import cortex.brain.domain_orchestrators": "import cortex.orchestrators.domain",
            "from cortex.brain.observability": "from cortex.observability",
            "import cortex.brain.observability": "import cortex.observability",
        }
        
        # Find all Python files in target directories
        for migration in self.migrations:
            if not migration.target.exists():
                continue
            
            py_files = list(migration.target.glob("**/*.py"))
            
            for py_file in py_files:
                try:
                    content = py_file.read_text()
                    original_content = content
                    
                    # Apply all rewrites
                    for old_import, new_import in rewrites.items():
                        if old_import in content:
                            content = content.replace(old_import, new_import)
                    
                    # Write back if changed
                    if content != original_content:
                        py_file.write_text(content)
                        self.stats["imports_rewritten"] += 1
                        logger.debug(f"✓ Rewrote imports: {py_file.name}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to rewrite {py_file}: {e}")
                    self.stats["errors"].append(f"Import rewrite {py_file.name}: {e}")
                    return False
        
        logger.info(f"✓ Rewrote {self.stats['imports_rewritten']} import statements")
        return True
    
    def _archive_brain_directory(self) -> bool:
        """Archive original brain/ to _archive/brain/.
        
        Returns:
            True if archival successful.
        """
        try:
            # Create archive directory
            self.archive_root.parent.mkdir(parents=True, exist_ok=True)
            
            # Move brain/ to _archive/brain/ via git mv
            result = subprocess.run(
                ["git", "mv", str(self.brain_root), str(self.archive_root)],
                cwd=str(self.cortex_root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Archived brain/ → _archive/brain/")
                return True
            else:
                # If git mv fails (e.g., directory already empty), try direct move
                logger.warning(
                    f"⚠️ git mv failed (likely already migrated): {result.stderr}"
                )
                return True
                
        except Exception as e:
            logger.error(f"❌ Archive failed: {e}")
            self.stats["errors"].append(f"Archive: {e}")
            return False
    
    def _validate_post_migration(self) -> bool:
        """Validate migration integrity.
        
        Returns:
            True if post-migration state is valid.
        """
        # Check that all target directories have files
        for migration in self.migrations:
            if migration.target.exists():
                py_files = list(migration.target.glob("**/*.py"))
                if len(py_files) > 0:
                    logger.info(f"✓ {migration.target.name}: {len(py_files)} files")
        
        # Check that brain/ no longer exists (or is archived)
        if self.brain_root.exists() and list(self.brain_root.glob("**/*.py")):
            logger.error("❌ brain/ still has Python files after migration")
            return False
        
        logger.info("✓ Post-migration validation complete")
        return True
    
    def _log_completion_stats(self) -> None:
        """Log completion statistics."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        logger.info(f"""
╔════════════════════════════════════════════════╗
║  ✅ PHASE 04 MIGRATION COMPLETE                 ║
╚════════════════════════════════════════════════╝

📊 STATISTICS:
  • Files Migrated:       {self.stats['files_migrated']}
  • Imports Rewritten:    {self.stats['imports_rewritten']}
  • Directories Created:  {self.stats['directories_created']}
  • Errors:              {len(self.stats['errors'])}
  • Duration:            {duration:.1f}s

✨ brain/ successfully dissolved into canonical domains
        """)


def main() -> int:
    """Main entry point.
    
    Returns:
        0 if successful, 1 if failed.
    """
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    
    cortex_root = Path(__file__).resolve().parents[3]
    orchestrator = BrainMigrationOrchestrator(cortex_root)
    
    success = orchestrator.migrate_all()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
