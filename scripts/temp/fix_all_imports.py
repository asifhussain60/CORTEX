#!/usr/bin/env python3
"""
Fix import statements in both source and test files
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
    
    # Also fix relative imports within cortex_agents
    # from CORTEX.src.cortex_agents. -> from src.cortex_agents. OR from cortex_agents.
    # We'll keep from src.cortex_agents. for now
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all source and test files"""
    root = Path(__file__).parent
    
    fixed_count = 0
    
    # Fix source files
    src_dir = root / 'src'
    for src_file in src_dir.rglob('*.py'):
        if fix_imports_in_file(src_file):
            print(f"Fixed: {src_file.relative_to(root)}")
            fixed_count += 1
    
    # Fix test files
    tests_dir = root / 'tests'
    for test_file in tests_dir.rglob('*.py'):
        if fix_imports_in_file(test_file):
            print(f"Fixed: {test_file.relative_to(root)}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
