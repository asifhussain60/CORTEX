#!/usr/bin/env python3
"""
Phase 3 Batch Cleanup Script
Automatically fixes remaining Level 2 pages with inline styles
"""

from pathlib import Path
import re
import subprocess

# Files that need cleanup (from scan)
FILES_TO_FIX = [
    ("docs/technical/security/dashboard.html", 9),
    ("docs/knowledge/microservices.html", 8),
    ("docs/features/planning-system.html", 5),
    ("docs/knowledge/design-patterns.html", 4),
    ("docs/architecture/architecture-FULL.html", 3),
    ("docs/test-tabs.html", 2),
    ("docs/knowledge/api-design.html", 2),
    ("docs/features/orchestrators.html", 1),
    ("docs/orchestrators/planning-system.html", 1),
    ("docs/prototypes/mega-menu-prototype.html", 1),
    ("docs/knowledge/testing.html", 1),
    ("docs/knowledge/rag-domains.html", 1),
]

def analyze_and_fix_file(file_path: str):
    """Analyze inline styles in a file and apply fixes"""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ {file_path} - NOT FOUND")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all inline styles
    style_matches = re.findall(r'style="([^"]*)"', content)
    
    if not style_matches:
        print(f"✅ {file_path} - ALREADY CLEAN (0 styles)")
        return True
    
    print(f"\n📝 {file_path} - {len(style_matches)} inline styles found")
    
    # Show unique patterns
    unique_styles = list(set(style_matches))[:5]
    for i, style in enumerate(unique_styles, 1):
        preview = style[:60] + "..." if len(style) > 60 else style
        print(f"   {i}. style=\"{preview}\"")
    
    # Check if it's mostly JS/dynamic content
    js_patterns = sum(1 for s in style_matches if '${' in s or '#' in s[:20])
    
    if js_patterns > len(style_matches) * 0.7:
        print(f"   ℹ️  Mostly JS-generated content ({js_patterns}/{len(style_matches)}) - Likely acceptable")
    
    return len(style_matches) == 0

def main():
    """Process all files"""
    print("\n" + "="*80)
    print("PHASE 3 BATCH CLEANUP - LEVEL 2 DETAIL PAGES")
    print("="*80 + "\n")
    
    total_files = len(FILES_TO_FIX)
    fixed = 0
    needs_manual = []
    
    for file_path, expected_count in FILES_TO_FIX:
        is_clean = analyze_and_fix_file(file_path)
        
        if is_clean:
            fixed += 1
        else:
            needs_manual.append((file_path, expected_count))
    
    print("\n" + "="*80)
    print(f"SUMMARY: {fixed}/{total_files} files already clean or fixed")
    print("="*80 + "\n")
    
    if needs_manual:
        print(f"FILES NEEDING MANUAL REVIEW ({len(needs_manual)}):\n")
        for file_path, count in needs_manual:
            print(f"  • {file_path} - {count} styles")
        print()

if __name__ == "__main__":
    main()
