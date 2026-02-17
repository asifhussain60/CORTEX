#!/usr/bin/env python3
"""
Eliminate Redirect Stub Files

Removes redirect stub files and updates all imports to point directly
to the actual implementation in cortex_brain.

Author: CORTEX Framework
Phase: 91.8 - Production Readiness
CORE Rules: CORE-002 (no stubs), CORE-035 (no duplicates)
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


def find_redirect_stubs(workspace: Path) -> List[Path]:
    """Find all redirect stub files in cortex/core/.
    
    Args:
        workspace: Workspace root path
        
    Returns:
        List of redirect stub file paths
    """
    redirect_stubs = []
    
    for py_file in workspace.rglob('cortex/core/**/*.py'):
        if py_file.name == '__init__.py':
            continue
        
        try:
            content = py_file.read_text()
            lines = [
                line for line in content.split('\n')
                if line.strip()
                and not line.strip().startswith('#')
                and not line.strip().startswith('"""')
                and not line.strip().endswith('"""')
            ]
            
            # Check if it's a redirect stub (very few actual code lines)
            if len(lines) <= 3 and ('REDIRECT' in content or 'Re-export' in content):
                redirect_stubs.append(py_file)
        except Exception:
            continue
    
    return redirect_stubs


def find_target_module(stub_file: Path) -> str:
    """Extract the target module from redirect stub file.
    
    Args:
        stub_file: Path to redirect stub file
        
    Returns:
        Target module path (e.g., 'cortex_intelligence.memory.tier2_adaptive.governance.pii_detection')
    """
    content = stub_file.read_text()
    
    # Look for REDIRECT comment with target module
    match = re.search(r'REDIRECT:.*→\s*([a-z_\.]+)', content)
    if match:
        return match.group(1)
    
    # Look for 'from X import *' pattern
    match = re.search(r'from\s+(cortex_brain\.[a-z_\.]+)\s+import', content)
    if match:
        return match.group(1)
    
    return ""


def find_imports(stub_file: Path, workspace: Path) -> List[Tuple[Path, str]]:
    """Find all files importing from a redirect stub.
    
    Args:
        stub_file: Path to redirect stub file
        workspace: Workspace root path
        
    Returns:
        List of (file_path, line_content) tuples
    """
    module = str(stub_file.relative_to(workspace)).replace('/', '.').replace('.py', '')
    imports = []
    
    # Search in tests and cortex directories
    for search_dir in ['tests', 'cortex']:
        try:
            result = subprocess.run(
                ['grep', '-rn', f'from {module}', search_dir, '--include=*.py'],
                capture_output=True,
                text=True,
                cwd=workspace
            )
            
            for line in result.stdout.split('\n'):
                if line:
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        file_path = workspace / parts[0]
                        line_content = parts[2]
                        imports.append((file_path, line_content))
        except Exception:
            continue
    
    return imports


def update_import(file_path: Path, old_import: str, new_module: str) -> bool:
    """Update an import statement to point to the correct module.
    
    Args:
        file_path: Path to file containing the import
        old_import: Old import line
        new_module: New module path
        
    Returns:
        True if updated successfully
    """
    try:
        content = file_path.read_text()
        
        # Replace the module name in the import
        old_module_pattern = r'from\s+([a-z_\.]+)\s+import'
        match = re.search(old_module_pattern, old_import)
        if match:
            old_module = match.group(1)
            new_import = old_import.replace(old_module, new_module)
            content = content.replace(old_import, new_import)
            file_path.write_text(content)
            return True
    except Exception as e:
        print(f"  Error updating {file_path}: {e}")
    
    return False


def main() -> None:
    """Main execution function."""
    workspace = Path.cwd()
    
    print("🔍 Phase 91.8: Eliminate Redirect Stubs")
    print(f"Workspace: {workspace}\n")
    
    # Step 1: Find all redirect stubs
    print("Step 1: Finding redirect stub files...")
    redirect_stubs = find_redirect_stubs(workspace)
    print(f"Found {len(redirect_stubs)} redirect stub files\n")
    
    # Step 2: Process each stub
    files_to_delete = []
    updates_made = 0
    
    for stub_file in redirect_stubs:
        rel_path = stub_file.relative_to(workspace)
        print(f"Processing: {rel_path}")
        
        # Find target module
        target_module = find_target_module(stub_file)
        if not target_module:
            print(f"  ⚠️  Could not find target module, skipping")
            continue
        
        print(f"  Target: {target_module}")
        
        # Find all imports
        imports = find_imports(stub_file, workspace)
        print(f"  Found {len(imports)} imports")
        
        # Update each import
        for import_file, import_line in imports:
            if update_import(import_file, import_line, target_module):
                updates_made += 1
                print(f"    ✓ Updated {import_file.relative_to(workspace)}")
        
        files_to_delete.append(stub_file)
        print()
    
    # Step 3: Delete stub files
    print(f"Step 2: Deleting {len(files_to_delete)} redirect stub files...")
    for stub_file in files_to_delete:
        stub_file.unlink()
        print(f"  ✓ Deleted {stub_file.relative_to(workspace)}")
    
    print(f"\n✅ Complete!")
    print(f"  Updated: {updates_made} imports")
    print(f"  Deleted: {len(files_to_delete)} stub files")


if __name__ == "__main__":
    main()
