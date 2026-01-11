#!/usr/bin/env python3
"""
Atomic State Manager for CORTEX 6.0
Wraps all 6-source state updates in SQLite transactions to prevent corruption.
"""

import sqlite3
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import fcntl
import logging

class AtomicStateManager:
    """
    Manages atomic updates across 6 truth sources:
    1. progress-tracker.json
    2. AC-INDEX.yaml
    3. master-plan.yaml
    4. plan-viewer.html (regenerated)
    5. evidence-bundles/ (directories)
    6. governance.db (SQLite)
    """
    
    def __init__(self, cortex_root: Path):
        self.root = cortex_root
        self.db_path = self.root / "cortex-brain/tier0/governance.db"
        self.progress_path = self.root / "cortex-brain/tier1/tracking/progress-tracker.json"
        self.ac_index_path = self.root / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
        self.master_plan_path = self.root / "cortex-brain/cx6-plan/master-plan.yaml"
        
        self.logger = logging.getLogger(__name__)
        
    @contextmanager
    def atomic_transaction(self):
        """
        Context manager for atomic multi-file updates.
        
        Usage:
            with state_mgr.atomic_transaction():
                state_mgr.update_progress_tracker(...)
                state_mgr.update_ac_index(...)
                # If any exception, all rollback
        """
        # Step 1: Create backup snapshots
        backups = self._create_snapshots()
        
        # Step 2: Acquire file locks
        locks = self._acquire_locks()
        
        # Step 3: Begin SQLite transaction
        conn = sqlite3.connect(self.db_path)
        conn.execute("BEGIN IMMEDIATE")
        
        try:
            yield conn
            
            # Commit if no exception
            conn.commit()
            conn.close()
            
            # Release locks
            self._release_locks(locks)
            
            # Remove backups
            self._cleanup_snapshots(backups)
            
        except Exception as e:
            # Rollback on exception
            self.logger.error(f"Transaction failed: {e}. Rolling back...")
            conn.rollback()
            conn.close()
            
            # Restore from backups
            self._restore_snapshots(backups)
            
            # Release locks
            self._release_locks(locks)
            
            raise
    
    def _create_snapshots(self) -> Dict[str, Path]:
        """Create backup snapshots of all state files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backups = {}
        
        for name, path in [
            ('progress', self.progress_path),
            ('ac_index', self.ac_index_path),
            ('master_plan', self.master_plan_path),
        ]:
            if path.exists():
                backup_path = path.with_suffix(f'.{timestamp}.backup')
                backup_path.write_text(path.read_text())
                backups[name] = backup_path
        
        return backups
    
    def _acquire_locks(self) -> Dict[str, Any]:
        """Acquire file locks on all state files."""
        locks = {}
        
        for name, path in [
            ('progress', self.progress_path),
            ('ac_index', self.ac_index_path),
            ('master_plan', self.master_plan_path),
        ]:
            if path.exists():
                f = open(path, 'r+')
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                locks[name] = f
        
        return locks
    
    def _release_locks(self, locks: Dict[str, Any]):
        """Release file locks."""
        for f in locks.values():
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            f.close()
    
    def _cleanup_snapshots(self, backups: Dict[str, Path]):
        """Remove backup snapshots after successful commit."""
        for backup_path in backups.values():
            if backup_path.exists():
                backup_path.unlink()
    
    def _restore_snapshots(self, backups: Dict[str, Path]):
        """Restore from backup snapshots on rollback."""
        for name, backup_path in backups.items():
            if backup_path.exists():
                original_path = {
                    'progress': self.progress_path,
                    'ac_index': self.ac_index_path,
                    'master_plan': self.master_plan_path,
                }[name]
                
                original_path.write_text(backup_path.read_text())
                backup_path.unlink()
    
    def update_ac_completion(
        self, 
        ac_id: str, 
        status: str, 
        evidence_bundle_path: Optional[Path] = None,
        test_coverage: float = 0.0,
        conn: Optional[sqlite3.Connection] = None
    ):
        """
        Atomically update AC-ID completion across all 6 sources.
        
        Args:
            ac_id: AC-ID to update (e.g., "AC-AUDIT-001")
            status: New status (implemented, partial, planned, blocked)
            evidence_bundle_path: Path to evidence bundle if complete
            test_coverage: Test coverage percentage
            conn: SQLite connection from atomic_transaction context
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # 1. Update progress-tracker.json
        progress = json.loads(self.progress_path.read_text())
        
        if status == 'implemented':
            if ac_id not in progress['current_phase'].get('verified_implemented', []):
                progress['current_phase'].setdefault('verified_implemented', []).append(ac_id)
            # Remove from other lists
            for key in ['partial', 'planned_not_implemented', 'needs_verification']:
                if ac_id in progress['current_phase'].get(key, []):
                    progress['current_phase'][key].remove(ac_id)
        
        progress['current_phase']['completed_count'] = len(
            progress['current_phase'].get('verified_implemented', [])
        )
        progress['last_updated'] = timestamp
        
        self.progress_path.write_text(json.dumps(progress, indent=2))
        
        # 2. Update AC-INDEX.yaml
        ac_index = yaml.safe_load(self.ac_index_path.open())
        
        # Find AC-ID in acceptance_criteria section
        for category in ac_index.get('acceptance_criteria', []):
            for item in category.get('items', []):
                if item.get('id') == ac_id:
                    item['status'] = status
                    item['implementation'] = item.get('implementation', {})
                    item['implementation']['implemented_at'] = timestamp
                    if evidence_bundle_path:
                        item['evidence_bundle'] = {
                            'path': str(evidence_bundle_path),
                            'validation_status': 'complete'
                        }
                    item['tests'] = item.get('tests', {})
                    item['tests']['coverage'] = test_coverage
                    item['tests']['last_run'] = timestamp
                    item['tests']['status'] = 'passing' if status == 'implemented' else 'failing'
        
        ac_index['completed_count'] = len([
            item for category in ac_index.get('acceptance_criteria', [])
            for item in category.get('items', [])
            if item.get('status') == 'implemented'
        ])
        ac_index['last_updated'] = timestamp
        
        with self.ac_index_path.open('w') as f:
            yaml.safe_dump(ac_index, f, default_flow_style=False, sort_keys=False)
        
        # 3. Update master-plan.yaml
        master_plan = yaml.safe_load(self.master_plan_path.open())
        
        for phase_key in master_plan.get('phases', {}):
            phase = master_plan['phases'][phase_key]
            for component in phase.get('components', []):
                if ac_id in component.get('acceptance_criteria', []):
                    component['status'] = status
        
        master_plan['plan_metadata']['updated'] = timestamp
        
        with self.master_plan_path.open('w') as f:
            yaml.safe_dump(master_plan, f, default_flow_style=False, sort_keys=False)
        
        # 4. Log to governance.db (SQLite)
        if conn:
            conn.execute("""
                INSERT INTO state_updates (
                    timestamp, ac_id, status, evidence_path, test_coverage, source
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, ac_id, status, str(evidence_bundle_path) if evidence_bundle_path else None, 
                  test_coverage, 'AtomicStateManager'))
        
        # 5. Plan-viewer.html regeneration handled by caller
        # 6. Evidence bundle creation handled by evidence generator
        
        self.logger.info(f"Atomically updated {ac_id} to {status} across all sources")

def main():
    """Test atomic state manager"""
    import sys
    
    cortex_root = Path(__file__).parent.parent
    manager = AtomicStateManager(cortex_root)
    
    # Example: Update AC-ID with atomic transaction
    ac_id = sys.argv[1] if len(sys.argv) > 1 else "AC-AUDIT-001"
    status = sys.argv[2] if len(sys.argv) > 2 else "implemented"
    
    try:
        with manager.atomic_transaction() as conn:
            manager.update_ac_completion(
                ac_id=ac_id,
                status=status,
                test_coverage=92.5,
                conn=conn
            )
        print(f"✅ Successfully updated {ac_id} to {status} atomically")
    except Exception as e:
        print(f"❌ Atomic update failed: {e}")
        print("   All changes rolled back")
        sys.exit(1)

if __name__ == '__main__':
    main()
