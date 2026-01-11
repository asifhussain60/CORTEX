#!/usr/bin/env python3
"""
CORTEX 6.0 Documentation Reorganization Script
Reorganizes cx6-holistic-analysis folder into proper structure with kebab-case naming
"""

import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import json
import sys

# Define workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent
CORTEX_BRAIN = WORKSPACE_ROOT / "cortex-brain"
DOCS_ROOT = CORTEX_BRAIN / "documents"

# Define target structure
TARGET_STRUCTURE = {
    "cx6-plan": CORTEX_BRAIN / "cx6-plan",
    "phases": CORTEX_BRAIN / "cx6-plan" / "phases",
    "architecture": CORTEX_BRAIN / "cx6-plan" / "architecture",
    "validation": CORTEX_BRAIN / "cx6-plan" / "validation",
    "archive": CORTEX_BRAIN / "cx6-plan" / "archive",
    "archive_legacy": CORTEX_BRAIN / "cx6-plan" / "archive" / "legacy"
}

# Define file relocation map
# Format: (source_path, target_path, new_name)
FILE_RELOCATIONS: List[Tuple[Path, Path, str]] = [
    # Master plan files
    (DOCS_ROOT / "cx6-holistic-analysis" / "holistic-snowball-plan.yaml", 
     TARGET_STRUCTURE["cx6-plan"], "master-plan.yaml"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "corrected-implementation-plan.md",
     TARGET_STRUCTURE["cx6-plan"], "implementation-roadmap.md"),
    
    # Phase documents
    (DOCS_ROOT / "cx6-holistic-analysis" / "phase-1-foundation.md",
     TARGET_STRUCTURE["phases"], "phase-1-foundation.md"),
    
    # Architecture diagrams
    (DOCS_ROOT / "cx6-holistic-analysis" / "phase-1-architecture.mmd",
     TARGET_STRUCTURE["architecture"], "phase-1-foundation.mmd"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "response-template-architecture.mmd",
     TARGET_STRUCTURE["architecture"], "response-templates.mmd"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "knowledge-flow.mmd",
     TARGET_STRUCTURE["architecture"], "knowledge-flow.mmd"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "hybrid-approach-architecture.yaml",
     TARGET_STRUCTURE["architecture"], "hybrid-approach.yaml"),
    
    # Validation documents
    (DOCS_ROOT / "cx6-holistic-analysis" / "FINAL-REVIEW-SUMMARY.md",
     TARGET_STRUCTURE["validation"], "final-review-summary.md"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "final-holistic-review.yaml",
     TARGET_STRUCTURE["validation"], "holistic-review.yaml"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "mcp-exposure-protocol-summary.md",
     TARGET_STRUCTURE["validation"], "mcp-exposure-protocol.md"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "PLAN-UPDATE-TEMPLATE-ARCHITECTURE.md",
     TARGET_STRUCTURE["validation"], "plan-update-template.md"),
    
    # Archive files
    (DOCS_ROOT / "cx6-holistic-analysis" / "4-week-implementation-plan.yaml",
     TARGET_STRUCTURE["archive"], "4-week-plan.yaml"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "gpt-analysis.txt",
     TARGET_STRUCTURE["archive"], "gpt-analysis.txt"),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "gpt-impl-plan.txt",
     TARGET_STRUCTURE["archive"], "gpt-impl-plan.txt"),
]

# Define directories to move entirely
DIRECTORY_MOVES: List[Tuple[Path, Path]] = [
    (DOCS_ROOT / "cx6-holistic-analysis" / "archive", 
     TARGET_STRUCTURE["archive_legacy"]),
    
    (DOCS_ROOT / "cx6-holistic-analysis" / "round 1",
     TARGET_STRUCTURE["archive_legacy"] / "round-1"),
]

