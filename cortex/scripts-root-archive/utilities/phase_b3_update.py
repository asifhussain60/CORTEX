#!/usr/bin/env python3
"""
Phase B-3 Automated Replacement: remaining test files

Updates all src.* imports to cortex.* in all remaining test files.
Strategy: Comprehensive directory scan excluding Phase B-1 and B-2 files.
"""

import os
import re
from pathlib import Path

REPLACEMENTS = {
    r'from src\.': 'from cortex.',
    r'import src': 'import cortex',
}

def update_file(filepath):
    """Update imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for pattern, replacement in REPLACEMENTS.items():
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"ERROR in {filepath}: {e}")
        return None

def find_remaining_test_files():
    """Find all test files NOT in Phase B-1 or B-2."""
    remaining_files = []
    
    # Exclude patterns for B-1 and B-2
    exclude_patterns = [
        'tests/unit/domain_brain',
        'tests/unit/core',
        'tests/unit/orchestrators',
    ]
    
    if os.path.exists('tests'):
        for dirpath, dirnames, filenames in os.walk('tests'):
            # Skip excluded directories
            skip = False
            for exclude in exclude_patterns:
                if dirpath.startswith(exclude):
                    skip = True
                    break
            if skip:
                continue
            
            for filename in filenames:
                if filename.startswith('test_') and filename.endswith('.py'):
                    filepath = os.path.join(dirpath, filename)
                    # Check if file has src.* imports
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if re.search(r'from src\.|import src', content):
                                remaining_files.append(filepath)
                    except:
                        pass
    
    return sorted(remaining_files)

def main():
    """Update all remaining test files."""
    print("=" * 70)
    print("PHASE B-3: Updating remaining test files")
    print("=" * 70)
    print()
    
    remaining_files = find_remaining_test_files()
    print(f"Found {len(remaining_files)} remaining test files with src.* imports")
    print()
    
    updated = 0
    skipped = 0
    errors = 0
    
    for filepath in remaining_files:
        result = update_file(filepath)
        if result is True:
            print(f"✓ {filepath}")
            updated += 1
        elif result is False:
            print(f"⏭️  {filepath} (no changes)")
            skipped += 1
        else:
            print(f"✗ {filepath}")
            errors += 1
    
    print()
    print("=" * 70)
    print(f"Results: Updated {updated}, Skipped {skipped}, Errors {errors}")
    print("=" * 70)
    
    return errors == 0

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
