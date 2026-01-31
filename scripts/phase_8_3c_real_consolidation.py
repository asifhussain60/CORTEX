#!/usr/bin/env python3
"""
Phase 8.3C: Automated P0 Consolidation - EXECUTION SCRIPT

Consolidates 6 real P0 duplicate files found in audit.
Each file has both canonical and duplicate versions.

Targets:
  1. bootstrap.py
  2. lazy_module_loader.py
  3. version_manager.py
  4. lens_integration.py
  5. testing_framework.py
  6. template_validator.py

AC_START: EXEC-Phase-8.3C-001
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

class P0ConsolidationExecutor:
    """Executes P0 consolidation for 6 duplicate files"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.repo_root = Path(__file__).parent.parent
        self.consolidations = [
            {
                "id": 1,
                "name": "bootstrap.py",
                "canonical": "cortex/bootstrap.py",
                "duplicates": ["cortex/wiring/bootstrap.py"],
                "imports_to_update": [
                    ("from cortex.wiring.bootstrap import", "from cortex.bootstrap import"),
                    ("from cortex.wiring import bootstrap", "from cortex import bootstrap"),
                ]
            },
            {
                "id": 2,
                "name": "lazy_module_loader.py",
                "canonical": "cortex/visualization/spa/lazy_module_loader.py",
                "duplicates": ["cortex/visualization/scripts/lazy_module_loader.py"],
                "imports_to_update": [
                    ("from cortex.visualization.scripts.lazy_module_loader import", 
                     "from cortex.visualization.spa.lazy_module_loader import"),
                ]
            },
            {
                "id": 3,
                "name": "version_manager.py",
                "canonical": "cortex/orchestrators/version_manager.py",
                "duplicates": ["cortex/domain_brain/version_manager.py"],
                "imports_to_update": [
                    ("from cortex.domain_brain.version_manager import",
                     "from cortex.orchestrators.version_manager import"),
                ]
            },
            {
                "id": 4,
                "name": "lens_integration.py",
                "canonical": "cortex/brain/discovery/lens_integration.py",
                "duplicates": ["cortex/domain_brain/lens_integration.py"],
                "imports_to_update": [
                    ("from cortex.domain_brain.lens_integration import",
                     "from cortex.brain.discovery.lens_integration import"),
                ]
            },
            {
                "id": 5,
                "name": "testing_framework.py",
                "canonical": "cortex/orchestrators/adaptive/testing_framework.py",
                "duplicates": ["cortex/tools/testing_framework.py"],
                "imports_to_update": [
                    ("from cortex.tools.testing_framework import",
                     "from cortex.orchestrators.adaptive.testing_framework import"),
                ]
            },
            {
                "id": 6,
                "name": "template_validator.py",
                "canonical": "cortex/templates/template_validator.py",
                "duplicates": ["cortex/tools/template_validator.py"],
                "imports_to_update": [
                    ("from cortex.tools.template_validator import",
                     "from cortex.templates.template_validator import"),
                ]
            },
        ]
        
        self.total_updates = 0
        self.total_deletions = 0
        self.errors = []
    
    def run(self):
        """Execute consolidation"""
        mode = "DRY-RUN" if self.dry_run else "EXECUTION"
        print(f"\n{'='*80}")
        print(f"🚀 PHASE 8.3C P0 CONSOLIDATION - {mode}")
        print(f"{'='*80}\n")
        
        for consolidation in self.consolidations:
            self._consolidate_file(consolidation)
        
        self._print_summary()
    
    def _consolidate_file(self, config):
        """Consolidate a single P0 duplicate"""
        file_id = config["id"]
        name = config["name"]
        canonical = config["canonical"]
        duplicates = config["duplicates"]
        
        print(f"📋 [{file_id}/6] Consolidating: {name}")
        print(f"   Canonical:  {canonical}")
        
        # Verify canonical exists
        canonical_path = self.repo_root / canonical
        if not canonical_path.exists():
            print(f"   ❌ Canonical not found: {canonical}")
            self.errors.append(f"Canonical missing: {canonical}")
            return
        
        updates = 0
        deletions = 0
        
        # Update imports in all files
        for old_import, new_import in config["imports_to_update"]:
            result = self._update_imports_in_codebase(old_import, new_import)
            updates += result
        
        # Delete duplicate files
        for duplicate in duplicates:
            duplicate_path = self.repo_root / duplicate
            if duplicate_path.exists():
                if not self.dry_run:
                    duplicate_path.unlink()
                    print(f"   🗑️  Deleted: {duplicate}")
                else:
                    print(f"   🗑️  Would delete: {duplicate}")
                deletions += 1
            else:
                print(f"   ✅ Already deleted: {duplicate}")
        
        self.total_updates += updates
        self.total_deletions += deletions
        
        if updates == 0 and deletions == 0:
            print(f"   ✅ Already consolidated")
        else:
            print(f"   ✅ Updated imports: {updates}")
            print(f"   ✅ Deleted duplicates: {deletions}")
        print()
    
    def _update_imports_in_codebase(self, old_import: str, new_import: str) -> int:
        """Update imports in all Python files"""
        count = 0
        
        # Find all files with the old import
        find_cmd = f"grep -r '{old_import}' {self.repo_root}/cortex {self.repo_root}/tests 2>/dev/null"
        try:
            result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True)
            files_with_import = [line.split(':')[0] for line in result.stdout.strip().split('\n') if line]
            
            for file_path_str in set(files_with_import):
                if not file_path_str:
                    continue
                
                file_path = Path(file_path_str)
                if not file_path.exists():
                    continue
                
                # Read file
                content = file_path.read_text()
                
                # Update if contains old import
                if old_import in content:
                    new_content = content.replace(old_import, new_import)
                    
                    if not self.dry_run:
                        file_path.write_text(new_content)
                    
                    count += 1
        except Exception as e:
            self.errors.append(f"Error updating imports: {e}")
        
        return count
    
    def _print_summary(self):
        """Print consolidation summary"""
        print(f"{'='*80}")
        print("📊 CONSOLIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Total import updates: {self.total_updates}")
        print(f"🗑️  Total files deleted: {self.total_deletions}")
        print(f"⚠️  Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        print(f"\nMode: {'DRY-RUN' if self.dry_run else 'EXECUTION'}")
        if self.dry_run:
            print("Run with --execute to apply changes")
        else:
            print("✅ Changes applied successfully")
        print()

if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv
    
    executor = P0ConsolidationExecutor(dry_run=dry_run)
    executor.run()
    
    # AC_COMPLETE: EXEC-Phase-8.3C-001
