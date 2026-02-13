#!/usr/bin/env python3
"""
CORTEX Company Reference Sanitizer
Morphs company-specific references to generic equivalents while maintaining consistency.

Authority: User request - sanitize HealthEquity/Hqy references in _workspaces/sts/sample-apps/_Real
Purpose: Make sample code generic for testing CORTEX capabilities
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Sanitization mapping (case-sensitive patterns)
SANITIZATION_MAP = {
    # Company names
    'HealthEquity': 'GenericCompany',
    'healthequity': 'genericcompany',
    'healthEquity': 'genericCompany',
    'HEALTHEQUITY': 'GENERICCOMPANY',
    
    # Company abbreviation (Hqy -> Gcc for Generic Company Code)
    'Hqy': 'Gcc',
    'HQY': 'GCC',
    'hqy': 'gcc',
    
    # Domains
    'www.healthEquity.com': 'www.genericcompany.com',
    'healthequity.com': 'genericcompany.com',
    
    # Method/class prefixes
    'RegisterHqy': 'RegisterGcc',
    'ConfigureHqy': 'ConfigureGcc',
    'ExistingHqy': 'ExistingGcc',
    'HqyLog': 'GccLog',
    'HqyDomain': 'GccDomain',
}

# File extensions to process
TEXT_EXTENSIONS = {'.md', '.json', '.txt', '.cs', '.csproj', '.sln', '.config', '.xml', '.yaml', '.yml'}

# Files to skip (binaries, packages, etc.)
SKIP_PATTERNS = {
    'node_modules',
    '.git',
    'bin',
    'obj',
    'packages',
    '.dll',
    '.exe',
    '.pdb',
    'package-lock.json',  # Skip - contains hashes that might match
}


def should_process_file(file_path: Path) -> bool:
    """Determine if file should be processed."""
    # Skip if in excluded directory
    for skip_pattern in SKIP_PATTERNS:
        if skip_pattern in str(file_path):
            return False
    
    # Only process text files
    return file_path.suffix in TEXT_EXTENSIONS


def sanitize_content(content: str, file_path: Path) -> Tuple[str, int]:
    """
    Sanitize content by replacing company-specific references.
    Returns: (sanitized_content, replacement_count)
    """
    sanitized = content
    total_replacements = 0
    
    # Apply replacements in order (most specific first)
    for old_text, new_text in SANITIZATION_MAP.items():
        # Count occurrences
        count = sanitized.count(old_text)
        if count > 0:
            sanitized = sanitized.replace(old_text, new_text)
            total_replacements += count
            print(f"  └─ {file_path.name}: '{old_text}' → '{new_text}' ({count}x)")
    
    return sanitized, total_replacements


def sanitize_directory(root_path: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Recursively sanitize all files in directory.
    Returns: Statistics dictionary
    """
    stats = {
        'files_scanned': 0,
        'files_modified': 0,
        'total_replacements': 0,
    }
    
    print(f"\n🔧 Sanitizing: {root_path}")
    print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()
    
    for file_path in root_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        if not should_process_file(file_path):
            continue
        
        stats['files_scanned'] += 1
        
        try:
            # Read file
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Sanitize
            sanitized, replacements = sanitize_content(content, file_path)
            
            if replacements > 0:
                stats['files_modified'] += 1
                stats['total_replacements'] += replacements
                
                # Write back (if not dry run)
                if not dry_run:
                    file_path.write_text(sanitized, encoding='utf-8')
        
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
    
    return stats


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sanitize company-specific references in STS sample apps')
    parser.add_argument('--target', default='_workspaces/sts/sample-apps/_Real',
                       help='Target directory to sanitize')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    # Get workspace root
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent
    target_path = workspace_root / args.target
    
    if not target_path.exists():
        print(f"❌ Target path does not exist: {target_path}")
        return 1
    
    # Run sanitization
    stats = sanitize_directory(target_path, dry_run=args.dry_run)
    
    # Report
    print()
    print("=" * 60)
    print("📊 Sanitization Complete")
    print("=" * 60)
    print(f"Files Scanned:      {stats['files_scanned']}")
    print(f"Files Modified:     {stats['files_modified']}")
    print(f"Total Replacements: {stats['total_replacements']}")
    print()
    
    if args.dry_run:
        print("⚠️  DRY RUN - No files were modified")
        print("   Run without --dry-run to apply changes")
    else:
        print("✅ Changes applied successfully")
        print()
        print("Mapping used:")
        for old, new in SANITIZATION_MAP.items():
            print(f"  • {old} → {new}")
    
    return 0


if __name__ == '__main__':
    exit(main())
