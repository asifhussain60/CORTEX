"""
Full Brain Centralization - Option 3: Namespace-Isolated Shared Brain
======================================================================

**Purpose:** Complete brain centralization with repository_id namespace isolation
**Author:** Asif Hussain
**Date:** December 21, 2025
**Phase:** CORTEX 4.0 Phase 5 - Brain Architecture Options

**Architecture:**
```
~/.cortex/
├── brain-templates/                 # From Option 1 (symlink-based)
│   ├── capabilities.yaml
│   ├── response-templates-v4.yaml
│   ├── brain-protection-rules.yaml
│   └── cortex.config.template.json
│
├── shared/                          # From Option 2 (hybrid)
│   └── tier2/
│       └── knowledge-graph.db
│
└── brain/                           # NEW: Option 3 (full centralization)
    ├── tier1/
    │   └── working-memory.db        # ALL repos, namespace by repository_id
    ├── tier2/
    │   └── knowledge-graph.db       # SHARED patterns (no namespace needed)
    └── tier3/
        └── development_context.db   # ALL repos, namespace by repository_id
```

**Database Schema Changes:**

**Tier 1 Working Memory:**
```sql
-- Add repository_id to conversations
ALTER TABLE conversations ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX';
CREATE INDEX idx_conversations_repo ON conversations(repository_id);

-- Add repository_id to messages
ALTER TABLE messages ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX';
CREATE INDEX idx_messages_repo ON messages(repository_id);

-- Add repository_id to sessions
ALTER TABLE sessions ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX';
CREATE INDEX idx_sessions_repo ON sessions(repository_id);
```

**Tier 3 Development Context:**
```sql
-- Add repository_id to git_metrics
ALTER TABLE git_metrics ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX';
CREATE INDEX idx_git_metrics_repo ON git_metrics(repository_id);

-- Add repository_id to file_hotspots
ALTER TABLE file_hotspots ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX';
CREATE INDEX idx_file_hotspots_repo ON file_hotspots(repository_id);

-- Add repository_id to test_metrics
ALTER TABLE test_metrics ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX';
CREATE INDEX idx_test_metrics_repo ON test_metrics(repository_id);
```

**Benefits:**
- ✅ Single brain instance for ALL repositories
- ✅ Pattern learning shared across all projects
- ✅ No duplication whatsoever
- ✅ Cross-repository context awareness
- ✅ Simpler backup strategy

**Risks:**
- ⚠️  Requires Tier 0 instinct modifications (3 critical rules)
- ⚠️  Complex namespace isolation required
- ⚠️  Privacy concerns (one brain knows about all projects)
- ⚠️  Migration complexity from per-repo model

**Usage:**
    from src.tier0.full_brain_manager import FullBrainManager
    
    manager = FullBrainManager()
    
    # All paths point to centralized location
    tier1_db = manager.get_tier1_db_path()  # ~/.cortex/brain/tier1/working-memory.db
    tier2_db = manager.get_tier2_db_path()  # ~/.cortex/brain/tier2/knowledge-graph.db
    tier3_db = manager.get_tier3_db_path()  # ~/.cortex/brain/tier3/development_context.db
    
    # Repository context managed via repository_id
    repo_id = manager.get_repository_id()
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import sqlite3


logger = logging.getLogger(__name__)


class FullBrainManager:
    """Manage fully centralized brain architecture with namespace isolation."""
    
    # Centralized brain location (shared across ALL repos)
    CENTRAL_BRAIN = Path.home() / ".cortex" / "brain"
    CENTRAL_TIER1 = CENTRAL_BRAIN / "tier1"
    CENTRAL_TIER2 = CENTRAL_BRAIN / "tier2"
    CENTRAL_TIER3 = CENTRAL_BRAIN / "tier3"
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize full brain manager.
        
        Args:
            repo_root: Repository root directory (default: current working directory)
        """
        self.repo_root = repo_root or Path.cwd()
        
        logger.info(f"🧠 FullBrainManager initialized")
        logger.info(f"   Repo root: {self.repo_root}")
        logger.info(f"   Central brain: {self.CENTRAL_BRAIN}")
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        self.CENTRAL_BRAIN.mkdir(parents=True, exist_ok=True)
        self.CENTRAL_TIER1.mkdir(exist_ok=True)
        self.CENTRAL_TIER2.mkdir(exist_ok=True)
        self.CENTRAL_TIER3.mkdir(exist_ok=True)
        
        logger.debug("✅ All central brain directories created")
    
    def get_tier1_path(self, create: bool = True) -> Path:
        """
        Get Tier 1 (Working Memory) path - CENTRALIZED.
        
        Args:
            create: Create directory if not exists
            
        Returns:
            Path to centralized Tier 1 directory
        """
        if create:
            self._ensure_directories()
        
        logger.debug(f"📁 Tier 1 (central): {self.CENTRAL_TIER1}")
        return self.CENTRAL_TIER1
    
    def get_tier2_path(self, create: bool = True) -> Path:
        """
        Get Tier 2 (Knowledge Graph) path - CENTRALIZED & SHARED.
        
        Args:
            create: Create directory if not exists
            
        Returns:
            Path to centralized Tier 2 directory
        """
        if create:
            self._ensure_directories()
        
        logger.debug(f"📁 Tier 2 (central+shared): {self.CENTRAL_TIER2}")
        return self.CENTRAL_TIER2
    
    def get_tier3_path(self, create: bool = True) -> Path:
        """
        Get Tier 3 (Development Context) path - CENTRALIZED.
        
        Args:
            create: Create directory if not exists
            
        Returns:
            Path to centralized Tier 3 directory
        """
        if create:
            self._ensure_directories()
        
        logger.debug(f"📁 Tier 3 (central): {self.CENTRAL_TIER3}")
        return self.CENTRAL_TIER3
    
    def get_tier1_db_path(self) -> Path:
        """Get Tier 1 working memory database path (centralized)."""
        return self.get_tier1_path() / "working-memory.db"
    
    def get_tier2_db_path(self) -> Path:
        """Get Tier 2 knowledge graph database path (centralized + shared)."""
        return self.get_tier2_path() / "knowledge-graph.db"
    
    def get_tier3_db_path(self) -> Path:
        """Get Tier 3 development context database path (centralized)."""
        return self.get_tier3_path() / "development_context.db"
    
    def get_repository_id(self) -> str:
        """
        Generate repository ID for namespacing data.
        
        Uses repository root directory name as identifier.
        
        Returns:
            Repository identifier string
        """
        repo_id = self.repo_root.name
        logger.debug(f"🔑 Repository ID: {repo_id}")
        return repo_id
    
    def is_full_centralization_enabled(self) -> bool:
        """
        Check if full centralization is enabled (central brain exists).
        
        Returns:
            True if central brain directory exists
        """
        return self.CENTRAL_BRAIN.exists()
    
    def get_architecture_info(self) -> Dict[str, Any]:
        """
        Get current architecture configuration info.
        
        Returns:
            Dict with architecture details
        """
        return {
            "architecture_type": "full_centralization",
            "version": "3.0",
            "repo_root": str(self.repo_root),
            "repo_id": self.get_repository_id(),
            "central_brain": str(self.CENTRAL_BRAIN),
            "central_brain_exists": self.CENTRAL_BRAIN.exists(),
            "tier1_db": str(self.get_tier1_db_path()),
            "tier2_db": str(self.get_tier2_db_path()),
            "tier3_db": str(self.get_tier3_db_path()),
            "namespace_isolation": True,
        }
    
    def migrate_tier1_schema(self) -> Dict[str, Any]:
        """
        Migrate Tier 1 database schema to add repository_id column.
        
        Returns:
            Migration summary dict
        """
        db_path = self.get_tier1_db_path()
        summary = {"success": False, "errors": [], "tables_migrated": []}
        
        if not db_path.exists():
            logger.info(f"⏭️  Tier 1 database doesn't exist yet, skipping migration")
            summary["success"] = True
            return summary
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if repository_id column already exists
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if "repository_id" not in columns:
                cursor.execute("""
                    ALTER TABLE conversations 
                    ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX'
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_repo 
                    ON conversations(repository_id)
                """)
                summary["tables_migrated"].append("conversations")
                logger.info("✅ Migrated conversations table")
            
            # Similar for messages and sessions
            for table in ["messages", "sessions"]:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if "repository_id" not in columns:
                    cursor.execute(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX'
                    """)
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS idx_{table}_repo 
                        ON {table}(repository_id)
                    """)
                    summary["tables_migrated"].append(table)
                    logger.info(f"✅ Migrated {table} table")
            
            conn.commit()
            conn.close()
            summary["success"] = True
            
        except Exception as e:
            summary["errors"].append(f"Tier 1 migration failed: {e}")
            logger.error(f"❌ Tier 1 migration failed: {e}")
        
        return summary
    
    def migrate_tier3_schema(self) -> Dict[str, Any]:
        """
        Migrate Tier 3 database schema to add repository_id column.
        
        Returns:
            Migration summary dict
        """
        db_path = self.get_tier3_db_path()
        summary = {"success": False, "errors": [], "tables_migrated": []}
        
        if not db_path.exists():
            logger.info(f"⏭️  Tier 3 database doesn't exist yet, skipping migration")
            summary["success"] = True
            return summary
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Migrate git_metrics, file_hotspots, test_metrics
            for table in ["git_metrics", "file_hotspots", "test_metrics"]:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if "repository_id" not in columns:
                    cursor.execute(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN repository_id TEXT NOT NULL DEFAULT 'CORTEX'
                    """)
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS idx_{table}_repo 
                        ON {table}(repository_id)
                    """)
                    summary["tables_migrated"].append(table)
                    logger.info(f"✅ Migrated {table} table")
            
            conn.commit()
            conn.close()
            summary["success"] = True
            
        except Exception as e:
            summary["errors"].append(f"Tier 3 migration failed: {e}")
            logger.error(f"❌ Tier 3 migration failed: {e}")
        
        return summary
    
    def get_tier0_instinct_modifications_required(self) -> List[Dict[str, str]]:
        """
        Get list of Tier 0 instinct modifications required for full centralization.
        
        Returns:
            List of dicts with instinct name, current rule, and proposed change
        """
        return [
            {
                "instinct": "DISTRIBUTED_DATABASE_ARCHITECTURE",
                "severity": "CRITICAL",
                "current_rule": "Use tier-specific databases, never monolithic",
                "proposed_change": "Allow centralized brain with namespace-isolated schemas",
                "rationale": "Centralization doesn't violate separation if namespace isolation enforced"
            },
            {
                "instinct": "GIT_ISOLATION_ENFORCEMENT",
                "severity": "CRITICAL",
                "current_rule": "CORTEX code NEVER committed to user repos",
                "proposed_change": "CORTEX brain stored in ~/.cortex/, never in user repos",
                "rationale": "Brain lives outside all repos, enforces isolation at OS level"
            },
            {
                "instinct": "BRAIN_ARCHITECTURE_INTEGRITY",
                "severity": "HIGH",
                "current_rule": "Protect 4-tier brain architecture from degradation",
                "proposed_change": "Maintain 4-tier logical separation with centralized physical storage",
                "rationale": "Logical tiers preserved, only physical location changes"
            }
        ]


