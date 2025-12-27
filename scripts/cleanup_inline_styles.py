#!/usr/bin/env python3
"""
CORTEX Inline Style Cleanup Script
Batch processes orchestrator HTML files to replace inline styles with CSS classes

Author: Asif Hussain
Date: December 27, 2025
"""

import re
from pathlib import Path

# Pattern replacements
REPLACEMENTS = [
    # Metadata item labels
    (r'<span style="color:#94a3b8">([^<]+):</span>', r'<span class="metadata-item-label">\1:</span>'),
    
    # Metadata item values
    (r'<span style="color:var\(--primary\);font-weight:600">([^<]+)</span>', r'<span class="metadata-item-value">\1</span>'),
    
    # Feature icons
    (r'<div style="font-size:2rem;margin-bottom:1rem">([^<]+)</div>', r'<div class="feature-icon">\1</div>'),
    
    # Feature titles
    (r'<div style="font-size:1\.25rem;font-weight:600;color:#f1f5f9;margin-bottom:0\.75rem">([^<]+)</div>', r'<div class="feature-title">\1</div>'),
    
    # Feature descriptions
    (r'<div style="color:#94a3b8">([^<]+)</div>', r'<div class="feature-description">\1</div>'),
]

def cleanup_file(file_path):
    """Clean up inline styles in a single file"""
    print(f"Processing: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    for pattern, replacement in REPLACEMENTS:
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            changes += matches
            print(f"  - Replaced {matches} instances of pattern")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Saved {changes} changes")
        return changes
    else:
        print(f"  ℹ️  No changes needed")
        return 0

def main():
    """Process all orchestrator HTML files"""
    orchestrator_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/docs/technical/orchestrators")
    
    # Target files
    files = [
        "tdd-orchestrator.html",
        "refinement-orchestrator.html",
        "cleanup-orchestrator.html",
        "autonomous-execution.html",
        "intelligent-dashboard.html",
        "pre-flight.html",
        "debug-orchestrator.html",
        "rollback-orchestrator.html",
        "maintenance-orchestrator.html",
        "ado-planning.html",
        "architectural-review.html",
        "system-integrity.html",
        "code-sanitization.html",
        "git-checkpoint.html",
        "cortex-lens.html",
    ]
    
    total_changes = 0
    for filename in files:
        file_path = orchestrator_dir / filename
        if file_path.exists():
            changes = cleanup_file(file_path)
            total_changes += changes
        else:
            print(f"⚠️  File not found: {filename}")
    
    print(f"\n✅ COMPLETE: {total_changes} inline styles removed across {len(files)} files")

if __name__ == "__main__":
    main()
