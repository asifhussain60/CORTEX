"""
Refactor ModificationRequest API Usage

Converts old API:
  ModificationRequest(operation="...", target_path="...", content="...", rationale="...")

To new API:
  ModificationRequest(intent="...", description="...", files=["..."], justification="...")

Author: Asif Hussain
"""

import re
from pathlib import Path
from typing import List, Tuple

def find_old_api_usage(content: str) -> List[Tuple[int, str]]:
    """Find all lines with old ModificationRequest API."""
    matches = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Look for old parameters
        if 'ModificationRequest' in line and any(param in line for param in ['operation=', 'target_path=', 'content=', 'rationale=']):
            matches.append((i, line))
    
    return matches

def convert_api_call(old_call: str) -> str:
    """Convert old API call to new API."""
    
    # Extract parameters from old API
    operation_match = re.search(r'operation=["\']([^"\']+)["\']', old_call)
    target_path_match = re.search(r'target_path=["\']([^"\']+)["\']', old_call)
    content_match = re.search(r'content=["\']([^"\']+)["\']', old_call)
    rationale_match = re.search(r'rationale=["\']([^"\']+)["\']', old_call)
    
    # Map to new API
    intent = operation_match.group(1) if operation_match else "modify"
    files_value = f'["{target_path_match.group(1)}"]' if target_path_match else '[]'
    description = content_match.group(1) if content_match else "No description"
    justification = rationale_match.group(1) if rationale_match else None
    
    # Build new API call
    new_call = old_call
    
    # Replace parameters
    new_call = re.sub(r'operation=["\'][^"\']+["\']', f'intent="{intent}"', new_call)
    new_call = re.sub(r'target_path=["\'][^"\']+["\']', f'files={files_value}', new_call)
    new_call = re.sub(r'content=["\'][^"\']+["\']', f'description="{description}"', new_call)
    
    if justification:
        new_call = re.sub(r'rationale=["\'][^"\']+["\']', f'justification="{justification}"', new_call)
    else:
        new_call = re.sub(r',?\s*rationale=["\'][^"\']*["\']', '', new_call)
    
    return new_call

def refactor_file(file_path: Path, dry_run: bool = True) -> dict:
    """Refactor a single file."""
    try:
        rel_path = file_path.relative_to(Path.cwd())
    except ValueError:
        rel_path = file_path
    
    print(f"\nProcessing: {rel_path}")
    
    content = file_path.read_text(encoding='utf-8')
    old_usage = find_old_api_usage(content)
    
    if not old_usage:
        print("   OK: No old API usage found")
        return {"file": str(file_path), "changes": 0}
    
    print(f"   Found {len(old_usage)} old API calls")
    
    changes = 0
    new_content = content
    
    for line_num, old_line in old_usage:
        new_line = convert_api_call(old_line)
        
        if old_line != new_line:
            print(f"   Line {line_num}:")
            print(f"     OLD: {old_line.strip()}")
            print(f"     NEW: {new_line.strip()}")
            
            new_content = new_content.replace(old_line, new_line)
            changes += 1
    
    if not dry_run and changes > 0:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"   DONE: Written {changes} changes")
    elif dry_run and changes > 0:
        print(f"   DRY RUN: Would write {changes} changes")
    
    return {"file": str(file_path), "changes": changes}

def main(dry_run: bool = True):
    """Main refactoring function."""
    print("ModificationRequest API Refactoring Tool")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}\n")
    
    # Find all test files
    test_files = list(Path('tests').rglob('*.py'))
    
    print(f"Found {len(test_files)} test files\n")
    print("="*60)
    
    results = []
    total_changes = 0
    
    for test_file in test_files:
        result = refactor_file(test_file, dry_run=dry_run)
        results.append(result)
        total_changes += result['changes']
    
    print("\n" + "="*60)
    print(f"\nSummary:")
    print(f"   Files processed: {len(test_files)}")
    print(f"   Files with changes: {sum(1 for r in results if r['changes'] > 0)}")
    print(f"   Total changes: {total_changes}")
    
    if dry_run and total_changes > 0:
        print(f"\n   DRY RUN MODE - No files modified")
        print(f"   Run with --execute flag to apply changes")
    elif total_changes > 0:
        print(f"\n   All changes applied!")

if __name__ == "__main__":
    import sys
    
    # Check for --execute flag
    execute = "--execute" in sys.argv
    
    main(dry_run=not execute)
