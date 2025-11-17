#!/usr/bin/env python3
"""
Fix relative imports in src/ directory
Converts relative imports to absolute imports for better compatibility
"""

import re
from pathlib import Path

def fix_relative_imports(file_path, root_path):
    """Fix relative imports in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Convert relative imports to absolute
    # from .. -> from src.
    # from ... -> from src.
    
    # Get the module path for this file
    rel_path = file_path.relative_to(root_path / 'src')
    module_parts = rel_path.parts[:-1]  # Exclude filename
    
    # Pattern: from ..something import X
    # Count the dots to determine parent levels
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Match: from ..module import something
        match = re.match(r'^(\s*)from (\.+)([a-zA-Z_][\w\.]*)\s+import\s+(.+)$', line)
        if match:
            indent, dots, module, imports = match.groups()
            dot_count = len(dots)
            
            if dot_count >= 2:  # Relative import
                # Convert to absolute
                new_line = f"{indent}from src.{module} import {imports}"
                new_lines.append(new_line)
                continue
        
        # Match: from .. import something (import from parent __init__)
        match = re.match(r'^(\s*)from (\.+)\s+import\s+(.+)$', line)
        if match:
            indent, dots, imports = match.groups()
            dot_count = len(dots)
            
            if dot_count >= 2:  # Relative import from parent
                # This is trickier - need to know what module we're in
                if len(module_parts) > 0:
                    parent_module = '.'.join(module_parts[: -(dot_count - 1)] if dot_count > 1 else module_parts)
                    new_line = f"{indent}from src.{parent_module} import {imports}"
                    new_lines.append(new_line)
                    continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all source files"""
    root = Path(__file__).parent
    src_dir = root / 'src'
    
    fixed_count = 0
    
    for src_file in src_dir.rglob('*.py'):
        if src_file.name == '__init__.py':
            continue  # Skip __init__ files for now
        
        if fix_relative_imports(src_file, root):
            print(f"Fixed: {src_file.relative_to(root)}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
