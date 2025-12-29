"""
Brain Tier 3 Workspace Segmentation

Workspace-aware storage and retrieval for development context.
Enables one CORTEX installation to maintain separate context per workspace.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.workspace_registry import get_workspace_registry, RegisteredWorkspace

logger = logging.getLogger(__name__)


class BrainTier3:
    """
    Workspace-aware Brain Tier 3 storage manager.
    
    Features:
    - Automatic workspace detection
    - Isolated storage per workspace (workspace-{uuid}/)
    - Backward compatibility (migrates old global context.db)
    - Performance: <50ms workspace context loading
    
    Directory Structure:
        cortex-brain/tier3/
        ├── workspace-{uuid-1}/
        │   ├── context.db
        │   ├── metrics.db
        │   └── cache/
        ├── workspace-{uuid-2}/
        │   ├── context.db
        │   └── ...
        └── workspace-cortex/  # CORTEX self-context
            └── context.db
    
    Usage:
        # Auto-detects workspace
        tier3 = BrainTier3()
        
        # Store context for current workspace
        tier3.store_metric("build_success", {"duration": 45})
        
        # Retrieve context
        metrics = tier3.query_metrics(since="2025-01-01")
        
        # Explicit workspace
        tier3 = BrainTier3(workspace_id="specific-uuid")
    """
    
    def __init__(
        self,
        cortex_root: Optional[Path] = None,
        workspace_id: Optional[str] = None
    ):
        """
        Initialize workspace-aware Tier 3.
        
        Args:
            cortex_root: Path to CORTEX installation (auto-detected if None)
            workspace_id: Explicit workspace UUID (auto-detected if None)
        """
        self.cortex_root = cortex_root or self._find_cortex_root()
        self.tier3_root = self.cortex_root / "cortex-brain" / "tier3"
        
        # Determine workspace
        if workspace_id:
            self.workspace_id = workspace_id
        else:
            self.workspace_id = self._detect_workspace_id()
        
        # Set workspace directory
        self.workspace_dir = self.tier3_root / f"workspace-{self.workspace_id}"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Database paths
        self.context_db = self.workspace_dir / "context.db"
        self.metrics_db = self.workspace_dir / "metrics.db"
        
        logger.debug(f"BrainTier3 initialized for workspace: {self.workspace_id}")
    
    def _detect_workspace_id(self) -> str:
        """
        Detect current workspace ID.
        
        Returns:
            Workspace UUID or "cortex" for CORTEX self-context
        """
        try:
            from src.core.workspace_detector import detect_active_workspace
            
            workspace_info = detect_active_workspace()
            
            # Check if this is CORTEX itself
            if workspace_info.path.resolve() == self.cortex_root.resolve():
                return "cortex"
            
            # Get workspace ID from registry
            registry = get_workspace_registry()
            registered = registry.get_by_path(str(workspace_info.path))
            
            if registered:
                return registered.workspace_id
            else:
                # Register and get UUID
                registered = registry.register_workspace(workspace_info)
                return registered.workspace_id
                
        except Exception as e:
            logger.warning(f"Workspace detection failed, using 'default': {e}")
            return "default"
    
    def store_context(self, context_type: str, data: Dict[str, Any]) -> bool:
        """
        Store context data for current workspace.
        
        Args:
            context_type: Type of context (e.g., "git_metric", "build_result")
            data: Context data dictionary
            
        Returns:
            True if stored successfully
        """
        try:
            conn = sqlite3.connect(self.context_db)
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes separately
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_type ON context(context_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON context(created_at)
            """)
            
            # Insert context with microsecond precision timestamp
            import json
            from datetime import datetime
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO context (context_type, data, created_at) VALUES (?, ?, ?)",
                (context_type, json.dumps(data), now)
            )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Stored context: {context_type} for workspace {self.workspace_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False
    
    def query_context(
        self,
        context_type: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query context data for current workspace.
        
        Args:
            context_type: Type of context to retrieve
            since: Only return context after this timestamp
            limit: Max number of results
            
        Returns:
            List of context dictionaries
        """
        try:
            if not self.context_db.exists():
                return []
            
            conn = sqlite3.connect(self.context_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM context WHERE context_type = ?"
            params = [context_type]
            
            if since:
                query += " AND created_at >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Parse JSON data
            import json
            results = []
            for row in rows:
                data = json.loads(row['data'])
                data['id'] = row['id']
                data['created_at'] = row['created_at']
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query context: {e}")
            return []
    
    def get_workspace_summary(self) -> Dict[str, Any]:
        """
        Get summary of workspace context.
        
        Returns:
            Dictionary with workspace statistics
        """
        summary = {
            'workspace_id': self.workspace_id,
            'workspace_dir': str(self.workspace_dir),
            'databases': {},
            'total_records': 0
        }
        
        # Check context.db
        if self.context_db.exists():
            try:
                conn = sqlite3.connect(self.context_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM context")
                count = cursor.fetchone()[0]
                summary['databases']['context'] = count
                summary['total_records'] += count
                conn.close()
            except Exception as e:
                summary['databases']['context'] = f"Error: {e}"
        
        # Check metrics.db
        if self.metrics_db.exists():
            summary['databases']['metrics'] = 'exists'
        
        return summary
    
    def clear_workspace_context(self, confirm: bool = False) -> bool:
        """
        Clear all context for current workspace.
        
        Args:
            confirm: Must be True to actually clear
            
        Returns:
            True if cleared
        """
        if not confirm:
            logger.warning("clear_workspace_context requires confirm=True")
            return False
        
        try:
            import shutil
            if self.workspace_dir.exists():
                shutil.rmtree(self.workspace_dir)
                logger.info(f"Cleared context for workspace: {self.workspace_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to clear workspace context: {e}")
            return False
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX installation root."""
        current = Path(__file__).parent
        
        while current != current.parent:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        raise RuntimeError("CORTEX installation not found")


class Tier3MigrationManager:
    """
    Migrate legacy Tier 3 data to workspace-segmented structure.
    
    Migrates:
    - cortex-brain/tier3/context.db → workspace-cortex/context.db
    - cortex-brain/tier3/metrics.db → workspace-cortex/metrics.db
    
    Usage:
        manager = Tier3MigrationManager()
        manager.migrate()
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """Initialize migration manager."""
        self.cortex_root = cortex_root or self._find_cortex_root()
        self.tier3_root = self.cortex_root / "cortex-brain" / "tier3"
        self.workspace_cortex_dir = self.tier3_root / "workspace-cortex"
    
    def needs_migration(self) -> bool:
        """Check if migration is needed."""
        legacy_db = self.tier3_root / "context.db"
        return legacy_db.exists() and not legacy_db.is_dir()
    
    def migrate(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate legacy Tier 3 data.
        
        Args:
            dry_run: If True, only report what would be done
            
        Returns:
            Migration report dictionary
        """
        report = {
            'dry_run': dry_run,
            'started': datetime.now().isoformat(),
            'files_migrated': [],
            'errors': [],
            'success': False
        }
        
        if not self.needs_migration():
            report['message'] = "No migration needed"
            report['success'] = True
            return report
        
        try:
            # Create workspace-cortex directory
            if not dry_run:
                self.workspace_cortex_dir.mkdir(parents=True, exist_ok=True)
            
            # Migrate context.db
            legacy_context = self.tier3_root / "context.db"
            if legacy_context.exists():
                target = self.workspace_cortex_dir / "context.db"
                if not dry_run:
                    import shutil
                    shutil.move(str(legacy_context), str(target))
                report['files_migrated'].append(f"context.db → {target}")
            
            # Migrate metrics (if exists)
            legacy_metrics = self.tier3_root / "metrics.db"
            if legacy_metrics.exists():
                target = self.workspace_cortex_dir / "metrics.db"
                if not dry_run:
                    import shutil
                    shutil.move(str(legacy_metrics), str(target))
                report['files_migrated'].append(f"metrics.db → {target}")
            
            # Migrate token-efficiency-metrics.yaml
            legacy_yaml = self.tier3_root / "token-efficiency-metrics.yaml"
            if legacy_yaml.exists():
                target = self.workspace_cortex_dir / "token-efficiency-metrics.yaml"
                if not dry_run:
                    import shutil
                    shutil.move(str(legacy_yaml), str(target))
                report['files_migrated'].append(f"token-efficiency-metrics.yaml → {target}")
            
            report['success'] = True
            report['completed'] = datetime.now().isoformat()
            
            if dry_run:
                logger.info("Dry run complete - no files moved")
            else:
                logger.info(f"Migration complete: {len(report['files_migrated'])} files moved")
            
        except Exception as e:
            report['errors'].append(str(e))
            logger.error(f"Migration failed: {e}")
        
        return report
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX installation root."""
        current = Path(__file__).parent
        
        while current != current.parent:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        raise RuntimeError("CORTEX installation not found")


# Global Tier 3 instance
_tier3: Optional[BrainTier3] = None


def get_brain_tier3(workspace_id: Optional[str] = None) -> BrainTier3:
    """
    Get global Brain Tier 3 instance.
    
    Args:
        workspace_id: Explicit workspace UUID (auto-detected if None)
        
    Returns:
        BrainTier3 instance for current/specified workspace
    """
    global _tier3
    
    # If workspace_id specified, always create new instance
    if workspace_id:
        return BrainTier3(workspace_id=workspace_id)
    
    # Use cached global instance for current workspace
    if _tier3 is None:
        _tier3 = BrainTier3()
    
    return _tier3
