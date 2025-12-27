#!/usr/bin/env python3
"""Fix missing closing HTML tags across documentation."""

import os
from pathlib import Path

def fix_missing_closing_tags(file_path: Path) -> bool:
    """Add missing </html> tags if they're missing.
    
    Returns:
        True if file was modified, False otherwise
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has </body> but no </html>
    if '</body>' in content and '</html>' not in content:
        # Add </html> after the last </body>
        content = content.replace('</body>', '</body>\n</html>')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Process all HTML files in docs/."""
    docs_dir = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    fixed_count = 0
    for html_file in docs_dir.rglob('*.html'):
        if fix_missing_closing_tags(html_file):
            print(f"✅ Fixed: {html_file.relative_to(docs_dir)}")
            fixed_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
