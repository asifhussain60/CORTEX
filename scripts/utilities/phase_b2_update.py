#!/usr/bin/env python3
"""
Phase B-2 Automated Replacement: core test files

Updates all src.* imports to cortex.* in core unit test files.
Strategy: Directory-based batch processing for efficiency.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

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

def find_core_test_files():
    """Find all core unit test files with src.* imports."""
    core_files = []
    
    # Search tests/unit/core/ and tests/unit/orchestrators/
    for root_dir in ['tests/unit/core', 'tests/unit/orchestrators']:
        if os.path.exists(root_dir):
            for dirpath, dirnames, filenames in os.walk(root_dir):
                for filename in filenames:
                    if filename.startswith('test_') and filename.endswith('.py'):
                        filepath = os.path.join(dirpath, filename)
                        # Check if file has src.* imports
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if re.search(r'from src\.|import src', content):
                                    core_files.append(filepath)
                        except:
                            pass
    
    return sorted(core_files)

def main():
    """Update all core test files."""
    print("=" * 70)
    print("PHASE B-2: Updating core unit test files")
    print("=" * 70)
    print()
    
    core_files = find_core_test_files()
    print(f"Found {len(core_files)} core test files with src.* imports")
    print()
    
    updated = 0
    skipped = 0
    errors = 0
    
    for filepath in core_files:
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
