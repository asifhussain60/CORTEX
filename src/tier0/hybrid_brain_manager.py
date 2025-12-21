"""
Hybrid Brain Architecture - Option 2: Shared Patterns + Per-Repo Context
========================================================================

**Purpose:** Implement hybrid centralization with shared Tier 2 and isolated Tier 1/3
**Author:** Asif Hussain
**Date:** December 21, 2025
**Phase:** CORTEX 4.0 Phase 5 - Brain Architecture Options

**Architecture:**
```
~/.cortex/
├── shared/
│   ├── capabilities.yaml            # Shared capabilities (from Option 1)
│   ├── response-templates-v4.yaml   # Shared templates (from Option 1)
│   ├── brain-protection-rules.yaml  # Shared governance (from Option 1)
│   └── tier2/
│       └── knowledge-graph.db       # SHARED pattern learning across repos
│
/Users/username/PROJECTS/USER-REPO-1/
├── .cortex/
│   ├── tier1/                       # PER-REPO conversations
│   │   └── working-memory.db
│   └── tier3/                       # PER-REPO development context
│       └── development_context.db
└── .cortex-config.json
```

**Benefits:**
- ✅ Pattern learning shared (Tier 2)
- ✅ Templates shared (no duplication)
- ✅ Repository context isolated (Tier 1, Tier 3)
- ✅ Minimal Tier 0 instinct violations
- ✅ Privacy preserved (repo-specific data stays local)

**Storage Savings:** 50-70% for users with 3+ repos

**Usage:**
    from src.tier0.hybrid_brain_manager import HybridBrainManager
    
    manager = HybridBrainManager()
    
    # Get paths with hybrid architecture
    tier1_path = manager.get_tier1_path()  # Per-repo
    tier2_path = manager.get_tier2_path()  # Shared
    tier3_path = manager.get_tier3_path()  # Per-repo
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import os


logger = logging.getLogger(__name__)


class HybridBrainManager:
    """Manage hybrid brain architecture with shared Tier 2 and isolated Tier 1/3."""
    
    # Centralized locations (shared across repos)
    SHARED_ROOT = Path.home() / ".cortex" / "shared"
    SHARED_TIER2 = SHARED_ROOT / "tier2"
    
    # Per-repo locations (isolated by repository)
    REPO_CORTEX_DIR = ".cortex"
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize hybrid brain manager.
        
        Args:
            repo_root: Repository root directory (default: current working directory)
        """
        self.repo_root = repo_root or Path.cwd()
        self.repo_cortex_dir = self.repo_root / self.REPO_CORTEX_DIR
        
        logger.info(f"🧠 HybridBrainManager initialized")
        logger.info(f"   Repo root: {self.repo_root}")
        logger.info(f"   Shared Tier 2: {self.SHARED_TIER2}")
        logger.info(f"   Per-repo context: {self.repo_cortex_dir}")
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        # Shared directories
        self.SHARED_ROOT.mkdir(parents=True, exist_ok=True)
        self.SHARED_TIER2.mkdir(parents=True, exist_ok=True)
        
        # Per-repo directories
        self.repo_cortex_dir.mkdir(parents=True, exist_ok=True)
        (self.repo_cortex_dir / "tier1").mkdir(exist_ok=True)
        (self.repo_cortex_dir / "tier3").mkdir(exist_ok=True)
        
        logger.debug("✅ All hybrid brain directories created")
    
    def get_tier1_path(self, create: bool = True) -> Path:
        """
        Get Tier 1 (Working Memory) path - PER-REPO.
        
        Args:
            create: Create directory if not exists
            
        Returns:
            Path to per-repo Tier 1 directory
        """
        if create:
            self._ensure_directories()
        
        path = self.repo_cortex_dir / "tier1"
        logger.debug(f"📁 Tier 1 (per-repo): {path}")
        return path
    
    def get_tier2_path(self, create: bool = True) -> Path:
        """
        Get Tier 2 (Knowledge Graph) path - SHARED.
        
        Args:
            create: Create directory if not exists
            
        Returns:
            Path to shared Tier 2 directory
        """
        if create:
            self._ensure_directories()
        
        logger.debug(f"📁 Tier 2 (shared): {self.SHARED_TIER2}")
        return self.SHARED_TIER2
    
    def get_tier3_path(self, create: bool = True) -> Path:
        """
        Get Tier 3 (Development Context) path - PER-REPO.
        
        Args:
            create: Create directory if not exists
            
        Returns:
            Path to per-repo Tier 3 directory
        """
        if create:
            self._ensure_directories()
        
        path = self.repo_cortex_dir / "tier3"
        logger.debug(f"📁 Tier 3 (per-repo): {path}")
        return path
    
    def get_tier1_db_path(self) -> Path:
        """Get Tier 1 working memory database path (per-repo)."""
        return self.get_tier1_path() / "working-memory.db"
    
    def get_tier2_db_path(self) -> Path:
        """Get Tier 2 knowledge graph database path (shared)."""
        return self.get_tier2_path() / "knowledge-graph.db"
    
    def get_tier3_db_path(self) -> Path:
        """Get Tier 3 development context database path (per-repo)."""
        return self.get_tier3_path() / "development_context.db"
    
    def get_repository_id(self) -> str:
        """
        Generate repository ID for namespacing shared data.
        
        Uses repository root directory name as identifier.
        
        Returns:
            Repository identifier string
        """
        repo_id = self.repo_root.name
        logger.debug(f"🔑 Repository ID: {repo_id}")
        return repo_id
    
    def is_hybrid_architecture_enabled(self) -> bool:
        """
        Check if hybrid architecture is enabled (shared Tier 2 exists).
        
        Returns:
            True if shared Tier 2 directory exists
        """
        return self.SHARED_TIER2.exists()
    
    def get_architecture_info(self) -> Dict[str, Any]:
        """
        Get current architecture configuration info.
        
        Returns:
            Dict with architecture details
        """
        return {
            "architecture_type": "hybrid",
            "version": "2.0",
            "repo_root": str(self.repo_root),
            "repo_id": self.get_repository_id(),
            "shared_tier2": str(self.SHARED_TIER2),
            "shared_tier2_exists": self.SHARED_TIER2.exists(),
            "per_repo_tier1": str(self.get_tier1_path(create=False)),
            "per_repo_tier3": str(self.get_tier3_path(create=False)),
            "tier1_db": str(self.get_tier1_db_path()),
            "tier2_db": str(self.get_tier2_db_path()),
            "tier3_db": str(self.get_tier3_db_path()),
        }
    
    def migrate_from_legacy(self, legacy_brain_dir: Path) -> Dict[str, Any]:
        """
        Migrate from legacy per-repo brain to hybrid architecture.
        
        Steps:
        1. Copy Tier 2 knowledge graph to shared location (if not exists)
        2. Move Tier 1 to .cortex/tier1/
        3. Move Tier 3 to .cortex/tier3/
        4. Keep templates in shared location (already done via Option 1)
        
        Args:
            legacy_brain_dir: Path to legacy cortex-brain/ directory
            
        Returns:
            Migration summary dict
        """
        import shutil
        
        if not legacy_brain_dir.exists():
            raise FileNotFoundError(f"Legacy brain directory not found: {legacy_brain_dir}")
        
        self._ensure_directories()
        
        summary = {
            "tier1_migrated": False,
            "tier2_migrated": False,
            "tier3_migrated": False,
            "errors": []
        }
        
        # Migrate Tier 1 (per-repo working memory)
        try:
            legacy_tier1 = legacy_brain_dir / "tier1"
            if legacy_tier1.exists():
                target_tier1 = self.get_tier1_path()
                shutil.copytree(legacy_tier1, target_tier1, dirs_exist_ok=True)
                summary["tier1_migrated"] = True
                logger.info(f"✅ Tier 1 migrated: {legacy_tier1} → {target_tier1}")
        except Exception as e:
            summary["errors"].append(f"Tier 1 migration failed: {e}")
            logger.error(f"❌ Tier 1 migration failed: {e}")
        
        # Migrate Tier 2 (shared knowledge graph)
        try:
            legacy_tier2 = legacy_brain_dir / "tier2"
            legacy_kg_file = legacy_tier2 / "knowledge-graph.db"
            
            if legacy_kg_file.exists():
                target_kg_file = self.get_tier2_db_path()
                
                # If shared KG doesn't exist, copy from legacy
                # If it exists, merge would be needed (complex, skip for now)
                if not target_kg_file.exists():
                    target_kg_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(legacy_kg_file, target_kg_file)
                    summary["tier2_migrated"] = True
                    logger.info(f"✅ Tier 2 migrated: {legacy_kg_file} → {target_kg_file}")
                else:
                    logger.warning("⚠️  Shared Tier 2 already exists, skipping migration")
        except Exception as e:
            summary["errors"].append(f"Tier 2 migration failed: {e}")
            logger.error(f"❌ Tier 2 migration failed: {e}")
        
        # Migrate Tier 3 (per-repo development context)
        try:
            legacy_tier3 = legacy_brain_dir / "tier3"
            if legacy_tier3.exists():
                target_tier3 = self.get_tier3_path()
                shutil.copytree(legacy_tier3, target_tier3, dirs_exist_ok=True)
                summary["tier3_migrated"] = True
                logger.info(f"✅ Tier 3 migrated: {legacy_tier3} → {target_tier3}")
        except Exception as e:
            summary["errors"].append(f"Tier 3 migration failed: {e}")
            logger.error(f"❌ Tier 3 migration failed: {e}")
        
        return summary