# Define reference update patterns
REFERENCE_UPDATES = {
    "documents/cx6-holistic-analysis/holistic-snowball-plan.yaml": "cx6-plan/master-plan.yaml",
    "documents/cx6-holistic-analysis/corrected-implementation-plan.md": "cx6-plan/implementation-roadmap.md",
    "documents/cx6-holistic-analysis/phase-1-architecture.mmd": "cx6-plan/architecture/phase-1-foundation.mmd",
    "documents/cx6-holistic-analysis/phase-1-foundation.md": "cx6-plan/phases/phase-1-foundation.md",
    "documents/cx6-holistic-analysis/": "cx6-plan/",
    "cx6-holistic-analysis/": "cx6-plan/",
}

# Files that reference the old structure
FILES_TO_UPDATE = [
    WORKSPACE_ROOT / "src" / "orchestrators" / "core" / "state_synchronizer.py",
    WORKSPACE_ROOT / ".github" / "prompts" / "CORTEX.prompt.md",
    WORKSPACE_ROOT / "templates" / "plan-viewer" / "README.md",
    WORKSPACE_ROOT / "templates" / "plan-viewer" / "README-QUICKSTART.md",
]


class ReorganizationExecutor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.actions_log: List[str] = []
        self.errors_log: List[str] = []
        
    def log_action(self, action: str):
        """Log an action"""
        prefix = "[DRY-RUN] " if self.dry_run else "[EXECUTE] "
        message = f"{prefix}{action}"
        self.actions_log.append(message)
        print(message)
        
    def log_error(self, error: str):
        """Log an error"""
        message = f"[ERROR] {error}"
        self.errors_log.append(message)
        print(message, file=sys.stderr)
    
    def create_directories(self):
        """Create target directory structure"""
        self.log_action("=== Creating Target Directory Structure ===")
        
        for name, path in TARGET_STRUCTURE.items():
            if not self.dry_run:
                path.mkdir(parents=True, exist_ok=True)
            self.log_action(f"Created: {path.relative_to(WORKSPACE_ROOT)}")
    
    def relocate_files(self):
        """Relocate files according to FILE_RELOCATIONS"""
        self.log_action("\n=== Relocating Files ===")
        
        for source, target_dir, new_name in FILE_RELOCATIONS:
            if not source.exists():
                self.log_error(f"Source file not found: {source.relative_to(WORKSPACE_ROOT)}")
                continue
            
            target_path = target_dir / new_name
            
            if not self.dry_run:
                try:
                    shutil.move(str(source), str(target_path))
                except Exception as e:
                    self.log_error(f"Failed to move {source.name}: {e}")
                    continue
            
            self.log_action(f"Moved: {source.relative_to(WORKSPACE_ROOT)} → {target_path.relative_to(WORKSPACE_ROOT)}")
    
    def move_directories(self):
        """Move entire directories"""
        self.log_action("\n=== Moving Directories ===")
        
        for source, target in DIRECTORY_MOVES:
            if not source.exists():
                self.log_error(f"Source directory not found: {source.relative_to(WORKSPACE_ROOT)}")
                continue
            
            if not self.dry_run:
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(target))
                except Exception as e:
                    self.log_error(f"Failed to move directory {source.name}: {e}")
                    continue
            
            self.log_action(f"Moved: {source.relative_to(WORKSPACE_ROOT)} → {target.relative_to(WORKSPACE_ROOT)}")
    
    def update_references(self):
        """Update references in code files"""
        self.log_action("\n=== Updating References in Code Files ===")
        
        for file_path in FILES_TO_UPDATE:
            if not file_path.exists():
                self.log_error(f"File to update not found: {file_path.relative_to(WORKSPACE_ROOT)}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                updates_made = []
                
                # Apply all reference updates
                for old_ref, new_ref in REFERENCE_UPDATES.items():
                    if old_ref in content:
                        content = content.replace(old_ref, new_ref)
                        updates_made.append(f"{old_ref} → {new_ref}")
                
                # Special handling for state_synchronizer.py (Path components)
                if file_path.name == "state_synchronizer.py":
                    # Update Path construction
                    old_path_pattern = 'self.brain_root / "documents" / "cx6-holistic-analysis" / "holistic-snowball-plan.yaml"'
                    new_path_pattern = 'self.brain_root / "cx6-plan" / "master-plan.yaml"'
                    if old_path_pattern in content:
                        content = content.replace(old_path_pattern, new_path_pattern)
                        updates_made.append(f"Path construction updated")
                
                if content != original_content:
                    if not self.dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    self.log_action(f"Updated: {file_path.relative_to(WORKSPACE_ROOT)}")
                    for update in updates_made:
                        self.log_action(f"  - {update}")
                else:
                    self.log_action(f"No changes needed: {file_path.relative_to(WORKSPACE_ROOT)}")
                    
            except Exception as e:
                self.log_error(f"Failed to update {file_path.name}: {e}")
    
    def cleanup_empty_directories(self):
        """Remove empty directories after reorganization"""
        self.log_action("\n=== Cleaning Up Empty Directories ===")
        
        old_dir = DOCS_ROOT / "cx6-holistic-analysis"
        
        if not old_dir.exists():
            return
        
        # Check if directory is empty or only contains empty subdirs
        def is_empty_recursive(path: Path) -> bool:
            if not path.is_dir():
                return False
            items = list(path.iterdir())
            if not items:
                return True
            return all(is_empty_recursive(item) for item in items)
        
        if is_empty_recursive(old_dir):
            if not self.dry_run:
                shutil.rmtree(old_dir)
            self.log_action(f"Removed empty directory: {old_dir.relative_to(WORKSPACE_ROOT)}")
        else:
            remaining_files = list(old_dir.rglob("*"))
            self.log_action(f"Directory not empty, {len(remaining_files)} items remain: {old_dir.relative_to(WORKSPACE_ROOT)}")
    
    def generate_summary_report(self):
        """Generate summary report"""
        self.log_action("\n" + "="*70)
        self.log_action("=== REORGANIZATION SUMMARY ===")
        self.log_action("="*70)
        
        self.log_action(f"\nMode: {'DRY-RUN (no changes made)' if self.dry_run else 'EXECUTE (changes applied)'}")
        self.log_action(f"Total Actions: {len(self.actions_log)}")
        self.log_action(f"Total Errors: {len(self.errors_log)}")
        
        if self.errors_log:
            self.log_action("\n⚠️  ERRORS ENCOUNTERED:")
            for error in self.errors_log:
                print(error)
        
        if not self.dry_run:
            self.log_action("\n✅ Reorganization complete!")
            self.log_action("\nNext steps:")
            self.log_action("1. Run: python3 -m src.main 'synchronize state' --format markdown")
            self.log_action("2. Run: pytest tests/ -v")
            self.log_action("3. Verify plan-viewer loads correctly")
            self.log_action("4. Run vacuum orchestrator to clean redundant files")
        else:
            self.log_action("\n✅ Dry-run complete. Review the actions above.")
            self.log_action("\nTo execute, run:")
            self.log_action("  python3 scripts/reorganize_cx6_docs.py --execute")
    
    def execute(self):
        """Execute the full reorganization"""
        try:
            self.create_directories()
            self.relocate_files()
            self.move_directories()
            self.update_references()
            self.cleanup_empty_directories()
            self.generate_summary_report()
            
            return len(self.errors_log) == 0
        
        except Exception as e:
            self.log_error(f"Fatal error during reorganization: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Reorganize CORTEX 6.0 documentation structure"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the reorganization (default is dry-run)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without executing (default)"
    )
    
    args = parser.parse_args()
    
    # Execute is opposite of dry-run
    dry_run = not args.execute
    
    print("="*70)
    print("CORTEX 6.0 DOCUMENTATION REORGANIZATION")
    print("="*70)
    print(f"Mode: {'DRY-RUN (preview only)' if dry_run else 'EXECUTE (apply changes)'}")
    print("="*70)
    print()
    
    executor = ReorganizationExecutor(dry_run=dry_run)
    success = executor.execute()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
