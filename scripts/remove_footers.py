#!/usr/bin/env python3
"""
Remove footer sections from all HTML documentation files.
"""
import re
from pathlib import Path

def remove_footer_from_file(file_path: Path) -> bool:
    """Remove footer section from an HTML file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Pattern 1: <!-- Footer --> comment with <footer> tag
        pattern1 = r'\s*<!-- Footer -->\s*<footer[^>]*>.*?</footer>\s*'
        content = re.sub(pattern1, '\n', content, flags=re.DOTALL)
        
        # Pattern 2: Just <footer> tag without comment
        pattern2 = r'\s*<footer[^>]*>.*?</footer>\s*'
        content = re.sub(pattern2, '\n', content, flags=re.DOTALL)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    docs_dir = Path('docs')
    html_files = list(docs_dir.rglob('*.html'))
    
    modified_count = 0
    for html_file in html_files:
        if remove_footer_from_file(html_file):
            print(f"✅ Removed footer from: {html_file}")
            modified_count += 1
    
    print(f"\n🎉 Modified {modified_count} files")

if __name__ == '__main__':
    main()