# Singleton instance for global access
_manager_instance: Optional[FullBrainManager] = None


def get_manager(repo_root: Optional[Path] = None) -> FullBrainManager:
    """
    Get singleton full brain manager instance.
    
    Args:
        repo_root: Override repository root (optional)
        
    Returns:
        FullBrainManager instance
    """
    global _manager_instance
    if _manager_instance is None or repo_root is not None:
        _manager_instance = FullBrainManager(repo_root)
    return _manager_instance


# Convenience functions for quick access
def get_tier1_path(repo_root: Optional[Path] = None) -> Path:
    """Get Tier 1 path (centralized)."""
    return get_manager(repo_root).get_tier1_path()


def get_tier2_path(repo_root: Optional[Path] = None) -> Path:
    """Get Tier 2 path (centralized + shared)."""
    return get_manager(repo_root).get_tier2_path()


def get_tier3_path(repo_root: Optional[Path] = None) -> Path:
    """Get Tier 3 path (centralized)."""
    return get_manager(repo_root).get_tier3_path()


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    manager = FullBrainManager()
    
    print("\n=== Full Brain Centralization Info ===")
    info = manager.get_architecture_info()
    for key, value in info.items():
        print(f"{key:30s} → {value}")
    
    print("\n=== Database Paths (ALL CENTRALIZED) ===")
    print(f"Tier 1 DB: {manager.get_tier1_db_path()}")
    print(f"Tier 2 DB: {manager.get_tier2_db_path()}")
    print(f"Tier 3 DB: {manager.get_tier3_db_path()}")
    
    print(f"\n=== Tier 0 Instinct Modifications Required ===")
    for mod in manager.get_tier0_instinct_modifications_required():
        print(f"\n{mod['instinct']} ({mod['severity']})")
        print(f"  Current: {mod['current_rule']}")
        print(f"  Proposed: {mod['proposed_change']}")
        print(f"  Rationale: {mod['rationale']}")
    
    print(f"\n=== Centralization Status ===")
    if manager.is_full_centralization_enabled():
        print("✅ Full centralization ENABLED")
    else:
        print("⏳ Full centralization NOT YET ENABLED")
