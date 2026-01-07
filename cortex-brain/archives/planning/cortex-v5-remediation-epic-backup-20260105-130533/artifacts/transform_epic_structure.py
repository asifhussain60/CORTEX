#!/usr/bin/env python3
"""
EPIC Structure Transformation Script
Transforms CORTEX-5.0 to C50-cortex-v5-remediation with proper EPIC structure.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

# Child plan mapping: old folder name -> new C50 ID
CHILD_PLAN_MAPPING = {
    "00A-epic-structure-cleanup": "C50-00A",
    "00B-epic-feature-planner": "C50-00B",
    "00C-test-coverage-sprint": "C50-00C",
    "00D-vscode-cache-optimization": "C50-00D",
    "01-refinement-orchestrator": "C50-01",
    "02-debug-orchestrator": "C50-02",
    "03-knowledge-library-phase": "C50-03",
    "04-ast-scanning-planning": "C50-04",
    "05-context-middleware": "C50-05",
    "06-visual-progress": "C50-06",
    "07-refactor-enforcement": "C50-07",
    "08-orchestrator-migrations": "C50-08",
    "09-final-validation": "C50-09",
    "10-acceptance-validation-system": "C50-10",
    "11-cortex-lens-admin": "C50-11",
    "12-production-validation-pipeline": "C50-12",
    "13-onboarding-system": "C50-13",
    "14-demo-tutorials": "C50-14",
    "15-user-response-templates": "C50-15",
    "16-planning-system-v5-fix": "C50-16",
    "17-planning-v5-enhancement": "C50-17",
    "18-planning-v5-fix": "C50-18",
}

# Standard subfolder structure for all plans
STANDARD_SUBFOLDERS = [
    "analysis",
    "artifacts",
    "context",
    "reports",
    "tracking"
]


def create_child_plan_structure(c50_root: Path, old_name: str, new_id: str):
    """
    Create child plan folder with 5-subfolder structure.
    
    Args:
        c50_root: Path to C50-cortex-v5-remediation root
        old_name: Original folder name (e.g., "00A-epic-structure-cleanup")
        new_id: New C50 ID (e.g., "C50-00A")
    """
    # Create child plan root
    child_root = c50_root / new_id
    child_root.mkdir(parents=True, exist_ok=True)
    
    # Create 5 standard subfolders
    for subfolder in STANDARD_SUBFOLDERS:
        (child_root / subfolder).mkdir(parents=True, exist_ok=True)
        # Create .gitkeep
        (child_root / subfolder / ".gitkeep").touch()
    
    print(f"✅ Created {new_id}/ with 5 subfolders")
    
    return child_root


def copy_plan_content(old_path: Path, new_path: Path):
    """
    Copy relevant content from old structure to new structure.
    
    Args:
        old_path: Path to old child plan folder
        new_path: Path to new C50 child plan folder
    """
    if not old_path.exists():
        print(f"⚠️  Old path does not exist: {old_path}")
        return
    
    # Copy master plan document (00-*.md)
    for md_file in old_path.glob("00-*.md"):
        dest = new_path / md_file.name
        shutil.copy2(md_file, dest)
        print(f"   📄 Copied {md_file.name}")
    
    # Copy tracking files
    old_tracking = old_path / "tracking"
    new_tracking = new_path / "tracking"
    if old_tracking.exists():
        for file in old_tracking.glob("*"):
            if file.is_file():
                dest = new_tracking / file.name
                shutil.copy2(file, dest)
                print(f"   📊 Copied tracking/{file.name}")
    
    # Copy context files
    old_context = old_path / "context"
    new_context = new_path / "context"
    if old_context.exists():
        for file in old_context.glob("*"):
            if file.is_file():
                dest = new_context / file.name
                shutil.copy2(file, dest)
                print(f"   📝 Copied context/{file.name}")
    
    # Copy artifacts
    old_artifacts = old_path / "artifacts"
    new_artifacts = new_path / "artifacts"
    if old_artifacts.exists():
        for file in old_artifacts.glob("*"):
            if file.is_file():
                dest = new_artifacts / file.name
                shutil.copy2(file, dest)
                print(f"   🔧 Copied artifacts/{file.name}")
    
    # Copy reports
    old_reports = old_path / "reports"
    new_reports = new_path / "reports"
    if old_reports.exists():
        for file in old_reports.glob("*"):
            if file.is_file():
                dest = new_reports / file.name
                shutil.copy2(file, dest)
                print(f"   📋 Copied reports/{file.name}")
    
    # Copy analysis (if exists in old structure)
    old_analysis = old_path / "analysis"
    new_analysis = new_path / "analysis"
    if old_analysis.exists():
        for file in old_analysis.glob("*"):
            if file.is_file():
                dest = new_analysis / file.name
                shutil.copy2(file, dest)
                print(f"   🔍 Copied analysis/{file.name}")


def main():
    """Main transformation execution."""
    print("🚀 CORTEX-5.0 → C50 EPIC Structure Transformation")
    print("=" * 60)
    
    # Paths
    workspace_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
    old_epic = workspace_root / "cortex-brain/documents/planning/active/CORTEX-5.0"
    c50_root = workspace_root / "cortex-brain/documents/planning/active/C50-cortex-v5-remediation"
    
    # Verify old structure exists
    if not old_epic.exists():
        print(f"❌ ERROR: CORTEX-5.0 not found at {old_epic}")
        return
    
    # Verify C50 root exists
    if not c50_root.exists():
        print(f"❌ ERROR: C50 root not found at {c50_root}")
        return
    
    print(f"📂 Source: {old_epic}")
    print(f"📂 Destination: {c50_root}")
    print()
    
    # Transform each child plan
    total_plans = len(CHILD_PLAN_MAPPING)
    for idx, (old_name, new_id) in enumerate(CHILD_PLAN_MAPPING.items(), 1):
        print(f"\n[{idx}/{total_plans}] Transforming {old_name} → {new_id}")
        print("-" * 60)
        
        # Create new structure
        new_child_path = create_child_plan_structure(c50_root, old_name, new_id)
        
        # Copy content from old structure
        old_child_path = old_epic / old_name
        copy_plan_content(old_child_path, new_child_path)
    
    print("\n" + "=" * 60)
    print("✅ Transformation Complete!")
    print(f"\n📊 Summary:")
    print(f"   • Transformed {total_plans} child plans")
    print(f"   • Created {total_plans * 5} subfolders")
    print(f"   • Copied master plans, tracking, context, artifacts, reports")
    print(f"\n📂 New EPIC structure: {c50_root}")
    print(f"📂 Original preserved: {old_epic}")


if __name__ == "__main__":
    main()
