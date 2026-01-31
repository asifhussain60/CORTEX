#!/usr/bin/env python3
"""
Phase 8.3D: Real Duplicates Consolidation - LOW RISK FIRST

Consolidates 7 low-risk duplicate files:
  1. governance_heatmap (workspace internal)
  2. dashboard_launch (workspace internal)
  3. serve_dashboard (workspace internal)
  4. copy_assets (build hook)
  5. core_files (empty stubs) - keep database.py, delete decorators.py + intelligence.py
  6. lens_commands (CLI)
  7. remote_cache (cache)

AC_START: CONSOLIDATION-LOW-RISK-001
"""

import os
import subprocess
from pathlib import Path

class LowRiskConsolidator:
    """Consolidates 7 low-risk duplicates"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.repo_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
        self.deletions = [
            # Workspace internal (enhancements_* duplicates)
            "_workspaces/dashboard/enhancements_dashboard_governance_heatmap.py",
            "_workspaces/dashboard/enhancements_dashboard_launch.py",
            "_workspaces/dashboard/enhancements_dashboard_serve-cortex-dashboard.py",
            
            # Build hook
            "_workspaces/docs/_hooks/copy_assets.py",
            
            # Empty core stubs (keep database.py, delete others)
            "cortex/core/decorators.py",
            "cortex/core/intelligence.py",
            
            # CLI command (keep cortex/cli/commands/lens.py)
            "_workspaces/dashboard/lens_commands.py",
            
            # Cache (keep cortex/brain/analysis/remote_cache.py)
            "_workspaces/dashboard/remote_cache.py",
        ]
        self.total_deleted = 0
        self.errors = []
    
    def run(self):
        """Execute LOW RISK consolidation"""
        mode = "DRY-RUN" if self.dry_run else "EXECUTION"
        print(f"\n{'='*80}")
        print(f"🟢 LOW RISK CONSOLIDATION - {mode}")
        print(f"{'='*80}\n")
        
        for i, file_path in enumerate(self.deletions, 1):
            self._delete_file(i, file_path)
        
        self._print_summary()
    
    def _delete_file(self, num, file_path):
        """Delete a duplicate file"""
        full_path = self.repo_root / file_path
        
        print(f"{num}. {file_path}")
        
        if not full_path.exists():
            print(f"   ✅ Already deleted (not found)")
            return
        
        if self.dry_run:
            print(f"   🗑️  Would delete: {full_path}")
        else:
            try:
                full_path.unlink()
                print(f"   ✅ Deleted")
                self.total_deleted += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.errors.append((file_path, str(e)))
    
    def _print_summary(self):
        """Print consolidation summary"""
        print(f"\n{'='*80}")
        print("📊 LOW RISK CONSOLIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Files deleted: {self.total_deleted}")
        print(f"⚠️  Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for file_path, error in self.errors:
                print(f"  - {file_path}: {error}")
        
        print(f"\nMode: {'DRY-RUN' if self.dry_run else 'EXECUTION'}")
        if self.dry_run:
            print("Run with --execute to apply deletions")
        else:
            print("✅ LOW RISK consolidation complete!")
            print("\nNext: Run tests to validate, then commit")
        print()

if __name__ == "__main__":
    import sys
    dry_run = "--execute" not in sys.argv
    
    consolidator = LowRiskConsolidator(dry_run=dry_run)
    consolidator.run()
    
    # AC_COMPLETE: CONSOLIDATION-LOW-RISK-001
