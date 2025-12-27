#!/usr/bin/env python3
"""Comprehensive HTML repair using html5lib for proper parsing."""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

def repair_html_with_html5lib(file_path: Path, dry_run: bool = False) -> dict:
    """Repair HTML using html5lib parser which follows HTML5 spec exactly.
    
    html5lib advantages:
    - Handles unclosed tags exactly like browsers do
    - Creates proper tree structure
    - Auto-closes tags in correct order
    - Preserves semantic meaning
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Parse with html5lib - it handles HTML exactly like browsers
        soup = BeautifulSoup(original_content, 'html5lib')
        
        # html5lib adds html/head/body if missing, which is correct HTML5
        # Generate output
        repaired_content = str(soup)
        
        changes = {
            'file': file_path,
            'original_size': len(original_content),
            'repaired_size': len(repaired_content),
            'modified': original_content != repaired_content
        }
        
        if not dry_run and changes['modified']:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(repaired_content)
        
        return changes
        
    except Exception as e:
        return {'file': file_path, 'error': str(e)}

def main():
    """Repair all HTML files using html5lib."""
    docs_dir = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    print("🔧 HTML5 Standards-Compliant Repair (html5lib)")
    print("=" * 60)
    print("Using html5lib parser - repairs HTML exactly like browsers\n")
    
    files_to_repair = list(docs_dir.rglob('*.html'))
    print(f"Files to process: {len(files_to_repair)}\n")
    
    modified_count = 0
    error_count = 0
    
    for file_path in sorted(files_to_repair):
        result = repair_html_with_html5lib(file_path)
        
        if 'error' in result:
            print(f"❌ {file_path.relative_to(docs_dir)}")
            print(f"   Error: {result['error']}\n")
            error_count += 1
        elif result['modified']:
            size_diff = result['repaired_size'] - result['original_size']
            sign = '+' if size_diff > 0 else ''
            print(f"✅ {file_path.relative_to(docs_dir)} ({sign}{size_diff} bytes)")
            modified_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Repaired: {modified_count} files")
    
    if error_count > 0:
        print(f"❌ Errors: {error_count} files")
    
    print("\n💡 html5lib ensures browser-compatible HTML structure")
    
    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
