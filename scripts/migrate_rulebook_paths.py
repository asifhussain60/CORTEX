#!/usr/bin/env python3
"""
CORTEX Rulebook Path Migration Script

Automatically updates all Python files to use new organized directory structure.

Usage:
    python3 scripts/migrate_rulebook_paths.py [--dry-run] [--verbose]

Author: CORTEX System
Date: November 25, 2025
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Path mappings: old_path -> new_path
PATH_MIGRATIONS = {
    'cortex-brain/protection/brain-protection-rules.yaml': 'cortex-brain/protection/brain-protection-rules.yaml',
    'cortex-brain/templates/response-templates.yaml': 'cortex-brain/templates/response-templates.yaml',
    'cortex-brain/templates/response-templates-condensed.yaml': 'cortex-brain/templates/response-templates-condensed.yaml',
    'cortex-brain/templates/response-templates-enhanced.yaml': 'cortex-brain/templates/response-templates-enhanced.yaml',
    'cortex-brain/operations/cleanup-rules.yaml': 'cortex-brain/operations/cleanup-rules.yaml',
    'cortex-brain/operations/publish-config.yaml': 'cortex-brain/operations/publish-config.yaml',
    'cortex-brain/operations/operations-config.yaml': 'cortex-brain/operations/operations-config.yaml',
    'cortex-brain/learning/knowledge-graph.yaml': 'cortex-brain/learning/knowledge-graph.yaml',
    'cortex-brain/learning/lessons-learned.yaml': 'cortex-brain/learning/lessons-learned.yaml',
    'cortex-brain/learning/user-dictionary.yaml': 'cortex-brain/learning/user-dictionary.yaml',
    'cortex-brain/metadata/capabilities.yaml': 'cortex-brain/metadata/capabilities.yaml',
    'cortex-brain/metadata/module-definitions.yaml': 'cortex-brain/metadata/module-definitions.yaml',
    'cortex-brain/metadata/development-context.yaml': 'cortex-brain/metadata/development-context.yaml',
}

# Directories to scan
SCAN_DIRS = [
    'src/',
    'tests/',
    'scripts/',
]

# Files to exclude (archives, publish directories)
EXCLUDE_PATTERNS = [
    '*/archives/*',
    '*/publish/*',
    '*/dist/*',
    '*/__pycache__/*',
    '*.pyc',
]


def should_exclude(file_path: Path) -> bool:
    """Check if file should be excluded from migration."""
    str_path = str(file_path)
    return any(pattern.replace('*', '') in str_path for pattern in EXCLUDE_PATTERNS)


def migrate_file(file_path: Path, dry_run: bool = False, verbose: bool = False) -> Tuple[int, List[str]]:
    """
    Migrate file paths in a single Python file.
    
    Returns:
        Tuple of (changes_count, change_descriptions)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        changes = []
        
        # Replace each old path with new path
        for old_path, new_path in PATH_MIGRATIONS.items():
            # Match various quote styles and contexts
            patterns = [
                (rf"(['\"]){re.escape(old_path)}(['\"])", rf"\1{new_path}\2"),  # Quoted strings
                (rf"(Path\(['\"]){re.escape(old_path)}(['\"])\)", rf"\1{new_path}\2)"),  # Path() calls
                (rf"(default=)['\"]{ re.escape(old_path)}['\"]", rf"\1'{new_path}'"),  # default= args
            ]
            
            for pattern, replacement in patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    content = re.sub(pattern, replacement, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        changes.append(f"  Line {line_num}: {old_path} → {new_path}")
        
        # Write changes if any
        if content != original_content:
            if not dry_run:
                file_path.write_text(content, encoding='utf-8')
            
            if verbose or dry_run:
                print(f"\n✅ {file_path}")
                for change in changes:
                    print(change)
            
            return len(changes), changes
        
        return 0, []
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return 0, []


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate CORTEX rulebook paths')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--verbose', action='store_true', help='Show detailed changes')
    args = parser.parse_args()
    
    print("🧠 CORTEX Rulebook Path Migration")
    print("=" * 60)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be modified\n")
    
    # Collect all Python files
    python_files = []
    project_root = Path(__file__).parent.parent
    
    for scan_dir in SCAN_DIRS:
        dir_path = project_root / scan_dir
        if dir_path.exists():
            for py_file in dir_path.rglob('*.py'):
                if not should_exclude(py_file):
                    python_files.append(py_file)
    
    print(f"📁 Scanning {len(python_files)} Python files...\n")
    
    # Process files
    total_changes = 0
    files_modified = 0
    all_changes: Dict[Path, List[str]] = {}
    
    for py_file in python_files:
        changes_count, changes = migrate_file(py_file, dry_run=args.dry_run, verbose=args.verbose)
        if changes_count > 0:
            total_changes += changes_count
            files_modified += 1
            all_changes[py_file] = changes
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary")
    print("=" * 60)
    print(f"Files scanned: {len(python_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total changes: {total_changes}")
    
    if args.dry_run:
        print("\n⚠️  This was a DRY RUN. Re-run without --dry-run to apply changes.")
    else:
        print("\n✅ Migration complete!")
    
    # Show file list
    if files_modified > 0 and not args.verbose:
        print("\n📝 Modified files:")
        for file_path in sorted(all_changes.keys()):
            print(f"  • {file_path.relative_to(project_root)}")
    
    return 0 if files_modified > 0 or args.dry_run else 1


if __name__ == '__main__':
    sys.exit(main())
