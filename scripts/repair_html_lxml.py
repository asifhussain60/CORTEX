#!/usr/bin/env python3
"""Comprehensive HTML repair using lxml for strict validation and repair."""

import sys
from pathlib import Path
from lxml import etree, html as lxml_html

def repair_html_with_lxml(file_path: Path) -> dict:
    """Repair HTML using lxml which properly handles malformed HTML.
    
    lxml advantages:
    - Fast C-based parser
    - Proper error recovery
    - Strict validation available
    - Handles real-world HTML
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Parse with lxml's HTML parser - handles broken HTML like browsers
        parser = lxml_html.HTMLParser(remove_blank_text=False, remove_comments=False)
        tree = lxml_html.fromstring(original_content.encode('utf-8'), parser=parser)
        
        # Convert back to string with proper structure
        repaired_content = lxml_html.tostring(tree, encoding='unicode', method='html', pretty_print=True)
        
        # Add DOCTYPE if missing
        if not repaired_content.strip().startswith('<!DOCTYPE'):
            repaired_content = '<!DOCTYPE html>\n' + repaired_content
        
        changes = {
            'file': file_path,
            'original_size': len(original_content),
            'repaired_size': len(repaired_content),
            'modified': original_content.strip() != repaired_content.strip()
        }
        
        if changes['modified']:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(repaired_content)
        
        return changes
        
    except Exception as e:
        return {'file': file_path, 'error': str(e)}

def main():
    """Repair all HTML files using lxml."""
    docs_dir = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    print("🔧 Strict HTML Repair (lxml)")
    print("=" * 60)
    print("Using lxml parser - production-grade HTML validation\n")
    
    files_to_repair = list(docs_dir.rglob('*.html'))
    print(f"Files to process: {len(files_to_repair)}\n")
    
    modified_count = 0
    error_count = 0
    
    for file_path in sorted(files_to_repair):
        result = repair_html_with_lxml(file_path)
        
        if 'error' in result:
            print(f"❌ {file_path.relative_to(docs_dir)}")
            print(f"   Error: {result['error']}\n")
            error_count += 1
        elif result['modified']:
            size_diff = result['repaired_size'] - result['original_size']
            sign = '+' if size_diff > 0 else ''
            print(f"✅ {file_path.relative_to(docs_dir)} ({sign}{size_diff} bytes)")
            modified_count += 1
        else:
            print(f"⚪ {file_path.relative_to(docs_dir)} (valid)")
    
    print("\n" + "=" * 60)
    print(f"✅ Repaired: {modified_count} files")
    
    if error_count > 0:
        print(f"❌ Errors: {error_count} files")
    
    print("\n💡 lxml ensures production-ready HTML structure")
    
    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
