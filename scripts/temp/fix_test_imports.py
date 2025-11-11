#!/usr/bin/env python3
"""
Fix import statements in test files
Replaces 'from CORTEX.src.' with 'from src.'
"""

import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace 'from CORTEX.src.' with 'from src.'
    original_content = content
    content = re.sub(r'from CORTEX\.src\.', 'from src.', content)
    
    # Replace 'import CORTEX.src.' with 'import src.'
    content = re.sub(r'import CORTEX\.src\.', 'import src.', content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all test files"""
    root = Path(__file__).parent
    tests_dir = root / 'tests'
    
    fixed_count = 0
    for test_file in tests_dir.rglob('*.py'):
        if fix_imports_in_file(test_file):
            print(f"Fixed: {test_file.relative_to(root)}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
