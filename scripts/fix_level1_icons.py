#!/usr/bin/env python3
"""
Fix Font Awesome Icon Classes in Level 1 Pages
===============================================

Issue: Missing 'fas' prefix on Font Awesome icons causing icons not to display.
Fix: Add 'fas' prefix to all fa-* icon classes that are missing it.

Following cortex-docs.prompt.md v2.0 - Python-only HTML generation.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

project_root = Path(__file__).parent.parent


def fix_font_awesome_classes(html_file: Path) -> dict:
    """
    Fix missing Font Awesome class prefixes.
    
    Args:
        html_file: Path to HTML file
        
    Returns:
        dict with changes made
    """
    print(f"\n🔧 Processing: {html_file.name}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    changes = []
    
    # Find all <i> tags with class attributes
    icons = soup.find_all('i', class_=True)
    
    for icon in icons:
        classes = icon.get('class', [])
        
        # Check if has fa-* but missing fas/far/fab/fal prefix
        has_fa_icon = any(cls.startswith('fa-') for cls in classes)
        has_fa_prefix = any(cls in ['fas', 'far', 'fab', 'fal', 'fad'] for cls in classes)
        
        if has_fa_icon and not has_fa_prefix:
            # Add 'fas' prefix (solid icons are most common)
            icon['class'].insert(0, 'fas')
            
            old_classes = ' '.join(classes)
            new_classes = ' '.join(icon['class'])
            changes.append(f"  ✓ {old_classes} → {new_classes}")
    
    if changes:
        # Save fixed HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"✅ Fixed {len(changes)} icon(s)")
        for change in changes:
            print(change)
    else:
        print("  ℹ️  No fixes needed")
    
    return {
        "file": str(html_file),
        "fixes": len(changes),
        "details": changes
    }


def process_all_level1_pages():
    """Process all Level 1 pages"""
    docs_dir = project_root / "docs"
    
    level1_pages = [
        'architecture',
        'security',
        'features',
        'story',
        'sts',
        'getting-started',
        'knowledge',
        'learning-paths',
        'lens',
        'token-optimization',
        'toolkit-manager'
    ]
    
    print("🚀 Fixing Font Awesome Icons in Level 1 Pages")
    print(f"📋 Pages to check: {len(level1_pages)}")
    
    results = []
    for page_name in level1_pages:
        page_path = docs_dir / page_name / "index.html"
        
        if not page_path.exists():
            print(f"⚠️  Skipping {page_name}: File not found")
            continue
        
        result = fix_font_awesome_classes(page_path)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    
    total_fixes = sum(r['fixes'] for r in results)
    fixed_files = sum(1 for r in results if r['fixes'] > 0)
    
    print(f"✅ Files processed: {len(results)}")
    print(f"✅ Files fixed: {fixed_files}")
    print(f"✅ Total icon fixes: {total_fixes}")
    
    if total_fixes == 0:
        print("\n🎉 All icons already have correct Font Awesome prefixes!")
    else:
        print(f"\n🎉 Fixed {total_fixes} icon class issues!")


if __name__ == "__main__":
    process_all_level1_pages()
