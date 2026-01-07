#!/usr/bin/env python3
"""
CORTEX Footer Remover

Removes footer elements from Level 1 and Level 2 pages per glassmorphism design standards.
Level 1/2 pages should use breadcrumbs for navigation, not footers.

Author: Asif Hussain
Version: 1.0.0
"""

import os
import re
from pathlib import Path

def remove_footer_from_file(filepath: Path) -> bool:
    """Remove footer element from HTML file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Pattern to match footer element (handles multi-line)
        footer_pattern = r'\s*<footer[^>]*>[\s\S]*?</footer>\s*'
        
        if re.search(footer_pattern, content):
            new_content = re.sub(footer_pattern, '\n', content)
            filepath.write_text(new_content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"  ⚠️  Error processing {filepath}: {e}")
        return False

def main():
    """Main execution."""
    # Use absolute path to docs folder
    docs_path = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    # Pages that should have footers removed (Level 1 and Level 2)
    # Excluding index.html (home page) which SHOULD have footer
    level1_dirs = [
        'security', 'architecture', 'features', 'orchestrators', 
        'knowledge', 'getting-started', 'toolkit-manager', 'technical',
        'roi-calculator', 'lens', 'token-optimization', 'sts', 'governance'
    ]
    
    removed_count = 0
    processed_files = []
    
    print("🧹 CORTEX Footer Remover")
    print("=" * 50)
    print(f"Docs path: {docs_path}")
    print()
    
    for dir_name in level1_dirs:
        dir_path = docs_path / dir_name
        if not dir_path.exists():
            continue
            
        # Process all HTML files in this directory and subdirectories
        for html_file in dir_path.rglob('*.html'):
            if remove_footer_from_file(html_file):
                removed_count += 1
                processed_files.append(str(html_file.relative_to(docs_path)))
                print(f"  ✅ Removed footer: {html_file.relative_to(docs_path)}")
    
    print()
    print("=" * 50)
    print(f"✅ Removed footers from {removed_count} files")
    
    if processed_files:
        print("\nProcessed files:")
        for f in processed_files[:10]:
            print(f"  • {f}")
        if len(processed_files) > 10:
            print(f"  ... and {len(processed_files) - 10} more")

if __name__ == '__main__':
    main()
