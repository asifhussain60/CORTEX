#!/usr/bin/env python3
"""
Phase B-1 Automated Replacement: domain_brain test files

Updates all src.* imports to cortex.* in domain_brain test files.
Strategy: Python-based replacement (more reliable than sed for macOS)
"""

import os
import re
from pathlib import Path

# Replacement mappings
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

def main():
    """Update all domain_brain test files."""
    domain_brain_tests = [
        'tests/unit/domain_brain/test_ac_db_006_01.py',
        'tests/unit/domain_brain/test_ac_db_005_01.py',
        'tests/unit/domain_brain/test_ac_db_003_01.py',
        'tests/unit/domain_brain/test_ac_db_004_01.py',
        'tests/unit/domain_brain/test_ac_db_e03.py',
        'tests/unit/domain_brain/test_ac_db_e02.py',
        'tests/unit/domain_brain/test_ac_db_e01.py',
        'tests/unit/domain_brain/test_ac_db_002_01.py',
        'tests/unit/domain_brain/test_ac_db_001_01.py',
        'tests/unit/domain_brain/test_ac_db_007_01.py',
        'tests/unit/domain_brain/test_ac_db_008_01.py',
        'tests/unit/domain_brain/test_ac_db_009_01.py',
    ]
    
    print("=" * 70)
    print("PHASE B-1: Updating domain_brain test files")
    print("=" * 70)
    print()
    
    updated = 0
    skipped = 0
    errors = 0
    
    for filepath in domain_brain_tests:
        if not os.path.exists(filepath):
            print(f"⏭️  SKIP: {filepath} (not found)")
            skipped += 1
            continue
        
        result = update_file(filepath)
        if result is True:
            print(f"✓ UPDATE: {filepath}")
            updated += 1
        elif result is False:
            print(f"⏭️  SKIP: {filepath} (no changes needed)")
            skipped += 1
        else:
            print(f"✗ ERROR: {filepath}")
            errors += 1
    
    print()
    print("=" * 70)
    print(f"Results: Updated {updated}, Skipped {skipped}, Errors {errors}")
    print("=" * 70)
    
    return errors == 0

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
