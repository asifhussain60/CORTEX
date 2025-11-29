#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Garbled UTF-8 in Source Markdown Files

The source markdown files have Windows-1252 encoded bytes that were
misinterpreted as UTF-8, resulting in garbled text like:
- ΓÇö instead of —
- Γ£à instead of ✓
- ≡ƒôï instead of 🎯

This script fixes these by converting back to proper UTF-8.
"""

import sys
import io
from pathlib import Path
import re

# Force UTF-8 encoding for stdout/stderr
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# Mapping of garbled patterns to correct UTF-8 characters
FIXES = {
    # Em dash
    'ΓÇö': '—',
    'ΓÇô': '–',  # En dash
    
    # Quotes
    'ΓÇ£': '"',
    'ΓÇ¥': '"',
    'ΓÇÖ': ''',
    'ΓÇÖ': ''',
    
    # Other punctuation
    'ΓÇª': '…',
    'Γäó': '™',
    
    # Arrows
    'ΓåÆ': '→',  # Rightward arrow
    'Γåê': '←',  # Leftward arrow
    
    # Checkmarks and symbols
    'Γ£à': '✓',
    '≡ƒÿÉ': '😐',
    '≡ƒôï': '📋',
    '≡ƒöä': '📊',
    'ΓÜá∩╕Å': '⚠️',
    '≡ƒ¢í∩╕Å': '🛡️',
    '≡ƒƒú': '🎨',
    '≡ƒÜÇ': '💡',
    
    # Additional emoji patterns
    'Γ£à': '✅',  # Check mark button
    '≡ƒôï': '📋',  # Clipboard
    'Γ¥î': '❌',   # Cross mark
    
}


def fix_file(file_path: Path) -> tuple[bool, int]:
    """
    Fix garbled UTF-8 in a single file.
    
    Returns:
        (changed, num_fixes) tuple
    """
    try:
        # Read file as UTF-8
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Apply fixes
        num_fixes = 0
        for garbled, correct in FIXES.items():
            if garbled in content:
                count = content.count(garbled)
                content = content.replace(garbled, correct)
                num_fixes += count
                print(f"  '{garbled}' → '{correct}' ({count}x)")
        
        # Write back if changed
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True, num_fixes
        return False, 0
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False, 0


def main():
    """Fix all markdown files in docs directory."""
    print("🔧 Fixing Garbled UTF-8 in Source Files\n")
    print("=" * 60)
    
    # Find all markdown files
    docs_dir = Path('docs')
    md_files = list(docs_dir.rglob('*.md'))
    
    print(f"\nFound {len(md_files)} markdown files")
    print()
    
    total_fixed = 0
    total_changes = 0
    
    for md_file in md_files:
        # Check if file has garbled text
        try:
            content = md_file.read_text(encoding='utf-8')
            has_garbled = any(pattern in content for pattern in FIXES.keys())
            
            if has_garbled:
                print(f"📝 {md_file.relative_to(docs_dir)}")
                changed, num_fixes = fix_file(md_file)
                if changed:
                    total_fixed += 1
                    total_changes += num_fixes
                    print(f"  ✓ Fixed {num_fixes} issues\n")
        except Exception as e:
            print(f"✗ Error reading {md_file}: {e}\n")
    
    print("=" * 60)
    print(f"\n✅ Fixed {total_changes} issues in {total_fixed} files")
    print("\nNext steps:")
    print("  1. Review changes: git diff")
    print("  2. Rebuild site: mkdocs build --clean")
    print("  3. Verify encoding: python tests/test_mkdocs_encoding.py")


if __name__ == '__main__':
    main()
