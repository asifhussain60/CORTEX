#!/usr/bin/env python3
"""
Remove Separator Lines from CORTEX Files

Purpose: Remove all horizontal separator lines that break into multiple lines
         in VS Code Copilot Chat interface.

Issue: Separator characters (━━━, ═══, ───, ___) render incorrectly in VS Code
       Copilot Chat, breaking into multiple lines instead of single horizontal rule.

Solution: Remove ALL separator lines from CORTEX response templates and documentation.

Author: Asif Hussain
Date: 2025-11-15
Related: YAML Migration Phase 0.5
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Separator patterns to remove
SEPARATOR_PATTERNS = [
    r'^[━═─_-]{3,}\s*$',  # Lines of repeated separator characters
    r'^\s*[#]\s*[━═─_-]{3,}\s*$',  # Commented separator lines
    r'^[╚╔╗╝╠╣╦╩╬║].*[╚╔╗╝╠╣╦╩╬║]\s*$',  # Box drawing characters
]

# Files to process
FILES_TO_CLEAN = [
    'cortex-brain/templates/response-templates.yaml',
    '.github/copilot-instructions.md',
]


def remove_separators(content: str) -> Tuple[str, int]:
    """
    Remove separator lines from content.
    
    Args:
        content: File content to process
        
    Returns:
        Tuple of (cleaned content, number of lines removed)
    """
    lines = content.splitlines(keepends=True)
    cleaned_lines = []
    removed_count = 0
    
    for line in lines:
        # Check if line matches any separator pattern
        is_separator = False
        for pattern in SEPARATOR_PATTERNS:
            if re.match(pattern, line.strip()):
                is_separator = True
                removed_count += 1
                break
        
        if not is_separator:
            cleaned_lines.append(line)
    
    return ''.join(cleaned_lines), removed_count


def clean_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Remove separators from a single file.
    
    Args:
        file_path: Path to file to clean
        dry_run: If True, only report what would be changed
        
    Returns:
        Tuple of (success, lines_removed)
    """
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False, 0
    
    # Read original content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Remove separators
    cleaned_content, removed_count = remove_separators(original_content)
    
    if removed_count == 0:
        print(f"✅ {file_path.name}: No separators found")
        return True, 0
    
    if dry_run:
        print(f"📋 {file_path.name}: Would remove {removed_count} separator lines")
        return True, removed_count
    
    # Write cleaned content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✅ {file_path.name}: Removed {removed_count} separator lines")
    return True, removed_count


def main():
    """Main execution."""
    dry_run = '--dry-run' in sys.argv
    
    print("🧹 CORTEX Separator Line Removal")
    print("=" * 70)
    if dry_run:
        print("Mode: DRY RUN (no changes will be made)")
    else:
        print("Mode: EXECUTE (files will be modified)")
    print()
    
    # Get CORTEX root
    cortex_root = Path(__file__).parent.parent
    
    total_removed = 0
    success_count = 0
    fail_count = 0
    
    for file_rel_path in FILES_TO_CLEAN:
        file_path = cortex_root / file_rel_path
        success, removed = clean_file(file_path, dry_run=dry_run)
        
        if success:
            success_count += 1
            total_removed += removed
        else:
            fail_count += 1
    
    print()
    print("=" * 70)
    print(f"Results: {success_count} files processed, {fail_count} failures")
    print(f"Total separator lines removed: {total_removed}")
    
    if dry_run:
        print()
        print("This was a DRY RUN. Run without --dry-run to apply changes.")
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
