#!/usr/bin/env python3
"""
Remove version numbers from orchestrator references across CORTEX codebase.
Standardize to CORTEX 4.0 with no version numbers in orchestrator names.
"""

import re
from pathlib import Path
from typing import List, Tuple

# Replacements to make
REPLACEMENTS = [
    # Planning System 2.0 → Planning System
    (r"Planning System 2\.0", "Planning System"),
    (r"planning-system-2\.0", "planning-system"),
    (r"planning_system_2\.0", "planning_system"),
    
    # Maintenance v3 → Maintenance
    (r"Maintenance Orchestrator v3\.0", "Maintenance Orchestrator"),
    (r"MaintenanceOrchestratorV3", "MaintenanceOrchestrator"),
    (r"maintenance_orchestrator_v3", "maintenance_orchestrator"),
    (r"maintenance_v3", "maintenance"),
    
    # TDD v4 → TDD
    (r"TDD Orchestrator v4\.0", "TDD Orchestrator"),
    (r"TDDOrchestratorV4", "TDDOrchestrator"),
    (r"tdd_orchestrator_v4", "tdd_orchestrator"),
    
    # Other versioned references
    (r"Orchestrator v[0-9]+\.[0-9]+", "Orchestrator"),
    (r"System 3\.0", "System"),
]

# Files to exclude
EXCLUDE_PATTERNS = [
    "*_archived.py",
    "*_migrated.py",
    "*.db",
    "*.pyc",
    "__pycache__",
    ".venv",
    "site-packages",
]

def should_process(file_path: Path) -> bool:
    """Check if file should be processed."""
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in str(file_path):
            return False
    
    # Only process specific file types
    return file_path.suffix in [".py", ".md", ".yaml", ".yml", ".json", ".txt"]

def process_file(file_path: Path) -> Tuple[bool, int]:
    """
    Process a single file, applying all replacements.
    
    Returns:
        (changed, num_replacements)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        num_replacements = 0
        
        for pattern, replacement in REPLACEMENTS:
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                num_replacements += count
        
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True, num_replacements
        
        return False, 0
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0

def main():
    """Main execution."""
    cortex_root = Path(__file__).parent.parent
    
    # Directories to process
    search_dirs = [
        cortex_root / "src",
        cortex_root / "cortex-sample-apps",
        cortex_root / "cortex-brain",
        cortex_root / "tests",
    ]
    
    total_files = 0
    changed_files = 0
    total_replacements = 0
    
    print("🔄 Removing version numbers from orchestrator references...")
    print()
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        
        for file_path in search_dir.rglob("*"):
            if not file_path.is_file():
                continue
            
            if not should_process(file_path):
                continue
            
            total_files += 1
            changed, num_replacements = process_file(file_path)
            
            if changed:
                changed_files += 1
                total_replacements += num_replacements
                rel_path = file_path.relative_to(cortex_root)
                print(f"✓ {rel_path} ({num_replacements} replacements)")
    
    print()
    print(f"✅ Complete: {changed_files}/{total_files} files changed, {total_replacements} replacements made")

if __name__ == "__main__":
    main()
