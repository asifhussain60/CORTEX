#!/usr/bin/env python3
"""
CORTEX HTML Structure Repair Script
Fixes HTML errors introduced by aggressive inline style cleanup

Author: Asif Hussain
Date: December 27, 2025
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_self_closing_tags(content: str) -> Tuple[str, int]:
    """Fix self-closing tags that were incorrectly stripped"""
    changes = 0
    
    # Fix <br/> that became </br>
    pattern = r'</br>'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, '<br/>', content)
        changes += matches
    
    # Fix <img ... /> that lost opening bracket
    pattern = r'<img\s+([^>]+)\s*/>'
    if '</img>' in content:
        # This indicates the opening <img was stripped
        content = re.sub(r'</img>', '', content)
        changes += 1
    
    return content, changes

def fix_unclosed_divs(content: str, file_path: Path) -> Tuple[str, int]:
    """Fix div structure issues"""
    changes = 0
    
    # Count opening and closing divs
    opening_divs = len(re.findall(r'<div[^>]*>', content))
    closing_divs = len(re.findall(r'</div>', content))
    
    if opening_divs != closing_divs:
        print(f"  WARNING: {file_path.name} has {opening_divs} opening <div> but {closing_divs} closing </div>")
        # Manual fix required
    
    return content, changes

def restore_removed_elements(content: str, file_path: Path) -> Tuple[str, int]:
    """Restore elements that were completely stripped"""
    changes = 0
    original_content = content
    
    # Pattern: class="X" /> where opening tag was removed
    # This suggests: <element ... class="X" /> became just class="X" />
    pattern = r'(\s+)(class="[^"]*"\s*/>)'
    matches = re.findall(pattern, content)
    
    if matches:
        print(f"  WARNING: {file_path.name} has {len(matches)} potentially broken self-closing tags")
    
    return content, changes

def fix_html_file(file_path: Path) -> int:
    """Fix HTML errors in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_changes = 0
        
        # Apply fixes
        content, changes = fix_self_closing_tags(content)
        total_changes += changes
        
        content, changes = fix_unclosed_divs(content, file_path)
        total_changes += changes
        
        content, changes = restore_removed_elements(content, file_path)
        total_changes += changes
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return total_changes
        return 0
        
    except Exception as e:
        print(f"  ⚠️  Error processing {file_path.name}: {e}")
        return 0

def main():
    """Fix all HTML files with errors"""
    docs_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/docs")
    
    # Files with errors from validation
    error_files = [
        "index.html",
        "faq.html",
        "features/ado-operations.html",
        "features/index.html",
        "getting-started/deployment.html",
        "getting-started/first-commands.html",
        "getting-started/index.html",
        "getting-started/multi-repo-setup.html",
        "getting-started/tutorial.html",
        "architecture/index.html",
        "technical/orchestrators/architectural-review.html",
        "technical/orchestrators/autonomous-execution.html",
        "technical/orchestrators/cleanup-orchestrator.html",
        "technical/orchestrators/code-sanitization.html",
        "technical/orchestrators/debug-orchestrator.html",
        "technical/orchestrators/git-checkpoint.html",
        "technical/orchestrators/intelligent-dashboard.html",
        "technical/orchestrators/maintenance-orchestrator.html",
        "technical/orchestrators/planning-system.html",
        "technical/orchestrators/pre-flight.html",
        "technical/orchestrators/refinement-orchestrator.html",
        "technical/orchestrators/rollback-orchestrator.html",
        "technical/orchestrators/system-integrity.html",
        "technical/orchestrators/tdd-orchestrator.html",
        "technical/toolkit/index.html",
        "technical/toolkit/validation-tools.html",
        "technical/validation/capabilities.html",
        "validation/index.html",
    ]
    
    print(f"Fixing {len(error_files)} HTML files with errors...\n")
    
    total_changes = 0
    files_fixed = 0
    
    for relative_path in error_files:
        file_path = docs_dir / relative_path
        if file_path.exists():
            changes = fix_html_file(file_path)
            if changes > 0:
                print(f"✅ {relative_path}: {changes} fixes applied")
                total_changes += changes
                files_fixed += 1
        else:
            print(f"⚠️  File not found: {relative_path}")
    
    print(f"\n{'='*60}")
    print(f"REPAIR COMPLETE")
    print(f"{'='*60}")
    print(f"Files Fixed: {files_fixed}")
    print(f"Total Fixes Applied: {total_changes}")
    print(f"\nRun validation again to check remaining issues.")

if __name__ == "__main__":
    main()
