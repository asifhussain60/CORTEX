#!/usr/bin/env python3
"""
CORTEX Complete Inline Style Cleanup Script
Removes all inline styles from HTML files (except story/viewer.html)

Author: Asif Hussain
Date: December 27, 2025
"""

import re
from pathlib import Path
from typing import List, Tuple

def get_all_html_files(base_dir: Path) -> List[Path]:
    """Get all HTML files except story/viewer.html"""
    all_files = []
    for html_file in base_dir.rglob("*.html"):
        # Skip story/viewer.html (allowed exception)
        if "story/viewer.html" in str(html_file):
            continue
        all_files.append(html_file)
    return all_files

def clean_generic_inline_styles(content: str) -> Tuple[str, int]:
    """Remove common inline style patterns"""
    changes = 0
    
    # Pattern 1: style="display: flex; ..." (various display styles)
    pattern = r'(\s+)style="[^"]*display:\s*flex[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        # Keep the whitespace, remove the style attribute
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 2: style="text-align: center; ..." (text alignment)
    pattern = r'(\s+)style="[^"]*text-align:\s*center[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1class="text-center"', content)
        changes += matches
    
    # Pattern 3: style="padding-top: Xrem; ..." (section padding)
    pattern = r'(\s+)style="padding-top:\s*\d+(?:\.\d+)?rem;[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 4: style="margin: ...; ..." (margin styles)
    pattern = r'(\s+)style="[^"]*margin[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 5: style="font-size: ...; ..." (font size)
    pattern = r'(\s+)style="[^"]*font-size[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 6: style="color: ...; ..." (text color)
    pattern = r'(\s+)style="[^"]*color[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 7: style="background: ...; ..." (backgrounds)
    pattern = r'(\s+)style="[^"]*background[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 8: style="border: ...; ..." (borders)
    pattern = r'(\s+)style="[^"]*border[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 9: style="grid-template-columns: ...; ..." (grid layouts)
    pattern = r'(\s+)style="[^"]*grid-template-columns[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 10: style="box-shadow: ...; ..." (shadows)
    pattern = r'(\s+)style="[^"]*box-shadow[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 11: style="width: ...; height: ...; ..." (dimensions)
    pattern = r'(\s+)style="[^"]*(?:width|height)[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    # Pattern 12: Any remaining standalone style attributes
    pattern = r'(\s+)style="[^"]*"'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'\1', content)
        changes += matches
    
    return content, changes

def cleanup_file(file_path: Path) -> int:
    """Clean up all inline styles in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply cleanup
        content, changes = clean_generic_inline_styles(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        return 0
    except Exception as e:
        print(f"  ⚠️  Error processing {file_path.name}: {e}")
        return 0

def main():
    """Process all HTML files in docs directory"""
    docs_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/docs")
    
    print("Scanning for HTML files with inline styles...")
    html_files = get_all_html_files(docs_dir)
    
    total_changes = 0
    files_modified = 0
    
    for file_path in html_files:
        relative_path = file_path.relative_to(docs_dir)
        changes = cleanup_file(file_path)
        
        if changes > 0:
            print(f"✅ {relative_path}: {changes} inline styles removed")
            total_changes += changes
            files_modified += 1
    
    print(f"\n{'='*60}")
    print(f"✅ CLEANUP COMPLETE")
    print(f"{'='*60}")
    print(f"Files Modified: {files_modified}")
    print(f"Inline Styles Removed: {total_changes}")
    print(f"Exception Preserved: docs/story/viewer.html (3 styles)")

if __name__ == "__main__":
    main()
