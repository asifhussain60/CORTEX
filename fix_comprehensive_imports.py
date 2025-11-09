#!/usr/bin/env python3
"""
Comprehensive import fixer for CORTEX codebase
Fixes various incorrect import patterns
"""

import re
from pathlib import Path

def fix_imports_comprehensive(file_path):
    """Fix all import patterns in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: from CORTEX.src. -> from src.
    content = re.sub(r'from CORTEX\.src\.', 'from src.', content)
    content = re.sub(r'import CORTEX\.src\.', 'import src.', content)
    
    # Pattern 2: from plugins. -> from src.plugins. (for files in src/)
    if 'src/' in str(file_path):
        content = re.sub(r'\nfrom plugins\.', '\nfrom src.plugins.', content)
        content = re.sub(r'\nimport plugins\.', '\nimport src.plugins.', content)
    
    # Pattern 3: from cortex_agents. -> from src.cortex_agents. (for files NOT in src/cortex_agents/)
    if 'src/cortex_agents' not in str(file_path) and 'src/' in str(file_path):
        content = re.sub(r'\nfrom cortex_agents\.', '\nfrom src.cortex_agents.', content)
        content = re.sub(r'\nimport cortex_agents\.', '\nimport src.cortex_agents.', content)
    
    # Pattern 4: from workflows. -> from src.workflows. (for files NOT in src/workflows/)
    if 'src/workflows' not in str(file_path) and 'src/' in str(file_path):
        content = re.sub(r'\nfrom workflows\.', '\nfrom src.workflows.', content)
        content = re.sub(r'\nimport workflows\.', '\nimport src.workflows.', content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all source files"""
    root = Path(__file__).parent
    
    fixed_count = 0
    
    # Fix all Python files in src/
    src_dir = root / 'src'
    for src_file in src_dir.rglob('*.py'):
        if fix_imports_comprehensive(src_file):
            print(f"Fixed: {src_file.relative_to(root)}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