# Singleton instance for global access
_manager_instance: Optional[HybridBrainManager] = None


def get_manager(repo_root: Optional[Path] = None) -> HybridBrainManager:
    """
    Get singleton hybrid brain manager instance.
    
    Args:
        repo_root: Override repository root (optional)
        
    Returns:
        HybridBrainManager instance
    """
    global _manager_instance
    if _manager_instance is None or repo_root is not None:
        _manager_instance = HybridBrainManager(repo_root)
    return _manager_instance


# Convenience functions for quick access
def get_tier1_path(repo_root: Optional[Path] = None) -> Path:
    """Get Tier 1 path (per-repo)."""
    return get_manager(repo_root).get_tier1_path()


def get_tier2_path(repo_root: Optional[Path] = None) -> Path:
    """Get Tier 2 path (shared)."""
    return get_manager(repo_root).get_tier2_path()


def get_tier3_path(repo_root: Optional[Path] = None) -> Path:
    """Get Tier 3 path (per-repo)."""
    return get_manager(repo_root).get_tier3_path()


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    manager = HybridBrainManager()
    
    print("\n=== Hybrid Brain Architecture Info ===")
    info = manager.get_architecture_info()
    for key, value in info.items():
        print(f"{key:25s} → {value}")
    
    print("\n=== Database Paths ===")
    print(f"Tier 1 DB (per-repo):  {manager.get_tier1_db_path()}")
    print(f"Tier 2 DB (shared):    {manager.get_tier2_db_path()}")
    print(f"Tier 3 DB (per-repo):  {manager.get_tier3_db_path()}")
    
    print(f"\n=== Hybrid Architecture Status ===")
    if manager.is_hybrid_architecture_enabled():
        print("✅ Hybrid architecture ENABLED")
    else:
        print("⏳ Hybrid architecture NOT YET ENABLED (run migration)")
