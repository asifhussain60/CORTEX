#!/usr/bin/env python3
"""
Phase 8.3D: MEDIUM + HIGH RISK Consolidation - All remaining 11 duplicate files

MEDIUM RISK (6 groups, ~8 files):
  1. metrics_dashboard (observability)
  2. intent_reflection_protocol (brain/core)
  3. knowledge_graph (brain/core)
  4. lens_context_builder (intent logic)
  5. relationship_analyzer (orchestrator)
  6. dashboard_extensibility (core duplication)

HIGH RISK (2 groups, ~4 files):
  7. dashboard_api (API implementation)
  8. dashboard_api_main (API endpoint)

Total: 11 files to delete

AC_START: CONSOLIDATION-MEDIUM-HIGH-RISK-001
"""

import os
import subprocess
from pathlib import Path

class MediumHighRiskConsolidator:
    """Consolidates remaining MEDIUM + HIGH RISK duplicates"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.repo_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
        
        # MEDIUM RISK deletions
        self.medium_risk_deletions = [
            # metrics_dashboard
            "_workspaces/dashboard/enhancements_dashboard_metrics_dashboard.py",
            
            # intent_reflection_protocol
            "_workspaces/dashboard/intent_reflection_protocol.py",
            
            # knowledge_graph
            "_workspaces/dashboard/knowledge_graph.py",
            
            # lens_context_builder
            "_workspaces/dashboard/lens_context_builder.py",
            
            # relationship_analyzer
            "_workspaces/dashboard/relationship_analyzer.py",
            
            # dashboard_extensibility (keep cortex/brain/observability/, delete cortex/observability/)
            "cortex/observability/dashboard_extensibility.py",
        ]
        
        # HIGH RISK deletions
        self.high_risk_deletions = [
            # dashboard_api
            "_workspaces/dashboard/api/main.py",
            "_workspaces/dashboard/enhancements_dashboard_api_main.py",
            
            # dashboard_api_main
            "_workspaces/dashboard/enhancements_dashboard_api.py",
        ]
        
        self.total_deleted = 0
        self.errors = []
    
    def run(self):
        """Execute MEDIUM + HIGH RISK consolidation"""
        mode = "DRY-RUN" if self.dry_run else "EXECUTION"
        print(f"\n{'='*80}")
        print(f"🟡 MEDIUM + HIGH RISK CONSOLIDATION - {mode}")
        print(f"{'='*80}\n")
        
        print("🟡 MEDIUM RISK DELETIONS (6 files):")
        print("-" * 80)
        for i, file_path in enumerate(self.medium_risk_deletions, 1):
            self._delete_file(i, file_path, "MEDIUM")
        
        print("\n🔴 HIGH RISK DELETIONS (5 files):")
        print("-" * 80)
        for i, file_path in enumerate(self.high_risk_deletions, len(self.medium_risk_deletions) + 1):
            self._delete_file(i, file_path, "HIGH")
        
        self._print_summary()
    
    def _delete_file(self, num, file_path, risk_level):
        """Delete a duplicate file"""
        full_path = self.repo_root / file_path
        
        print(f"{num}. {file_path}")
        
        if not full_path.exists():
            print(f"   ✅ Already deleted (not found)")
            return
        
        if self.dry_run:
            print(f"   🗑️  Would delete")
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
        print("📊 MEDIUM + HIGH RISK CONSOLIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Files deleted: {self.total_deleted}")
        print(f"⚠️  Errors: {len(self.errors)}")
        print(f"🟡 MEDIUM RISK: 6 files")
        print(f"🔴 HIGH RISK: 5 files")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for file_path, error in self.errors:
                print(f"  - {file_path}: {error}")
        
        print(f"\nMode: {'DRY-RUN' if self.dry_run else 'EXECUTION'}")
        if self.dry_run:
            print("Run with --execute to apply deletions")
        else:
            print("✅ MEDIUM + HIGH RISK consolidation complete!")
            print("\nNext: Run comprehensive tests to validate")
        print()

if __name__ == "__main__":
    import sys
    dry_run = "--execute" not in sys.argv
    
    consolidator = MediumHighRiskConsolidator(dry_run=dry_run)
    consolidator.run()
    
    # AC_COMPLETE: CONSOLIDATION-MEDIUM-HIGH-RISK-001
