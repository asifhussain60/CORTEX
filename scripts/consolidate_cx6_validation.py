#!/usr/bin/env python3
"""
CORTEX 6 Validation Files Consolidation
Moves CX6-related files from documents/validation to cx6-plan/validation
Follows governance rules: kebab-case naming, duplicate detection, cleanup
"""

import hashlib
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class ValidationConsolidator:
    """Consolidates CX6 validation files with governance enforcement."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.source_dir = workspace_root / "cortex-brain" / "documents" / "validation"
        self.target_dir = workspace_root / "cortex-brain" / "cx6-plan" / "validation"
        self.actions_log = []
        self.duplicates_detected = []
        self.files_to_delete = []
        
    def to_kebab_case(self, filename: str) -> str:
        """Convert filename to kebab-case following governance rules."""
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        
        # Handle AC-ID formats:
        # Format 1: AC-{CATEGORY}-{NUMBER} (e.g., AC-STS-001)
        # Format 2: AC-{CATEGORY}-{WORD}-{NUMBER} (e.g., AC-MCP-EXPOSE-001)
        # Format 3: AC-{CATEGORY}-{NUMBER}-{NUMBER}-{NUMBER} (e.g., AC-STS-001-002-003)
        
        ac_pattern = r'^(AC-[A-Z]+(?:-[A-Z]+)*-\d+(?:-\d+)*)(.*)$'
        match = re.match(ac_pattern, name)
        
        if match:
            # AC-ID part stays uppercase, rest converts to kebab-case
            ac_id = match.group(1)  # Keep AC-ID as-is
            rest = match.group(2)   # Convert rest to kebab-case
            
            # Convert rest to kebab-case
            rest = rest.replace('_', '-')
            rest = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', rest)
            rest = rest.lower()
            rest = re.sub(r'-+', '-', rest)  # Remove multiple hyphens
            rest = rest.strip('-')  # Remove leading/trailing hyphens
            
            name = ac_id + ('-' + rest if rest else '')
        else:
            # Standard kebab-case conversion for non-AC-ID files
            name = name.replace('_', '-')
            name = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name)
            name = name.lower()
            # Remove multiple consecutive hyphens
            name = re.sub(r'-+', '-', name)
            # Remove leading/trailing hyphens
            name = name.strip('-')
        
        return f"{name}.{ext}" if ext else name
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    
    def is_cx6_related(self, filename: str) -> bool:
        """Check if file is CORTEX 6 related."""
        # ALL files in documents/validation are CX6-related
        # This is the consolidation target - move everything
        return True
    
    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Find duplicate files based on content hash."""
        hash_map: Dict[str, List[Path]] = {}
        
        # Scan source directory
        if self.source_dir.exists():
            for file_path in self.source_dir.glob('*'):
                if file_path.is_file():
                    file_hash = self.calculate_file_hash(file_path)
                    hash_map.setdefault(file_hash, []).append(file_path)
        
        # Scan target directory
        if self.target_dir.exists():
            for file_path in self.target_dir.glob('*'):
                if file_path.is_file():
                    file_hash = self.calculate_file_hash(file_path)
                    hash_map.setdefault(file_hash, []).append(file_path)
        
        # Filter to only duplicates
        duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
        return duplicates
    
    def analyze_duplicate_group(self, paths: List[Path]) -> Tuple[Path, List[Path]]:
        """
        Analyze duplicate files and decide which to keep.
        Priority: cx6-plan/validation > documents/validation
        """
        # Sort by priority (cx6-plan first, then by modification time)
        def priority_key(p: Path) -> Tuple[int, float]:
            is_in_cx6 = 'cx6-plan' in str(p)
            mtime = p.stat().st_mtime
            return (0 if is_in_cx6 else 1, -mtime)  # 0 = higher priority
        
        sorted_paths = sorted(paths, key=priority_key)
        keep = sorted_paths[0]
        delete = sorted_paths[1:]
        
        return keep, delete
    
    def plan_consolidation(self) -> Dict[str, any]:
        """Plan the consolidation actions without executing."""
        plan = {
            'cx6_files_to_move': [],
            'files_to_rename': [],
            'duplicates_to_delete': [],
            'non_cx6_files': [],
            'total_actions': 0,
        }
        
        # Find duplicates first
        duplicates = self.find_duplicates()
        
        for file_hash, paths in duplicates.items():
            keep, delete = self.analyze_duplicate_group(paths)
            for del_path in delete:
                plan['duplicates_to_delete'].append({
                    'path': del_path,
                    'reason': f'Duplicate of {keep.name}',
                    'hash': file_hash[:8],
                })
        
        # Analyze source directory files
        if self.source_dir.exists():
            for file_path in sorted(self.source_dir.glob('*')):
                if not file_path.is_file():
                    continue
                
                # Check if file is CX6-related
                if self.is_cx6_related(file_path.name):
                    # Check if it will be renamed
                    new_name = self.to_kebab_case(file_path.name)
                    target_path = self.target_dir / new_name
                    
                    # Skip if it's a duplicate that will be deleted
                    will_be_deleted = any(
                        str(file_path) == str(d['path']) 
                        for d in plan['duplicates_to_delete']
                    )
                    
                    if not will_be_deleted:
                        action = {
                            'source': file_path,
                            'target': target_path,
                            'original_name': file_path.name,
                            'new_name': new_name,
                            'renamed': file_path.name != new_name,
                        }
                        
                        if action['renamed']:
                            plan['files_to_rename'].append(action)
                        else:
                            plan['cx6_files_to_move'].append(action)
                else:
                    plan['non_cx6_files'].append(file_path)
        
        plan['total_actions'] = (
            len(plan['cx6_files_to_move']) + 
            len(plan['files_to_rename']) + 
            len(plan['duplicates_to_delete'])
        )
        
        return plan
    
    def execute_consolidation(self, plan: Dict[str, any], dry_run: bool = True):
        """Execute the consolidation plan."""
        # Create target directory if needed
        if not dry_run:
            self.target_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'=' * 80}")
        print(f"CORTEX 6 Validation Files Consolidation")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        print(f"{'=' * 80}\n")
        
        # Step 1: Delete duplicates
        if plan['duplicates_to_delete']:
            print(f"\n🗑️  STEP 1: Delete Duplicates ({len(plan['duplicates_to_delete'])} files)")
            print("-" * 80)
            
            for item in plan['duplicates_to_delete']:
                path = item['path']
                print(f"  DELETE: {path.relative_to(self.workspace_root)}")
                print(f"          Reason: {item['reason']} (hash: {item['hash']})")
                
                if not dry_run:
                    path.unlink()
                    self.actions_log.append(f"DELETED: {path.name}")
        
        # Step 2: Move and rename CX6 files
        all_moves = plan['cx6_files_to_move'] + plan['files_to_rename']
        
        if all_moves:
            print(f"\n📦 STEP 2: Move CX6 Files ({len(all_moves)} files)")
            print("-" * 80)
            
            for action in all_moves:
                source = action['source']
                target = action['target']
                
                if action['renamed']:
                    print(f"  MOVE + RENAME:")
                    print(f"    From: {source.relative_to(self.workspace_root)}")
                    print(f"    To:   {target.relative_to(self.workspace_root)}")
                    print(f"    Renamed: {action['original_name']} → {action['new_name']}")
                else:
                    print(f"  MOVE:")
                    print(f"    From: {source.relative_to(self.workspace_root)}")
                    print(f"    To:   {target.relative_to(self.workspace_root)}")
                
                if not dry_run:
                    # Check if target exists
                    if target.exists():
                        print(f"    ⚠️  WARNING: Target exists, skipping to prevent overwrite")
                        self.actions_log.append(f"SKIPPED: {source.name} (target exists)")
                    else:
                        shutil.move(str(source), str(target))
                        self.actions_log.append(f"MOVED: {source.name} → {target.name}")
        
        # Step 3: Report non-CX6 files (left in place)
        if plan['non_cx6_files']:
            print(f"\n📋 STEP 3: Non-CX6 Files (left in documents/validation)")
            print("-" * 80)
            
            for file_path in plan['non_cx6_files']:
                print(f"  KEPT: {file_path.name}")
        
        # Summary
        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        print(f"  Total actions: {plan['total_actions']}")
        print(f"  Files moved: {len(all_moves)}")
        print(f"  Files renamed: {len(plan['files_to_rename'])}")
        print(f"  Duplicates deleted: {len(plan['duplicates_to_delete'])}")
        print(f"  Non-CX6 files kept: {len(plan['non_cx6_files'])}")
        
        if dry_run:
            print(f"\n⚠️  DRY RUN: No changes made. Run with --execute to apply changes.")
        else:
            print(f"\n✅ CONSOLIDATION COMPLETE")
            
            # Write log file
            log_file = self.workspace_root / "cortex-brain" / "cx6-plan" / "validation" / f"consolidation-log-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            with open(log_file, 'w') as f:
                f.write(f"CORTEX 6 Validation Consolidation Log\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write(f"{'=' * 80}\n\n")
                for action in self.actions_log:
                    f.write(f"{action}\n")
            
            print(f"  Log written: {log_file.relative_to(self.workspace_root)}")
        
        print(f"{'=' * 80}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Consolidate CORTEX 6 validation files with governance enforcement"
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the consolidation (default: dry-run)'
    )
    parser.add_argument(
        '--workspace',
        type=Path,
        default=Path.cwd(),
        help='Workspace root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    consolidator = ValidationConsolidator(args.workspace)
    plan = consolidator.plan_consolidation()
    consolidator.execute_consolidation(plan, dry_run=not args.execute)


if __name__ == '__main__':
    main()
