#!/usr/bin/env python3
"""
CORTEX Toolkit - Planning System Version Renamer

Renames all references to Planning System X.0 to Planning System Y.0 across the entire codebase.

Usage:
    python cortex-toolkit/rename_planning_system_version.py --from 4.0 --to 3.0
    python cortex-toolkit/rename_planning_system_version.py --from 3.0 --to 4.0 --dry-run

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple
import sys


class PlanningSystemRenamer:
    """Renames Planning System version references across CORTEX codebase."""
    
    def __init__(self, project_root: Path, from_version: str, to_version: str, dry_run: bool = False):
        self.project_root = project_root
        self.from_version = from_version
        self.to_version = to_version
        self.dry_run = dry_run
        
        # Files/directories to exclude
        self.exclude_patterns = [
            '.git',
            '.venv',
            'venv',
            '__pycache__',
            '*.pyc',
            'node_modules',
            'build',
            'dist',
            '*.egg-info',
            'cortex-lens-output',
            'archive'
        ]
        
        # File extensions to process
        self.include_extensions = [
            '.py',
            '.md',
            '.yaml',
            '.yml',
            '.txt',
            '.json',
            '.sh',
            '.bat'
        ]
        
        self.changes: List[Tuple[Path, int, str, str]] = []
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        # Check extension
        if file_path.suffix not in self.include_extensions:
            return False
        
        # Check if in excluded directory
        for part in file_path.parts:
            if any(part.startswith(pattern.rstrip('*')) for pattern in self.exclude_patterns if '*' not in pattern):
                return False
        
        return True
    
    def should_rename_file(self, file_path: Path) -> bool:
        """Check if filename itself should be renamed."""
        filename = file_path.name
        return f"PLANNING-SYSTEM-{self.from_version}" in filename.upper() or \
               f"Planning-System-{self.from_version}" in filename
    
    def get_new_filename(self, file_path: Path) -> str:
        """Generate new filename with updated version."""
        filename = file_path.name
        # Handle different case variations
        patterns = [
            (f"PLANNING-SYSTEM-{self.from_version}", f"PLANNING-SYSTEM-{self.to_version}"),
            (f"Planning-System-{self.from_version}", f"Planning-System-{self.to_version}"),
            (f"planning-system-{self.from_version}", f"planning-system-{self.to_version}"),
        ]
        
        for old, new in patterns:
            if old in filename:
                return filename.replace(old, new)
        
        return filename
    
    def process_file_content(self, file_path: Path) -> int:
        """Process file content and track changes."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Skip binary files
            return 0
        
        # Replace patterns (case-sensitive)
        patterns = [
            (f"Planning System {self.from_version}", f"Planning System {self.to_version}"),
            (f"PLANNING SYSTEM {self.from_version}", f"PLANNING SYSTEM {self.to_version}"),
            (f"planning system {self.from_version}", f"planning system {self.to_version}"),
            (f"Planning-System-{self.from_version}", f"Planning-System-{self.to_version}"),
            (f"PLANNING-SYSTEM-{self.from_version}", f"PLANNING-SYSTEM-{self.to_version}"),
            (f"planning-system-{self.from_version}", f"planning-system-{self.to_version}"),
        ]
        
        new_content = content
        changes_count = 0
        
        for old_pattern, new_pattern in patterns:
            if old_pattern in new_content:
                matches = new_content.count(old_pattern)
                changes_count += matches
                new_content = new_content.replace(old_pattern, new_pattern)
        
        if changes_count > 0:
            # Track changes
            for i, line in enumerate(content.split('\n'), 1):
                for old_pattern, new_pattern in patterns:
                    if old_pattern in line:
                        self.changes.append((file_path, i, old_pattern, new_pattern))
            
            # Write changes if not dry run
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
        
        return changes_count
    
    def rename_file(self, file_path: Path) -> Tuple[Path, Path]:
        """Rename file with new version number."""
        new_name = self.get_new_filename(file_path)
        new_path = file_path.parent / new_name
        
        if not self.dry_run:
            file_path.rename(new_path)
        
        return file_path, new_path
    
    def scan_and_rename(self) -> Dict[str, int]:
        """Scan entire project and perform renaming."""
        stats = {
            'files_scanned': 0,
            'files_modified': 0,
            'files_renamed': 0,
            'total_replacements': 0
        }
        
        renamed_files = []
        
        # First pass: rename files
        print(f"\n🔍 Scanning for files to rename...")
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            if self.should_rename_file(file_path):
                old_path, new_path = self.rename_file(file_path)
                renamed_files.append((old_path, new_path))
                stats['files_renamed'] += 1
                
                mode = "DRY RUN" if self.dry_run else "RENAMED"
                print(f"  [{mode}] {old_path.name} → {new_path.name}")
        
        # Second pass: process file contents
        print(f"\n🔍 Scanning for content references...")
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            if not self.should_process_file(file_path):
                continue
            
            stats['files_scanned'] += 1
            replacements = self.process_file_content(file_path)
            
            if replacements > 0:
                stats['files_modified'] += 1
                stats['total_replacements'] += replacements
                
                mode = "DRY RUN" if self.dry_run else "MODIFIED"
                rel_path = file_path.relative_to(self.project_root)
                print(f"  [{mode}] {rel_path} ({replacements} replacements)")
        
        return stats
    
    def print_summary(self, stats: Dict[str, int]):
        """Print summary of changes."""
        print("\n" + "="*70)
        print("📊 RENAMING SUMMARY")
        print("="*70)
        print(f"From Version: Planning System {self.from_version}")
        print(f"To Version:   Planning System {self.to_version}")
        print(f"Mode:         {'DRY RUN (no changes made)' if self.dry_run else 'LIVE (changes applied)'}")
        print("-"*70)
        print(f"Files Scanned:        {stats['files_scanned']}")
        print(f"Files Modified:       {stats['files_modified']}")
        print(f"Files Renamed:        {stats['files_renamed']}")
        print(f"Total Replacements:   {stats['total_replacements']}")
        print("="*70)
        
        if self.dry_run:
            print("\n⚠️  This was a DRY RUN. No files were modified.")
            print("   Run without --dry-run to apply changes.")
        else:
            print("\n✅ Renaming complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Rename Planning System version references across CORTEX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rename from 4.0 to 3.0 (dry run)
  python cortex-toolkit/rename_planning_system_version.py --from 4.0 --to 3.0 --dry-run
  
  # Rename from 4.0 to 3.0 (apply changes)
  python cortex-toolkit/rename_planning_system_version.py --from 4.0 --to 3.0
  
  # Rename from 3.0 to 4.0
  python cortex-toolkit/rename_planning_system_version.py --from 3.0 --to 4.0
        """
    )
    
    parser.add_argument(
        '--from',
        dest='from_version',
        required=True,
        help='Source version (e.g., 4.0)'
    )
    
    parser.add_argument(
        '--to',
        dest='to_version',
        required=True,
        help='Target version (e.g., 3.0)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path.cwd(),
        help='Project root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Validate versions
    if not re.match(r'^\d+\.\d+$', args.from_version):
        print(f"❌ Invalid source version format: {args.from_version}")
        print("   Expected format: X.Y (e.g., 4.0)")
        sys.exit(1)
    
    if not re.match(r'^\d+\.\d+$', args.to_version):
        print(f"❌ Invalid target version format: {args.to_version}")
        print("   Expected format: X.Y (e.g., 3.0)")
        sys.exit(1)
    
    # Initialize renamer
    renamer = PlanningSystemRenamer(
        project_root=args.project_root,
        from_version=args.from_version,
        to_version=args.to_version,
        dry_run=args.dry_run
    )
    
    # Perform renaming
    print(f"🚀 CORTEX Planning System Version Renamer")
    print(f"   Project Root: {args.project_root}")
    print(f"   From: Planning System {args.from_version}")
    print(f"   To:   Planning System {args.to_version}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be modified")
    
    stats = renamer.scan_and_rename()
    renamer.print_summary(stats)


if __name__ == '__main__':
    main()
