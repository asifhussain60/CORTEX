#!/usr/bin/env python3
"""
Update C50 EPIC Manifest with new folder references.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path


def update_manifest():
    """Update manifest with C50 folder references."""
    
    manifest_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/C50-cortex-v5-remediation/c50-epic-manifest.yaml")
    
    # Read manifest
    content = manifest_path.read_text()
    
    # Mapping of old folder names to new C50 IDs
    folder_mappings = {
        "00A-epic-structure-cleanup/": "C50-00A/",
        "00B-epic-feature-planner/": "C50-00B/",
        "00C-test-coverage-sprint/": "C50-00C/",
        "00D-vscode-cache-optimization/": "C50-00D/",
        "01-refinement-orchestrator/": "C50-01/",
        "02-debug-orchestrator/": "C50-02/",
        "03-knowledge-library-phase/": "C50-03/",
        "04-ast-scanning-planning/": "C50-04/",
        "05-context-middleware/": "C50-05/",
        "06-visual-progress/": "C50-06/",
        "07-refactor-enforcement/": "C50-07/",
        "08-orchestrator-migrations/": "C50-08/",
        "09-final-validation/": "C50-09/",
        "10-acceptance-validation-system/": "C50-10/",
        "11-cortex-lens-admin/": "C50-11/",
        "12-production-validation-pipeline/": "C50-12/",
        "13-onboarding-system/": "C50-13/",
        "14-demo-tutorials/": "C50-14/",
        "15-user-response-templates/": "C50-15/",
        "16-planning-system-v5-fix/": "C50-16/",
        "17-planning-v5-enhancement/": "C50-17/",
        "18-planning-v5-fix/": "C50-18/",
    }
    
    # Update all folder references
    for old_folder, new_folder in folder_mappings.items():
        content = content.replace(old_folder, new_folder)
    
    # Update master plan file name
    content = content.replace("00-MASTER-REMEDIATION-PLAN.md", "00-cortex-v5-remediation.md")
    
    # Update epic ID
    content = content.replace("cortex-5.0-epic-manifest.yaml", "c50-epic-manifest.yaml")
    
    # Update total child plans to 22 (actual count)
    content = re.sub(r"total_child_plans:\s*18", "total_child_plans: 22", content)
    
    # Update "All 18 child plan" references to "All 22 child plans"
    content = content.replace("All 18 child", "All 22 child")
    content = content.replace("18 child plans", "22 child plans")
    content = content.replace("manages 18 child", "manages 22 child")
    
    # Update version and dates
    content = content.replace("version: 5.0.1", "version: 5.1.0")
    content = content.replace("last_updated: '2026-01-04'", "last_updated: '2026-01-04'")
    content = content.replace("last_validated: '2026-01-04'", "last_validated: '2026-01-04'")
    
    # Add C50 metadata
    c50_section = """  # C50-specific metadata
  epic_folder: C50-cortex-v5-remediation
  naming_convention: 3-char alphanumeric ID (C50) + descriptive name
  folder_structure: 5 subfolders (analysis/, artifacts/, context/, reports/, tracking/)
  legacy_folder: CORTEX-5.0 (preserved for reference)
"""
    
    # Insert C50 metadata after viewer line
    content = content.replace("  viewer: plan-viewer.html\n", f"  viewer: plan-viewer.html\n{c50_section}")
    
    # Write updated manifest
    manifest_path.write_text(content)
    
    print("✅ Manifest updated successfully!")
    print(f"📄 File: {manifest_path}")
    print(f"\n📊 Updates:")
    print(f"   • Folder references: 22 child plans updated to C50-* naming")
    print(f"   • Master plan file: 00-cortex-v5-remediation.md")
    print(f"   • Total child plans: 18 → 22")
    print(f"   • Version: 5.0.1 → 5.1.0")
    print(f"   • Added C50-specific metadata section")


if __name__ == "__main__":
    update_manifest()
