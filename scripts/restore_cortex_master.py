#!/usr/bin/env python3
"""
Restore _cortex-master phases with proper governance compliance.

This script:
1. Restores all phase files from git history
2. Applies kebab-case naming (CORTEX governance)
3. Numbers phases sequentially
4. Validates YAML integrity
5. Organizes into proper folder structure
"""

import subprocess
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Git commit with complete phase history
GIT_REF = "1b1e7ddee^"

# Target structure
BASE_PATH = Path("cortex-registry/_cortex-master/phases")
COMPLETED = BASE_PATH / "completed"
DEFERRED = BASE_PATH / "deferred"
PLANNED = BASE_PATH / "planned"
CONSOLIDATED = BASE_PATH / "consolidated"

def run_git_command(cmd: List[str]) -> str:
    """Execute git command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def get_phase_files_from_git() -> Dict[str, List[str]]:
    """Get all phase files from git history, organized by status."""
    # Get completed phases
    completed_cmd = ["git", "ls-tree", "-r", "--name-only", GIT_REF]
    all_files = run_git_command(completed_cmd).split("\n")
    
    phases = {
        "completed": [],
        "active": [],
        "deferred": [],
        "planned": []
    }
    
    for file in all_files:
        if "phases/completed" in file and file.endswith(".yaml"):
            phases["completed"].append(file)
        elif "phases/active" in file and file.endswith(".yaml"):
            phases["active"].append(file)
        elif "phases/deferred" in file and file.endswith(".yaml"):
            phases["deferred"].append(file)
        elif "phases/planned" in file and file.endswith(".yaml"):
            phases["planned"].append(file)
    
    return phases

def extract_phase_number(filename: str) -> int:
    """Extract phase number from filename."""
    match = re.search(r'phase-(\d+)', filename)
    if match:
        return int(match.group(1))
    return 9999  # Put unnumbered phases at end

def apply_governance_naming(filename: str) -> str:
    """Convert filename to kebab-case (CORTEX governance)."""
    # Already in correct format: phase-XX-description.yaml
    # Just ensure no SCREAMING_CASE
    parts = filename.split('/')
    name = parts[-1]
    
    # Convert any remaining uppercase sequences
    name = re.sub(r'([A-Z]+)', lambda m: m.group(1).lower(), name)
    name = re.sub(r'_+', '-', name)  # underscores to hyphens
    name = re.sub(r'-+', '-', name)  # collapse multiple hyphens
    
    return name

def restore_phase_file(git_path: str, target_dir: Path) -> Tuple[str, bool, str]:
    """
    Restore a phase file from git and validate it.
    
    Returns: (filename, success, error_message)
    """
    filename = apply_governance_naming(git_path)
    target_path = target_dir / filename
    
    # Extract content from git
    try:
        content = run_git_command(["git", "show", f"{GIT_REF}:{git_path}"])
    except subprocess.CalledProcessError as e:
        return filename, False, f"Git extraction failed: {e}"
    
    # Validate YAML
    try:
        yaml_data = yaml.safe_load(content)
        if not isinstance(yaml_data, dict):
            return filename, False, "YAML root is not a dict"
    except yaml.YAMLError as e:
        return filename, False, f"YAML parse error: {e}"
    
    # Write file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding='utf-8')
    
    return filename, True, ""

def restore_recent_phases():
    """Restore phase-90, phase-98, phase-102, phase-104 from recent commits."""
    recent_phases = [
        ("edc5d02ee", "cortex-registry/_cortex-master/phases/completed/phase-90-toolkit-centralization.yaml", COMPLETED),
        ("50b5166a7", "cortex-registry/planning/phases/deferred/phase-98-documentation-site-pipeline.yaml", DEFERRED),
        ("ad3f3f5a8", "cortex-registry/planning/phases/planned/phase-102-workflow-runtime-foundation.yaml", PLANNED),
        ("50b5166a7", "cortex-registry/planning/phases/planned/phase-104-registry-intelligence-consolidation.yaml", PLANNED),
    ]
    
    for commit, path, target_dir in recent_phases:
        try:
            content = run_git_command(["git", "show", f"{commit}:{path}"])
            filename = apply_governance_naming(path)
            target_path = target_dir / filename
            
            # Validate YAML
            yaml.safe_load(content)
            
            target_path.write_text(content, encoding='utf-8')
            print(f"✓ Restored {filename} from {commit}")
        except Exception as e:
            print(f"✗ Failed to restore {path}: {e}")

def create_master_index():
    """Create cortex-master.yaml index from restored phases."""
    # Move existing master-index.yaml if it exists
    old_index = Path("cortex-registry/master-index.yaml")
    new_index = Path("cortex-registry/cortex-master.yaml")
    
    if old_index.exists():
        content = old_index.read_text()
        new_index.write_text(content)
        print(f"✓ Renamed master-index.yaml → cortex-master.yaml")
    
    return new_index.exists()

def main():
    """Main restoration process."""
    print("=" * 70)
    print("CORTEX Master Registry Restoration")
    print("=" * 70)
    print()
    
    # Step 1: Get phase files from git
    print("Step 1: Scanning git history...")
    try:
        phases = get_phase_files_from_git()
        print(f"  Found {len(phases['completed'])} completed phases")
        print(f"  Found {len(phases['active'])} active phases")
        print(f"  Found {len(phases['deferred'])} deferred phases")
        print(f"  Found {len(phases['planned'])} planned phases")
    except Exception as e:
        print(f"✗ Failed to scan git: {e}")
        return 1
    
    print()
    
    # Step 2: Restore completed phases
    print("Step 2: Restoring completed phases...")
    completed_files = sorted(phases['completed'], key=lambda x: extract_phase_number(x))
    success_count = 0
    fail_count = 0
    
    for git_path in completed_files:
        filename, success, error = restore_phase_file(git_path, COMPLETED)
        if success:
            success_count += 1
            print(f"  ✓ {filename}")
        else:
            fail_count += 1
            print(f"  ✗ {filename}: {error}")
    
    print(f"\n  Completed: {success_count} success, {fail_count} failures")
    print()
    
    # Step 3: Restore active phases (treat as completed since they're historical)
    print("Step 3: Restoring historical active phases as deferred...")
    active_files = sorted(phases['active'], key=lambda x: extract_phase_number(x))
    
    for git_path in active_files:
        filename, success, error = restore_phase_file(git_path, DEFERRED)
        if success:
            print(f"  ✓ {filename}")
    
    print()
    
    # Step 4: Restore recent phases (90, 98, 102, 104)
    print("Step 4: Restoring recent phases (90, 98, 102, 104)...")
    restore_recent_phases()
    print()
    
    # Step 5: Create master index
    print("Step 5: Creating cortex-master.yaml...")
    if create_master_index():
        print("  ✓ cortex-master.yaml created")
    else:
        print("  ✗ Failed to create cortex-master.yaml")
    print()
    
    # Step 6: Summary
    print("=" * 70)
    print("Restoration Complete!")
    print("=" * 70)
    completed_count = len(list(COMPLETED.glob("*.yaml")))
    deferred_count = len(list(DEFERRED.glob("*.yaml")))
    planned_count = len(list(PLANNED.glob("*.yaml")))
    
    print(f"\nFinal Structure:")
    print(f"  cortex-registry/")
    print(f"  ├── cortex-master.yaml")
    print(f"  └── _cortex-master/")
    print(f"      └── phases/")
    print(f"          ├── completed/ ({completed_count} files)")
    print(f"          ├── deferred/ ({deferred_count} files)")
    print(f"          ├── planned/ ({planned_count} files)")
    print(f"          └── consolidated/ (0 files)")
    print()
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
