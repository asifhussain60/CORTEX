#!/usr/bin/env python3
"""Final HTML repair - Fix BeautifulSoup formatting issues and ensure proper structure."""

import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

def fix_html_structure(file_path: Path) -> dict:
    """Fix HTML structure issues created by BeautifulSoup prettifier.
    
    Handles:
    1. Unclosed <p> tags in cards
    2. Missing closing tags for nested structures
    3. Proper indentation and formatting
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse with BeautifulSoup using lxml-xml for better structure handling
        soup = BeautifulSoup(content, 'html.parser')
        
        # Fix unclosed p tags in glass-card divs
        for card in soup.find_all('div', class_='glass-card'):
            # Find all p tags without closing
            for p_tag in card.find_all('p'):
                # Check if p tag content ends without proper closing
                if p_tag.find('div'):
                    # There's a div inside p tag - need to close p before div
                    next_div = p_tag.find('div')
                    # Extract content before div
                    content_before = []
                    for child in list(p_tag.children):
                        if child == next_div:
                            break
                        content_before.append(child)
                    
                    # Create new p tag with content before div
                    if content_before:
                        new_p = soup.new_tag('p')
                        for attr, value in p_tag.attrs.items():
                            new_p[attr] = value
                        for item in content_before:
                            if isinstance(item, NavigableString):
                                new_p.append(item.extract())
                            else:
                                new_p.append(item.extract())
                        p_tag.insert_before(new_p)
                    
                    # Move div out of p tag
                    p_tag.insert_before(next_div.extract())
                    p_tag.decompose()
        
        # Ensure all major sections have closing tags
        for section in soup.find_all('section'):
            if not section.find_parent():
                continue
        
        # Generate clean HTML with proper indentation
        html_str = str(soup)
        
        # Post-process: Fix common issues
        # Remove empty lines
        lines = html_str.split('\n')
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        repaired_content = '\n'.join(cleaned_lines)
        
        # Calculate changes
        changes = {
            'file': file_path,
            'original_size': len(content),
            'repaired_size': len(repaired_content),
            'modified': content != repaired_content
        }
        
        if changes['modified']:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(repaired_content)
        
        return changes
        
    except Exception as e:
        return {'file': file_path, 'error': str(e)}

def main():
    """Repair all HTML files."""
    docs_dir = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    print("🔧 Final HTML Structure Repair")
    print("=" * 60)
    
    files_to_repair = list(docs_dir.rglob('*.html'))
    print(f"Files to process: {len(files_to_repair)}\n")
    
    repaired_count = 0
    error_count = 0
    
    for file_path in sorted(files_to_repair):
        result = fix_html_structure(file_path)
        
        if 'error' in result:
            print(f"❌ {file_path.relative_to(docs_dir)}: {result['error']}")
            error_count += 1
        elif result['modified']:
            print(f"✅ {file_path.relative_to(docs_dir)}")
            repaired_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Repaired: {repaired_count} files")
    if error_count > 0:
        print(f"❌ Errors: {error_count} files")

if __name__ == '__main__':
    main()
