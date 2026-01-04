#!/usr/bin/env python3
"""
CORTEX-5.0 Folder Structure Migration Script

Moves root-level markdown files to proper subfolders according to
planning-system-4.0-manifest.yaml requirements.

Usage:
    python migrate-folder-structure.py --dry-run  # Preview changes
    python migrate-folder-structure.py --execute  # Apply changes

Author: Asif Hussain
Date: January 4, 2026
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# File categorization based on content/purpose
MIGRATIONS = {
    # Context documents (vision, design, reference)
    "context": [
        ("EPIC-FEATURE-PLANNER-VISION.md", "epic-feature-planner-vision.md"),
        ("ONBOARDING-UX-OVERVIEW.md", "onboarding-ux-overview.md"),
        ("USER-PERSONAS.md", "user-personas.md"),
        ("ORCHESTRATOR-QUICK-REFERENCE.md", "orchestrator-quick-ref.md"),
        ("QUICK-START.md", "quick-start.md"),
        ("README-ORCHESTRATOR.md", "orchestrator-readme.md"),
        ("README.md", "plan-readme.md"),
        ("master-orchestrator-wiring.md", "orchestrator-wiring.md"),
        ("13-14-15-README.md", "sub-plans-13-15-readme.md"),
    ],
    
    # Reports (completion, status, analysis)
    "reports": [
        ("EPIC-TRANSFORMATION-COMPLETE.md", "epic-transformation-complete.md"),
        ("HOLISTIC-REFINEMENT-ANALYSIS.md", "holistic-refinement-analysis.md"),
        ("ONBOARDING-PLANNING-COMPLETE.md", "onboarding-planning-complete.md"),
        ("SHARED-ORCHESTRATOR-INFRASTRUCTURE-COMPLETE.md", "shared-infra-complete.md"),
        ("VISUAL-SUMMARY.md", "visual-summary.md"),
    ],
}

# Special case: Move to sub-plan context
SUB_PLAN_MIGRATIONS = [
    ("vscode-cache-optimization-enhancement.md", "00D-vscode-cache-optimization/context/enhancement-proposal.md"),
]

def migrate_files(plan_root: Path, dry_run: bool = True):
    """Migrate files to proper folder structure."""
    
    print(f"\n{'🔍 DRY RUN' if dry_run else '⚡ EXECUTING'} Migration")
    print("=" * 60)
    
    # Create universal subfolders
    for folder in ["context", "reports", "artifacts"]:
        folder_path = plan_root / folder
        if not folder_path.exists():
            print(f"\n📁 Create: {folder}/")
            if not dry_run:
                folder_path.mkdir(parents=True, exist_ok=True)
    
    # Migrate files by category
    for category, files in MIGRATIONS.items():
        print(f"\n📂 Category: {category}/")
        for old_name, new_name in files:
            old_path = plan_root / old_name
            new_path = plan_root / category / new_name
            
            if old_path.exists():
                print(f"   📄 {old_name}")
                print(f"   └─→ {category}/{new_name}")
                
                if not dry_run:
                    shutil.move(str(old_path), str(new_path))
                    print("      ✅ Moved")
            else:
                print(f"   ⚠️  File not found: {old_name}")
    
    # Migrate sub-plan specific files
    print(f"\n📂 Sub-Plan Context:")
    for old_name, relative_new_path in SUB_PLAN_MIGRATIONS:
        old_path = plan_root / old_name
        new_path = plan_root / relative_new_path
        
        if old_path.exists():
            print(f"   📄 {old_name}")
            print(f"   └─→ {relative_new_path}")
            
            if not dry_run:
                new_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_path), str(new_path))
                print("      ✅ Moved")
        else:
            print(f"   ⚠️  File not found: {old_name}")
    
    print(f"\n{'✅ Dry run complete' if dry_run else '🎉 Migration complete'}")
    print("=" * 60)
    
    if dry_run:
        print("\n💡 To execute migration: python migrate-folder-structure.py --execute")

if __name__ == "__main__":
    import sys
    
    plan_root = Path(__file__).parent.parent  # CORTEX-5.0 folder
    
    if len(sys.argv) < 2:
        print("Usage: python migrate-folder-structure.py [--dry-run|--execute]")
        sys.exit(1)
    
    dry_run = sys.argv[1] == "--dry-run"
    migrate_files(plan_root, dry_run=dry_run)
